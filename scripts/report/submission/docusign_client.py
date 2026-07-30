#!/usr/bin/env python3
"""DocuSign eSignature 集成（沙盒脚手架）——把需签字件发美代理电子签、API 回收签署版。

用于 US 递交环节5/6：把需签字子集(POA/Transmittal/Petition/Transmittal-submitting-Declarations 等)
放同一信封发 DocuSign 给美代理签，签完经 API 取回签署版 PDF（替代邮箱抓件/改名匹配）。纯确定性调用，无 AI。
签字位按文档类型定锚点（POA/Transmittal→"Signature"、Petition/Declarations→"By:"）+ 偏移；.docx 先转 PDF。

鉴权：JWT Grant（服务端对服务端、无人值守）。前置（DocuSign 后台一次性配置）：
  1. 建 integration key（= client_id），生成/上传 RSA 密钥对（私钥存本地 .pem）；
  2. 拿 API 用户 GUID（user_id）与 API account id；
  3. 首次一次性 admin consent：把 consent_url() 打印的链接在浏览器打开、同意一次。

端点：沙盒(demo) oauth=account-d.docusign.com、REST base 用 userinfo 返回的 base_uri；
     生产改 env=production（oauth=account.docusign.com）。

⚠️ 沙盒脚手架：凭据/私钥留占位（docusign_config.json，参照 docusign_config.example.json）。
   本脚本连真实 DocuSign，按项目规矩只写不跑，由人工在沙盒发起。
依赖：requests、PyJWT（RS256 需 cryptography）。
"""
import base64
import json
import sys
import tempfile
import time
from pathlib import Path

import requests

CONFIG_PATH = Path(__file__).with_name("docusign_config.json")

DEMO_OAUTH_HOST = "account-d.docusign.com"   # 沙盒
PROD_OAUTH_HOST = "account.docusign.com"     # 生产


def load_config(path=None) -> dict:
    p = Path(path or CONFIG_PATH)
    if not p.is_file():
        raise RuntimeError(f"缺配置 {p}（参照同目录 docusign_config.example.json 建；沙盒填 demo 凭据）")
    return json.loads(p.read_text(encoding="utf-8"))


def _firm_key(cfg: dict, firm) -> str:
    """把案件的代理所名（如 'Porus IP LLC'）归一到 firm_accounts 的 key（如 'Porus'）。
    先查 firm_map 精确/大小写不敏感，再按 key 子串包含兜底（'...porus...'→Porus）。找不到返回 ''。"""
    fa = cfg.get("firm_accounts") or {}
    if not fa or not firm:
        return ""
    f = str(firm).strip()
    fmap = cfg.get("firm_map") or {}
    if f in fmap:
        return fmap[f]
    low = f.lower()
    for k, v in fmap.items():          # firm_map 大小写不敏感
        if k.lower() == low:
            return v
    for k in fa:                       # 按账号 key 子串兜底（Metis/Poseidon/Porus）
        if k.lower() in low:
            return k
    return ""


def resolve_account(cfg: dict, firm=None) -> dict:
    """按代理所选 DocuSign 发送账号：返回"共享默认 + 该所账号覆盖"合并后的有效 cfg。
    无 firm_accounts（沙盒单账号）→ 原样返回（老行为不变）。匹配不到 firm → 用 default_firm。
    账号缺 user_id/account_id → 抛错（避免误用别的账号发生产件）。"""
    fa = cfg.get("firm_accounts") or {}
    if not fa:
        return cfg                                     # 单账号（沙盒）老行为
    key = _firm_key(cfg, firm) or cfg.get("default_firm") or ""
    acct = fa.get(key)
    if acct is None:
        raise RuntimeError(f"代理所「{firm}」未匹配到 DocuSign 账号（firm_accounts 无 '{key}'）；"
                           "请在 docusign_config.json 的 firm_map/firm_accounts 补齐")
    merged = {**cfg, **acct}
    merged.pop("firm_accounts", None)
    merged.pop("firm_map", None)
    if not merged.get("user_id") or not merged.get("account_id"):
        raise RuntimeError(f"代理所「{firm}」→账号 '{key}' 的 DocuSign 凭据未配全（缺 user_id/account_id）")
    merged["_firm_key"] = key
    return merged


