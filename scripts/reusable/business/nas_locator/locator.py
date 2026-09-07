"""NAS 申请文件定位（业务支撑层）。

抽自 oa/oa_report_ai.py 的 _resolve_app_dir / find_application_files，逻辑不变。
按案号 + 地区在 NAS（Z 盘）目录树里定位「递交文件」目录、取其中的说明书 docx。

可复用做法：NAS 路径规则（根目录、列出客户、地区关键词）作 config 传入；
"客户码→客户简称"这类查库动作注入为 shortname_lookup（调用方用 db.mysql_query 实现），
故本组件不直接依赖数据库。选文件复用 doc_utils.pick_latest_docx。
"""
import glob
import os
import sys

# 让本组件能找到 foundation 的 doc_utils
_LIB = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
_p = os.path.join(_LIB, "foundation")
if _p not in sys.path:
    sys.path.insert(0, _p)
from doc_utils import pick_latest_docx  # noqa: E402

# NAS 路径规则默认值（生产 Z 盘；换环境时传 config 覆盖）
DEFAULT_NAS_CONFIG = {
    "nas_base": "Z:\\",                       # 普通案号根：{码}-{简称}\{组内号}\{案号}\*递交文件*\
    "zhuohui_dir": "Z:\\众慧优创知识产权",     # 含 -H 案号：\{名字含码的目录}\{案号}\*递交文件*\
    "toplevel_customers": {"20608", "20615", "20618", "20633", "20735", "20849"},  # 列在根，其余在"其他客户"下
    "keywords": {"US": ["spec"], "CN": ["说明书", "申请文件"], "EP": None},  # 各地区挑说明书的文件名关键词
}


def resolve_app_dir(project, region, config=None, shortname_lookup=None):
    """定位案号对应的「递交文件」目录，找不到返回 None。

    输入：
      project          案号（≥10 位）
      region           US/CN/EP（EP 会再进一层 *新申请*）
      config           NAS 路径规则 dict（可选，默认 DEFAULT_NAS_CONFIG）
      shortname_lookup callable(code)->客户简称（普通案号必需；含 -H 案号不需要）
    输出：目录路径 str 或 None。
    """
    cfg = config or DEFAULT_NAS_CONFIG
    if not project or len(project) < 10:
        return None
    if "-H" in project:
        for parent in sorted(glob.glob(os.path.join(cfg["zhuohui_dir"], f"*{project[:5]}*"))):
            case_dir = os.path.join(parent, project)
            if os.path.isdir(case_dir):
                submit = sorted(glob.glob(os.path.join(case_dir, "*递交文件*")))
                if submit:
                    return submit[0]
        return None
    code, zu = project[:5], project[:10]
    shortname = shortname_lookup(code) if shortname_lookup else None
    if not shortname:
        return None
    cust_dir = f"{code}-{shortname}"
    root = (os.path.join(cfg["nas_base"], cust_dir) if code in cfg["toplevel_customers"]
            else os.path.join(cfg["nas_base"], "其他客户", cust_dir))
    submit = sorted(glob.glob(os.path.join(root, zu, project, "*递交文件*")))
    if not submit:
        return None
    d = submit[0]
    if region == "EP":
        xin = sorted(glob.glob(os.path.join(d, "*新申请*")))
        return xin[0] if xin else None
    return d


def find_application_file(project, region="", config=None, shortname_lookup=None):
    """定位说明书文件路径（先定位「递交文件」目录，再按地区关键词取最新 docx）。找不到返回 None。

    输入：同 resolve_app_dir。
    输出：说明书 docx 路径 str 或 None（权要可再用 doc_utils.split_spec 从中切出）。
    """
    cfg = config or DEFAULT_NAS_CONFIG
    d = resolve_app_dir(project, region, cfg, shortname_lookup)
    if not d:
        return None
    return pick_latest_docx(d, cfg["keywords"].get(region))
