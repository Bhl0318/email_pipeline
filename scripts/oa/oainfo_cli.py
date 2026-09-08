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


def find_customer_case_no(project):
    """从 IPEasy p_case_info 查客户案号(委托方案号 case_volume_customer)。查不到/异常返回 ''。"""
    if not project:
        return ''
    import pymssql
    try:
        conn = pymssql.connect(MSSQL_HOST, MSSQL_USER, MSSQL_PWD, MSSQL_DB, charset='utf8')
        try:
            cur = conn.cursor()
            cur.execute("SELECT case_volume_customer FROM p_case_info WHERE case_volume = %s", (project,))
            row = cur.fetchone()
            return (row[0] or '') if row else ''
        finally:
            conn.close()
    except Exception as e:
        logger.warning(f"查客户案号失败 {project}: {e}")
        return ''


# IPEasy 案件状态中文名属于这几种 → 视为已结案（无需转 OA）
CLOSED_CASE_STATUSES = {"终止", "维持", "结案"}


def get_case_status(case_volume):
    """从 IPEasy 查询案件状态中文名：
    p_case_info JOIN i_case_status ON case_status_id，按 case_volume(案号) 过滤。
    查不到返回空串。"""
    import pymssql
    conn = pymssql.connect(MSSQL_HOST, MSSQL_USER, MSSQL_PWD, MSSQL_DB, charset='utf8')
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT s.case_status_zh_cn "
            "FROM p_case_info p "
            "JOIN i_case_status s ON p.case_status_id = s.case_status_id "
            "WHERE p.case_volume = %s",
            (case_volume,),
        )
        row = cur.fetchone()
        return (row[0] or "") if row else ""
    finally:
        conn.close()


def is_case_closed(case_volume):
    """案件是否已结案（IPEasy 状态中文名 ∈ {终止, 维持, 结案}）。
    查不到 / 连接异常 → 按未结案(False)处理（对齐 OP02：状态查不到按未结案继续）。"""
    try:
        return get_case_status(case_volume).strip() in CLOSED_CASE_STATUSES
    except Exception as e:
        logger.warning(f"[结案查询] {case_volume} 查询失败，按未结案处理: {e}")
        return False


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


# 同族里出现这些立项名关键词，即视为该族已有 OA 类立项 → 当前案为「非同族首案」
FAMILY_OA_KEYWORDS = (
    "OA",
    "审查意见",
    "Requirement for Restriction",
    "Partial Supplementary European Search Report",
)


def family_first_case_remark(project, project_name="", execute=None):
    """其他OA 的「同族首案/非同族首案」备注判定。
    查 atw projects 中同族(project 前10位 = 组内号)的所有 (project, project_name)，
    排除当前案自身这行后，只要有任一 project_name 含 FAMILY_OA_KEYWORDS 任一关键词
    （OA / 审查意见 / Requirement for Restriction / Partial Supplementary European Search Report）
    → '非同族首案'，否则 → '同族首案'。
    （当前案的 OA 立项此时尚未写入 projects；防御性排除自身行以防调用次序变化。）
    查不到/异常 → 返回 ''（留空，人工补）。execute 可注入（测试用，返回 dict 行）。"""
    prefix = (project or "")[:10]
    if not prefix:
        return ""
    try:
        if execute is not None:
            rows = execute(f"SELECT project, project_name FROM projects WHERE project LIKE '{prefix}%'")
            recs = [(r.get("project", ""), r.get("project_name", "") or "") for r in rows]
        else:
            conn = get_mysql_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT project, project_name FROM projects WHERE project LIKE %s", (f"{prefix}%",))
                recs = [(row[0], row[1] or "") for row in cur.fetchall()]
            finally:
                conn.close()
        for pj, name in recs:
            if pj == project and name == project_name:
                continue  # 排除当前案自身这行
            if any(k in name for k in FAMILY_OA_KEYWORDS):
                return "非同族首案"
        return "同族首案"
    except Exception as e:
        logger.warning(f"同族首案判定失败 {project}: {e}")
        return ""


# 公布/公告文件根目录；下列客户的案件目录直接在根下，其余客户在「其他客户」子目录下。
# 客户名部分统一用 {客户码}-* 通配匹配（名称不写死）。
PUBLICATION_BASE_DIR = "Z:\\"
PUBLICATION_TOPLEVEL_CUSTOMERS = {"20608", "20615", "20618", "20633", "20735", "20849"}


def find_publication_file(project, region="", shortname="", base_dir=None):
    """按案号定位公布/公告文件 PDF：
      列出客户： {base}\\{码}-{客户简称}\\{组内号}\\{案号}\\*官方文件*\\
      其他客户： {base}\\其他客户\\{码}-{客户简称}\\{组内号}\\{案号}\\*官方文件*\\
    客户目录名 = 案号前5位 + '-' + atw customer.customer_shortname（由调用方查好传入 shortname）；
    shortname 为空（查不到简称）直接返回 None，不猜路径。列出客户在根下，其余在「其他客户」子目录下。
    官方文件目录名不固定（2.官方文件 / 2官方文件 / 官方文件），只要含「官方文件」即可。
    文件名关键词：US/EP=publication（大小写不限），CN=公告文件。
    找不到简称/文件不存在/异常均返回 None；多份取字典序第一。"""
    import glob
    if not project or len(project) < 10 or not shortname:
        return None
    base = base_dir or PUBLICATION_BASE_DIR
    code, zu = project[:5], project[:10]
    cust_dir = f"{code}-{shortname}"
    if code in PUBLICATION_TOPLEVEL_CUSTOMERS:
        cust_glob = os.path.join(base, cust_dir)
    else:
        cust_glob = os.path.join(base, "其他客户", cust_dir)
    keyword = "公告文件" if region == "CN" else "publication"
    try:
        pattern = os.path.join(cust_glob, zu, project, "*官方文件*", "*")
        hits = [f for f in sorted(glob.glob(pattern))
                if keyword.lower() in os.path.basename(f).lower()
                and f.lower().endswith(".pdf")]
        if len(hits) > 1:
            logger.warning(f"公布文件多份 {project}，取第一份: {[os.path.basename(h) for h in hits]}")
        return hits[0] if hits else None
    except Exception as e:
        logger.warning(f"查公布文件失败 {project}: {e}")
        return None


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

    def get_page_by_id(self, page_id):
        """按 pageId 获取页面（storage 格式），返回 {id, title, version, body, space_key} 或 None。"""
        url = f"{WIKI_BASE}/rest/api/content/{page_id}"
        try:
            resp = requests.get(url, params={'expand': 'body.storage,version,space'},
                                auth=self.auth, headers=self.headers, timeout=15)
            resp.raise_for_status()
            page = resp.json()
            return {
                "id": page['id'],
                "title": page['title'],
                "version": page['version']['number'],
                "body": page['body']['storage']['value'],
                "space_key": page['space']['key'],
            }
        except requests.RequestException as e:
            logger.error(f"Wiki 按ID获取页面失败 [{page_id}]: {e}")
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

