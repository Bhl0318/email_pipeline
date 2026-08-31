#!/usr/bin/env python3
"""Patent Center 新申请上传（UI 自动化·环节7 执行器）。

基于本机 Playwright codegen 录制（playwright_test.py）参数化而来。走【真实界面】操作，
让 SPA 自己处理鉴权/token（绕开直调 API 反复撞的 "No token for authenticated route"）。

流程：Okta 登录(OTP 终端输入) → New submission → 选申请类型 → 选 practitioner(代理所) →
      上传 ADS(单独, Continue) → 上传其余文档(一次多选) → **Save progress 存草稿**。
⚠️ 只到"存草稿"，绝不 submit/交费；由人工在 Patent Center 复审后再递交（环节8）。
   选择器按录制来，真实页面若有出入按 [TODO 实测] 调。
"""
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

import threading
try:  # 复用同目录 sendInfobyDing 的底层发送 helpers（按姓名查 userId + OTO 主动推送）；不 import ttt.py
    from sendInfobyDing import get_access_token, getAllinfos, send_to_user
    _DING_SEND_OK = True
except Exception:
    _DING_SEND_OK = False

BASE = "https://patentcenter.uspto.gov/"

import os
import json

# 内置默认账号（uspto_accounts.json 读不到时回退）
_LOGIN_FALLBACK = {"email": "DSfiling@porus-ip.com", "password": "metisIP@2023"}


def _load_login_account():
    """从同目录 uspto_accounts.json 读 USPTO 登录账号；**手动选账号**优先级：
       环境变量 USPTO_ACCOUNT（整数下标 或 邮箱子串）→ json 的 "active"（下标或邮箱）→ 默认 0。
       读不到文件/账号 → 回退内置默认。返回 {email, password}。"""
    try:
        cfg = json.loads((Path(__file__).resolve().parent / "uspto_accounts.json").read_text(encoding="utf-8"))
        accts = cfg.get("accounts") or []
        if not accts:
            return dict(_LOGIN_FALLBACK)
        sel = os.environ.get("USPTO_ACCOUNT")
        if sel is None:
            sel = cfg.get("active", 0)
        s = str(sel).strip()
        idx = int(s) if s.isdigit() else next(
            (i for i, a in enumerate(accts) if s and s.lower() in (a.get("user") or "").lower()), 0)
        if idx < 0 or idx >= len(accts):
            idx = 0
        a = accts[idx]
        print(f"[login] 使用账号 accounts[{idx}] = {a.get('user')}（{a.get('note', '')}）")
        return {"email": a.get("user") or _LOGIN_FALLBACK["email"],
                "password": a.get("password") or _LOGIN_FALLBACK["password"]}
    except Exception as e:  # noqa: BLE001
        print(f"[login] 读 uspto_accounts.json 失败，用内置默认账号：{e}")
        return dict(_LOGIN_FALLBACK)


LOGIN = {"headless": False}
LOGIN.update(_load_login_account())   # email/password 来自 uspto_accounts.json（可手动切换）

# OTP 获取：dingtalk=钉钉机器人 Stream Mode 直接收你的回复（无 :5000/公网）；terminal=终端手输
OTP = {
    "via": "dingtalk",
    "ding_name": "成萍",
    "message": "USPTO 登录需验证码：请打开 Okta Verify 查看 6 位码，直接【回复本机器人】该验证码。",
    "wait_seconds": 300,          # 等你在钉钉回复的最长秒数，超时回退终端
    # 钉钉应用凭据（同一应用：Stream Mode 收回复 + OTO 主动推送发提示）
    "client_id": "dingkllkaswb21bl6ycg",
    "client_secret": "VeGbUyN0WWtLt6MaK4YCBk8kyaBRgFnedoZ3EBzvdTcTRLolNWn3p_tu-0bVvGIO",
    "robot_code": "dingkllkaswb21bl6ycg",           # 机器人 robotCode（多数=client_id）
}


def _log(m):
    print(f"[pc-ui] {m}", flush=True)


def _wait_no_spinner(page, timeout=120000, settle=10000):
    """等页面 loading spinner(<div role=status class="spinner-border">)消失，再缓冲 settle 毫秒，
    才进行下一步。spinner 不存在时立即通过。"""
    try:
        page.locator("div.spinner-border").first.wait_for(state="hidden", timeout=timeout)
    except Exception:
        pass
    _log(f"无 spinner，缓冲 {settle//1000}s 再下一步")
    page.wait_for_timeout(settle)


