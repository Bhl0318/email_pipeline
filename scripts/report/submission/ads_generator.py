#!/usr/bin/env python3
"""ADS（Application Data Sheet, USPTO XFA 表单）生成 —— 本地填表，不走 pdfRest 云。

与旧 old_submission/confirm/fill_xfa_form.py 的差异：
- 数据 XML 生成逻辑（_generate_ads_xml）原样移植；
- 填表方式由"POST pdfRest 云 API"改为**本地 pikepdf 注入 XFA datasets 包**，
  数据不出本机（满足《US递交的改进》对数据管控的要求）。

原理：XFA 表单的数据存在 PDF 的 /Root/AcroForm/XFA 数组里名为 "datasets" 的流中，
形如 <xfa:datasets><xfa:data><us-request>…</us-request></xfa:data></xfa:datasets>。
本模块把 case_info 拼成该数据包、替换模板里的 datasets 流、置 NeedsRendering，
Adobe 打开时按"模板+datasets"重渲染出填好的 ADS。

⚠️ 上线前置/未决：
- 空 ADS.pdf（XFA 版）模板需放到 submission/templates/ADS.pdf（见 common.ADS_TEMPLATE，
  当前仓库未带，需从旧机取回）。
- 数据根节点名 us-request 及各 sf* 节点必须与该 ADS 模板的 XFA 绑定(SOM)一致；
  旧 XML 原为 pdfRest 导入准备，需用真模板 + Adobe 验证绑定，必要时按模板 datasets 微调。
- 动态 XFA 仅 Adobe Acrobat/Reader 渲染；浏览器/LibreOffice 看不到内容，
  故审核页对 ADS 只提供下载、不做内联预览。
- case_info 富结构（Inventors/Applicants/Parent Applications/Priorities/Customer Number/
  Deposit/图纸页数/Continuity Type 等）来源见环节1抽取 + agent_info 表 + 定稿文件，
  由 submission_tasks.fields_json → case_info 的映射另行实现（部分字段仍是缺口）。
"""
import datetime
import re
import sys
import traceback
from pathlib import Path

import pikepdf

from .common import ADS_TEMPLATE


def safe_escape_xml(text):
    """安全转义 XML 特殊字符，避免重复转义（对齐旧 fill_xfa_form.safe_escape_xml）。"""
    if not text:
        return ""
    text = str(text)
    temp = (text.replace('&amp;', '&').replace('&quot;', '"').replace('&apos;', "'"))
    return (temp.replace('&', '&amp;').replace('"', '&quot;').replace("'", '&apos;'))


def _ads_appnum(raw):
    """ADS 母案(Domestic Benefit)申请号规范：美国申请号要纯数字(如 18/649,137 → 18649137)。
    仅当值只由数字+分隔符(/ . , 空格 -)组成时去分隔留数字；含字母的(如 PCT/CN2024/...)原样保留。"""
    s = str(raw or "").strip()
    if s and re.fullmatch(r"[\d\s/.,\-]+", s):
        return re.sub(r"\D", "", s)
    return s


