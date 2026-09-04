"""JSON 点号路径读写（可复用纯函数）。

抽自 report/submission/qa_seed.py 的 get_by_path/set_by_path，逻辑不变。
零依赖，零业务耦合。路径用 '.' 分段，纯数字段按列表下标处理。
"""


def get_by_path(obj, path):
    """按 'a.0.b' 取值；任一段缺失返回 None。

    输入：obj (dict/list 嵌套结构)、path (str，如 "inventors.0.name")
    输出：取到的值 | None（路径任一段不存在/越界/类型不符）
    示例：get_by_path({"inventors": [{"name": "张三"}]}, "inventors.0.name") -> "张三"
    """
    cur = obj
    for part in path.split("."):
        if part.isdigit():
            if not isinstance(cur, list) or int(part) >= len(cur):
                return None
            cur = cur[int(part)]
        else:
            if not isinstance(cur, dict):
                return None
            cur = cur.get(part)
        if cur is None:
            return None
    return cur


def set_by_path(obj, path, val):
    """按 'a.0.b' 写值；中间段须已存在（写前建议先用 get_by_path 确认）。

    输入：obj (dict/list)、path (str)、val (任意)
    输出：无（就地修改 obj）；中间段缺失会抛 KeyError/IndexError
    示例：set_by_path(d, "inventors.0.name", "李四")
    """
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        cur = cur[int(part)] if part.isdigit() else cur[part]
    last = parts[-1]
    if last.isdigit():
        cur[int(last)] = val
    else:
        cur[last] = val
