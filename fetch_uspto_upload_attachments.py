#!/usr/bin/env python3
"""抓取「美代理回邮」附件，按案号归档为待上传 USPTO 的文件包。

场景：环节4 把递交件发给美国代理人后，美代理签好回邮到指定邮箱文件夹。本脚本读取该
文件夹里每封邮件的附件（无附件则跳过），从**附件文件名**里解析案号，把同一案号的附件
存到同一个文件夹（以案号命名）。这些文件即环节7 要上传 Patent Center 的件。

参考 projects/set_skill/skill-catalog/skills/email/scripts/read_email.py 的 IMAP
登录 / UTF-7 文件夹名 / 邮件头解码。默认账号 agent@metis-ip.com 内置于本脚本
（明文口令，走 partner.outlook.cn 密码认证）；其它账号可退回 scripts/email_config.json。

用法（默认读 agent@metis-ip.com 的 FilingSignatures 文件夹）：
  python3 fetch_uspto_upload_attachments.py                          # 用默认
  python3 fetch_uspto_upload_attachments.py FilingSignatures agent uspto_upload

处理完把邮件归位：成功（有附件入库）-> FilingSignatures-done，未落任何附件
-> FilingSignatures-skipped（两个文件夹自动创建）。传 move=False 可只抓不移。

⚠️ 会移动邮件（copy+删除原件+expunge），非只读；连真实邮箱，请在受控环境运行。
"""
import sys
import os
import re
import json
import base64
import imaplib
import email
from email.header import decode_header

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "scripts", "email_config.json")

# 案号格式：[0-9A-Z]{5}-[0-9A-Z]{4}[A-Z]{2}[0-9A-Z]{2}（如 20609-0083US01）
CASE_RE = re.compile(r"[0-9A-Z]{5}-[0-9A-Z]{4}[A-Z]{2}[0-9A-Z]{2}")

# 内置账号：美代理回邮所在邮箱（agent@metis-ip.com）。metis-ip.com 在世纪互联
# partner.outlook.cn，IMAP 基本认证已被停用，必须走 OAuth2 的 ROPC（密码）授权：
# 账号口令喂 token 端点换 access_token，再用 XOAUTH2 登 IMAP smtp.partner.outlook.cn:993。
# Azure 应用（client_id/secret/tenant/resource）沿用 downUSPTO/single_parse_uspto.py 那套。
# 明文口令按用户偏好直接内置，不抽到 gitignore。
BUILTIN_ACCOUNTS = {
    "agent": {
        "imap_host": "smtp.partner.outlook.cn",
        "imap_port": "993",
        "user": "agent@metis-ip.com",
        "password": "Metisip@2026",
        "oauth2": {
            "enabled": True,
            "token_url": "https://login.partner.microsoftonline.cn/"
                         "7ca924ee-7831-4688-9f0f-369a714e8514/oauth2/token",
            "client_id": "52ac8b85-7f91-4507-8750-393c9ea91300",
            "client_secret": "dJESX3wTl2_KRpgnTDL4Bz3g-7-QiHje4-",
            "resource": "https://partner.outlook.cn",
        },
    },
}


def load_account(account_key):
    """取账号配置：先查内置账号，再退回 scripts/email_config.json 的 accounts。"""
    if account_key in BUILTIN_ACCOUNTS:
        return BUILTIN_ACCOUNTS[account_key]
    if not os.path.exists(CONFIG_PATH):
        raise SystemExit(f"账号 '{account_key}' 不是内置账号，且 {CONFIG_PATH} 不存在")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    accounts = cfg.get("accounts") or {}
    if account_key not in accounts:
        raise SystemExit(f"找不到账号 '{account_key}'，内置：{list(BUILTIN_ACCOUNTS)}，"
                         f"email_config.json：{list(accounts)}")
    return accounts[account_key]


def _truthy(v):
    """配置里 enabled 可能是布尔 True 或字符串 'True'，统一判真。"""
    return str(v).strip().lower() in ("1", "true", "yes")