# 跟进人轮转分配名单（当前未启用：append_oa_to_wiki 不分配、跟进人留空）。
# 如需恢复轮转，在 append_oa_to_wiki 里按此列表给 _build_table_row 传 followup。
FOLLOWUP_ROTATION = ["苏雅", "苏雅", "姚涓涓"]


def _build_table_row(item, followup=""):
    """根据筛选结果构建一行 HTML。列序对应页面表头（12 列）：
    案号/备注/OA收到日/OA发文日/答复期限/OA类别/跟进人/其它备注事项/人员分配/分配人/分配时间/是否正式立项。
    分配人/分配时间在提交分配时回写（write_oa_assignment），立项时留空。"""
    project = item.get("project", "")
    oa_remark = item.get("oa_remark", "")
    entrust_date = item.get("entrust_date", "")
    oa_doc_date = item.get("oa_doc_date", "")
    project_deadline = item.get("project_deadline", "")
    project_name = item.get("project_name", "")
    oa_id = item.get("oa_id", "")          # 立项唯一 id(=projects.row_id)，供 OA 分配按 id 回写人员分配
    # 埋进 class(Confluence 会清洗 data-* 属性；class 比 data-* 易保留，若也被清则改按可见内容定位)
    tr_open = f'<tr class="oaid-{oa_id}">' if oa_id else "<tr>"

    return (
        tr_open
        + f"<td>{project}</td>"            # 案号
        f"<td>{oa_remark}</td>"            # 备注
        f"<td>{entrust_date}</td>"         # OA收到日
        f"<td>{oa_doc_date}</td>"          # OA发文日
        f"<td>{project_deadline}</td>"     # 答复期限
        f"<td>{project_name}</td>"         # OA类别
        f"<td>{followup}</td>"             # 跟进人
        f"<td></td>"                       # 其它备注事项
        f"<td></td>"                       # 人员分配
        f"<td></td>"                       # 分配人（提交分配时回写）
        f"<td></td>"                       # 分配时间（提交分配时回写）
        f"<td></td>"                       # 是否正式立项
        f"</tr>"
    )


# 新建月份折叠块用的表格骨架（列宽/表头对齐现有页面的 12 列，含 分配人/分配时间）
_OA_LIST_COLGROUP = (
    '<colgroup><col style="width: 134.0px;" /><col style="width: 123.0px;" />'
    '<col style="width: 95.0px;" /><col style="width: 95.0px;" />'
    '<col style="width: 111.0px;" /><col style="width: 248.0px;" />'
    '<col style="width: 84.0px;" /><col style="width: 127.0px;" />'
    '<col style="width: 373.0px;" /><col style="width: 99.0px;" />'
    '<col style="width: 101.0px;" /><col style="width: 246.0px;" /></colgroup>'
)
_OA_LIST_HEADER_ROW = (
    '<tr><th>案号</th><th>备注</th><th>OA收到日</th><th>OA发文日</th><th>答复期限</th>'
    '<th>OA类别</th><th>跟进人</th><th>其它备注事项</th><th>人员分配</th>'
    '<th>分配人</th><th>分配时间</th><th>是否正式立项</th></tr>'
)


def _month_title(dt):
    """写入时间 → 折叠块标题，如 2026年7月（月份不补零，对齐现有页面）。"""
    return f"{dt.year}年{dt.month}月"


def _new_month_block(month_title, rows_html, colgroup=_OA_LIST_COLGROUP, header_row=_OA_LIST_HEADER_ROW):
    """构造一个新的月份折叠块（expand 宏 + 表头 + 数据行）。colgroup/header_row 可换页面。"""
    return (
        '<ac:structured-macro ac:name="expand" ac:schema-version="1">'
        f'<ac:parameter ac:name="title">{month_title}</ac:parameter>'
        '<ac:rich-text-body>'
        f'<table class="fixed-table wrapped">{colgroup}<tbody>'
        f'{header_row}{rows_html}</tbody></table>'
        '</ac:rich-text-body></ac:structured-macro>'
    )


