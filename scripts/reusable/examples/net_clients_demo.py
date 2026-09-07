"""net_clients 用法示例。

号码归一/文档匹配等纯逻辑离线实跑；真实下载需联网(+ USPTO key)，只示范写法。

运行：python3 scripts/reusable/examples/net_clients_demo.py
"""
import os
import sys
import tempfile

_LIB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # scripts/reusable
sys.path.insert(0, os.path.join(_LIB, "foundation"))
from net_clients import USPTOApplication, download_patent_pdf  # noqa: E402
from net_clients.patent_pdf import _digits  # noqa: E402


if __name__ == "__main__":
    print("== patent_pdf 号码归一（离线）==")
    for raw in ["US20250150762A1", "20250150762", "US 2025/0150762 A1", "CN110693604A"]:
        print(f"  {raw!r:24} -> {_digits(raw)}")

    print("\n== USPTOApplication 文档匹配（离线）==")
    with tempfile.TemporaryDirectory() as d:
        app = USPTOApplication(download_dir=d, project="2222", api_key="demo-key")
        bag = [
            {"documentCode": "CTNF", "officialDate": "2025-02-11T00:00:00"},
            {"documentCode": "CTFR", "officialDate": "2025-06-01T00:00:00"},
        ]
        hit = app.filter_documents(bag, "CTNF", "2025-02-11")
        print("  匹配 CTNF@2025-02-11:", [d["documentCode"] for d in hit])   # -> ['CTNF']
        print("  文件名清理:", app.sanitize_filename('Non-Final: A/B?'))       # 非法字符→_

    print("\n== 真实下载（需联网，仅示范写法）==")
    print('''
    # USPTO 官文（api_key 走参数/环境变量 USPTO_API_KEY/email_config.json 的 uspto.api_key）
    app = USPTOApplication(download_dir="out", project="20849-0032US01")
    app.downLoad_Documents_ByAPI("17456882", "CTNF", "2025-02-11", "20849-0032US01", "官文")
    # -> {"20849-0032US01": ["out/20849-0032US01/2025-02-11-...-....pdf"]}；app.last_http_status 可查(403=未公开)

    # FreePatentsOnline 专利 PDF
    download_patent_pdf("US20250150762A1", "out.pdf")   # -> 'out.pdf' 或 None
    ''')