def get_oauth2_token(cfg):
    oauth = cfg.get("oauth2", {})
    if not _truthy(oauth.get("enabled")):
        return None
    import requests
    try:
        resp = requests.post(oauth["token_url"], data={
            "client_id": oauth["client_id"],
            "client_secret": oauth["client_secret"],
            "resource": oauth["resource"],
            "username": cfg["user"],
            "password": cfg.get("password", ""),
            "grant_type": "password",
        }, headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "login.partner.microsoftonline.cn",
        })
        data = resp.json()
        if "access_token" in data:
            return data["access_token"]
        print(f"OAuth2 获取 token 失败：{data.get('error_description', data)}")
        return None
    except Exception as e:
        print(f"OAuth2 请求失败：{e}")
        return None


def login_imap(cfg):
    """登录 IMAP，优先 OAuth2，失败降级密码认证（同参考脚本）。"""
    imap = imaplib.IMAP4_SSL(cfg["imap_host"], int(cfg["imap_port"]))
    token = get_oauth2_token(cfg)
    if token:
        auth_string = f"user={cfg['user']}\x01auth=Bearer {token}\x01\x01"
        try:
            imap.authenticate("XOAUTH2", lambda x: auth_string.encode())
            return imap
        except Exception as e:
            print(f"OAuth2 IMAP 登录失败，降级到密码认证：{e}")
    imap.login(cfg["user"], cfg["password"])
    return imap


def imap_utf7_encode(s):
    """把文件夹名编码为 IMAP modified UTF-7（中文文件夹名需要）。"""
    if all(0x20 <= ord(c) <= 0x7E for c in s):
        return s.replace("&", "&-")
    out, buf = [], []

    def flush():
        if buf:
            b64 = base64.b64encode("".join(buf).encode("utf-16-be")).decode()
            out.append("&" + b64.rstrip("=").replace("/", ",") + "-")
            buf.clear()

    for c in s:
        if 0x20 <= ord(c) <= 0x7E:
            flush()
            out.append("&-" if c == "&" else c)
        else:
            buf.append(c)
    flush()
    return "".join(out)


def select_folder(imap, folder, readonly=True):
    status, data = imap.select(f'"{imap_utf7_encode(folder)}"', readonly=readonly)
    if status != "OK":
        detail = data[0].decode(errors="replace") if data and data[0] else "不存在或无权限"
        raise SystemExit(f"无法打开文件夹 {folder}：{detail}")


def _move_nums(imap, nums, target_folder):
    """把 nums（当前所选源文件夹的序号列表）复制到 target_folder 并标记删除（不 expunge）。
    目标不存在则创建。返回成功复制数。调用方在两类都移完后统一 expunge 一次
    （expunge 前序号不变，故先 copy+store、最后一次 expunge 是安全的）。"""
    if not nums:
        return 0
    enc = imap_utf7_encode(target_folder)
    imap.create(f'"{enc}"')  # 已存在会返回 NO，忽略
    moved = 0
    for num in nums:
        status, _ = imap.copy(num, f'"{enc}"')
        if status == "OK":
            imap.store(num, "+FLAGS", "\\Deleted")
            moved += 1
        else:
            print(f"  [移动失败] 序号 {num} 复制到 {target_folder} 未成功，保留原处")
    return moved