def _insert_rows_by_month(body, rows_html, month_title,
                          colgroup=_OA_LIST_COLGROUP, header_row=_OA_LIST_HEADER_ROW):
    """把 rows_html 插入 month_title 对应折叠块表格的顶部（表头行之后）。
    该月折叠块不存在时，新建并插到所有折叠块最前面。colgroup/header_row 可换页面。
    返回 (new_body, created)。"""
    title_tag = f'<ac:parameter ac:name="title">{month_title}</ac:parameter>'
    idx = body.find(title_tag)
    if idx != -1:
        # 该 title 之后第一个 <tbody...> → 其后第一个 </tr>（表头行结束）→ 插到其后（表格顶部）
        tb = body.find('<tbody', idx)
        if tb != -1:
            tb_gt = body.find('>', tb)
            hdr_end = body.find('</tr>', tb_gt)
            if hdr_end != -1:
                pos = hdr_end + len('</tr>')
                return body[:pos] + rows_html + body[pos:], False
        # 结构异常兜底：插到全页第一个 </tbody> 前
        return body.replace('</tbody>', rows_html + '</tbody>', 1), False
    # 该月折叠块不存在 → 新建，插到第一个 expand 宏之前（置顶）
    block = _new_month_block(month_title, rows_html, colgroup, header_row)
    m = re.search(r'<ac:structured-macro ac:name="expand"', body)
    if m:
        return body[:m.start()] + block + body[m.start():], True
    return body + block, True


# ── 分配人专属历史页（如 薛虹/延总：193786632）：分配提交时追加一行 ──
# 表列：案号/类型/答复期限/OA信息表/人员分配/分配人·分配时间/是否立项/备注（8列）
_ASSIGNEE_HISTORY_PAGES = {
    "薛虹": "193786632",
}
_ASSIGNEE_HIST_COLGROUP = (
    '<colgroup><col style="width: 167.0px;" /><col style="width: 111.0px;" />'
    '<col style="width: 128.0px;" /><col style="width: 162.0px;" />'
    '<col style="width: 340.0px;" /><col style="width: 157.0px;" />'
    '<col style="width: 148.0px;" /><col style="width: 295.0px;" /></colgroup>'
)
_ASSIGNEE_HIST_HEADER_ROW = (
    '<tr><th>案号</th><th>类型</th><th>答复期限</th><th>OA信息表</th>'
    '<th>人员分配</th><th>分配人/分配时间</th><th>是否立项</th><th>备注</th></tr>'
)


def _oa_type_short(oa_type):
    """OA类别 → 历史页「类型」短名：
    OA{数字}-… → OA{数字}；第[一二三…]次审查意见 → {数字}通；审查意见(无次) → 一通；其余原样。"""
    s = oa_type or ""
    m = re.search(r'OA(\d+)', s)
    if m:
        return f"OA{m.group(1)}"
    m = re.search(r'第([一二三四五六七八九十]+)次审查意见', s)
    if m:
        return f"{m.group(1)}通"
    if "审查意见" in s:
        return "一通"
    return s


def _assignee_hist_row(oa_id, project, oa_type, deadline, oa_info_cell,
                       person_text, assign_cell, remark=""):
    """8列行；行上埋 oaid class 供幂等去重。是否立项默认留空、备注=分配附言+自定义方案说明。"""
    tr = f'<tr class="oaid-{oa_id}">' if oa_id else "<tr>"
    return (tr
            + f"<td>{project}</td>"        # 案号
            f"<td>{oa_type}</td>"          # 类型
            f"<td>{deadline}</td>"         # 答复期限
            f"<td>{oa_info_cell}</td>"     # OA信息表
            f"<td>{person_text}</td>"      # 人员分配
            f"<td>{assign_cell}</td>"      # 分配人/分配时间
            f"<td></td>"                   # 是否立项（默认空）
            f"<td>{remark}</td>"           # 备注（分配附言 + 自定义方案说明）
            "</tr>")


def _assignee_hist_row_html(assign_person, oa_id, project, oa_type, deadline,
                            person_text, assign_time, remark=""):
    """构建一行分配人历史页行（OA信息表超链 + 类型短名 + 「薛虹/2026/8/25」分配人时间 + 备注）。"""
    record_url = oa_record_url(project)
    oa_info_cell = (f'<a href="{record_url}">{project}-OA信息记录表</a>'
                    if record_url else "")
    # 分配人/分配时间 → 「薛虹/2026/8/25」（斜杠、年/月/日不补零、不带时分）
    _date = ""
    if assign_time:
        _p = assign_time.split()[0].split("-")   # "2026-08-25 14:30" → ["2026","08","25"]
        _date = f"{_p[0]}/{int(_p[1])}/{int(_p[2])}" if len(_p) == 3 else assign_time.split()[0]
    assign_cell = f"{assign_person}/{_date}" if _date else assign_person
    return _assignee_hist_row(oa_id, project, _oa_type_short(oa_type), deadline, oa_info_cell,
                              person_text, assign_cell, remark)


def write_assignee_history(assign_person, oa_id, project, oa_type, deadline,
                           person_text, assign_time, remark=""):
    """把某分配人(如薛虹)分配的案子追加到其专属历史页(当月折叠块)。
    remark=分配附言+自定义方案说明。仅当该分配人配了页面才写；同 oaid 已在页上则跳过(幂等)。返回 {code,msg}。"""
    page_id = _ASSIGNEE_HISTORY_PAGES.get(assign_person)
    if not page_id:
        return {"code": 0, "msg": "该分配人无专属历史页，跳过"}
    try:
        wiki = WikiClient()
        page = wiki.get_page_by_id(page_id)
        if not page:
            return {"code": 1, "msg": f"历史页不存在: {page_id}"}
        if oa_id and f"oaid-{oa_id}" in page["body"]:
            return {"code": 0, "msg": "已写过，跳过"}
        row = _assignee_hist_row_html(assign_person, oa_id, project, oa_type, deadline,
                                      person_text, assign_time, remark)
        from datetime import datetime
        month_title = f"{datetime.now():%Y-%m}"   # 该页月份标题格式 2026-08
        new_body, _ = _insert_rows_by_month(page["body"], row, month_title,
                                            _ASSIGNEE_HIST_COLGROUP, _ASSIGNEE_HIST_HEADER_ROW)
        code = wiki.update_page(page["id"], page["title"], new_body, page["version"])
        return {"code": 0 if code == 200 else 1, "msg": f"HTTP {code}"}
    except Exception as e:
        logger.warning(f"写分配人历史页失败 {assign_person}/{project}: {e}")
        return {"code": 1, "msg": str(e)}


