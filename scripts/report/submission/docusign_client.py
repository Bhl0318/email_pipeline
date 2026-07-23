#!/usr/bin/env python3
"""DocuSign eSignature 集成（沙盒脚手架）——把需签字件发美代理电子签、API 回收签署版。

用于 US 递交环节5/6：只把需签字子集(POA/Transmittal/ADS)放同一信封发 DocuSign 给美代理签，
签完经 API 取回签署版 PDF（替代邮箱抓件/改名匹配）。纯确定性调用，无 AI。

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
import time
from pathlib import Path

import requests

CONFIG_PATH = Path(__file__).with_name("docusign_config.json")

DEMO_OAUTH_HOST = "account-d.docusign.com"   # 沙盒
PROD_OAUTH_HOST = "account.docusign.com"     # 生产


def load_config(path=None) -> dict:
    p = Path(path or CONFIG_PATH)
    if not p.is_file():
        raise SystemExit(f"缺配置 {p}（参照同目录 docusign_config.example.json 建；沙盒填 demo 凭据）")
    return json.loads(p.read_text(encoding="utf-8"))


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
    if kp and Path(kp).is_file():
        return Path(kp).read_text(encoding="utf-8")
    if cfg.get("private_key"):
        return cfg["private_key"]
    raise SystemExit("缺 RSA 私钥：请在配置里给 private_key_path（指向 .pem）或 private_key")


def get_access_token(cfg: dict) -> dict:
    """JWT Grant 换 token。:return: {access_token, base_uri, account_id}"""
    try:
        import jwt  # PyJWT
    except Exception:
        raise SystemExit("需安装：pip install pyjwt cryptography")
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
        raise SystemExit(f"JWT Grant 失败 {r.status_code}: {r.text}\n"
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
        raise SystemExit(f"userinfo 未返回账号：{ui}")
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


def build_envelope(documents, recipient, email_subject=None, anchor="Signature",
                   date_anchor=None, status="sent") -> dict:
    """构造信封请求体（不发送，便于 dry-run 核对）。
    :param documents: [{"path", "name"(可选), "kind"(可选)}]，全放同一信封（一案一信封）
    :param recipient: {"name","email"}（美代理签字人）
    :param anchor: 签名位锚点文本（PDF 里该文本出现处放签名框；按真实文档调，也可改用坐标）
    """
    docs = []
    for i, d in enumerate(documents, start=1):
        p = Path(d["path"])
        docs.append({
            "documentId": str(i),
            "name": d.get("name") or p.name,
            "fileExtension": (p.suffix.lstrip(".").lower() or "pdf"),
            "documentBase64": _b64(p),
        })
    tabs = {
        "signHereTabs": [{"anchorString": anchor, "anchorUnits": "pixels",
                          "anchorXOffset": "0", "anchorYOffset": "0"}],
        "dateSignedTabs": [{"anchorString": date_anchor or anchor, "anchorUnits": "pixels",
                            "anchorXOffset": "220", "anchorYOffset": "0"}],
    }
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
        raise SystemExit(f"建信封失败 {r.status_code}: {r.text}")
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
        print("用法: python docusign_client.py [consent|token|status <envId>|download <envId> <outdir>|demo]")
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
    if cmd == "status" and len(sys.argv) > 2:
        print("status:", get_status(cfg, auth, sys.argv[2]))
    elif cmd == "download" and len(sys.argv) > 3:
        print("saved:", download_signed(cfg, auth, sys.argv[2], sys.argv[3]))
