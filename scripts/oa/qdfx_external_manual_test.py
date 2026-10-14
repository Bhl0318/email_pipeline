"""手工上传 Markdown 到外部前端分析接口的离线测试。"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(__file__))
from qdfx_external_manual import submit_markdown_files


class ManualSubmitTests(unittest.TestCase):
    @patch("qdfx_external_manual._connection_config", return_value=("test-token", "http://example.test/assist"))
    def test_uploads_original_markdown_files_and_returns_parse_id(self, config):
        with tempfile.TemporaryDirectory() as tmp:
            paths = [Path(tmp) / name for name in ("oa.md", "application.md", "ref1.md", "ref2.md")]
            for path in paths:
                path.write_text(f"# {path.stem}\n原始内容", encoding="utf-8")

            def post(url, *, files, data, headers, timeout):
                self.assertEqual(url, "http://example.test/assist/qdfx/external/parse")
                self.assertEqual([field for field, _ in files], ["scyj", "sqwj", "dbwj", "dbwj"])
                self.assertEqual([entry[1].read().decode("utf-8") for _, entry in files],
                                 [path.read_text(encoding="utf-8") for path in paths])
                self.assertEqual(data, {"caseNo": "90009-0001CN00", "createdBy": "writeSYS"})
                self.assertEqual(headers, {"X-Api-Token": "test-token"})
                return Mock(status_code=202, json=lambda: {"code": 202, "data": {"parseId": "p1"}})

            result = submit_markdown_files("90009-0001CN00", *paths[:2], paths[2:], post=post)
        self.assertEqual(result["parseId"], "p1")


if __name__ == "__main__":
    unittest.main()
