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
        <domPriorAppNum>{app.get("Prior Application Number", '')}</domPriorAppNum>
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
        assignee_applicant += f"""
    <sfAssigneeInformation>
      <sfAssigneebtn>
        <appSeq>{idx}</appSeq>
        <lstInvType/>
        <LegalRadio>{applicant.get("Assigneebtn", '')}</LegalRadio>
      </sfAssigneebtn>
      <sfAssigneorgChoice>
        <chkOrg>{applicant.get("chkOrg", '')}</chkOrg>
        <sforgName><orgName>{applicant.get("Organization Name", '')}</orgName></sforgName>
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


def inject_ads_datasets(template_pdf, datasets_xml: str, out_path) -> None:
    """把 datasets XML 注入 XFA 模板的 datasets 流并保存。
    本地 pikepdf 实现，替代旧 pdfRest 云 API。"""
    template_pdf = Path(template_pdf)
    if not template_pdf.is_file():
        raise FileNotFoundError(f"ADS XFA 模板不存在: {template_pdf}（需从旧机取回放入 submission/templates/）")
    data = datasets_xml.encode("utf-8")
    pdf = pikepdf.open(str(template_pdf))
    acro = pdf.Root.get("/AcroForm")
    if acro is None or "/XFA" not in acro:
        raise ValueError(f"模板不含 XFA 表单: {template_pdf}")
    xfa = acro.XFA
    injected = False
    if isinstance(xfa, pikepdf.Array):
        # [name, stream, name, stream, ...] 形式，定位 "datasets"
        for i in range(0, len(xfa) - 1, 2):
            if str(xfa[i]) == "datasets":
                xfa[i + 1].write(data)
                injected = True
                break
    else:
        # 单一流形式：整包就是一段 XFA，直接覆盖（少见，多为静态/混合）
        xfa.write(data)
        injected = True
    if not injected:
        raise ValueError("XFA 数组中未找到 datasets 项，无法注入")
    acro.NeedsRendering = True  # 让 Adobe 重渲染动态 XFA
    pdf.save(str(out_path))


def generate_ads(case_info: dict, output_dir, template_pdf=None) -> dict:
    """生成 ADS PDF（本地 XFA 注入）。
    :return: {"file_path", "file_name"}
    """
    template_pdf = template_pdf or ADS_TEMPLATE
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    ref = case_info.get("Our Ref.", "UNKNOWN")
    file_name = f"{today}-ADS-{ref}.pdf"
    file_path = output_dir / file_name
    datasets_xml = build_ads_datasets_xml(case_info)
    inject_ads_datasets(template_pdf, datasets_xml, file_path)
    return {"file_path": str(file_path), "file_name": file_name}


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
    print(xml[:600], "...\n")
    print(f"[self-test] datasets XML 长度={len(xml)}，含案号={'64504-H006US00' in xml}，"
          f"含客户号={'194498' in xml}")
    if len(sys.argv) > 1:  # 传模板路径则真注入
        r = generate_ads(sample, "/tmp/ads_out", template_pdf=sys.argv[1])
        print("生成:", r)
