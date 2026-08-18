import os,requests,json
from collections import defaultdict
from datetime import datetime

LOG_FILENAME = "uspto_download_log.jsonl"


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
    """USPTO专利申请页面自动化类"""

    def __init__(self, download_dir="output", mail_id=None, project=None, log_path=None):
        """
        初始化USPTO页面自动化类

        Args:
            download_dir (str): 基础下载目录路径
            project (str): 项目文件夹名称
            log_path (str): 下载 JSON 日志路径；不给则默认落下载基目录下的 uspto_download_log.jsonl，
                            可用环境变量 USPTO_DOWNLOAD_LOG 覆盖。
        """
        self.base_download_dir = download_dir
        self.project = project
        self.l = mail_id
        self.apikey = "oarxhcottmeqhpgausxoghscnjhllr"
        # 日志路径不写死：优先入参 → 环境变量 → 下载基目录下
        self.log_path = (log_path or os.environ.get("USPTO_DOWNLOAD_LOG")
                         or os.path.join(download_dir, LOG_FILENAME))

        # 构建完整的下载目录路径
        if project:
            self.download_dir = os.path.join(download_dir, project)
        else:
            self.download_dir = download_dir

        # 确保下载目录存在
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"创建下载目录: {self.download_dir}")



    def downLoad_Documents_ByAPI(self,application,document_code,official_date,project,descriptionWiki,kind="oa"):
        url = f"https://api.uspto.gov/api/v1/patent/applications/{application}/documents"
        print(url)
        headers = {
            "X-API-KEY": self.apikey
        }
        # 下载日志一条：kind=oa 官文 / ref 文献(892·1449)
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
            # 无匹配：列出该申请下实际可用的 (documentCode@officialDate)，便于诊断代码/日期为何没对上
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
                downUrl = i['downloadUrl']
                fileType = i['mimeTypeIdentifier']
                fName, err = self.downLoad_file(downUrl, fileType, description, official_date, project)
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
        """清理文件名中的非法字符"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def downLoad_file(self,url,filetype,description,officeDate,project):
        """下载单个文件。返回 (本地路径, '') 成功 / ('', 失败原因)。"""
        headers = {
            "X-API-KEY": self.apikey
        }
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=120)  # 用 stream=True
        except Exception as e:
            print("下载异常/超时:", e)
            return '', f"下载请求异常/超时: {e}"

        if response.status_code == 200:
            safe_description = self.sanitize_filename(description)
            if filetype == "PDF":
                fileName = f"{officeDate}-{safe_description}-{project}.pdf"
            elif filetype == "MS_WORD":
                fileName = f'{officeDate}-{safe_description}-{project}.docx'
            else:
                fileName = f'{officeDate}-{safe_description}-{project}.txt'
            try:
                full = os.path.join(self.download_dir, fileName)
                with open(full, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("PDF 下载成功！")
                return full, ''
            except Exception as e:
                print("写文件失败:", e)
                return '', f"写文件失败: {e}"
        else:
            print("下载失败，状态码:", response.status_code)
            return '', f"文件下载返回{response.status_code}"



    def filter_documents(self,documents, document_code, official_date):
        filtered = []
        for doc in documents:
            # 提取并格式化 officialDate
            doc_date = doc.get('officialDate', '')[:10]  # 截取前10位 yyyy-mm-dd
            if doc.get('documentCode') == document_code and doc_date == official_date:
                filtered.append(doc)
        return filtered






if __name__ == "__main__":
    uspto = USPTOApplication(
        # download_dir=os.path.join("T:\\USPTO", today_str),                        #目录修改
        download_dir="uspto",
        mail_id='1233',
        project='2222'
    )

    res = uspto.downLoad_Documents_ByAPI("17456882","EGRANT.PDF","2025-02-11",'2222','wikiTest')
    print("res:",res)





