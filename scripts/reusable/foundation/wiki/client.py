"""Confluence Wiki 读写客户端（基础通用层 · 网络与服务调用）。

抽自 oa/oainfo_cli.py 的 WikiClient，逻辑不变；改动：base_url/账号不再硬编码，改为
参数 > 环境变量（WIKI_BASE_URL/WIKI_USER/WIKI_PASSWORD）> email_config.json 的 wiki 段；
去掉原 headers 里残留的无效 `Authorization: Bearer <access_token>` 占位（实际走 basic auth）。
依赖：requests。
"""
import json
import logging
import os

import requests

logger = logging.getLogger(__name__)

# 本模块在 scripts/reusable/foundation/wiki/ 下，email_config.json 在 scripts/（上溯三级）
_SCRIPTS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))

_HEADERS = {"content-type": "application/json", "Accept": "application/json"}


def _wiki_cfg():
    """读 email_config.json 的 wiki 段；读不到返回 {}。"""
    try:
        with open(os.path.join(_SCRIPTS_DIR, "email_config.json"), encoding="utf-8") as f:
            return json.load(f).get("wiki") or {}
    except Exception:
        return {}


class WikiClient:
    """Confluence REST 客户端：搜页 / 读页 / 建子页 / 更新页 / 传附件。"""

    def __init__(self, base_url=None, user=None, password=None):
        """base_url/user/password 不给则走 环境变量 > email_config.json 的 wiki 段。"""
        cfg = _wiki_cfg()
        self.base = (base_url or os.environ.get("WIKI_BASE_URL")
                     or cfg.get("base_url") or "").rstrip("/")
        self.auth = (user or os.environ.get("WIKI_USER") or cfg.get("user"),
                     password or os.environ.get("WIKI_PASSWORD") or cfg.get("password"))
        self.headers = dict(_HEADERS)

    def search_page(self, title):
        """按标题搜索页面，返回 results 列表（失败返回 []）。"""
        url = f"{self.base}/rest/api/content"
        params = {'title': title, 'start': 0, 'limit': 10,
                  'expand': 'space,history,body.view,metadata.labels'}
        try:
            resp = requests.get(url, params=params, auth=self.auth, headers=self.headers, timeout=15)
            resp.raise_for_status()
            return resp.json().get('results', [])
        except requests.RequestException as e:
            logger.error(f"Wiki 搜索页面失败 [{title}]: {e}")
            return []

    def get_page(self, title):
        """按标题取页面（storage 格式），返回 {id, version, body, space_key} 或 None。"""
        url = f"{self.base}/rest/api/content"
        params = {'title': title, 'start': 0, 'limit': 1, 'expand': 'body.storage,version,space'}
        try:
            resp = requests.get(url, params=params, auth=self.auth, headers=self.headers, timeout=15)
            resp.raise_for_status()
            results = resp.json().get('results', [])
            if results:
                page = results[0]
                return {"id": page['id'], "version": page['version']['number'],
                        "body": page['body']['storage']['value'], "space_key": page['space']['key']}
        except requests.RequestException as e:
            logger.error(f"Wiki 获取页面失败 [{title}]: {e}")
        return None

    def get_page_by_id(self, page_id):
        """按 pageId 取页面，返回 {id, title, version, body, space_key} 或 None。"""
        url = f"{self.base}/rest/api/content/{page_id}"
        try:
            resp = requests.get(url, params={'expand': 'body.storage,version,space'},
                                auth=self.auth, headers=self.headers, timeout=15)
            resp.raise_for_status()
            page = resp.json()
            return {"id": page['id'], "title": page['title'], "version": page['version']['number'],
                    "body": page['body']['storage']['value'], "space_key": page['space']['key']}
        except requests.RequestException as e:
            logger.error(f"Wiki 按ID获取页面失败 [{page_id}]: {e}")
            return None

    def update_page(self, page_id, title, content, version):
        """更新页面内容（version 传当前版本号，内部 +1）。返回 HTTP 状态码。"""
        data = {"type": "page", "title": title, "version": {"number": version + 1},
                "body": {"storage": {"representation": "storage", "value": content}}}
        try:
            resp = requests.put(f"{self.base}/rest/api/content/{page_id}",
                                auth=self.auth, headers=self.headers,
                                data=json.dumps(data), timeout=15)
            if resp.status_code == 200:
                logger.info(f"页面更新成功: {title}")
            else:
                logger.error(f"页面更新失败 [{title}]: HTTP {resp.status_code} - {resp.text[:200]}")
            return resp.status_code
        except requests.RequestException as e:
            logger.error(f"Wiki 更新页面异常 [{title}]: {e}")
            return 500

    def create_child_page(self, title, content, space_key, parent_id):
        """在父页面下创建子页面。返回 HTTP 状态码。"""
        data = {"type": "page", "ancestors": [{"id": str(parent_id)}],
                "space": {"key": str(space_key)}, "title": title,
                "body": {"storage": {"representation": "storage", "value": content}}}
        try:
            resp = requests.post(f"{self.base}/rest/api/content/",
                                 auth=self.auth, headers=self.headers,
                                 data=json.dumps(data), timeout=15)
            if resp.status_code == 200:
                logger.info(f"页面创建成功: {title}")
            else:
                logger.error(f"页面创建失败 [{title}]: HTTP {resp.status_code} - {resp.text[:200]}")
            return resp.status_code
        except requests.RequestException as e:
            logger.error(f"Wiki 创建页面异常 [{title}]: {e}")
            return 500

    def upload_attachment(self, page_id, filepath):
        """上传附件到页面（同名会更新为新版本，不重复）。返回 True/False。

        注意：multipart 上传只带 X-Atlassian-Token 头，不能带 application/json。
        """
        if not page_id:
            logger.error(f"附件上传跳过：page_id 为空 ({filepath})")
            return False
        if not os.path.exists(filepath):
            logger.error(f"附件上传跳过：文件不存在 {filepath}")
            return False
        url = f"{self.base}/rest/api/content/{page_id}/child/attachment"
        try:
            with open(filepath, "rb") as fh:
                resp = requests.post(url, auth=self.auth,
                                     headers={"X-Atlassian-Token": "nocheck"},
                                     files={"file": fh}, timeout=60)
            if resp.status_code in (200, 201):
                logger.info(f"附件上传成功: {os.path.basename(filepath)} → page {page_id}")
                return True
            logger.error(f"附件上传失败 [{os.path.basename(filepath)}]: "
                         f"HTTP {resp.status_code} - {resp.text[:200]}")
            return False
        except requests.RequestException as e:
            logger.error(f"附件上传异常 [{filepath}]: {e}")
            return False
