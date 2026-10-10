"""手工参数入口调用正式 OA 前端分析流程的离线测试。"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(__file__))
from qdfx_external_manual import run_case


class ManualSubmitTests(unittest.TestCase):
    @patch("qdfx_external_manual.submit_oa_analysis", return_value={"status": "submitted", "parseId": "p1"})
    def test_hardcoded_inputs_reach_formal_submit(self, submit):
        with tempfile.TemporaryDirectory() as tmp:
            oa, app = Path(tmp) / "oa.md", Path(tmp) / "spec.md"
            oa.write_text("本通知书引用下列对比文件\n1 CN110693604A 2019-11-19", encoding="utf-8")
            app.write_text("申请文件正文", encoding="utf-8")
            result = run_case("20618-0001CN00", str(oa), str(app))
        self.assertEqual(result["status"], "submitted")
        args, kwargs = submit.call_args
        self.assertEqual(args[0], {"project": "20618-0001CN00", "region": "CN"})
        self.assertEqual(args[2], [{"no": "1", "doc_no": "CN110693604A", "pub_date": "2019-11-19"}])
        self.assertEqual(kwargs["application_text"], "申请文件正文")


if __name__ == "__main__":
    unittest.main()