def _wait_upload(page, path, timeout=90000):
    """等单个文件上传完成：set_input_files 只是选文件，SPA 还要异步上传+入列表。
    优先等页面出现该文件名（上传成功后会列出），退而等 networkidle，最后兜底 sleep。"""
    name = Path(path).name
    _log(f"等待上传完成: {name}")
    try:
        page.get_by_text(name, exact=False).first.wait_for(state="visible", timeout=timeout)
        _log(f"已入列表: {name}")
        page.wait_for_timeout(1500)   # 再缓冲一下，等按钮可用
        return
    except Exception:
        _log(f"⚠️ 未在页面看到文件名 {name}（可能显示名不同），改等网络空闲")
    try:
        page.wait_for_load_state("networkidle", timeout=timeout)
    except Exception:
        pass
    page.wait_for_timeout(4000)


def _file_input(page):
    """定位文件上传的 <input type=file>（Patent Center 上 "Browse files" 会同时命中
    真正的 input#customInput 和一个拖拽 div[role=button]，strict 模式报命中 2 个；
    set_input_files 本就作用在 input 上，直接瞄 input 即可）。优先 id，退 input[type=file]。"""
    loc = page.locator("input#customInput")
    if loc.count() == 0:
        loc = page.locator('input[type="file"]')
    return loc.first


def _otp_terminal():
    otp = ""
    while not otp:
        otp = input(">>> 请输入收到的 USPTO 验证码后回车: ").strip()
    return otp


def _otp():
    """默认走钉钉 Stream Mode：发提示 → 机器人 WebSocket 直接收你的回复 → 提取数字验证码。
    未装 dingtalk-stream / 未配 secret / 超时 → 回退终端手输。"""
    import re
    if OTP["via"] != "dingtalk":
        return _otp_terminal()
    try:
        import dingtalk_stream
    except Exception:
        _log("未安装 dingtalk-stream（pip install dingtalk-stream），改用终端输入")
        return _otp_terminal()
    cid, csec = OTP.get("client_id"), OTP.get("client_secret")
    if not cid or not csec or "****" in (csec or ""):
        _log("未配置完整的钉钉 Stream client_id/secret（secret 不能是掩码），改用终端输入")
        return _otp_terminal()

    # 发提示（best-effort）：同一应用按姓名查 userId + OTO 主动推送（和收码同一个机器人）
    if _DING_SEND_OK:
        try:
            token = get_access_token(cid, csec)
            uid = (getAllinfos(token) or {}).get(OTP["ding_name"]) if token else None
            if token and uid:
                send_to_user(OTP.get("robot_code") or cid, token, uid, OTP["message"])
                _log(f"已向 {OTP['ding_name']}(userId={uid}) 发送验证码提示")
            else:
                _log("发提示跳过：token/userId 取不到（不阻断，直接回复机器人即可）")
        except Exception as ex:
            _log(f"钉钉提示发送失败（不阻断）：{ex}")

    result = {"otp": None}
    got = threading.Event()

    def run_stream():
        try:
            import logging
            from dingtalk_stream import AckMessage
            # 打开 DEBUG，看底层有没有消息帧进来、topic 是什么
            dlog = logging.getLogger("dingtalk_stream")
            dlog.setLevel(logging.DEBUG)
            if not dlog.handlers:
                _h = logging.StreamHandler()
                _h.setLevel(logging.DEBUG)
                dlog.addHandler(_h)
            _log(f"ChatbotMessage.TOPIC = {dingtalk_stream.ChatbotMessage.TOPIC}")

            class Handler(dingtalk_stream.ChatbotHandler):
                async def process(self, callback):
                    try:
                        m = dingtalk_stream.ChatbotMessage.from_dict(callback.data)
                        txt = (m.text.content if getattr(m, "text", None) else "") or ""
                    except Exception as ex:
                        _log(f"钉钉消息解析失败：{ex}；raw={str(callback.data)[:200]}")
                        return AckMessage.STATUS_OK, "OK"
                    _log(f"钉钉收到消息: {txt!r}")   # 诊断：收到任何消息都打印
                    digits = re.sub(r"\D", "", txt)
                    if len(digits) >= 4:                 # Okta 6 位；≥4 位即采纳
                        result["otp"] = digits
                        got.set()
                    return AckMessage.STATUS_OK, "OK"

            cred = dingtalk_stream.Credential(cid, csec)
            client = dingtalk_stream.DingTalkStreamClient(cred, logger=dlog)
            client.register_callback_handler(dingtalk_stream.ChatbotMessage.TOPIC, Handler())
            client.start_forever()
        except Exception as ex:
            _log(f"钉钉 Stream 启动失败：{ex}")
            got.set()

    threading.Thread(target=run_stream, daemon=True).start()
    _log(f"已请你在钉钉【回复机器人】验证码，最多等 {OTP['wait_seconds']}s...")
    if got.wait(OTP["wait_seconds"]) and result["otp"]:
        _log("已从钉钉收到验证码")
        return result["otp"]
    _log("钉钉未取到验证码（超时/失败），改用终端输入")
    return _otp_terminal()