def build_ads_datasets_xml(case_info: dict) -> str:
    """把 case_info 拼成 ADS 的 XFA datasets 数据包 XML（移植自旧 _generate_ads_xml）。
    返回完整的 <xfa:datasets>…</xfa:datasets> 字符串。"""
    inventors = case_info.get('Inventors', [])
    inventor_information = ""
    for inventor in inventors:
        inventor_information += f"""
<sfApplicantInformation>
      <sfAuth>
        <appSeq>1</appSeq>
      </sfAuth>
      <sfApplicantName>
        <prefix/>
        <firstName>{inventor.get("firstName", '')}</firstName>
        <middleName>{inventor.get("middleName", '')}</middleName>
        <lastName>{inventor.get('lastName', '')}</lastName>
        <suffix/>
      </sfApplicantName>
      <sfAppResChk>
        <resCheck>
          <ResidencyRadio>{inventor.get("Residence Information", '')}</ResidencyRadio>
        </resCheck>
        <sfUSres>
          <rsCityTxt/>
          <rsStTxt/>
          <rsCtryTxt/>
        </sfUSres>
        <sfNonUSRes>
          <nonresCity>{inventor.get("City", '')}</nonresCity>
          <nonresCtryList>{inventor.get("Country of Residence", '')}</nonresCtryList>
        </sfNonUSRes>
        <sfMil>
          <actMilDropDown/>
        </sfMil>
      </sfAppResChk>
      <sfCitz>
        <CitizedDropDown/>
      </sfCitz>
      <sfApplicantMail>
        <mailCountry>{inventor.get("Mailing Address of Inventor Country", '')}</mailCountry>
        <postcode>{inventor.get("Mailing Address of Inventor Postal Code", '')}</postcode>
        <address1>{inventor.get("Mailing Address of Inventor address_1", '')}</address1>
        <address2>{inventor.get("Mailing Address of Inventor address_2", '')}</address2>
        <city>{inventor.get("Mailing Address of Inventor city", '')}</city>
        <state>{inventor.get("Mailing Address of Inventor State", '')}</state>
      </sfApplicantMail>
      <sfInventorRepInfo>
        <sfReporgChoice>
          <chkOrg/>
          <org><orgName/></org>
          <sfRepApplicantName>
            <prefix/><firstName/><middleName/><lastName/><suffix/>
          </sfRepApplicantName>
        </sfReporgChoice>
        <sfRepAppResChk>
          <resCheck/>
          <sfUSres><rsCityTxt/><rsStTxt/><rsCtryTxt/></sfUSres>
          <sfNonUSRes><nonresCity/><nonresCtryList/></sfNonUSRes>
          <sfMil><actMilDropDown/></sfMil>
        </sfRepAppResChk>
        <sfRepCitz><CitizedDropDown/></sfRepCitz>
        <sfRepApplicantMail>
          <address1/><address2/><city/><state/><postcode/><mailCountry/>
        </sfRepApplicantMail>
      </sfInventorRepInfo>
    </sfApplicantInformation>
"""

    corr = case_info.get("Correspondence Information", {})
    corr_customer_number = f"""
<sfCorrCustNo>
      <customerNumber>{corr.get("Customer Number", '')}</customerNumber>
    </sfCorrCustNo>
"""
    corr_emails = corr.get("Email Address", []) or []
    corr_email = ""
    for email in corr_emails:
        corr_email += f"<sfemail><email>{email}</email></sfemail>\n"
    if not corr_email:
        corr_email = "<sfemail><email></email></sfemail>"

    appinfo = case_info.get("Application Information", {})
    appinfo_basic = f"""
    <invention-title>{case_info.get("Title", '')}</invention-title>
  <attorney-docket-number>{case_info.get("Our Ref.", '')}</attorney-docket-number>
"""
    appinfo_other = f"""
    <sfAppPos>
        <chkSmallEntity>{appinfo.get("Small Entity Status Claimed", '')}</chkSmallEntity>
        <class/>
        <subclass/>
        <us_suggested-tech_center/>
        <us-total_number_of_drawing-sheets>{appinfo.get("Total Number of Drawing Sheets", '')}</us-total_number_of_drawing-sheets>
        <us-suggested_representative_figure></us-suggested_representative_figure>
        <application_type>{appinfo.get("Application Type", '')}</application_type>
        <us_submission_type>{appinfo.get("Subject Matter", '')}</us_submission_type>
      </sfAppPos>
"""

    fbr = case_info.get("Filing_By_Reference", {})
    filing_by_reference = f"""
    <sffilingby>
      <app>{fbr.get("app", '')}</app>
      <date>{fbr.get("date", '')}</date>
      <intellectual>{fbr.get("intellectual", '')}</intellectual>
    </sffilingby>
"""

    rep = case_info.get("Representative Information", {})
    rep_check = "<attornyChoice>customer-number</attornyChoice>"
    rep_customer_number = f"""
    <sfcustomerNumber>
<customerNumberTxt>{rep.get("Customer Number", '')}</customerNumberTxt>
</sfcustomerNumber>
"""

    domestic_benefit = ""
    for idx, app in enumerate(case_info.get("Parent Applications", []), start=1):
        domestic_benefit += f"""
<sfDomesticContinuity>
      <sfDomesContinuity>
        <sfdomesContAppStat>
          <domAppStatusList>{app.get("Prior Application Status", '')}</domAppStatusList>
          <domsequence>{idx}</domsequence>
        </sfdomesContAppStat>
      </sfDomesContinuity>
      <sfDomesContInfo>
        <domappNumber>{app.get("Application No", '')}</domappNumber>
        <domesContList>{app.get('Continuity Type', '')}</domesContList>
        <domPriorAppNum>{_ads_appnum(app.get("Prior Application Number", ''))}</domPriorAppNum>
        <DateTimeField1>{app.get("Filing Date", '')}</DateTimeField1>
      </sfDomesContInfo>
      <sfDomesContinfoPatent>
        <patAppNum/><domesContList/><patContType/><patprDate/><patPatNum/><patIsDate/>
      </sfDomesContinfoPatent>
    </sfDomesticContinuity>
"""

    foreign_priority = ""
    for priority in case_info.get("Priorities", []):
        foreign_priority += f"""
<sfForeignPriorityInfo>
      <frprAppNum>{priority.get("Priority", '')}</frprAppNum>
      <accessCode>{priority.get("DAS code", '')}</accessCode>
      <frprctryList>{priority.get("Country", '')}</frprctryList>
      <frprParentDate>{priority.get("Priority date", '')}</frprParentDate>
      <prClaim/>
      <forsequence>1</forsequence>
    </sfForeignPriorityInfo>
"""

    assignee_applicant = ""
    for idx, applicant in enumerate(case_info.get("Applicants", []), start=1):
        # XFA 单位申请人需 chkOrg 命中才显示 orgName 子表单；有单位名时兜底勾选，
        # 否则裸 case_info（未过 fields_mapping）会丢单位名。
        org_name = applicant.get("Organization Name", '') or applicant.get("Name", '')
        chk_org = applicant.get("chkOrg", '') or (1 if org_name else '')
        legal = applicant.get("Assigneebtn", '') or ("assignee" if org_name else '')
        assignee_applicant += f"""
    <sfAssigneeInformation>
      <sfAssigneebtn>
        <appSeq>{idx}</appSeq>
        <lstInvType/>
        <LegalRadio>{legal}</LegalRadio>
      </sfAssigneebtn>
      <sfAssigneorgChoice>
        <chkOrg>{chk_org}</chkOrg>
        <sforgName><orgName>{org_name}</orgName></sforgName>
      </sfAssigneorgChoice>
      <sfApplicantName>
        <prefix/><first-name/><middle-name/><last-name/><suffix/>
      </sfApplicantName>
      <sfAssigneeAddress>
        <address-1>{applicant.get("Address", '')}</address-1>
        <address-2>{applicant.get("Applicant address2", '')}</address-2>
        <city>{applicant.get("Applicant city", '')}</city>
        <state></state>
        <postcode>{applicant.get("Applicant Postal Code", '')}</postcode>
        <phone></phone>
        <fax></fax>
        <txtCorrCtry>{applicant.get("Nationality", '')}</txtCorrCtry>
      </sfAssigneeAddress>
      <sfAssigneeEmail><email></email></sfAssigneeEmail>
    </sfAssigneeInformation>
"""

    assignee_info = ""
    for idx, assignee in enumerate(case_info.get("Assignees", []), start=1):
        assignee_info += f"""
    <sfNonApplicantInfo>
      <sfNonAsigneeBtn><appSeq>{idx}</appSeq></sfNonAsigneeBtn>
      <sfNonapplicantOrg>
        <chkOrg>1</chkOrg>
        <sfNonOrg><orgName>{assignee.get("Organization Name", '')}</orgName></sfNonOrg>
      </sfNonapplicantOrg>
      <sfApplicantName>
        <prefix/><first-name/><middle-name/><last-name/><suffix/>
      </sfApplicantName>
      <sfAssigneeAddress>
        <address-1>{assignee.get("Address 1", '')}</address-1>
        <address-2>{assignee.get("Address 2", '')}</address-2>
        <city>{assignee.get("City", '')}</city>
        <state></state>
        <postcode>{assignee.get("Postal Code", '')}</postcode>
        <phone/><fax/>
        <txtCorrCtry>{assignee.get("Country", '')}</txtCorrCtry>
        <email/>
      </sfAssigneeAddress>
    </sfNonApplicantInfo>
"""

    sig = case_info.get("Signature", {})
    signature = f"""
    <sfSig>
        <registration-number>{sig.get("Registration Number", '')}</registration-number>
        <last-name>{sig.get("Last Name", '')}</last-name>
        <signature>{sig.get("Signature", '')}</signature>
        <date>{sig.get("Date", '')}</date>
        <first-name>{sig.get("First Name", '')}</first-name>
      </sfSig>
"""

    us_request = f"""<us-request>
  <ContentArea1>
    <chkSecret>0</chkSecret>
    {inventor_information}
  </ContentArea1>
  <ContentArea2>
    <sfCorrepondInfo><corresInfoChk>0</corresInfoChk></sfCorrepondInfo>
    {corr_customer_number}
    <sfCorrAddress>
      <Name1/><Name2/><address1/><address2/><city/><state/><corrCountry/><postcode/><phone/><fax/>
    </sfCorrAddress>
      {corr_email}
    <sfInvTitle/>
    <sfversion/>
    <sfAppinfoFlow>
      {appinfo_other}
    </sfAppinfoFlow>
    <sfPlant><latin_name/><variety/></sfPlant>
    {filing_by_reference}
    <sfPub><early>0</early><nonPublication/></sfPub>
    <sfRepHeader/>
    <sfAttorny>
      <sfrepheader>{rep_check}</sfrepheader>
      <sfAttornyFlow>
        {rep_customer_number}
        <sfAttrynyName>
          <prefix/><first-name/><middle-name/><last-name/><suffix/><attrnyRegNameTxt/><attsequence>1</attsequence>
        </sfAttrynyName>
        <sfrepcfr119>
          <repcfr119RegNameTxt/><prefix/><first-name/><middle-name/><last-name/><suffix/><repsequence>1</repsequence>
        </sfrepcfr119>
      </sfAttornyFlow>
    </sfAttorny>
    <sfDomContinuityHeader/>
    {domestic_benefit}
    <sfForeignPriorityHeader/>
    {foreign_priority}
    <sfpermit><check/></sfpermit>
    <AIATransition><AIACheck>0</AIACheck></AIATransition>
    <authorization><IP>0</IP><EPO>0</EPO></authorization>
    <sfAssigneeHeader/>
    {assignee_applicant}
    <NonApplicantHeader/>
    {assignee_info}
    <sfSignature>
      <sfSigHeader/>
      {signature}
    </sfSignature>
  </ContentArea2>
  <ContentArea3/>
  {appinfo_basic}
  <version-info>2.1</version-info>
  <clientversion>15.7</clientversion>
  <numofpages>8</numofpages>
</us-request>"""

    datasets = (
        '<xfa:datasets xmlns:xfa="http://www.xfa.org/schema/xfa-data/1.0/"><xfa:data>'
        + safe_escape_xml(us_request)
        + '</xfa:data></xfa:datasets>'
    )
    return '<?xml version="1.0" encoding="UTF-8"?>' + datasets


