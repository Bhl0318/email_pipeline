# -*- coding: UTF-8 -*-
"""
OA信息记录表 Wiki 页面创建工具（独立脚本）

用法:
    python oainfo_cli.py <案号>
    python oainfo_cli.py 20849-0017US01
    python oainfo_cli.py 20849-0017US01 --dry-run   # 仅预览，不实际创建
"""
import sys
import os
import re
import json
import logging
import argparse

import requests
# pymssql / pymysql 延迟到用到 DB 的函数里再 import：
# 让 WikiClient、对比文件写回等纯 HTTP/字符串逻辑在缺 DB 驱动的环境也能导入。

# ============================================================
# 日志配置
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================
# 配置（按需修改）
# ============================================================
WIKI_BASE = "http://10.10.70.90:9090"
WIKI_ADMIN = "confluence"
WIKI_PWD = "wikimaster"

MYSQL_HOST = "10.10.70.88"
MYSQL_PORT = 3306
MYSQL_USER = "tip88"
MYSQL_PWD = "tipadmin"
MYSQL_DB = "atw"

MSSQL_HOST = "10.10.70.88"
MSSQL_USER = "ipeasy"
MSSQL_PWD = "!@#123."
MSSQL_DB = "IPEasy"

# 简版模板的客户代码列表
SIMPLE_CUSTOMERS = [
    '20849', '20769', '20228', '20229', '20231', '20235',
    '20236', '20239', '20245', '20252', '20254', '20256',
    '20257', '20901'
]

WIKI_HEADERS = {
    'content-type': "application/json",
    "Accept": "application/json",
    "Authorization": "Bearer <access_token>"
}

# ============================================================
# 族页面模板（ZUCON）
# ============================================================
ZUCON = """<ac:layout><ac:layout-section ac:type="two_right_sidebar"><ac:layout-cell><h3>基本情况：</h3><table class="relative-table wrapped" style="width: 96.7409%;"><colgroup><col style="width: 13.1579%;" /><col style="width: 86.8421%;" /></colgroup><tbody><tr><th>案件名称</th><td></td></tr><tr><th>发明人（以优先权为准）</th><td><br /></td></tr><tr><th colspan="1">IPC分类</th><td colspan="1"><br /></td></tr><tr><th colspan="1">优先权日期</th><td colspan="1"><br /></td></tr><tr><th colspan="1">案件KOD目录&nbsp;</th><td colspan="1"></td></tr></tbody></table><h3><span>撰写类型</span></h3><table class="relative-table wrapped" style="width: 96.7409%;"><colgroup><col style="width: 13.1579%;" /><col style="width: 86.8421%;" /></colgroup><tbody><tr><th><strong>撰写类型</strong></th><td><ac:task-list>
<ac:task><ac:task-id>73</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>CN</ac:task-body></ac:task>
<ac:task><ac:task-id>74</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>PCT/US/EP</ac:task-body></ac:task>
<ac:task><ac:task-id>75</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>基于优先权的PCT/US/EP</ac:task-body></ac:task>
</ac:task-list></td></tr></tbody></table><p><br /></p><p><span style="font-size: 16.0px;font-weight: bold;">交底、技术理解、预检索和相关申请</span></p><table class="relative-table wrapped" style="width: 96.7409%;"><colgroup><col style="width: 13.1579%;" /><col style="width: 86.8421%;" /></colgroup><tbody><tr><th><strong>交底文件</strong></th><td><ac:task-list>
<ac:task><ac:task-id>1</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>下级技术理解页面中</ac:task-body></ac:task>
<ac:task><ac:task-id>2</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>单独下级页面</ac:task-body></ac:task>
<ac:task><ac:task-id>3</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>KOD文件夹中</ac:task-body></ac:task>
<ac:task><ac:task-id>4</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>无交底文件</ac:task-body></ac:task>
</ac:task-list></td></tr><tr><th colspan="1">技术理解</th><td colspan="1"><ac:task-list>
<ac:task><ac:task-id>5</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>下级技术理解页面</ac:task-body></ac:task>
<ac:task><ac:task-id>6</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>交底足够清晰，无单独技术理解内容</ac:task-body></ac:task>
</ac:task-list></td></tr><tr><th colspan="1">预检索</th><td colspan="1"><ac:task-list>
<ac:task><ac:task-id>26</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>按客户要求不进行预检索</ac:task-body></ac:task>
<ac:task><ac:task-id>27</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>客户提供预检索信息</ac:task-body></ac:task>
<ac:task><ac:task-id>28</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>我方进行预检索</ac:task-body></ac:task>
</ac:task-list></td></tr><tr><th colspan="1">相关申请</th><td colspan="1"><ac:task-list>
<ac:task><ac:task-id>76</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>无相关申请</ac:task-body></ac:task>
<ac:task><ac:task-id>77</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>客户提供相关申请</ac:task-body></ac:task>
</ac:task-list></td></tr></tbody></table></ac:layout-cell><ac:layout-cell><h3>详细记录子页面：</h3><p><strong><ac:structured-macro ac:name="children" ac:schema-version="2"><ac:parameter ac:name="all">true</ac:parameter></ac:structured-macro></strong></p></ac:layout-cell></ac:layout-section><ac:layout-section ac:type="single"><ac:layout-cell><h3>撰写阶段的相关文献</h3><table class="relative-table wrapped"><colgroup><col style="width: 49.0px;" /><col style="width: 447.0px;" /></colgroup><tbody><tr><th class="numberingColumn">序号</th><th>客户提供的其他文献</th></tr><tr><td class="numberingColumn">1</td><td><br /></td></tr><tr><td class="numberingColumn">2</td><td><br /></td></tr></tbody></table></ac:layout-cell></ac:layout-section></ac:layout>"""