def decode_str(s):
    """解码邮件头 / 附件名。"""
    if s is None:
        return ""
    parts = decode_header(s)
    result = []
    for content, charset in parts:
        if isinstance(content, bytes):
            result.append(content.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(content)
    return "".join(result)


def iter_attachments(msg):
    """产出 (filename, payload_bytes)。只认真正的附件（有文件名或 Content-Disposition=attachment）。"""
    for part in msg.walk():
        if part.get_content_maintype() == "multipart":
            continue
        disp = (part.get("Content-Disposition") or "").lower()
        raw_name = part.get_filename()
        if not raw_name and "attachment" not in disp:
            continue  # 正文等非附件部分
        filename = decode_str(raw_name).strip() if raw_name else ""
        if not filename:
            continue
        payload = part.get_payload(decode=True)
        if payload is None:
            continue
        yield filename, payload


def _safe_name(name):
    """清洗附件名，得到跨平台安全的文件名：
    - 取 basename（去路径分隔符，防越界写入）；
    - 折叠换行/制表等空白为单空格（MIME 头折行会带 \\r\\n，Windows 不允许文件名含换行）；
    - 替换 Windows 非法字符 <>:"/\\|?* 和控制字符为 _。"""
    base = os.path.basename(name.replace("\\", "/"))
    base = re.sub(r"\s+", " ", base)                  # 换行/多空白 → 单空格
    base = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", base)  # 非法/控制字符 → _
    return base.strip().strip(".") or "attachment"


def _unique_path(dir_path, filename):
    """同名文件已存在时追加 -1/-2… 避免覆盖。"""
    base, ext = os.path.splitext(filename)
    path = os.path.join(dir_path, filename)
    i = 1
    while os.path.exists(path):
        path = os.path.join(dir_path, f"{base}-{i}{ext}")
        i += 1
    return path


def fetch(folder, account_key="agent", output_root="uspto_upload", move=True):
    """读 folder 抓附件归档；move=True 时把处理成功的邮件移到 {folder}-done、
    未落任何附件的移到 {folder}-skipped（两个兜底文件夹自动创建）。"""
    cfg = load_account(account_key)
    out_root = output_root if os.path.isabs(output_root) else os.path.join(SCRIPT_DIR, output_root)
    done_folder = f"{folder}-done"
    skipped_folder = f"{folder}-skipped"

    imap = login_imap(cfg)
    try:
        # move 需读写模式（copy/store/expunge）；仅抓取用只读
        select_folder(imap, folder, readonly=not move)
        _, msg_nums = imap.search(None, "ALL")
        msg_list = msg_nums[0].split()
        print(f"文件夹「{folder}」共 {len(msg_list)} 封邮件")

        saved_by_case = {}       # 案号 -> 存了几个附件
        done_nums = []           # 至少存下 1 个附件的邮件（成功）
        skipped_nums = []        # 未落任何附件的邮件（无附件 / 附件名都无案号）
        skipped_no_case = 0      # 附件名无案号被跳过的附件数

        for num in msg_list:
            _, data = imap.fetch(num, "(RFC822)")
            if not data or not data[0]:
                continue
            msg = email.message_from_bytes(data[0][1])
            subject = decode_str(msg.get("Subject", ""))

            saved_this_email = 0
            for filename, payload in iter_attachments(msg):
                fname = _safe_name(filename)
                m = CASE_RE.search(fname)
                if not m:
                    skipped_no_case += 1
                    print(f"  [跳过] 附件名无案号：{fname}（邮件：{subject[:40]}）")
                    continue
                case_no = m.group(0)
                case_dir = os.path.join(out_root, case_no)
                os.makedirs(case_dir, exist_ok=True)
                dest = _unique_path(case_dir, fname)
                with open(dest, "wb") as f:
                    f.write(payload)
                saved_by_case[case_no] = saved_by_case.get(case_no, 0) + 1
                saved_this_email += 1
                print(f"  [存] {case_no}/ <- {os.path.basename(dest)}")

            (done_nums if saved_this_email else skipped_nums).append(num)

        # 移动：成功 -> {folder}-done，未落附件 -> {folder}-skipped，最后统一 expunge
        moved_done = moved_skipped = 0
        if move:
            moved_done = _move_nums(imap, done_nums, done_folder)
            moved_skipped = _move_nums(imap, skipped_nums, skipped_folder)
            if moved_done or moved_skipped:
                imap.expunge()

        print("\n===== 汇总 =====")
        print(f"成功（有附件入库）：{len(done_nums)} 封  未落附件：{len(skipped_nums)} 封")
        print(f"归档案号：{len(saved_by_case)} 个 -> {out_root}")
        for case_no, n in sorted(saved_by_case.items()):
            print(f"  {case_no}: {n} 个附件")
        if skipped_no_case:
            print(f"附件名无案号被跳过：{skipped_no_case} 个")
        if move:
            print(f"已移动：{moved_done} 封 -> {done_folder}，{moved_skipped} 封 -> {skipped_folder}")
        else:
            print("（move=False，未移动邮件）")
    finally:
        try:
            imap.logout()
        except Exception:
            pass


if __name__ == "__main__":
    # 默认：agent@metis-ip.com 的 FilingSignatures 文件夹 → uspto_upload/{案号}/
    folder_arg = sys.argv[1] if len(sys.argv) > 1 else "FilingSignatures"
    account_arg = sys.argv[2] if len(sys.argv) > 2 else "agent"
    output_arg = sys.argv[3] if len(sys.argv) > 3 else "uspto_upload"
    fetch(folder_arg, account_arg, output_arg)
