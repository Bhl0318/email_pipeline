"""wiki 用法示例。

构造客户端离线可跑（只存地址/账号，不联网）；真实读写需连 Confluence，只示范写法。

运行：python3 scripts/reusable/examples/wiki_demo.py
"""
import os
import sys

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "foundation"))
from wiki import WikiClient  # noqa: E402


if __name__ == "__main__":
    # 构造：不给参数则走 环境变量 / email_config.json 的 wiki 段；这里显式传，离线演示
    wc = WikiClient(base_url="http://10.10.70.90:9090", user="confluence", password="***")
    print("客户端已构造，base =", wc.base)   # 不联网，仅演示配置生效

    print("\n真实读写（需连 Confluence，仅示范写法）：")
    print('''
    wc = WikiClient()                              # 走配置/环境变量

    # 读
    page = wc.get_page("OA信息记录表-20849")        # -> {id, version, body, space_key} 或 None
    page = wc.get_page_by_id("241276196")           # 按 pageId 读
    hits = wc.search_page("OA信息记录表")            # 按标题搜，返回列表

    # 写
    wc.update_page(page["id"], page["title"] if "title" in page else "标题",
                   new_storage_html, page["version"])     # version 传当前号，内部+1
    wc.create_child_page("新子页标题", storage_html, space_key="ZU123", parent_id="123456")
    wc.upload_attachment("241276196", "/path/to/官文.pdf")  # 同名自动更新版本
    ''')