# ============================================================
# 数据库查询
# ============================================================
def get_mysql_connection():
    import pymysql
    return pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PWD,
        database=MYSQL_DB, charset='utf8'
    )


def get_cus_space_map():
    """从 cus_space 表获取客户代码 → Wiki空间映射"""
    conn = get_mysql_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT cus_code, s_key, p_id FROM cus_space WHERE cus_code != ''")
        wiki_key = {}
        for row in cur.fetchall():
            wiki_key[row[0]] = {"key": row[1], "pid": row[2]}
        return wiki_key
    finally:
        conn.close()


def find_project_info(project):
    """从 IPEasy 查询案件名称和公开号（参数化查询）"""
    import pymssql
    conn = pymssql.connect(MSSQL_HOST, MSSQL_USER, MSSQL_PWD, MSSQL_DB, charset='utf8')
    try:
        cur = conn.cursor()
        cur.execute("SELECT case_name, pub_no FROM p_case_info WHERE case_volume = %s", (project,))
        row = cur.fetchone()
        if row:
            return row[0] or '', row[1] or ''
        return '', ''
    finally:
        conn.close()


def query_project_write_info(zu_code, project):
    """查询撰写案的 QC/负责人/参与人"""
    conn = get_mysql_connection()
    try:
        cur = conn.cursor()
        # 先查当前案号
        cur.execute(
            "SELECT project_participant, project_qc, project_leader FROM projects "
            "WHERE project = %s AND project_type IN ('CN撰写','EN撰写') LIMIT 1",
            (project,)
        )
        row = cur.fetchone()
        if row and any(row):
            return row[0] or '', row[1] or '', row[2] or ''

        # 查同族
        cur.execute(
            "SELECT project_participant, project_qc, project_leader FROM projects "
            "WHERE project LIKE %s AND project_type IN ('CN撰写','EN撰写')",
            (f'{zu_code}%',)
        )
        for row in cur.fetchall():
            if row[0]:
                return row[0] or '', row[1] or '', row[2] or ''
        return '', '', ''
    finally:
        conn.close()


def query_first_case_info(zu_code):
    """查询同族首案信息"""
    conn = get_mysql_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT project, project_name, project_participant, project_qc, project_leader "
            "FROM projects WHERE project LIKE %s AND oa_remark LIKE '%%首案%%' "
            "AND project_type LIKE '%%答复及其他%%'",
            (f'{zu_code}%',)
        )
        lines = []
        for row in cur.fetchall():
            pro, name, par, qc, pm = row
            lines.append(f"{pro}{name or ''}，QC:{qc or ''}；负责人：{pm or ''}；参与人：{par or ''}")
        return '<br/>'.join(lines)
    finally:
        conn.close()