def _write_assignee_history_page_batch(person, rows):
    """把某分配人本批的多行一次性写入其历史页：一次取页 → 跳过已在页上的 oaid → 合并插当月块 → 一次存页。
    rows: [(oa_id, row_html)]。"""
    page_id = _ASSIGNEE_HISTORY_PAGES.get(person)
    if not page_id or not rows:
        return
    wiki = WikiClient()
    page = wiki.get_page_by_id(page_id)
    if not page:
        return
    body = page["body"]
    fresh = [html for (oa_id, html) in rows if not (oa_id and f"oaid-{oa_id}" in body)]
    if not fresh:
        return
    from datetime import datetime
    month_title = f"{datetime.now():%Y-%m}"
    new_body, _ = _insert_rows_by_month(body, "".join(fresh), month_title,
                                        _ASSIGNEE_HIST_COLGROUP, _ASSIGNEE_HIST_HEADER_ROW)
    wiki.update_page(page["id"], page["title"], new_body, page["version"])


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

    # 构建新行（跟进人当前不分配，留空；如需恢复轮转，用 FOLLOWUP_ROTATION 给 _build_table_row 传 followup）
    new_rows = ""
    for item in results:
        if not item.get("project"):
            continue
        new_rows += _build_table_row(item) + "\n"

    if not new_rows:
        return {"code": 0, "msg": "无有效数据写入", "count": 0}

    # 按写入时间的月份，插到对应折叠块表格顶部（表头之后）；该月不存在则新建并置顶
    from datetime import datetime
    month_title = _month_title(datetime.now())
    body, created = _insert_rows_by_month(body, new_rows, month_title)
    if created:
        logger.info(f"新增月份折叠块: {month_title}")

    # 更新页面
    status = wiki.update_page(page["id"], OA_LIST_PAGE_TITLE, body, page["version"])
    if status == 200:
        count = len([r for r in results if r.get("project")])
        logger.info(f"新增 OA 页面写入成功: {count} 条")
        return {"code": 0, "msg": f"写入成功 {count} 条", "count": count}
    else:
        return {"code": 1, "msg": f"页面更新失败 (HTTP {status})", "count": 0}


# ============================================================
# OA 分配：按 oa_id 回写「测试页面-写入新增OA」人员分配格
# ============================================================
def format_oa_person(responder, qc):
    """人员分配格文案：一行『负责人：X；QC：Y』（缺哪个省哪个）。"""
    parts = []
    if (responder or "").strip():
        parts.append(f"负责人：{responder.strip()}")
    if (qc or "").strip():
        parts.append(f"QC：{qc.strip()}")
    return "；".join(parts)


def _join_remark(*parts):
    """拼「备注」：分配附言 + 说明，去空 + 去重（附言与说明同为默认「按照此前的人员安排」时不重复）。"""
    out = []
    for p in parts:
        p = (p or "").strip()
        if p and p not in out:
            out.append(p)
    return "；".join(out)


def _append_person_inner(inner, person_text):
    """人员分配格：在原内容后追加一行（不覆盖）。原为空则直接写；新文案已存在则不重复。"""
    cur = (inner or "").strip()
    # 空格子（含仅 <br/> / 空段落）→ 直接写
    if not cur or re.fullmatch(r'(?:<br\s*/?>|<p>\s*(?:<br\s*/?>)?\s*</p>|\s)*', cur, re.IGNORECASE):
        return person_text
    if person_text in inner:            # 已有相同文案，不重复追加
        return inner
    return inner.rstrip() + "<br/>" + person_text


def _fill_if_empty(inner, value):
    """单元格为空（含仅 <br/>/空段落）才写 value，否则保留原内容。"""
    return value if not _strip_tags(inner) else inner


def _set_oa_person_cell(body, oa_id, person_text, assign_person="", assign_time="", expected_project=""):
    """在 <tr class="oaid-{oa_id}"> 行里回写分配相关单元格（纯字符串处理，便于测试）：
    第9格「人员分配」(idx8) **追加** person_text（不覆盖）；
    第10格「分配人」(idx9)、第11格「分配时间」(idx10) 空则填（幂等：已有不覆盖）。
    expected_project 非空时**必须**行内第1格案号一致才写（防手动复制导致 class 重复而写错行）。
    返回 (new_body, found)。列不足（旧结构）时按已有列数尽量填。"""
    tr_start, tr_end = _find_oa_row(body, oa_id, expected_project)
    if tr_start == -1:
        return body, False
    row = body[tr_start:tr_end]
    # 用 finditer 按位置替换单元格；不能用 replace——空格 <td></td> 彼此相同会替错
    matches = list(re.finditer(r'<td\b[^>]*>.*?</td>', row, re.DOTALL))
    if len(matches) < 9:
        return body, False
    # 各格的改写函数（idx → inner→new_inner）
    edits = {8: lambda inner: _append_person_inner(inner, person_text)}
    # 分配人(idx9)/分配时间(idx10) 只在整行满 12 列时填，避免误写进老结构(10列)的其它格
    if len(matches) >= 12:
        if assign_person:
            edits[9] = lambda inner: _fill_if_empty(inner, assign_person)
        if assign_time:
            edits[10] = lambda inner: _fill_if_empty(inner, assign_time)
    # 从右到左应用，避免前面替换改变后续 match 的偏移
    new_row = row
    for idx in sorted(edits, reverse=True):
        m = matches[idx]
        fn = edits[idx]
        new_cell = re.sub(r'(<td\b[^>]*>)(.*?)(</td>)',
                          lambda x: x.group(1) + fn(x.group(2)) + x.group(3),
                          m.group(0), count=1, flags=re.DOTALL)
        new_row = new_row[:m.start()] + new_cell + new_row[m.end():]
    return body[:tr_start] + new_row + body[tr_end:], True


