"""通用 HTML 文本助手（可复用纯函数）。

抽自 oa/oainfo_cli.py 的 _strip_tags/_split_cells，逻辑不变。
零依赖（仅标准库 re），零业务耦合——只做通用的去标签与 <td> 切分，
不含任何 OA/Confluence 业务表格结构逻辑（那些留在 oainfo_cli）。
"""
import re


def strip_tags(s):
    """去 HTML 标签 + 常见转义/空白，用于判断单元格是否为空、比对纯文本。

    输入：s (str|None)
    输出：str（去标签去 &nbsp;/\\xa0 并 strip 后的纯文本；None→""）
    示例：strip_tags("<td>  张三&nbsp;</td>") -> "张三"
    """
    t = re.sub(r'<[^>]+>', '', s or '')
    t = t.replace('&nbsp;', '').replace('\xa0', '')
    return t.strip()


def split_cells(row_html):
    """把一个 <tr>…</tr> 拆成完整的 <td>…</td> 列表（td 不嵌套 td，非贪婪安全）。

    输入：row_html (str，一行的 HTML)
    输出：list[str]（每个元素是完整 <td…>…</td>）
    示例：split_cells("<tr><td>a</td><td>b</td></tr>") -> ["<td>a</td>", "<td>b</td>"]
    """
    return re.findall(r'<td\b[^>]*>.*?</td>', row_html, re.DOTALL)
