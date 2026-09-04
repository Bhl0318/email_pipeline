"""日期工具（可复用纯函数）。

抽自 oa/filter_oa_email.py 的 _parse_date/_add_months/_move_to_workday，逻辑不变。
零依赖（仅标准库 datetime），零业务耦合。
"""
from datetime import datetime, timedelta


def parse_date(date_str):
    """解析多种日期格式，返回 datetime 或 None。

    支持：ISO `2026-02-14`（含带时间的前 10 位）、美式 `02/14/2026`、
    EP 英文 `February 12, 2026` / `February 12 2026`。

    输入：date_str (str|None)
    输出：datetime | None（无法解析或空输入时 None）
    示例：parse_date("2026-02-14") -> datetime(2026, 2, 14, 0, 0)
    """
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip()[:10], fmt)
        except ValueError:
            continue
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y")
    except ValueError:
        pass
    try:
        return datetime.strptime(date_str.strip(), "%B %d %Y")
    except ValueError:
        pass
    return None


def add_months(dt, months):
    """日期加 N 个月（跨年进位，落到月末时按当月最大天数取，闰年 2 月算 29）。

    输入：dt (datetime)、months (int，可为负)
    输出：datetime
    示例：add_months(datetime(2026, 1, 31), 1) -> datetime(2026, 2, 28)
    """
    month = dt.month + months
    year = dt.year + (month - 1) // 12
    month = (month - 1) % 12 + 1
    day = min(dt.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return dt.replace(year=year, month=month, day=day)


def move_to_workday(dt):
    """若落在周末，前移到最近的工作日（周五）。

    输入：dt (datetime)
    输出：datetime（周一~周五原样返回，周六→周五，周日→周五）
    示例：move_to_workday(datetime(2026, 2, 14)) -> datetime(2026, 2, 13)  # 周六→周五
    """
    while dt.weekday() >= 5:  # 5=周六, 6=周日
        dt -= timedelta(days=1)
    return dt