def _oauth_host(cfg: dict) -> str:
    return PROD_OAUTH_HOST if cfg.get("env") == "production" else DEMO_OAUTH_HOST


def consent_url(cfg: dict) -> str:
    """首次一次性授权同意链接（用有权限的账号在浏览器打开一次即可，之后 JWT 无人值守）。"""
    host = _oauth_host(cfg)
    redirect = cfg.get("redirect_uri", "https://www.docusign.com")
    return (f"https://{host}/oauth/auth?response_type=code&scope=signature%20impersonation"
            f"&client_id={cfg['integration_key']}&redirect_uri={redirect}")


def _private_key(cfg: dict) -> str:
    kp = cfg.get("private_key_path")
    if kp:
        p = Path(kp)
        # 相对路径按本模块所在目录(submission/)解析，不依赖进程工作目录（report_server cwd 不同）；
        # 再退回按 cwd 解析，兼容在 submission/ 里直接跑 CLI 的情况。
        for cand in ([p] if p.is_absolute() else [Path(__file__).with_name(p.name), Path(__file__).parent / kp, p]):
            if cand.is_file():
                return cand.read_text(encoding="utf-8")
    if cfg.get("private_key"):
        return cfg["private_key"]
    raise RuntimeError(f"缺 RSA 私钥：private_key_path={kp!r} 未找到（相对路径按 submission/ 解析）；"
                       "或在配置里给 private_key")