def oa_record_url(project):
    """返回 `案号-OA信息记录表` 页的 URL（按 pageId，跨空间可用、免标题编码）。找不到/异常返回 ""。"""
    if not project:
        return ""
    try:
        page = WikiClient().get_page(f"{project}-OA信息记录表")
        if page and page.get("id"):
            return f"{WIKI_BASE}/pages/viewpage.action?pageId={page['id']}"
    except Exception as e:
        logger.warning(f"取OA信息记录表URL失败 {project}: {e}")
    return ""


def _project_of_oa_id(oa_id):
    """查 projects 里 oa_id(=id) 对应的权威案号，供回写时比对。查不到/异常返回 ""。"""
    if not oa_id:
        return ""
    try:
        from db_query import execute
        _safe = str(oa_id).replace("'", "''")
        rows = execute(f"SELECT project FROM projects WHERE id='{_safe}'")
        if rows and not isinstance(rows, str):
            return (rows[0].get("project") or "").strip()
    except Exception as e:
        logger.warning(f"查案号失败 oa_id={oa_id}: {e}")
    return ""


def _find_oa_row(body, oa_id, expected_project=""):
    """定位 <tr class="oaid-{oa_id}"> 行，返回 (tr_start, tr_end) 或 (-1, -1)。
    给了 expected_project 时**必须**第1格案号一致才认（防手动复制导致 class 被复制到别案号行而写错行）；
    有 oaid 行但没一行案号对得上 → (-1,-1)（宁可不写也不写错）。未给期望案号 → 取第一处 oaid 行。"""
    marker = f'oaid-{oa_id}'
    exp = (expected_project or "").strip()
    pos, fallback = 0, (-1, -1)
    while True:
        a = body.find(marker, pos)
        if a == -1:
            break
        tr_start = body.rfind("<tr", 0, a)
        tr_end = body.find("</tr>", a)
        if tr_start == -1 or tr_end == -1:
            pos = a + len(marker)
            continue
        tr_end += len("</tr>")
        if not exp:
            return tr_start, tr_end
        m = re.search(r'<td\b[^>]*>(.*?)</td>', body[tr_start:tr_end], re.DOTALL)
        if m and _strip_tags(m.group(1)) == exp:
            return tr_start, tr_end
        if fallback == (-1, -1):
            fallback = (tr_start, tr_end)
        pos = tr_end
    return (-1, -1) if exp else fallback


def _oa_row_project_type(body, oa_id, expected_project=""):
    """从 oaid（+可选案号比对）行取 (案号=col0, OA类别=col5, 答复期限=col4)。取不到返回空串。"""
    tr_start, tr_end = _find_oa_row(body, oa_id, expected_project)
    if tr_start == -1:
        return "", "", ""
    cells = re.findall(r'<td\b[^>]*>(.*?)</td>', body[tr_start:tr_end], re.DOTALL)
    proj = _strip_tags(cells[0]) if cells else ""
    otype = _strip_tags(cells[5]) if len(cells) > 5 else ""
    deadline = _strip_tags(cells[4]) if len(cells) > 4 else ""
    return proj, otype, deadline


def write_oa_assignment(oa_id, responder, qc, project="", postscript="", custom_note=""):
    """按 oa_id **且案号一致** 找「测试页面-写入新增OA」里的行，回写：
    人员分配（追加）+ 分配人（=收到分配链接的人，按案号路由）+ 分配时间（当前时间，空则填）。
    期望案号取自入参 project，否则查 projects（防手动复制导致 class 重复而写错行）。
    返回 {code, msg}。找不到行/异常不抛。"""
    if not oa_id:
        return {"code": 1, "msg": "缺 oa_id"}
    text = format_oa_person(responder, qc)
    if not text:
        return {"code": 1, "msg": "负责人/QC 均为空，不写入"}
    try:
        wiki = WikiClient()
        page = wiki.get_page(OA_LIST_PAGE_TITLE)
        if not page:
            return {"code": 1, "msg": f"未找到页面: {OA_LIST_PAGE_TITLE}"}
        body = page["body"]
        # 期望案号：优先入参，否则查 projects（oa_id=projects.id 的权威案号）→ 回写时按案号比对
        expected = (project or "").strip() or _project_of_oa_id(oa_id)
        # 分配人：从命中行取 案号(col0)+OA类别(col5)+答复期限(col4) → 补正类看类型给杨姣、否则按案号路由取姓名
        row_proj, oa_type, deadline = _oa_row_project_type(body, oa_id, expected)
        proj = expected or row_proj
        assign_person = ""
        try:
            from forward_oa import assign_person_name
            assign_person = assign_person_name(proj, oa_type)
        except Exception as e:
            logger.warning(f"分配人解析失败 oa_id={oa_id}: {e}")
        from datetime import datetime
        assign_time = f"{datetime.now():%Y-%m-%d %H:%M}"
        new_body, found = _set_oa_person_cell(body, oa_id, text, assign_person, assign_time,
                                              expected_project=expected)
        if not found:
            return {"code": 1, "msg": f"未找到 oaid={oa_id} 且案号={expected or '?'} 的行（可能 class 被复制到别案号行）"}
        body = new_body
        status = wiki.update_page(page["id"], OA_LIST_PAGE_TITLE, body, page["version"])
        if status != 200:
            return {"code": 1, "msg": f"页面更新失败 HTTP {status}"}
        logger.info(f"人员分配写入成功 oa_id={oa_id}: {text}")
        # 分配人若配了专属历史页（如薛虹→193786632），额外追加一行（幂等，失败不影响主结果）
        remark = _join_remark(postscript, custom_note)
        hist = write_assignee_history(assign_person, oa_id, proj, oa_type, deadline, text,
                                      assign_time, remark)
        if hist.get("code") == 0 and "跳过" not in hist.get("msg", ""):
            logger.info(f"分配人历史页写入 {assign_person} {proj}: {hist.get('msg')}")
        return {"code": 0, "msg": f"写入成功: {text}", "history": hist.get("msg", "")}
    except Exception as e:
        logger.warning(f"人员分配写入失败 oa_id={oa_id}: {e}")
        return {"code": 1, "msg": f"异常: {e}"}