_DATA_RE = re.compile(r"<xfa:data\b[^>]*>.*</xfa:data\s*>", re.S)
_USREQ_RE = re.compile(r"<us-request\b.*</us-request\s*>", re.S)


def inject_ads_datasets(template_pdf, datasets_xml: str, out_path) -> None:
    """把数据注入 XFA 模板的 datasets 流并保存（本地 pikepdf，替代旧 pdfRest 云）。

    只替换模板 datasets 里的 <xfa:data>…</xfa:data> 子树，**保留 dd:dataDescription**
    （含重复节点 dd:maxOccur 等绑定约束，丢了会影响多发明人/多优先权等绑定）。
    模板 datasets 无 <xfa:data> 时，回退为整流写入。"""
    template_pdf = Path(template_pdf)
    if not template_pdf.is_file():
        raise FileNotFoundError(f"ADS XFA 模板不存在: {template_pdf}（需放入 submission/templates/ADS.pdf）")
    pdf = pikepdf.open(str(template_pdf))
    acro = pdf.Root.get("/AcroForm")
    if acro is None or "/XFA" not in acro:
        raise ValueError(f"模板不含 XFA 表单: {template_pdf}")
    xfa = acro.XFA
    if not isinstance(xfa, pikepdf.Array):
        # 单一流：整包覆盖（少见）
        xfa.write(datasets_xml.encode("utf-8"))
        acro.NeedsRendering = True
        pdf.save(str(out_path))
        return

    ds_stream = None
    for i in range(0, len(xfa) - 1, 2):
        if str(xfa[i]) == "datasets":
            ds_stream = xfa[i + 1]
            break
    if ds_stream is None:
        raise ValueError("XFA 数组中未找到 datasets 项，无法注入")

    tmpl_ds = bytes(ds_stream.read_bytes()).decode("utf-8", "ignore")
    m = _USREQ_RE.search(datasets_xml)
    data_inner = m.group(0) if m else datasets_xml  # 取生成数据里的 <us-request>…</us-request>

    if _DATA_RE.search(tmpl_ds):
        # 保留 dd:dataDescription，仅替换 <xfa:data> 子树
        new_ds = _DATA_RE.sub("<xfa:data>" + data_inner + "</xfa:data>", tmpl_ds, count=1)
    else:
        # 模板没有 <xfa:data>，在 </xfa:datasets> 前插入
        new_ds = tmpl_ds.replace(
            "</xfa:datasets>", "<xfa:data>" + data_inner + "</xfa:data></xfa:datasets>", 1)
    ds_stream.write(new_ds.encode("utf-8"))
    acro.NeedsRendering = True  # 让 Adobe 重渲染动态 XFA
    pdf.save(str(out_path))


