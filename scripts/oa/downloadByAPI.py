import os,requests,json
from collections import defaultdict


class USPTOApplication:
    """USPTO专利申请页面自动化类"""

    def __init__(self, download_dir="output", mail_id=None, project=None):
        """
        初始化USPTO页面自动化类

        Args:
            download_dir (str): 基础下载目录路径
            project (str): 项目文件夹名称
        """
        self.base_download_dir = download_dir
        self.project = project
        self.l = mail_id
        self.apikey = "oarxhcottmeqhpgausxoghscnjhllr"

        # 构建完整的下载目录路径
        if project:
            self.download_dir = os.path.join(download_dir, project)
        else:
            self.download_dir = download_dir

        # 确保下载目录存在
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            print(f"创建下载目录: {self.download_dir}")



    def downLoad_Documents_ByAPI(self,application,document_code,official_date,project,descriptionWiki):
        url = f"https://api.uspto.gov/api/v1/patent/applications/{application}/documents"
        print(url)
        headers = {
            "X-API-KEY": self.apikey
        }

        response = requests.get(url, headers=headers)

        # 打印状态码与返回内容
        print(response.status_code)
        doc_list = defaultdict(list)
        if response.status_code == 200:
            res = json.loads(response.text)
            documentBag = res["documentBag"]
            docRes = self.filter_documents(documentBag,document_code,official_date)
            for doc in docRes:
                description = doc["documentCodeDescriptionText"] if not descriptionWiki else descriptionWiki
                for i in doc["downloadOptionBag"]:
                    downUrl = i['downloadUrl']
                    fileType = i['mimeTypeIdentifier']
                    fName = self.downLoad_file(downUrl,fileType,description,official_date,project)
                    if fName:
                        doc_list[project].append(fName)
        return doc_list



    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    def downLoad_file(self,url,filetype,description,officeDate,project):
        headers = {
            "X-API-KEY": self.apikey
        }

        response = requests.get(url, headers=headers, stream=True)  # 用 stream=True

        if response.status_code == 200:
            safe_description = self.sanitize_filename(description)
            if filetype == "PDF":
                fileName = f"{officeDate}-{safe_description}-{project}.pdf"
            elif filetype == "MS_WORD":
                fileName = f'{officeDate}-{safe_description}-{project}.docx'
            else:
                fileName = f'{officeDate}-{safe_description}-{project}.txt'
            with open(os.path.join(self.download_dir, fileName), "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print("PDF 下载成功！")
            return os.path.join(self.download_dir, fileName)
        else:
            print("下载失败，状态码:", response.status_code)
            return ''



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