def write_oa_assignments_batch(items):
    """**批量**回写「测试页面-写入新增OA」：一次 get_page → 内存里逐案改行 → 一次 update_page；
    分配人有专属历史页(如薛虹)的，按页合并成一次取一次存。相比逐案回写，把 N 取 N 存降到 ~2 取 2 存。
    items: [{oa_id, responder, qc, project?, postscript?, custom_note?}]（project 建议传案号，用于案号双重比对）。
    返回 {oa_id: {code, msg}}。"""
    results = {}
    items = [it for it in (items or []) if (it or {}).get("oa_id")]
    if not items:
        return results
    from datetime import datetime
    now = f"{datetime.now():%Y-%m-%d %H:%M}"
    hist_by_person = {}   # 分配人 -> [(oa_id, row_html)]
    try:
        wiki = WikiClient()
        page = wiki.get_page(OA_LIST_PAGE_TITLE)
        if not page:
            return {it["oa_id"]: {"code": 1, "msg": f"未找到页面: {OA_LIST_PAGE_TITLE}"} for it in items}
        body = page["body"]
        for it in items:
            oa_id = (it.get("oa_id") or "").strip()
            text = format_oa_person(it.get("responder", ""), it.get("qc", ""))
            if not text:
                results[oa_id] = {"code": 1, "msg": "负责人/QC 均为空，不写入"}
                continue
            expected = (it.get("project") or "").strip() or _project_of_oa_id(oa_id)
            row_proj, oa_type, deadline = _oa_row_project_type(body, oa_id, expected)
            proj = expected or row_proj
            try:
                from forward_oa import assign_person_name
                assign_person = assign_person_name(proj, oa_type)
            except Exception:
                assign_person = ""
            new_body, found = _set_oa_person_cell(body, oa_id, text, assign_person, now,
                                                  expected_project=expected)
            if not found:
                results[oa_id] = {"code": 1, "msg": f"未找到 oaid={oa_id} 且案号={expected or '?'} 的行"}
                continue
            body = new_body
            results[oa_id] = {"code": 0, "msg": f"写入成功: {text}"}
            if assign_person in _ASSIGNEE_HISTORY_PAGES:
                remark = _join_remark(it.get("postscript"), it.get("custom_note"))
                row_html = _assignee_hist_row_html(assign_person, oa_id, proj, oa_type, deadline,
                                                   text, now, remark)
                hist_by_person.setdefault(assign_person, []).append((oa_id, row_html))
        # 一次性更新新增OA页
        code = wiki.update_page(page["id"], OA_LIST_PAGE_TITLE, body, page["version"])
        if code != 200:
            for k, v in results.items():
                if v.get("code") == 0:
                    results[k] = {"code": 1, "msg": f"页面更新失败 HTTP {code}"}
            return results
        logger.info(f"[批量]新增OA页回写 {sum(1 for v in results.values() if v.get('code')==0)} 条")
    except Exception as e:
        logger.warning(f"[批量]新增OA页回写失败: {e}")
        for it in items:
            results.setdefault(it["oa_id"], {"code": 1, "msg": f"异常: {e}"})
        return results
    # 专属历史页：每人一页，一次取一次存（失败不影响主结果）
    for person, rows in hist_by_person.items():
        try:
            _write_assignee_history_page_batch(person, rows)
        except Exception as e:
            logger.warning(f"[批量]写历史页失败 {person}: {e}")
    return results


# ============================================================
# 邮件动作记录页（按日折叠，每案一行，不漏每封邮件）
# ============================================================
EMAIL_ACTION_PAGE_TITLE = "邮件动作"
_EMAIL_ACTION_COLGROUP = (
    '<colgroup><col style="width: 150.0px;" /><col style="width: 300.0px;" />'
    '<col style="width: 130.0px;" /><col style="width: 140.0px;" />'
    '<col style="width: 220.0px;" /><col style="width: 80.0px;" /></colgroup>'
)
_EMAIL_ACTION_HEADER_ROW = (
    '<tr><th>案号</th><th>邮件主题</th><th>收件时间</th><th>动作</th>'
    '<th>判断依据</th><th>是否移动</th></tr>'
)


def _day_title(dt):
    """写入时间 → 日折叠块标题，如 2026年8月5日（不补零）。"""
    return f"{dt.year}年{dt.month}月{dt.day}日"


def _new_day_block(day_title, rows_html):
    """构造一个新的按日折叠块（expand 宏 + 表头 + 数据行）。"""
    return (
        '<ac:structured-macro ac:name="expand" ac:schema-version="1">'
        f'<ac:parameter ac:name="title">{day_title}</ac:parameter>'
        '<ac:rich-text-body>'
        f'<table class="fixed-table wrapped">{_EMAIL_ACTION_COLGROUP}<tbody>'
        f'{_EMAIL_ACTION_HEADER_ROW}{rows_html}</tbody></table>'
        '</ac:rich-text-body></ac:structured-macro>'
    )


