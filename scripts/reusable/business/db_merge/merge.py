"""跨库合并（业务支撑层）。

范式抽象自 report/enrich_report.py 的 enrich_cn_fields：同一个键（如案号 project）分别查
多个数据源（atw MySQL + 唯德 IPEasy MSSQL），在应用层把结果合并成一个 dict——不跨库 JOIN、
某个源查不到/连不上就跳过、不阻塞。

引擎只管"按键调多源、合并、逐源兜底"；每个源查什么、字段叫什么由调用方写在 fetcher 里。
"""
import sys


def merge_by_key(key, fetchers, skip_empty=True):
    """按同一 key 调多个数据源取 dict 并合并成一个；某源出错不阻塞（记 stderr 跳过）。

    输入：
      key        关联键（如案号 project），传给每个 fetcher
      fetchers   列表，每项为 callable(key)->dict（一个数据源的查询+字段命名）
      skip_empty 可选，默认 True：跳过值为 None/空串的字段（保留调用方原占位）
    输出：合并后的 dict（后面的源同名键会覆盖前面的）。
    """
    out = {}
    for fn in fetchers:
        name = getattr(fn, "__name__", str(fn))
        try:
            data = fn(key) or {}
        except Exception as e:  # noqa: BLE001
            print(f"[db_merge] 源 {name} 查询失败，跳过: {e}", file=sys.stderr)
            continue
        for k, v in data.items():
            if skip_empty and (v is None or v == ""):
                continue
            out[k] = v
    return out
