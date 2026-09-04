"""专利号归一化（可复用纯函数）。

抽自 oa/parse_us_refs.py 的 normalize_pub_no + _COUNTRIES，逻辑不变。
零依赖（仅标准库 re），零业务耦合。
"""
import re

# Google Patents 认的国别/地区前缀
COUNTRIES = ("US", "CN", "JP", "EP", "WO", "KR", "DE", "GB", "FR", "TW",
             "CA", "AU", "IN", "RU", "BR", "ES", "IT", "NL", "SE", "CH")


def normalize_pub_no(raw, default_country="US"):
    """把官文里的对比文件号归一化成 Google Patents 号（去逗号/空格/斜杠/连字符/点）。

    输入：raw (str|None)、default_country (str，无前缀时补的国别，默认 US)
    输出：str（归一化后的号；空输入返回 ""）
    示例：
      normalize_pub_no("US 9,123,456 B2")   -> "US9123456B2"
      normalize_pub_no("US 2015/0123456 A1")-> "US20150123456A1"
      normalize_pub_no("US-2015/0123456-A1")-> "US20150123456A1"
      normalize_pub_no("CN 216192880 U")    -> "CN216192880U"
      normalize_pub_no("2015/0123456 A1")   -> "US20150123456A1"  # 无前缀默认美国
    """
    if not raw:
        return ""
    s = re.sub(r'[\s,/.\-]', '', str(raw).strip().upper())
    if not s:
        return ""
    if s[:2] in COUNTRIES:
        return s
    if s[0].isdigit():
        return default_country + s
    return s