def _free_output_path(output_dir: Path, file_name: str) -> Path:
    """返回可安全写入的输出路径：目标已存在且能删则删（覆盖）；删不掉（Windows 上文件被
    Adobe/浏览器打开或杀软占用）则换唯一名——避免 pikepdf 保存时 os.replace 撞上被锁文件
    报 [WinError 5] 拒绝访问（重复点预览时常见）。"""
    p = output_dir / file_name
    if p.exists():
        try:
            p.unlink()
        except OSError:
            p = output_dir / f"{p.stem}-{datetime.datetime.now().strftime('%H%M%S%f')}{p.suffix}"
    return p


def generate_ads(case_info: dict, output_dir, template_pdf=None) -> dict:
    """生成 ADS PDF（本地 XFA 注入）。
    :return: {"file_path", "file_name"}
    """
    template_pdf = template_pdf or ADS_TEMPLATE
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    file_path = _free_output_path(output_dir, f"{today}-ADS-{ref}.pdf")
    file_name = file_path.name
    datasets_xml = build_ads_datasets_xml(case_info)
    inject_ads_datasets(template_pdf, datasets_xml, file_path)
    return {"file_path": str(file_path), "file_name": file_name, "type": "ADS"}


def generate_ads_flat(case_info: dict, output_dir) -> dict:
    """ADS 在线浏览版：本地 XFA 注入 → pdfRest 扁平化成静态 PDF（普通查看器可见）。

    同时产出 XFA 版（下载/发送用，数据不出本机）。扁平化走云端（会上传文件）；
    失败则回退到"数据核对版 docx"，保证在线浏览不中断。
    :return: {"file_path"(扁平化或回退版,内联用), "file_name", "type":"ADS-flat"|"ADS-preview",
              "xfa_file_path", "xfa_file_name", "warnings"}
    """
    from .common import flatten_pdf
    output_dir = Path(output_dir)
    xfa = generate_ads(case_info, output_dir)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    flat_path = _free_output_path(output_dir, f"{today}-ADS-{ref}-flat.pdf")
    warnings = []
    try:
        flatten_pdf(xfa["file_path"], flat_path)
        return {"file_path": str(flat_path), "file_name": flat_path.name, "type": "ADS-flat",
                "xfa_file_path": xfa["file_path"], "xfa_file_name": xfa["file_name"], "warnings": warnings}
    except Exception as e:
        print(f"[ADS] pdfRest 扁平化失败，回退数据核对版 docx：{e}", file=sys.stderr)
        traceback.print_exc()
        warnings.append(f"ADS 扁平化失败（{e}），在线浏览回退为数据核对版")
        prev = generate_ads_preview(case_info, output_dir)
        return {"file_path": prev["file_path"], "file_name": prev["file_name"], "type": "ADS-preview",
                "xfa_file_path": xfa["file_path"], "xfa_file_name": xfa["file_name"], "warnings": warnings}