def _insert_rows_by_day(body, rows_html, day_title):
    """把 rows_html 插入 day_title 对应折叠块表格的顶部（表头行之后）。
    该日折叠块不存在时，新建并插到所有折叠块最前面。返回 (new_body, created)。"""
    title_tag = f'<ac:parameter ac:name="title">{day_title}</ac:parameter>'
    idx = body.find(title_tag)
    if idx != -1:
        tb = body.find('<tbody', idx)
        if tb != -1:
            tb_gt = body.find('>', tb)
            hdr_end = body.find('</tr>', tb_gt)
            if hdr_end != -1:
                pos = hdr_end + len('</tr>')
                return body[:pos] + rows_html + body[pos:], False
        return body.replace('</tbody>', rows_html + '</tbody>', 1), False
    block = _new_day_block(day_title, rows_html)
    m = re.search(r'<ac:structured-macro ac:name="expand"', body)
    if m:
        return body[:m.start()] + block + body[m.start():], True
    return body + block, True


def _esc_html(s):
    """单元格文本转义，避免主题里的 <>& 破坏表格结构。"""
    return (str(s or "")).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _build_email_action_row(rec):
    """一条动作记录 → 一个 <tr>。rec: {project, subject, received_time, action, reason, moved(bool)}。"""
    cells = [
        rec.get("project", "") or "",
        rec.get("subject", "") or "",
        rec.get("received_time", "") or "",
        rec.get("action", "") or "",
        rec.get("reason", "") or "",
        "是" if rec.get("moved") else "否",
    ]
    return "<tr>" + "".join(f"<td>{_esc_html(c)}</td>" for c in cells) + "</tr>"


def build_email_action_records(all_results, all_emails, oa_actions, report_actions):
    """汇总两个 sink 的动作 → 邮件动作记录（每案一行，不漏每封邮件）。纯函数，便于测试。
    all_results: 分类结果(每条一个案，含 message_id/project/email_subject)。
    all_emails: [(acc, email_dict)]，email_dict 含 message_id/subject/date。
    oa_actions/report_actions: [{message_id, project, action, reason}]。
    返回 [{project, subject, received_time, action, reason, moved}]：
      命中邮件 → 每案一行(moved=True，动作/依据按 message_id+project 合并；无则「无动作」)；
      未命中邮件 → 一行(案号空，动作「无动作」，依据「未命中分类」，moved=False)。"""
    act_map = {}
    for a in list(oa_actions or []) + list(report_actions or []):
        key = (a.get("message_id", ""), a.get("project", ""))
        e = act_map.setdefault(key, {"actions": [], "reasons": []})
        act = a.get("action")
        if act and act not in e["actions"]:
            e["actions"].append(act)
        rsn = a.get("reason")
        if rsn and rsn not in e["reasons"]:
            e["reasons"].append(rsn)

    email_meta = {}
    for _acc, em in (all_emails or []):
        mid = em.get("message_id", "")
        if mid and mid not in email_meta:
            email_meta[mid] = (em.get("subject", "") or "", str(em.get("date", "") or ""))

    matched_mids = {it.get("message_id", "") for it in (all_results or []) if it.get("message_id")}

    records = []
    # 命中：每案一行
    for it in (all_results or []):
        mid = it.get("message_id", "")
        proj = it.get("project", "") or ""
        subject, rtime = email_meta.get(mid, (it.get("email_subject", "") or "", ""))
        e = act_map.get((mid, proj))
        action = "；".join(e["actions"]) if (e and e["actions"]) else "无动作"
        reason = "；".join(e["reasons"]) if (e and e["reasons"]) else ""
        records.append({"project": proj, "subject": subject, "received_time": rtime,
                        "action": action, "reason": reason, "moved": True})
    # 未命中：每封一行（去重 message_id）
    seen = set()
    for _acc, em in (all_emails or []):
        mid = em.get("message_id", "")
        if mid in matched_mids or mid in seen:
            continue
        seen.add(mid)
        records.append({"project": "", "subject": em.get("subject", "") or "",
                        "received_time": str(em.get("date", "") or ""),
                        "action": "无动作", "reason": "未命中OA/汇报信分类", "moved": False})
    return records


def append_email_actions_to_wiki(records):
    """把邮件处理动作按日折叠写入「邮件动作」页（每案一行，未命中邮件也记一行）。
    records: [{project, subject, received_time, action, moved}]。返回 {code, msg, count}。"""
    if not records:
        return {"code": 0, "msg": "无动作记录需要写入", "count": 0}
    wiki = WikiClient()
    page = wiki.get_page(EMAIL_ACTION_PAGE_TITLE)
    if not page:
        return {"code": 1, "msg": f"未找到页面: {EMAIL_ACTION_PAGE_TITLE}", "count": 0}
    body = page["body"]
    new_rows = "".join(_build_email_action_row(r) for r in records)

    from datetime import datetime
    day_title = _day_title(datetime.now())
    body, created = _insert_rows_by_day(body, new_rows, day_title)
    if created:
        logger.info(f"新增日折叠块: {day_title}")

    status = wiki.update_page(page["id"], EMAIL_ACTION_PAGE_TITLE, body, page["version"])
    if status == 200:
        logger.info(f"邮件动作页写入成功: {len(records)} 条")
        return {"code": 0, "msg": f"写入成功 {len(records)} 条", "count": len(records)}
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


