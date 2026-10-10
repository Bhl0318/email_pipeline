"""Offline checks for the standalone FPO reference downloader."""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import fitz

sys.path.insert(0, os.path.dirname(__file__))
from fpo_reference_cli import run


def _pdf(number):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((40, 40), f"{number}\n" +
                     ("Specification text. Specification text.\n" * 35) +
                     "CLAIMS\n" + ("Claim text. Claim text.\n" * 12))
    data = doc.tobytes()
    doc.close()
    return data


class FpoReferencesTests(unittest.TestCase):
    def test_extract_download_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp, patch("fpo_reference_cli._fpo_pdf") as fetch:
            base = Path(tmp)
            oa = base / "oa.md"
            app = base / "application.md"
            oa.write_text("本通知书引用下列对比文件\n1 CN110693604A 2019-11-19", encoding="utf-8")
            app.write_text("申请文件正文", encoding="utf-8")
            fetch.return_value = (_pdf("CN110693604A"), "https://www.freepatentsonline.com/CN110693604.pdf")
            result = run("20618-0001CN00", oa, app, output_root=base / "out")
            self.assertEqual(result["status"], "downloaded")
            self.assertEqual(result["reference_numbers"], ["CN110693604A"])
            self.assertTrue(Path(result["documents"][0]["pdf"]).is_file())
            self.assertEqual(json.loads(Path(result["summary"]).read_text())["status"], "downloaded")

    def test_wrong_publication_never_saved(self):
        with tempfile.TemporaryDirectory() as tmp, patch("fpo_reference_cli._fpo_pdf") as fetch:
            base = Path(tmp)
            oa = base / "oa.md"
            app = base / "application.md"
            oa.write_text("Office Action", encoding="utf-8")
            app.write_text("Application", encoding="utf-8")
            fetch.return_value = (_pdf("US20250150762B2"), "https://www.freepatentsonline.com/20250150762.pdf")
            result = run("20615-0011US00", oa, app, ["US20250150762A1"], base / "out")
            self.assertEqual(result["status"], "incomplete")
            self.assertFalse((base / "out" / "20615-0011US00" / "US20250150762A1.pdf").exists())


if __name__ == "__main__":
    unittest.main()