def _build_ads_preview_docx(case_info: dict, out_dir):
    """生成 ADS"数据核对版"docx（可读数据单，非官方表单外观）。"""
    from docx import Document
    doc = Document()
    doc.add_heading("Application Data Sheet — 数据核对版", level=1)
    doc.add_paragraph("非正式表单，仅供在线核对；正式递交以 XFA 版为准。")

    def kv_table(rows):
        t = doc.add_table(rows=0, cols=2)
        t.style = "Table Grid"
        for k, v in rows:
            c = t.add_row().cells
            c[0].text = str(k); c[1].text = "" if v is None else str(v)

    ai = case_info.get("Application Information", {})
    doc.add_heading("申请信息", level=2)
    kv_table([
        ("代理所案号", case_info.get("Our Ref.", "")),
        ("申请名称", case_info.get("Title", "")),
        ("Subject Matter", ai.get("Subject Matter", "")),
        ("Application Type", ai.get("Application Type", "")),
        ("Small Entity", ai.get("Small Entity Status Claimed", "")),
        ("图纸页数", ai.get("Total Number of Drawing Sheets", "")),
    ])

    doc.add_heading("发明人", level=2)
    ti = doc.add_table(rows=1, cols=3); ti.style = "Table Grid"
    h = ti.rows[0].cells; h[0].text, h[1].text, h[2].text = "First Name", "Last Name", "全名"
    for inv in case_info.get("Inventors", []):
        c = ti.add_row().cells
        c[0].text, c[1].text, c[2].text = inv.get("firstName", ""), inv.get("lastName", ""), inv.get("name", "")

    doc.add_heading("申请人 / 受让人", level=2)
    ta = doc.add_table(rows=1, cols=4); ta.style = "Table Grid"
    h = ta.rows[0].cells
    h[0].text, h[1].text, h[2].text, h[3].text = "名称", "地址", "国别", "实体"
    for ap in case_info.get("Applicants", []):
        c = ta.add_row().cells
        c[0].text = ap.get("Name", ""); c[1].text = ap.get("Address", "")
        c[2].text = ap.get("Nationality", ""); c[3].text = str(ap.get("Entity", ""))

    if case_info.get("Priorities"):
        doc.add_heading("优先权", level=2)
        tp = doc.add_table(rows=1, cols=4); tp.style = "Table Grid"
        h = tp.rows[0].cells
        h[0].text, h[1].text, h[2].text, h[3].text = "优先权号", "国别", "日期", "DAS"
        for pr in case_info["Priorities"]:
            c = tp.add_row().cells
            c[0].text = pr.get("Priority", ""); c[1].text = pr.get("Country", "")
            c[2].text = pr.get("Priority date", ""); c[3].text = pr.get("DAS code", "")

    if case_info.get("Parent Applications"):
        doc.add_heading("母案", level=2)
        tm = doc.add_table(rows=1, cols=3); tm.style = "Table Grid"
        h = tm.rows[0].cells
        h[0].text, h[1].text, h[2].text = "申请号", "申请日", "Continuity Type"
        for pa in case_info["Parent Applications"]:
            c = tm.add_row().cells
            c[0].text = pa.get("Application No", ""); c[1].text = pa.get("Filing Date", "")
            c[2].text = pa.get("Continuity Type", "")

    corr = case_info.get("Correspondence Information", {})
    sig = case_info.get("Signature", {})
    doc.add_heading("通信 / 签字", level=2)
    kv_table([
        ("Customer Number", corr.get("Customer Number", "")),
        ("Email", ", ".join(corr.get("Email Address", []) or [])),
        ("签字人", sig.get("Name", "")),
        ("执业号", sig.get("Registration Number", "")),
        ("日期", sig.get("Date", "")),
    ])

    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    docx_path = out_dir / f"{today}-ADS数据核对-{ref}.docx"
    doc.save(str(docx_path))
    return docx_path