def _splice_oa_row(body, oa_seq, cells_by_header):
    """在「OA过程」表 OA{oa_seq} 行按列名填多个单元格（纯字符串处理，便于测试）。

    cells_by_header: {列名关键字: 单元格内 HTML/文本}，如
        {"OA收文日": "2026-07-09", "期限": "2026-09-09", "对比文件链接": "<a…>…</a>"}
    只填空单元格（逐列幂等，不覆盖已有内容）。
    OA过程表以「表头含『OA次数』列」判定（完整版/简版都有）。列名按子串匹配：
    完整版「期限」命中「期限」列、简版「期限」命中「答复期限」列；「OA收文日」「对比文件链接」
    简版无对应列则自动落空、只写命中的列。

    Returns:
        (new_body, status)。status ∈
          filled          至少填入一个空单元格
          added_row        无 OA{N} 行，自动补一行并填入
          skip_no_column   页面无「OA次数」表 / 该表无任一待写列
          skip_nonempty    OA{N} 行存在但目标单元格都已有内容，不覆盖
    """
    # 1. 找「OA过程」表：表头含「OA次数」的那张（完整版/简版都有此列；table 不嵌套，非贪婪安全）
    target = None
    header_texts = []
    for m in re.finditer(r'<table\b.*?</table>', body, re.DOTALL):
        ths = re.findall(r'<th\b[^>]*>.*?</th>', m.group(0), re.DOTALL)
        hts = [_strip_tags(th) for th in ths]
        if any('OA次数' in h for h in hts):
            target = m
            header_texts = hts
            break
    if target is None:
        return body, "skip_no_column"
    tbl = target.group(0)
    col_count = len(header_texts)

    # 2. 表头 → 每个待填列名的列序号（子串匹配：简版「期限」命中「答复期限」列，
    #    完整版「期限」命中「期限」列；「OA收文日」「对比文件链接」简版无列自动落空）
    col_of = {}
    for key in cells_by_header:
        idx = next((i for i, h in enumerate(header_texts) if key in h), None)
        if idx is not None:
            col_of[key] = idx
    if not col_of:
        return body, "skip_no_column"   # 该表没有任一待写列

    tb = re.search(r'<tbody\b[^>]*>(.*?)</tbody>', tbl, re.DOTALL)
    if not tb:
        return body, "skip_no_column"
    tbody_inner = tb.group(1)
    want = f'OA{oa_seq}'

    # 3. 找 OA{N} 行，逐列填空单元格
    rows = re.findall(r'<tr\b[^>]*>.*?</tr>', tbody_inner, re.DOTALL)
    for row in rows:
        cells = _split_cells(row)
        if not cells or _strip_tags(cells[0]) != want:
            continue
        new_cells = cells[:]
        changed = False
        for key, idx in col_of.items():
            val = cells_by_header.get(key)
            if not val or idx >= len(new_cells):
                continue
            if _strip_tags(new_cells[idx]):
                continue  # 已有内容不覆盖
            new_cells[idx] = f'<td>{val}</td>'
            changed = True
        if not changed:
            return body, "skip_nonempty"
        tr_open = re.match(r'<tr\b[^>]*>', row).group(0)
        new_row = tr_open + ''.join(new_cells) + '</tr>'
        new_tbody = tbody_inner.replace(row, new_row, 1)
        new_tbl = tbl.replace(tbody_inner, new_tbody, 1)
        return body[:target.start()] + new_tbl + body[target.end():], "filled"

    # 4. 无 OA{N} 行 → 自动补一行（首列 OA{N}，待填列各就位，其余留空）
    idx_to_key = {idx: key for key, idx in col_of.items()}
    cells = []
    for i in range(col_count):
        if i == 0:
            cells.append(f'<td>{want}</td>')
        elif i in idx_to_key and cells_by_header.get(idx_to_key[i]):
            cells.append(f'<td>{cells_by_header[idx_to_key[i]]}</td>')
        else:
            cells.append('<td></td>')
    add_row = '<tr>' + ''.join(cells) + '</tr>'
    new_tbody = tbody_inner + add_row
    new_tbl = tbl.replace(tbody_inner, new_tbody, 1)
    return body[:target.start()] + new_tbl + body[target.end():], "added_row"


def _splice_ref_docs_into_body(body, oa_seq, cell_html):
    """向后兼容包装：只填「对比文件链接」列。"""
    return _splice_oa_row(body, oa_seq, {"对比文件链接": cell_html})


def fill_ref_docs_in_oa_row(page_title, oa_seq, ref_docs,
                            oa_doc_date="", project_deadline="", dry_run=False):
    """把对比文件 + OA收文日 + 期限写到 `案号-OA信息记录表` 页「OA过程」表 OA{oa_seq} 行。

    列映射：对比文件链接 ← ref_docs（Google Patent 链接）、OA收文日 ← oa_doc_date（官文发文日）、
    期限 ← project_deadline。仅完整版模板有这些列；简版 skip_no_column。逐列幂等：已有内容不覆盖。
    Returns: dict {status, http?}
    """
    if not oa_seq:
        logger.warning(f"[OA过程] {page_title} 无法确定 OA 次数，跳过")
        return {"status": "no_oa_seq"}

    # 对比文件链接为可选：ref_docs 为空时仍写 OA收文日/期限（都直接来自 item 字段，
    # 与「新增OA列表」同源，不依赖官文 PDF 解析）。三列都无内容才跳过。
    cells_by_header = {}
    cell_html = _ref_docs_cell_html(ref_docs) if ref_docs else ""
    if cell_html:
        cells_by_header["对比文件链接"] = cell_html
    if oa_doc_date:
        cells_by_header["OA收文日"] = oa_doc_date
    if project_deadline:
        cells_by_header["期限"] = project_deadline
    if not cells_by_header:
        return {"status": "nothing_to_write"}

    wiki = WikiClient()
    page = wiki.get_page(page_title)
    if not page:
        logger.warning(f"[OA过程] 未找到页面: {page_title}")
        return {"status": "page_not_found"}

    new_body, status = _splice_oa_row(page["body"], oa_seq, cells_by_header)
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
