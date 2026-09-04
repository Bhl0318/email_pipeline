"""MIME 邮件解析（可复用纯函数，仅标准库）。

抽自 oa/read_email.py 的 decode_str/_HTMLTextExtractor/html_to_text/get_body/
get_attachments/save_attachments/parse_email_date/parse_address_list/parse_message，
逻辑不变。零外部依赖，零业务耦合。
"""
import os
import re
from datetime import datetime
from email.header import decode_header
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser


def decode_str(s):
    """RFC2047 邮件头解码（主题/发件人等），返回可读字符串；None→""。"""
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


class _HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("style", "script"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("style", "script"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            self._text.append(data)

    def get_text(self):
        return "".join(self._text).strip()


def html_to_text(html):
    """HTML 转纯文本（剥 style/script）。输入 str → 输出 str。"""
    extractor = _HTMLTextExtractor()
    extractor.feed(html)
    return extractor.get_text()


def get_body(msg):
    """提取邮件正文，返回 (纯文本body, 原始html_body)。

    输入：email.message.Message
    输出：(str, str)；纯文本优先取 text/plain，无则从 html 提取。
    """
    plain_body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and not plain_body:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    plain_body = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and not html_body:
                charset = part.get_content_charset() or "utf-8"
                payload = part.get_payload(decode=True)
                if payload:
                    html_body = payload.decode(charset, errors="replace")
    else:
        charset = msg.get_content_charset() or "utf-8"
        payload = msg.get_payload(decode=True)
        if payload:
            text = payload.decode(charset, errors="replace")
            if msg.get_content_type() == "text/html":
                html_body = text
            else:
                plain_body = text

    body = plain_body.strip()
    if not body and html_body.strip():
        body = html_to_text(html_body)

    return body, html_body


def get_attachments(msg):
    """返回附件元信息列表 [{filename, content_type, size}]（不落盘）。

    输入：email.message.Message → 输出：list[dict]
    """
    attachments = []
    if not msg.is_multipart():
        return attachments
    for part in msg.walk():
        disposition = str(part.get("Content-Disposition", ""))
        if "attachment" in disposition or "inline" in disposition:
            filename = decode_str(part.get_filename())
            if not filename:
                continue
            filename = filename.replace("\x00", "")
            payload = part.get_payload(decode=True)
            size = len(payload) if payload else 0
            attachments.append({
                "filename": filename,
                "content_type": part.get_content_type(),
                "size": size,
            })
    return attachments


def save_attachments(msg, output_dir):
    """把附件落盘到 output_dir，返回保存的文件路径列表（重名加时分秒后缀）。

    输入：email.message.Message、output_dir(str) → 输出：list[str]（副作用：写盘）
    """
    saved = []
    if not msg.is_multipart():
        return saved
    os.makedirs(output_dir, exist_ok=True)
    for part in msg.walk():
        disposition = str(part.get("Content-Disposition", ""))
        if "attachment" not in disposition and "inline" not in disposition:
            continue
        filename = decode_str(part.get_filename())
        if not filename:
            continue
        filename = filename.replace("\x00", "")
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            name, ext = os.path.splitext(filename)
            filepath = os.path.join(output_dir, f"{name}_{datetime.now().strftime('%H%M%S')}{ext}")
        payload = part.get_payload(decode=True)
        if payload:
            with open(filepath, "wb") as f:
                f.write(payload)
            saved.append(filepath)
    return saved


def parse_email_date(msg):
    """邮件 Date 头 → ISO 字符串（解析失败返回原串，无则 ""）。"""
    date_str = msg.get("Date", "")
    if not date_str:
        return ""
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.isoformat()
    except Exception:
        return date_str


def parse_address_list(header_value):
    """收件人/CC 头 → 地址字符串列表（按 , 或 ; 分隔）。None→[]。"""
    if not header_value:
        return []
    decoded = decode_str(header_value)
    addresses = re.split(r'[;,]', decoded)
    return [a.strip() for a in addresses if a.strip()]


def parse_message(msg, attachment_dir=None):
    """把一封邮件解析成结构化 dict。

    输入：email.message.Message、attachment_dir(可选，传了就落盘附件)
    输出：dict — subject/from/to/cc/date/message_id/body/html_body/attachments
          （attachment_dir 非空时另含 saved_attachments 路径列表）
    """
    body, html_body = get_body(msg)
    result = {
        "subject": decode_str(msg.get("Subject", "")),
        "from": decode_str(msg.get("From", "")),
        "to": parse_address_list(msg.get("To")),
        "cc": parse_address_list(msg.get("Cc")),
        "date": parse_email_date(msg),
        # 去折行：Message-ID 头可能被折行含 \r\n\t，清掉内部空白
        "message_id": re.sub(r"\s+", "", msg.get("Message-ID", "") or ""),
        "body": body,
        "html_body": html_body,
        "attachments": get_attachments(msg),
    }
    if attachment_dir:
        result["saved_attachments"] = save_attachments(msg, attachment_dir)
    return result