# ============================================================
# Wiki API 操作
# ============================================================
class WikiClient:
    def __init__(self):
        self.auth = (WIKI_ADMIN, WIKI_PWD)
        self.headers = WIKI_HEADERS

    def search_page(self, title):
        """按标题搜索 Wiki 页面，返回 results 列表"""
        url = f"{WIKI_BASE}/rest/api/content"
        params = {
            'title': title, 'start': 0, 'limit': 10,
            'expand': 'space,history,body.view,metadata.labels'
        }
        try:
            resp = requests.get(url, params=params, auth=self.auth, headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp.json().get('results', [])
        except requests.RequestException as e:
            logger.error(f"Wiki 搜索页面失败 [{title}]: {e}")
            return []

    def get_page(self, title):
        """按标题获取页面内容（storage 格式），返回 {id, version, body, space_key} 或 None"""
        url = f"{WIKI_BASE}/rest/api/content"
        params = {
            'title': title, 'start': 0, 'limit': 1,
            'expand': 'body.storage,version,space'
        }
        try:
            resp = requests.get(url, params=params, auth=self.auth, headers=self.headers, timeout=15)
            resp.raise_for_status()
            results = resp.json().get('results', [])
            if results:
                page = results[0]
                return {
                    "id": page['id'],
                    "version": page['version']['number'],
                    "body": page['body']['storage']['value'],
                    "space_key": page['space']['key'],
                }
        except requests.RequestException as e:
            logger.error(f"Wiki 获取页面失败 [{title}]: {e}")
        return None

    def update_page(self, page_id, title, content, version):
        """更新页面内容"""
        data = {
            "type": "page",
            "title": title,
            "version": {"number": version + 1},
            "body": {"storage": {"representation": "storage", "value": content}}
        }
        try:
            resp = requests.put(
                f"{WIKI_BASE}/rest/api/content/{page_id}",
                auth=self.auth, headers=self.headers,
                data=json.dumps(data), timeout=15
            )
            if resp.status_code == 200:
                logger.info(f"页面更新成功: {title}")
            else:
                logger.error(f"页面更新失败 [{title}]: HTTP {resp.status_code} - {resp.text[:200]}")
            return resp.status_code
        except requests.RequestException as e:
            logger.error(f"Wiki 更新页面异常 [{title}]: {e}")
            return 500

    def create_child_page(self, title, content, space_key, parent_id):
        """在指定父页面下创建子页面"""
        data = {
            "type": "page",
            "ancestors": [{"id": str(parent_id)}],
            "space": {"key": str(space_key)},
            "title": title,
            "body": {"storage": {"representation": "storage", "value": content}}
        }
        try:
            resp = requests.post(
                f"{WIKI_BASE}/rest/api/content/",
                auth=self.auth, headers=self.headers,
                data=json.dumps(data), timeout=15
            )
            if resp.status_code == 200:
                logger.info(f"页面创建成功: {title}")
            else:
                logger.error(f"页面创建失败 [{title}]: HTTP {resp.status_code} - {resp.text[:200]}")
            return resp.status_code
        except requests.RequestException as e:
            logger.error(f"Wiki 创建页面异常 [{title}]: {e}")
            return 500

    def upload_attachment(self, page_id, filepath):
        """上传附件到指定页面（集成自 createwikioa.putAttachment）。
        同名附件 Confluence 会更新为新版本，不会重复。返回 True/False。
        注意：headers 只带 X-Atlassian-Token，不能带 application/json，
        否则 multipart 上传会失败。"""
        if not page_id:
            logger.error(f"附件上传跳过：page_id 为空 ({filepath})")
            return False
        if not os.path.exists(filepath):
            logger.error(f"附件上传跳过：文件不存在 {filepath}")
            return False
        url = f"{WIKI_BASE}/rest/api/content/{page_id}/child/attachment"
        try:
            with open(filepath, "rb") as fh:
                resp = requests.post(
                    url, auth=self.auth,
                    headers={"X-Atlassian-Token": "nocheck"},
                    files={"file": fh}, timeout=60,
                )
            if resp.status_code in (200, 201):
                logger.info(f"附件上传成功: {os.path.basename(filepath)} → page {page_id}")
                return True
            logger.error(f"附件上传失败 [{os.path.basename(filepath)}]: HTTP {resp.status_code} - {resp.text[:200]}")
            return False
        except requests.RequestException as e:
            logger.error(f"附件上传异常 [{filepath}]: {e}")
            return False


# ============================================================
# OA 页面 HTML 模板
# ============================================================
def build_simple_template(project, patentlink, tzu_link, tzu):
    """简版客户模板（无策略模块）"""
    p2 = f"""
    <table class="relative-table wrapped" style="width: 56.2396%;">
    <colgroup><col style="width: 10.2665%;" /><col style="width: 89.7335%;" /></colgroup>
    <tbody>
    <tr><th colspan="1"><p>申请文件链接</p></th><td colspan="1"><strong>填写Google Patent的公开链接:{patentlink}</strong></td></tr>
    <tr><th colspan="1"><p><strong>TIP同族信息</strong></p></th><td colspan="1">{tzu_link}</td></tr>
    <tr><th colspan="1">唯德同族信息</th><td colspan="1"><span style="color: rgb(23,43,77);">{tzu}</span></td></tr>
    <tr><th colspan="1">授权状态</th><td colspan="1"><span style="color: rgb(23,43,77);"></span></td></tr>
    </tbody></table>"""

    p4 = """
    <table class="relative-table wrapped" style="width: 99.5739%;">
    <colgroup><col style="width: 12.3016%;" /><col style="width: 87.6191%;" /></colgroup>
    <thead><tr>
    <th style="text-align: left;" colspan="1"><p>OA次数</p></th>
    <th style="text-align: left;"><p><span style="color: rgb(0,0,255);">答复期限</span></p></th>
    <th style="text-align: left;">送审记录</th>
    </tr></thead>
    <tbody>
    <tr><td>OA1</td><td></td><td></td></tr>
    <tr><td>OA2</td><td></td><td></td></tr>
    <tr><td>OA3</td><td></td><td></td></tr>
    </tbody></table>"""

    return '', p2, '', p4


def build_full_template(project, project_title, public, patentlink, tzu_link, tzu):
    """完整版客户模板（含策略模块）"""
    p1 = """<h2>案件整体策略</h2><p>说明:下表用于案件处理过程中记录整体思路及案件最终授权结果。</p>"""

    p2 = f"""
    <table class="relative-table wrapped" style="width: 56.2396%;">
    <colgroup><col style="width: 10.2665%;" /><col style="width: 89.7335%;" /></colgroup>
    <tbody>
    <tr><th style="text-align: left;"><span style="color: rgb(0,51,102);">案号</span></th><td style="text-align: left;">{project}</td></tr>
    <tr><th colspan="1">案件标题</th><td colspan="1">{project_title}</td></tr>
    <tr><th colspan="1">公开号</th><td colspan="1">{public}</td></tr>
    <tr><th colspan="1">分类号</th><td colspan="1"></td></tr>
    <tr><th colspan="1">申请文件链接</th><td colspan="1"><strong>填写Google Patent的公开链接:{patentlink}</strong></td></tr>
    <tr><th colspan="1">TIP同族信息</th><td colspan="1">{tzu_link}</td></tr>
    <tr><th colspan="1">唯德同族信息</th><td colspan="1"><span style="color: rgb(23,43,77);">{tzu}</span></td></tr>
    <tr><th colspan="1">授权状态</th><td colspan="1"><span style="color: rgb(23,43,77);"></span></td></tr>
    </tbody></table>"""

    p3 = """<ac:layout-section ac:type="single"><ac:layout-cell>
    <p><strong>整体策略思路记录及案件授权结果</strong></p>
    <table class="relative-table wrapped" style="width: 100.0%;">
    <colgroup><col style="width: 1.93%;" /><col style="width: 87.57%;" /><col /></colgroup>
    <tbody>
    <tr><th class="numberingColumn">1</th><td></td><td rowspan="4"><h3>案件授权结果：</h3><ac:task-list>
    <ac:task><ac:task-id>65</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body><strong>授权</strong></ac:task-body></ac:task>
    <ac:task><ac:task-id>67</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body><strong>放弃</strong></ac:task-body></ac:task>
    </ac:task-list></td></tr>
    <tr><th class="numberingColumn">2</th><td><br /></td></tr>
    <tr><th class="numberingColumn">3</th><td><br /></td></tr>
    <tr><th class="numberingColumn" colspan="1">4</th><td colspan="1"><br /></td></tr>
    </tbody></table>
    </ac:layout-cell></ac:layout-section>"""

    p4 = """<p><span>审查意见链接：将审查意见在<a href="http://10.10.70.88:8058/demand/word">http://10.10.70.88:8058/demand/word</a>生成Wiki页面。</span></p>
    <p><span><span style="color: rgb(0,51,102);">对比文件链接：可以是Google Patent链接。</span></span></p>
    <table class="relative-table wrapped" style="width: 100.0%;">
    <thead><tr>
    <th style="text-align: left;" colspan="1"><p>OA次数</p></th>
    <th colspan="1">OA收文日</th>
    <th style="text-align: left;"><p><span style="color: rgb(0,51,102);">期限</span></p></th>
    <th colspan="1">存在可授权</th>
    <th colspan="1"><p>对比文件链接</p></th>
    <th style="text-align: left;">送审记录</th>
    </tr></thead>
    <tbody>
    <tr><td>OA1</td><td></td><td></td><td><ac:task-list><ac:task><ac:task-id>106</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>&nbsp;</ac:task-body></ac:task></ac:task-list></td><td></td><td></td></tr>
    <tr><td>OA2</td><td></td><td></td><td><ac:task-list><ac:task><ac:task-id>107</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>&nbsp;</ac:task-body></ac:task></ac:task-list></td><td></td><td></td></tr>
    <tr><td>OA3</td><td></td><td></td><td><ac:task-list><ac:task><ac:task-id>108</ac:task-id><ac:task-status>incomplete</ac:task-status><ac:task-body>&nbsp;</ac:task-body></ac:task></ac:task-list></td><td></td><td></td></tr>
    </tbody></table>"""

    return p1, p2, p3, p4


def assemble_page(p1, p2, p3, p4):
    """将模板片段组装为完整 OA 页面"""
    return f"""<ac:layout>
    <ac:layout-section ac:type="two_right_sidebar">
    <ac:layout-cell>
    <ac:structured-macro ac:name="expand" ac:schema-version="1"><ac:parameter ac:name="title">模板使用说明：</ac:parameter>
    <ac:rich-text-body><p><strong>模板使用说明：</strong></p>
    <p><strong>1. 请复制本页至同族记录页面下，标题格式为：案号-OA信息记录表</strong></p>
    <p><strong>2. 对于审查意见及其他资料，请通过 <a href="http://10.10.70.88:8058/demand/word">http://10.10.70.88:8058/demand/word</a> 转换并生成Wiki页面</strong></p>
    </ac:rich-text-body></ac:structured-macro>
    <p><span style="color: rgb(255,0,0);"><strong>注意：</strong></span></p>
    <ul>
    <li><span style="color: rgb(255,0,0);"><strong>本页链接仅用于方便快速查看，最终准备答复意见时请核对正式文本。</strong></span></li>
    <li><span style="color: rgb(255,0,0);"><strong>答复策略需要与答复稿一致！！！</strong></span></li>
    </ul>
    {p1}
    </ac:layout-cell>
    <ac:layout-cell><p><strong>本页目录：</strong></p><p><ac:structured-macro ac:name="toc" ac:schema-version="1"><ac:parameter ac:name="maxLevel">3</ac:parameter><ac:parameter ac:name="minLevel">2</ac:parameter></ac:structured-macro></p></ac:layout-cell>
    </ac:layout-section>
    {p3}
    <ac:layout-section ac:type="single"><ac:layout-cell><h2>OA基本信息</h2>
    <h3><span style="color: rgb(17,31,44);">案件信息</span></h3>
    {p2}
    </ac:layout-cell></ac:layout-section>
    <ac:layout-section ac:type="two_right_sidebar"><ac:layout-cell><h3>OA过程</h3>
    {p4}
    <h3>本案原始文件</h3><p><strong>上传：递交文件终版+本次审查意见</strong></p>
    <p><ac:structured-macro ac:name="attachments" ac:schema-version="1"><ac:parameter ac:name="old">false</ac:parameter><ac:parameter ac:name="sortOrder">descending</ac:parameter><ac:parameter ac:name="sortBy">createddate</ac:parameter></ac:structured-macro></p>
    </ac:layout-cell><ac:layout-cell><strong>子页面（含程序生成的审查意见链接）</strong>
    <p><ac:structured-macro ac:name="children" ac:schema-version="2" /></p>
    </ac:layout-cell></ac:layout-section>
    <ac:layout-section ac:type="single"><ac:layout-cell><h2>OA1答复策略</h2><ac:structured-macro ac:name="expand" ac:schema-version="1"><ac:rich-text-body><p><br /></p></ac:rich-text-body></ac:structured-macro></ac:layout-cell></ac:layout-section>
    <ac:layout-section ac:type="single"><ac:layout-cell><h2>OA2答复策略</h2><ac:structured-macro ac:name="expand" ac:schema-version="1"><ac:rich-text-body><p><br /></p></ac:rich-text-body></ac:structured-macro></ac:layout-cell></ac:layout-section>
    <ac:layout-section ac:type="single"><ac:layout-cell><h2>US项目CIP或续案建议</h2><ac:structured-macro ac:name="expand" ac:schema-version="1"><ac:rich-text-body><p><br /></p></ac:rich-text-body></ac:structured-macro></ac:layout-cell></ac:layout-section>
    </ac:layout>"""


# ============================================================
# 核心逻辑
# ============================================================
def create_oa_page(project, dry_run=False):
    """
    根据案号创建/查找 OA 信息记录表 Wiki 页面

    Args:
        project: 案号，如 '20849-0017US01'
        dry_run: 仅预览，不实际创建

    Returns:
        dict: {code, msg, url}
    """
    logger.info(f"开始处理案号: {project}")

    # --- 1. 解析案号 ---
    customerzu_match = re.findall(r'[0-9A-Z]{5}-[a-zA-Z0-9]{4}', project)
    if not customerzu_match:
        return {"code": 400, "msg": "案号格式不正确，无法解析族号", "url": ""}
    zu_code = customerzu_match[0]
    customer_code = project.split('-')[0]
    if project[0:1] == '5':
        customer_code = '5'
    elif project[0:1] == '6':
        customer_code = '6'

    zutitle = zu_code + "族案件记录"
    fintitle = project + '-OA信息记录表'
    logger.info(f"族号: {zu_code}, 客户代码: {customer_code}")
    logger.info(f"族页面: {zutitle}, OA页面: {fintitle}")

    # --- 2. 查询案件信息 ---
    project_title, public = find_project_info(project)
    logger.info(f"案件名称: {project_title}, 公开号: {public}")

    ppar, pqc, ppm = query_project_write_info(zu_code, project)
    if ppar or pqc or ppm:
        logger.info(f"撰写人员: QC:{pqc};负责人:{ppm};参与人:{ppar}")

    tzu_wcon = query_first_case_info(zu_code)
    if tzu_wcon:
        logger.info(f"同族首案: {tzu_wcon}")

    # --- 3. 匹配 Wiki 空间 ---
    wiki_key_map = get_cus_space_map()
    if customer_code not in wiki_key_map:
        customer_code = 'other'
    wikikey = wiki_key_map.get(customer_code, wiki_key_map.get('other'))
    if not wikikey:
        return {"code": 400, "msg": f"未找到客户 {customer_code} 的Wiki空间配置", "url": ""}
    logger.info(f"Wiki 空间: key={wikikey['key']}, pid={wikikey['pid']}")

    # --- 4. 构造链接 ---
    tzu = f"<a href='http://10.10.70.88:8086/showProZu/{project[0:10]}'>http://10.10.70.88:8086/showProZu/{project[0:10]}</a>"
    tzu_link = f"<a target='_blank' href='http://10.10.70.88:8080/manage/prosummary_search?pro={zu_code}'>http://10.10.70.88:8080/manage/prosummary_search?pro={zu_code}</a>"
    patentlink = ''
    if public:
        patentlink = f"<a target='_blank' href='https://patents.google.com/patent/{public}'>{project}的申请文件</a>"

    # --- 5. 查找族页面 ---
    wiki = WikiClient()
    zu_results = wiki.search_page(zutitle)

    zu_page_id = None
    zu_space_key = None
    for page in zu_results:
        if page['space']['key'] == wikikey['key']:
            zu_page_id = page['id']
            zu_space_key = page['space']['key']
            break

    if not zu_page_id:
        # 族页面不存在，先创建
        logger.info(f"族页面不存在，创建: {zutitle}")
        if dry_run:
            logger.info("[DRY-RUN] 跳过创建族页面")
            return {"code": 0, "msg": "[DRY-RUN] 需要先创建族页面", "url": ""}
        wiki.create_child_page(zutitle, ZUCON, wikikey["key"], wikikey["pid"])
        # 递归调用（族页面创建后重新走流程）
        return create_oa_page(project, dry_run)

    logger.info(f"族页面已存在: id={zu_page_id}, space={zu_space_key}")

    # --- 6. 选择模板 ---
    is_simple = (customer_code in SIMPLE_CUSTOMERS or customer_code in ['5', '6'])
    if is_simple:
        logger.info("使用简版模板")
        p1, p2, p3, p4 = build_simple_template(project, patentlink, tzu_link, tzu)
    else:
        logger.info("使用完整版模板")
        p1, p2, p3, p4 = build_full_template(project, project_title, public, patentlink, tzu_link, tzu)

    page_html = assemble_page(p1, p2, p3, p4)

    # --- 7. 判断 OA 页面是否已存在 ---
    oa_results = wiki.search_page(fintitle)
    page_url = f"{WIKI_BASE}/display/{zu_space_key}/{fintitle}"

    if oa_results:
        logger.info(f"OA页面已存在: {page_url}")
        return {"code": 0, "msg": "OA页面已存在", "url": page_url, "id": oa_results[0].get("id")}

    if dry_run:
        logger.info(f"[DRY-RUN] 将创建OA页面: {fintitle}")
        logger.info(f"[DRY-RUN] 父页面ID: {zu_page_id}, 空间: {wikikey['key']}")
        return {"code": 0, "msg": "[DRY-RUN] OA页面将被创建", "url": page_url, "id": None}

    status = wiki.create_child_page(fintitle, page_html, wikikey["key"], zu_page_id)
    if status == 200:
        logger.info(f"OA页面创建成功: {page_url}")
        # create_child_page 只返回状态码，回查一次拿 page id（供上传附件用）
        created = wiki.get_page(fintitle)
        return {"code": 0, "msg": "OA页面创建成功", "url": page_url,
                "id": created.get("id") if created else None}
    else:
        return {"code": 1, "msg": f"OA页面创建失败 (HTTP {status})", "url": "", "id": None}


# ============================================================
# 写入新增 OA 页面（追加行到现有表格）
# ============================================================
OA_LIST_PAGE_TITLE = "测试页面-写入新增OA"


def _build_table_row(item):
    """根据筛选结果构建一行 HTML。"""
    project = item.get("project", "")
    oa_remark = item.get("oa_remark", "")
    entrust_date = item.get("entrust_date", "")
    oa_doc_date = item.get("oa_doc_date", "")
    project_deadline = item.get("project_deadline", "")
    project_name = item.get("project_name", "")

    return (
        f"<tr>"
        f"<td>{project}</td>"
        f"<td>{oa_remark}</td>"
        f"<td>{entrust_date}</td>"
        f"<td>{oa_doc_date}</td>"
        f"<td>{project_deadline}</td>"
        f"<td>{project_name}</td>"
        f"<td></td>"
        f"<td></td>"
        f"<td></td>"
        f"<td></td>"
        f"</tr>"
    )


def append_oa_to_wiki(results):
    """
    将筛选结果批量追加到 Wiki 新增 OA 页面的表格中。

    Args:
        results: filter_oa_email 的筛选结果列表

    Returns:
        dict: {code, msg, count}
    """
    if not results:
        return {"code": 0, "msg": "无数据需要写入", "count": 0}

    wiki = WikiClient()
    page = wiki.get_page(OA_LIST_PAGE_TITLE)
    if not page:
        return {"code": 1, "msg": f"未找到页面: {OA_LIST_PAGE_TITLE}", "count": 0}

    body = page["body"]

    # 构建新行
    new_rows = ""
    for item in results:
        if not item.get("project"):
            continue
        new_rows += _build_table_row(item) + "\n"

    if not new_rows:
        return {"code": 0, "msg": "无有效数据写入", "count": 0}

    # 在 </tbody> 前插入新行
    if "</tbody>" in body:
        body = body.replace("</tbody>", new_rows + "</tbody>", 1)
    else:
        logger.error("页面中未找到 </tbody> 标签")
        return {"code": 1, "msg": "页面格式异常，未找到表格", "count": 0}

    # 更新页面
    status = wiki.update_page(page["id"], OA_LIST_PAGE_TITLE, body, page["version"])
    if status == 200:
        count = len([r for r in results if r.get("project")])
        logger.info(f"新增 OA 页面写入成功: {count} 条")
        return {"code": 0, "msg": f"写入成功 {count} 条", "count": count}
    else:
        return {"code": 1, "msg": f"页面更新失败 (HTTP {status})", "count": 0}


# ============================================================
# 对比文件写回 OA信息记录表页（填「OA过程」表 OA{N} 行的「对比文件链接」列）
# ============================================================
def _strip_tags(s):
    """去 HTML 标签 + 常见转义/空白，用于判断单元格是否为空、比对首列文本。"""
    t = re.sub(r'<[^>]+>', '', s or '')
    t = t.replace('&nbsp;', '').replace('\xa0', '')
    return t.strip()


def _ref_docs_cell_html(ref_docs):
    """把对比文件列表拼成单元格 HTML：文件号超链到 Google Patent，带公开日，多件用「；」分隔。"""
    parts = []
    for d in ref_docs:
        doc_no = (d.get("doc_no") or "").strip()
        if not doc_no:
            continue
        pub = (d.get("pub_date") or "").strip()
        link = (f'<a href="https://patents.google.com/patent/{doc_no}">{doc_no}</a>')
        parts.append(f'{link}（{pub}）' if pub else link)
    return '；'.join(parts)


def _split_cells(row_html):
    """把一个 <tr>…</tr> 拆成完整的 <td>…</td> 列表（td 不嵌套 td，非贪婪安全）。"""
    return re.findall(r'<td\b[^>]*>.*?</td>', row_html, re.DOTALL)


def _splice_ref_docs_into_body(body, oa_seq, cell_html):
    """把对比文件单元格填进「OA过程」表 OA{oa_seq} 行的「对比文件链接」列（纯字符串处理，便于测试）。

    Returns:
        (new_body, status)。status ∈
          filled          成功填入已有 OA{N} 行
          added_row        无 OA{N} 行，自动补一行并填入
          skip_no_column   页面无「对比文件链接」列（简版模板）
          skip_nonempty    目标单元格已有内容，不覆盖
    """
    # 1. 找含「对比文件链接」的那张表（table 不嵌套，非贪婪安全）
    target = None
    for m in re.finditer(r'<table\b.*?</table>', body, re.DOTALL):
        if '对比文件链接' in m.group(0):
            target = m
            break
    if target is None:
        return body, "skip_no_column"
    tbl = target.group(0)

    # 2. 表头定位「对比文件链接」列序号
    ths = re.findall(r'<th\b[^>]*>.*?</th>', tbl, re.DOTALL)
    col_count = len(ths)
    col_index = next((i for i, th in enumerate(ths) if '对比文件链接' in _strip_tags(th)), None)
    if col_index is None:
        return body, "skip_no_column"

    tb = re.search(r'<tbody\b[^>]*>(.*?)</tbody>', tbl, re.DOTALL)
    if not tb:
        return body, "skip_no_column"
    tbody_inner = tb.group(1)

    new_cell = f'<td>{cell_html}</td>'
    want = f'OA{oa_seq}'

    # 3. 找 OA{N} 行并替换目标单元格
    rows = re.findall(r'<tr\b[^>]*>.*?</tr>', tbody_inner, re.DOTALL)
    for row in rows:
        cells = _split_cells(row)
        if not cells or _strip_tags(cells[0]) != want:
            continue
        if col_index >= len(cells):
            break  # 该行列数不够（异常），走补行
        if _strip_tags(cells[col_index]):
            return body, "skip_nonempty"
        new_cells = cells[:]
        new_cells[col_index] = new_cell
        # 用新单元格串按序重建该行（保留原 <tr ...> 开标签）
        tr_open = re.match(r'<tr\b[^>]*>', row).group(0)
        new_row = tr_open + ''.join(new_cells) + '</tr>'
        new_tbody = tbody_inner.replace(row, new_row, 1)
        new_tbl = tbl.replace(tbody_inner, new_tbody, 1)
        return body[:target.start()] + new_tbl + body[target.end():], "filled"

    # 4. 无 OA{N} 行 → 自动补一行（首列 OA{N}，目标列填对比文件，其余留空）
    cells = []
    for i in range(col_count):
        if i == 0:
            cells.append(f'<td>{want}</td>')
        elif i == col_index:
            cells.append(new_cell)
        else:
            cells.append('<td></td>')
    add_row = '<tr>' + ''.join(cells) + '</tr>'
    new_tbody = tbody_inner + add_row
    new_tbl = tbl.replace(tbody_inner, new_tbody, 1)
    return body[:target.start()] + new_tbl + body[target.end():], "added_row"


def fill_ref_docs_in_oa_row(page_title, oa_seq, ref_docs, dry_run=False):
    """把对比文件写到 `案号-OA信息记录表` 页「OA过程」表 OA{oa_seq} 行的「对比文件链接」列。

    仅完整版模板有该列；简版模板 skip_no_column。幂等：单元格已有内容不覆盖。
    Returns: dict {status, http?}
    """
    if not ref_docs:
        return {"status": "no_ref_docs"}
    if not oa_seq:
        logger.warning(f"[对比文件] {page_title} 无法确定 OA 次数，跳过")
        return {"status": "no_oa_seq"}

    wiki = WikiClient()
    page = wiki.get_page(page_title)
    if not page:
        logger.warning(f"[对比文件] 未找到页面: {page_title}")
        return {"status": "page_not_found"}

    cell_html = _ref_docs_cell_html(ref_docs)
    if not cell_html:
        return {"status": "no_ref_docs"}

    new_body, status = _splice_ref_docs_into_body(page["body"], oa_seq, cell_html)
    if status.startswith("skip") or new_body == page["body"]:
        logger.info(f"[对比文件] {page_title} OA{oa_seq}: {status}")
        return {"status": status}

    if dry_run:
        logger.info(f"[对比文件][dry-run] {page_title} OA{oa_seq}: {status} → {cell_html}")
        return {"status": status, "dry_run": True}

    code = wiki.update_page(page["id"], page_title, new_body, page["version"])
    logger.info(f"[对比文件] {page_title} OA{oa_seq}: {status} (HTTP {code})")
    return {"status": status, "http": code}


# ============================================================
# CLI 入口
# ============================================================
def main():
    parser = argparse.ArgumentParser(description='OA信息记录表 Wiki 页面创建工具')
    parser.add_argument('project', help='案号，如 20849-0017US01')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不实际创建页面')
    args = parser.parse_args()

    result = create_oa_page(args.project, dry_run=args.dry_run)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    sys.exit(0 if result['code'] == 0 else 1)


if __name__ == '__main__':
    main()