def generate_ads_preview(case_info: dict, output_dir) -> dict:
    """ADS 数据核对版 PDF（在线浏览用；docx → LibreOffice 转 PDF）。
    :return: {"file_path", "file_name", "type": "ADS-preview"}
    """
    from .preview import docx_to_pdf
    docx_path = _build_ads_preview_docx(case_info, output_dir)
    pdf_path = docx_to_pdf(docx_path, output_dir)
    return {"file_path": str(pdf_path), "file_name": Path(pdf_path).name, "type": "ADS-preview"}


if __name__ == "__main__":
    import sys
    # 自测：只构建 datasets XML（不依赖模板），验证移植无误
    sample = {
        "Our Ref.": "64504-H006US00", "Title": "SMART KNEE BRACE",
        "Inventors": [{"firstName": "Wei", "lastName": "", "Country of Residence": "CN"}],
        "Applicants": [{"Organization Name": "Mebotx", "chkOrg": 1, "Assigneebtn": "assignee"}],
        "Assignees": [], "Parent Applications": [], "Priorities": [],
        "Correspondence Information": {"Customer Number": 194498, "Email Address": ["docketing@x.com"]},
        "Representative Information": {"Customer Number": 194498},
        "Application Information": {"Application Type": "REGULAR", "Subject Matter": "UTL",
                                    "Small Entity Status Claimed": 1, "Total Number of Drawing Sheets": "7"},
        "Filing_By_Reference": {"app": "", "date": "", "intellectual": ""},
        "Signature": {"Registration Number": 82219, "First Name": "Yifei", "Last Name": "Guan",
                      "Signature": "", "Date": "2025-11-28", "title": "Patent Agent"},
    }
    xml = build_ads_datasets_xml(sample)
    print(f"[self-test] datasets XML 长度={len(xml)}，含案号={'64504-H006US00' in xml}，"
          f"含客户号={'194498' in xml}")
    # 默认用包内模板(submission/templates/ADS.pdf)生成到 report/ads_test_out/
    # 传参可覆盖模板：py -m submission.ads_generator <模板路径>
    template = sys.argv[1] if len(sys.argv) > 1 else None
    out_dir = Path(__file__).resolve().parent.parent / "ads_test_out"  # = report/ads_test_out/
    r = generate_ads(sample, out_dir, template_pdf=template)
    print("生成:", r)