def login(page):
    page.goto(BASE)
    page.get_by_role("link", name="Sign in").click()
    # 点 Sign in 会自动跳转到 Okta authorize（带一次性 PKCE/state），不要写死该 URL
    page.get_by_role("textbox", name="Email address").fill(LOGIN["email"])
    page.get_by_role("button", name="下一步").click()
    page.get_by_role("textbox", name="密码").fill(LOGIN["password"])
    page.get_by_role("button", name="验证").click()
    try:  # 选"输入 Okta Verify 代码"验证方式
        page.get_by_role("link", name="选择输入 Okta Verify 应用程序中的代码。").click(timeout=15000)
    except Exception:
        pass
    page.get_by_role("textbox", name="从Okta Verify 应用输入代码").fill(_otp())
    page.get_by_role("button", name="验证").click()
    # 可能出现 Okta"保持登录状态？"等附加页，best-effort 点过
    for nm in ("是", "Yes", "保持登录", "Stay signed in", "Do not"):
        try:
            page.get_by_role("button", name=nm).click(timeout=4000)
            break
        except Exception:
            continue
    # 录制实测：MFA 后不会自动跳应用，需主动 goto（此时会话已建，goto 静默完成 OAuth 回调）
    time.sleep(2)
    page.goto(BASE)
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    _log(f"登录后落地 URL: {page.url}")


def file_new_application(page, data):
    """data: {submission_type, practitioner(可选 label), ads_path, other_paths:[...]}"""
    page.goto(BASE)
    try:
        page.wait_for_load_state("networkidle", timeout=30000)
    except Exception:
        pass
    # 新建提交：文案/角色可能有出入，多策略容错
    candidates = [
        page.get_by_role("button", name="description New submission"),
        page.get_by_role("button", name="New submission"),
        page.get_by_role("link", name="New submission"),
        page.get_by_role("button", name=re.compile("New submission")),
        page.get_by_role("link", name=re.compile("New submission")),
        page.get_by_text("New submission", exact=False),
    ]
    clicked = False
    for loc in candidates:
        try:
            loc.first.click(timeout=8000)
            clicked = True
            break
        except Exception:
            continue
    if not clicked:
        raise RuntimeError("找不到 'New submission' 入口——请按真实页面确认按钮文案/角色")
    time.sleep(1)
    # 选申请类型（如 "Utility Nonprovisional"）
    page.get_by_role("link", name=data["submission_type"]).click()

    # 选 practitioner（「I am filing this submission on behalf of」下拉）。
    # 下拉项 label 形如 " Yangzhou Du - 65310 "（姓名 - 执业号）。data["practitioner"] 直接传执业号，
    # 用执业号去下拉项文字里定位（label 末尾就是 "- 执业号"），选中那条。
    # 匹配不到 → 报错留 pending（绝不乱选错人往 USPTO 交）；未指定 → 报错要求带执业号。
    reg = (str(data.get("practitioner") or "")).strip()
    if not reg:
        raise RuntimeError("未指定 practitioner 执业号（on behalf of），拒绝盲选。")
    sel = page.locator("#drDwn_practitioner")
    sel.wait_for(state="visible", timeout=20000)
    # Angular 异步填充选项：等含该执业号的 option 真出现再读，避免过早读到空/仅占位。
    try:
        sel.locator("option", has_text=reg).first.wait_for(state="attached", timeout=20000)
    except Exception:
        pass
    opts = sel.locator("option")
    all_txt = []
    picked = None
    for i in range(opts.count()):
        val = opts.nth(i).get_attribute("value") or ""
        # 用 text_content（非 inner_text）：<option> 在下拉收起时未渲染，inner_text 会返回空串
        txt = (opts.nth(i).text_content() or "").strip()
        all_txt.append(f"[{i}]{txt!r}(val={val!r})")
        if not val or not txt:          # 跳过占位 "Select a practitioner"（value 为空）
            continue
        if reg in txt:                  # 执业号唯一，直接在下拉文字里找
            # 用序号选（同最初 codegen 的 select_option(index=1)）：Angular 的 value 是
            # "1: Object" 这种，按 value 选不中，按 index 才行。
            sel.select_option(index=i)
            picked = txt
            break
    if not picked:
        _log(f"practitioner 下拉实际内容：{all_txt}")   # 诊断：看到底读到了啥
        raise RuntimeError(f"执业号「{reg}」未在 practitioner 下拉中匹配到（on behalf of）；下拉现有 {len(all_txt)} 项，见上。")
    _log(f"practitioner 选中: {picked}")
    # 进入下一步（录制中的 "Select"）
    try:
        page.get_by_role("link", name="Select").nth(1).click()
    except Exception:
        pass

    # 上传 ADS（单独一步，随后 Continue）。set_input_files 只是选了文件，SPA 还要上传+解析——
    # ADS 解析完成的标志是出现 "Review the following information to make sure it is correct…"，
    # 等这句话出现再点 Continue，否则 ADS 实际没上去。
    _log(f"上传 ADS: {data['ads_path']}")
    _file_input(page).set_input_files(data["ads_path"])
    _log("等待 ADS 解析完成（Review the following information…）")
    page.get_by_text("Review the following information to make sure it is correct",
                     exact=False).first.wait_for(state="visible", timeout=120000)
    _wait_no_spinner(page)      # 等 loading spinner 消失 + 缓冲 10s
    _log("ADS 已就绪，点 Continue")
    page.get_by_role("button", name="Continue").click()

    # 上传其余文档（一次多选），同样等上传 spinner 消失 + 缓冲后再往下走。
    others = data.get("other_paths") or []
    if others:
        _log(f"上传其余 {len(others)} 件文档")
        _file_input(page).set_input_files(others)
        _wait_no_spinner(page)  # 等 loading spinner 消失 + 缓冲 10s

    # 存草稿（不 submit）。⚠️ 全程绝不点 Submit/Pay/交费——只 Save progress，人工复审后再递交（环节8）。
    page.get_by_role("button", name="Save progress").click()
    time.sleep(3)
    _log(f"✅ 已 Save progress（存草稿），停在 submit 前。当前 URL: {page.url}")
    return page.url