def get_access_token(cfg: dict) -> dict:
    """JWT Grant 换 token。:return: {access_token, base_uri, account_id}"""
    try:
        import jwt  # PyJWT
    except Exception:
        raise RuntimeError("需安装：pip install pyjwt cryptography")
    host = _oauth_host(cfg)
    now = int(time.time())
    assertion = jwt.encode(
        {"iss": cfg["integration_key"], "sub": cfg["user_id"], "aud": host,
         "iat": now, "exp": now + 3600, "scope": "signature impersonation"},
        _private_key(cfg), algorithm="RS256")
    if isinstance(assertion, bytes):        # PyJWT<2 返回 bytes
        assertion = assertion.decode()
    r = requests.post(f"https://{host}/oauth/token", timeout=30, data={
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer", "assertion": assertion})
    if r.status_code != 200:
        raise RuntimeError(f"JWT Grant 失败 {r.status_code}: {r.text}\n"
                         "（若 consent_required：先浏览器打开 consent_url 授权一次）")
    token = r.json()["access_token"]
    ui = requests.get(f"https://{host}/oauth/userinfo", timeout=30,
                      headers={"Authorization": f"Bearer {token}"}).json()
    want = cfg.get("account_id")
    acct = None
    for a in ui.get("accounts", []):
        if (want and a["account_id"] == want) or (not want and a.get("is_default")):
            acct = a
            break
    if not acct and ui.get("accounts"):
        acct = ui["accounts"][0]
    if not acct:
        raise RuntimeError(f"userinfo 未返回账号：{ui}")
    return {"access_token": token, "base_uri": acct["base_uri"], "account_id": acct["account_id"]}


def _hdr(auth: dict, json_ct=True) -> dict:
    h = {"Authorization": f"Bearer {auth['access_token']}"}
    if json_ct:
        h["Content-Type"] = "application/json"
    return h


def _api(auth: dict, path: str) -> str:
    return f"{auth['base_uri']}/restapi/v2.1/accounts/{auth['account_id']}{path}"


def _b64(path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


def _locate_anchor(pdf_path, anchor, case_sensitive=True, whole_word=True, which="first"):
    """用 fitz 在 PDF 里定位 anchor 文本，返回匹配 (page_1based, x0, y0)（points，左上角，
    坐标系与 DocuSign 绝对定位一致：原点左上、Y 向下、72pt=1英寸）。找不到/无 fitz → None。
    which='first'（默认）取首个匹配；'last' 取全文最后一个匹配（如 "By:" 多处时取末尾签字块）。"""
    try:
        import fitz
    except Exception:
        return None
    try:
        doc = fitz.open(str(pdf_path))
    except Exception:
        return None
    try:
        tgt = anchor if case_sensitive else anchor.lower()
        found = None
        for pno in range(len(doc)):
            for w in doc[pno].get_text("words"):   # (x0,y0,x1,y1,word,block,line,wno)
                word = w[4] if case_sensitive else w[4].lower()
                if (word == tgt) if whole_word else (tgt in word):
                    found = (pno + 1, w[0], w[1])
                    if which != "last":
                        return found
        return found
    finally:
        doc.close()


def infer_kind(name):
    """按文件名推 DocuSign 文档类型（套用 anchor_offsets 里的按文档锚点/偏移）。
    注意顺序：'Transmittal_submitting_Declarations' 同时含 Transmittal/Declaration，
    需先判 Petition/Declaration，避免误归为普通 Transmittal。"""
    n = Path(name).name.upper()
    if "PETITION" in n:
        return "Petition"
    if "DECLARATION" in n:          # 如 Transmittal_submitting_Declarations（签字在 "By:"）
        return "Declarations"
    if "POA" in n:
        return "POA"
    if "TRANSMITTAL" in n:
        return "Transmittal"
    if "ADS" in n:
        return "ADS"
    return None


def _ensure_pdf(path):
    """DocuSign 走 fitz 绝对定位 + PDF 上传：.docx/.doc 先用 LibreOffice 转 PDF（转到临时目录），
    已是 PDF 原样返回。转换能力缺失（无 soffice）时抛错，让调用方明确失败而非静默丢签名框。"""
    p = Path(path)
    if p.suffix.lower() in (".pdf",):
        return p
    if p.suffix.lower() in (".docx", ".doc"):
        try:
            from .preview import docx_to_pdf
        except ImportError:
            from preview import docx_to_pdf     # 作为脚本直跑时
        return Path(docx_to_pdf(str(p), out_dir=tempfile.mkdtemp(prefix="ds_pdf_")))
    return p


def build_envelope(documents, recipient, email_subject=None, anchor="Signature",
                   date_anchor=None, status="sent",
                   anchor_x=0, anchor_y=0, anchor_units="pixels",
                   anchor_case_sensitive=True, anchor_whole_word=True,
                   anchor_offsets=None) -> dict:
    """构造信封请求体（不发送，便于 dry-run 核对）。
    :param documents: [{"path", "name"(可选), "kind"(可选)}]，全放同一信封（一案一信封）
    :param recipient: {"name","email"}（美代理签字人）
    :param anchor: 全局默认签名位锚点文本；某文档类型可在 anchor_offsets[kind].anchor 覆盖
        （如 Petition/Declarations 用 "By:"，POA/Transmittal 用 "Signature"）。
    :param anchor_offsets: 按文档类型 {kind: {"anchor"(可选), "x", "y"}, "_default": {...}}；缺省用全局 anchor + anchor_x/anchor_y。
        每份文档用 fitz 找该类型 anchor 坐标 + 偏移 → 放**绝对坐标**签名框（一个信封、各文档各自落点）。
        .docx/.doc 文档先转 PDF 再定位与上传。fitz 不可用/全都定位不到 → 退回单锚点（全局偏移，老行为）。
    """
    # 逐文档解析成 PDF（.docx→PDF），供 fitz 定位与 DocuSign 上传共用
    pdf_paths = [_ensure_pdf(d["path"]) for d in documents]

    docs = []
    for i, (d, pdf) in enumerate(zip(documents, pdf_paths), start=1):
        src = Path(d["path"])
        docs.append({
            "documentId": str(i),
            "name": d.get("name") or (src.stem + ".pdf" if src.suffix.lower() != ".pdf" else src.name),
            "fileExtension": "pdf",
            "documentBase64": _b64(pdf),
        })

    def _anchor_off(kind):
        """返回该文档类型的 (锚点文本, x偏移, y偏移, 匹配位置)；anchor 缺省回退全局 anchor，
        match 缺省 'first'（'last' 则取该锚点在文档中的最后一处，如 "By:" 多处取末尾）。"""
        ao = anchor_offsets or {}
        o = ao.get(kind) or ao.get("_default") or {"x": anchor_x, "y": anchor_y}
        a = o.get("anchor") or anchor
        which = (o.get("match") or "first").lower()
        return a, int(round(float(o.get("x", 0)))), int(round(float(o.get("y", 0)))), which

    # 逐文档 fitz 定位（按各自锚点）→ 绝对坐标签名框（一个信封、各文档各自落点）
    sign_tabs = []
    for i, (d, pdf) in enumerate(zip(documents, pdf_paths), start=1):
        a, ox, oy, which = _anchor_off(d.get("kind"))
        loc = _locate_anchor(pdf, a, anchor_case_sensitive, anchor_whole_word, which)
        if loc:
            pg, x0, y0 = loc
            fx, fy = int(round(x0)) + ox, int(round(y0)) + oy
            print(f"[docusign] doc{i} kind={d.get('kind')} anchor={a!r}({which}) "
                  f"定位=(p{pg}, x0={x0:.1f}, y0={y0:.1f}) 偏移=({ox},{oy}) → 落点=(p{pg}, x={fx}, y={fy})",
                  file=sys.stderr)
            sign_tabs.append({"documentId": str(i), "pageNumber": str(pg), "recipientId": "1",
                              "xPosition": str(fx), "yPosition": str(fy)})
        else:
            print(f"[docusign] doc{i} kind={d.get('kind')} anchor={a!r}({which}) 未定位到 "
                  f"（{Path(pdf).name}）→ 该文档无绝对签名框", file=sys.stderr)
    if not sign_tabs:
        # fitz 不可用 / 全都没定位到 → 退回单锚点（全局偏移）
        _a, ox, oy, _w = _anchor_off(None)
        sign_tabs = [{"anchorString": anchor, "anchorUnits": anchor_units,
                      "anchorCaseSensitive": anchor_case_sensitive,
                      "anchorMatchWholeWord": anchor_whole_word,
                      "anchorXOffset": str(ox), "anchorYOffset": str(oy)}]
    tabs = {"signHereTabs": sign_tabs}
    if date_anchor:   # 需要单独日期框才配（仍用锚点，跨文档）
        tabs["dateSignedTabs"] = [{"anchorString": date_anchor, "anchorUnits": anchor_units,
                                   "anchorCaseSensitive": anchor_case_sensitive,
                                   "anchorMatchWholeWord": anchor_whole_word,
                                   "anchorXOffset": "0", "anchorYOffset": "0"}]
    signer = {"email": recipient["email"], "name": recipient["name"],
              "recipientId": "1", "routingOrder": "1", "tabs": tabs}
    return {
        "emailSubject": email_subject or "Please sign the US filing documents",
        "documents": docs,
        "recipients": {"signers": [signer]},
        "status": status,      # "sent"=立即发；"created"=存草稿
    }


def send_envelope(cfg, auth, documents, recipient, **kw) -> str:
    """建并发送信封，返回 envelopeId。"""
    body = build_envelope(documents, recipient, **kw)
    r = requests.post(_api(auth, "/envelopes"), headers=_hdr(auth), json=body, timeout=60)
    if r.status_code not in (200, 201):
        raise RuntimeError(f"建信封失败 {r.status_code}: {r.text}")
    return r.json()["envelopeId"]


def get_status(cfg, auth, envelope_id) -> str:
    r = requests.get(_api(auth, f"/envelopes/{envelope_id}"), headers=_hdr(auth, False), timeout=30)
    r.raise_for_status()
    return r.json().get("status")    # sent / delivered / completed / declined / voided


def download_signed(cfg, auth, envelope_id, out_dir, which="combined") -> list:
    """取签署版 PDF（envelope 须 completed）。which='combined' 合并版；否则逐个文档。"""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = f"/envelopes/{envelope_id}/documents"
    saved = []

    def _get(doc_id, fname):
        r = requests.get(_api(auth, f"{base}/{doc_id}"), headers=_hdr(auth, False), timeout=60)
        r.raise_for_status()
        fp = out_dir / fname
        fp.write_bytes(r.content)
        saved.append(str(fp))

    if which == "combined":
        _get("combined", f"{envelope_id}-signed-combined.pdf")
    else:
        lst = requests.get(_api(auth, base), headers=_hdr(auth, False), timeout=30).json()
        for d in lst.get("envelopeDocuments", []):
            if d.get("type") == "content":
                _get(d["documentId"], f"{envelope_id}-{d.get('name', 'doc')}.pdf")
    return saved


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"
    if cmd == "help":
        print(__doc__)
        print("用法: python docusign_client.py <命令>\n"
              "  consent                         打印一次性授权链接\n"
              "  token                           验证 JWT Grant 换 token\n"
              "  send <收件邮箱> <文件1> [文件2…]   建并发送信封（沙盒测试发件）\n"
              "  status <envId>                  查信封状态\n"
              "  download <envId> <输出目录>      取回签署版 PDF\n"
              "  demo                            dry-run 打印信封结构（不连网）")
        sys.exit(0)
    if cmd == "consent":
        print("浏览器打开授权一次：\n" + consent_url(load_config()))
        sys.exit(0)
    if cmd == "demo":
        # dry-run：打印将发送的信封体（不连网、不发送），核对结构/锚点
        docs = [{"path": "example-POA.pdf", "kind": "POA"},
                {"path": "example-Transmittal.pdf", "kind": "Transmittal"},
                {"path": "example-ADS.pdf", "kind": "ADS"}]
        # 不读真实文件，仅展示信封结构（documentBase64 用占位）核对锚点/收件人
        preview = {
            "emailSubject": "Please sign the US filing documents",
            "documents": [{"documentId": str(i), "name": Path(d["path"]).name,
                           "fileExtension": "pdf", "documentBase64": "<base64>"} for i, d in enumerate(docs, 1)],
            "recipients": {"signers": [{"email": "agent@example.com", "name": "US Agent",
                                        "recipientId": "1", "routingOrder": "1",
                                        "tabs": {"signHereTabs": [{"anchorString": "Signature"}],
                                                 "dateSignedTabs": [{"anchorString": "Signature", "anchorXOffset": "220"}]}}]},
            "status": "sent",
        }
        print(json.dumps(preview, ensure_ascii=False, indent=2))
        sys.exit(0)
    # 以下真连 DocuSign（需配置好凭据 + 沙盒 consent）
    cfg = load_config()
    auth = get_access_token(cfg)
    print(f"token OK; base_uri={auth['base_uri']} account={auth['account_id']}")
    if cmd == "send" and len(sys.argv) > 3:
        to_email = sys.argv[2]
        files = sys.argv[3:]
        for f in files:
            if not Path(f).is_file():
                raise RuntimeError(f"文件不存在: {f}")
        agent = cfg.get("agent") or {}
        recip = {"name": agent.get("name") or "US Agent", "email": to_email}
        env_id = send_envelope(cfg, auth, [{"path": f, "kind": infer_kind(f)} for f in files], recip,
                               anchor=cfg.get("anchor", "Signature"),
                               date_anchor=cfg.get("date_anchor"),
                               anchor_x=cfg.get("anchor_x_offset", 0),
                               anchor_y=cfg.get("anchor_y_offset", 0),
                               anchor_units=cfg.get("anchor_units", "pixels"),
                               anchor_case_sensitive=cfg.get("anchor_case_sensitive", True),
                               anchor_whole_word=cfg.get("anchor_whole_word", True),
                               anchor_offsets=cfg.get("anchor_offsets"))
        print(f"已发送信封 envelopeId={env_id} → {to_email}（沙盒收件箱查收，签完用 status/download）")
    elif cmd == "status" and len(sys.argv) > 2:
        print("status:", get_status(cfg, auth, sys.argv[2]))
    elif cmd == "download" and len(sys.argv) > 3:
        print("saved:", download_signed(cfg, auth, sys.argv[2], sys.argv[3]))
