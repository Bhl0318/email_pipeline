"""USPTO 官文下载客户端（基础通用层 · 网络与服务调用）。

抽自 oa/downloadByAPI.py，逻辑不变；唯一改动：API key 不再硬编码，改为
参数 > 环境变量 USPTO_API_KEY > email_config.json 的 uspto.api_key。

按申请号调 USPTO 官方 API（api.uspto.gov）列文档、按 documentCode+officialDate 精确匹配下载，
写 JSONL 下载日志，暴露 last_http_status（403=未公开/受限）。
依赖：requests。
"""
import json
import os
from collections import defaultdict
from datetime import datetime

LOG_FILENAME = "uspto_download_log.jsonl"

# 本模块在 scripts/reusable/foundation/net_clients/ 下，email_config.json 在 scripts/（上溯三级）
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def _resolve_api_key(explicit=None):
    """API key：参数 > 环境变量 USPTO_API_KEY > email_config.json 的 uspto.api_key。"""
    if explicit:
        return explicit
    env = os.environ.get("USPTO_API_KEY")
    if env:
        return env
    try:
        with open(os.path.join(_SCRIPTS_DIR, "email_config.json"), encoding="utf-8") as f:
            return (json.load(f).get("uspto") or {}).get("api_key")
    except Exception:
        return None


def log_download(entry, log_path):
    """把一条下载记录追加到 JSONL 日志。路径由调用方给（不写死）。写日志出错绝不影响下载。"""
    if not log_path:
        return
    try:
        entry.setdefault("time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        d = os.path.dirname(log_path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[uspto-log] 写日志失败: {e}")


class USPTOApplication:
    """按申请号从 USPTO 官方 API 下载文档。"""

    def __init__(self, download_dir="output", mail_id=None, project=None,
                 log_path=None, api_key=None):
        """
        download_dir  下载基目录
        project       项目子目录名（下到 download_dir/project/）
        log_path      JSONL 日志路径；不给则默认 download_dir/uspto_download_log.jsonl，
                      可用环境变量 USPTO_DOWNLOAD_LOG 覆盖
        api_key       USPTO API key；不给则走环境变量/配置（见 _resolve_api_key）
        """
        self.base_download_dir = download_dir
        self.project = project
        self.l = mail_id
        self.apikey = _resolve_api_key(api_key)
        self.last_http_status = None
        self.log_path = (log_path or os.environ.get("USPTO_DOWNLOAD_LOG")
                         or os.path.join(download_dir, LOG_FILENAME))
        self.download_dir = os.path.join(download_dir, project) if project else download_dir
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"创建下载目录: {self.download_dir}")

    def downLoad_Documents_ByAPI(self, application, document_code, official_date,
                                 project, descriptionWiki, kind="oa"):
        """列申请文档→按 documentCode+officialDate 精确匹配→逐个下载。返回 {project: [本地路径]}。"""
        import requests
        url = f"https://api.uspto.gov/api/v1/patent/applications/{application}/documents"
        print(url)
        headers = {"X-API-KEY": self.apikey}
        entry = {"kind": kind, "project": project, "application": application,
                 "document_code": document_code, "official_date": official_date,
                 "status": "failed", "reason": ""}
        doc_list = defaultdict(list)

        try:
            response = requests.get(url, headers=headers, timeout=60)
        except Exception as e:
            entry["reason"] = f"API请求异常/超时: {e}"
            log_download(entry, self.log_path)
            return doc_list

        print(response.status_code)
        self.last_http_status = response.status_code
        entry["http_status"] = response.status_code
        if response.status_code != 200:
            entry["reason"] = f"API返回{response.status_code}: {response.text[:200]}"
            log_download(entry, self.log_path)
            return doc_list

        try:
            res = json.loads(response.text)
            documentBag = res.get("documentBag", []) or []
        except Exception as e:
            entry["reason"] = f"响应解析失败: {e}"
            log_download(entry, self.log_path)
            return doc_list

        entry["docs_in_bag"] = len(documentBag)
        docRes = self.filter_documents(documentBag, document_code, official_date)
        entry["matched"] = len(docRes)
        if not docRes:
            avail = sorted({(d.get("documentCode", ""), (d.get("officialDate", "") or "")[:10])
                            for d in documentBag})
            entry["available"] = [f"{c}@{dt}" for c, dt in avail][:60]
            entry["reason"] = f"无匹配文档(需 documentCode={document_code} 且 officialDate={official_date})"
            log_download(entry, self.log_path)
            return doc_list

        file_errs = []
        for doc in docRes:
            description = doc["documentCodeDescriptionText"] if not descriptionWiki else descriptionWiki
            for i in doc["downloadOptionBag"]:
                fName, err = self.downLoad_file(i['downloadUrl'], i['mimeTypeIdentifier'],
                                                description, official_date, project)
                if fName:
                    doc_list[project].append(fName)
                else:
                    file_errs.append(err or "未知错误")

        got = doc_list.get(project, [])
        entry["files"] = [os.path.basename(f) for f in got]
        if got:
            entry["status"] = "success"
            if file_errs:
                entry["reason"] = f"部分文件下载失败: {file_errs}"
        else:
            entry["reason"] = f"匹配到文档但下载失败: {file_errs}"
        log_download(entry, self.log_path)
        return doc_list

    def sanitize_filename(self, filename):
        """清理文件名中的非法字符。"""
        for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
            filename = filename.replace(char, '_')
        return filename

    def downLoad_file(self, url, filetype, description, officeDate, project):
        """下载单个文件。返回 (本地路径, '') 成功 / ('', 失败原因)。"""
        import requests
        headers = {"X-API-KEY": self.apikey}
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=120)
        except Exception as e:
            print("下载异常/超时:", e)
            return '', f"下载请求异常/超时: {e}"

        if response.status_code == 200:
            safe = self.sanitize_filename(description)
            ext = {"PDF": "pdf", "MS_WORD": "docx"}.get(filetype, "txt")
            fileName = f"{officeDate}-{safe}-{project}.{ext}"
            try:
                full = os.path.join(self.download_dir, fileName)
                with open(full, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("文件下载成功！")
                return full, ''
            except Exception as e:
                print("写文件失败:", e)
                return '', f"写文件失败: {e}"
        print("下载失败，状态码:", response.status_code)
        return '', f"文件下载返回{response.status_code}"

    def filter_documents(self, documents, document_code, official_date):
        """从文档列表里挑 documentCode 与 officialDate(前10位) 都匹配的。"""
        return [doc for doc in documents
                if doc.get('documentCode') == document_code
                and doc.get('officialDate', '')[:10] == official_date]