def _screenshot(page, tag):
    """失败/收尾时截图留证到 seleTest/_pc_shots/，best-effort，不抛。"""
    try:
        shots = Path(__file__).resolve().parent / "_pc_shots"
        shots.mkdir(exist_ok=True)
        # 无 Date.* 依赖：用页面 URL 尾段 + tag 命名，避免时间戳
        safe = re.sub(r"[^0-9A-Za-z_-]", "_", tag)[:60]
        fp = shots / f"{safe}.png"
        page.screenshot(path=str(fp), full_page=True)
        _log(f"已截图留证: {fp}")
    except Exception as ex:
        _log(f"截图失败（忽略）：{ex}")


def run(data, dry_run=False):
    """无人值守执行器。成功返回落地 URL；任何环节失败抛异常（调用方据此保留 pending 重试）。

    契约（run_uspto_upload.py 依赖）：正常返回 = 上传成功可置 done；抛异常 = 失败留 pending。
    绝不阻塞（无 input()），绝不 submit/交费。
    """
    for p in [data["ads_path"], *data.get("other_paths", [])]:
        if dry_run:
            miss = "" if Path(p).exists() else "  ⚠️文件不存在"
            _log(f"[dry-run] 将上传: {p}{miss}")
        elif not Path(p).exists():
            raise FileNotFoundError(f"文件不存在: {p}")
    if dry_run:
        _log(f"[dry-run] 类型={data['submission_type']} practitioner={data.get('practitioner')}")
        _log("[dry-run] 登录 → New submission → 选类型/代理所 → 传 ADS → 传其余 → Save progress")
        return None

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=LOGIN["headless"])
        context = browser.new_context()
        page = context.new_page()
        try:
            login(page)
            url = file_new_application(page, data)
            _screenshot(page, "ok_saved")
            return url
        except Exception:
            _screenshot(page, "error")
            raise
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    import sys
    D = "6M201-H001US00 CON+PCT-PPH"
    example = {
        "submission_type": "Utility Nonprovisional",
        "practitioner": None,   # None=按序号1；或填执业人 label（如 "Runzhi Lai"）
        "ads_path": f"{D}/2026-07-10-ADS-6M201-H001US00.pdf",
        "other_paths": [
            f"{D}/Signed_Declaration-6M201-H001US00.pdf",
            f"{D}/2026-07-10-Spec-6M201-H001US00.docx",
            f"{D}/2026-07-10-Transmittal-6M201-H001US00.pdf",
            f"{D}/2026-07-10-FIGS-6M201-H001US00.pdf",
            f"{D}/2026-07-10-POA-6M201-H001US00.pdf",
        ],
    }
    # 默认 dry-run，避免误连真实 USPTO；加 --live 才真正驱动浏览器。
    live = "--live" in sys.argv
    url = run(example, dry_run=not live)
    _log(f"完成，落地 URL: {url}" if live else "dry-run 结束（加 --live 真正执行）")
