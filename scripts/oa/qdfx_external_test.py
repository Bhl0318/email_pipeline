"""外部 OA 前端分析材料提交的离线测试。"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(__file__))
from qdfx_external import _ep_reference_numbers, _fpo_pdf, _reference_markdown, submit_oa_analysis
from mistral_ocr import fpo_reference_to_markdown


class ExternalAnalysisTests(unittest.TestCase):
    def setUp(self):
        self.item = {"project": "20615-0011US00", "region": "US"}
        self.refs = [{"doc_no": "US20250150762A1"}]

    @patch("mistral_ocr._config", return_value=("https://ocr.example", "test-key"))
    @patch("requests.post")
    def test_reference_client_sends_number_to_ocr_vps(self, post, config):
        post.return_value.json.return_value = {
            "publication_number": "US20250150762A1", "source": "https://www.freepatentsonline.com/20250150762.pdf",
            "markdown": "US 2025/0150762 A1\n# CLAIMS\n1. test",
        }
        md, source = fpo_reference_to_markdown("US20250150762A1")
        self.assertIn("CLAIMS", md)
        self.assertIn("freepatentsonline", source)
        post.assert_called_once()
        self.assertEqual(post.call_args.args[0], "https://ocr.example/fpo-reference")
        self.assertEqual(post.call_args.kwargs["json"], {"publication_number": "US20250150762A1"})

    @patch("mistral_ocr.fpo_reference_to_markdown")
    def test_reference_must_match_full_publication_number_and_contain_full_text(self, remote):
        def markdown(number):
            return (f"{number}\n" +
                    ("Specification text. Specification text.\n" * 35) +
                    "# CLAIMS\n" + ("Claim text. Claim text.\n" * 12))
        remote.return_value = (markdown("US20250150762A1"), "https://www.freepatentsonline.com/20250150762.pdf")
        md = _reference_markdown("US 2025/0150762 A1")
        self.assertIn("Specification", md)
        self.assertIn("Claim text", md)
        remote.assert_called_once_with("US20250150762A1")

        remote.return_value = (markdown("US20250150762B2"), "https://www.freepatentsonline.com/20250150762.pdf")
        with self.assertRaisesRegex(ValueError, "公开号与请求不符"):
            _reference_markdown("US20250150762A1")

    def test_fpo_is_direct_source_and_country_is_kept(self):
        session = Mock()
        page = Mock(text='<iframe src="https://s3.amazonaws.com/pdf.sumobrain.com/110693604.pdf?X-Amz-Date=1"></iframe>')
        pdf = Mock(content=b"%PDF-1.7")
        session.get.side_effect = [page, pdf]
        content, source = _fpo_pdf("CN110693604A", session)
        self.assertEqual(content, b"%PDF-1.7")
        self.assertEqual(source, "https://www.freepatentsonline.com/CN110693604.pdf")
        self.assertEqual(session.get.call_args_list[0].args[0], source)
        self.assertEqual(session.get.call_args_list[1].args[0],
                         "https://s3.amazonaws.com/pdf.sumobrain.com/110693604.pdf?X-Amz-Date=1")

    def test_fpo_cookie_challenge_reloads_pdf_page(self):
        session = Mock()
        challenge = Mock(text=("<script>var a='ABC123',b='DEF456';"
                               "document.cookie='fpo_ck='+b+a+';path=/'</script>"))
        page = Mock(text='<iframe src="https://s3.amazonaws.com/pdf.sumobrain.com/123.pdf?X-Amz-Date=1"></iframe>')
        pdf = Mock(content=b"%PDF-1.7")
        session.get.side_effect = [challenge, page, pdf]
        content, _ = _fpo_pdf("US20250150762A1", session)
        self.assertEqual(content, b"%PDF-1.7")
        session.cookies.set.assert_called_once_with(
            "fpo_ck", "DEF456ABC123", domain="www.freepatentsonline.com", path="/"
        )
        self.assertEqual(session.get.call_args_list[0].args[0],
                         session.get.call_args_list[1].args[0])

    @patch.dict(os.environ, {"QDFX_API_TOKEN": "test-token", "QDFX_API_BASE_URL": "http://example.test/assist"})
    @patch("oa_report_ai.find_application_files", return_value={"spec": "/tmp/spec.docx"})
    @patch("oa_report_ai._docx_text", return_value="Application text")
    @patch("qdfx_external._reference_markdown", return_value="# cited patent\nfull text")
    def test_upload_requires_complete_refs_and_checks_http_and_body(self, ref_text, docx, find_app):
        session = Mock()
        session.post.return_value.status_code = 202
        session.post.return_value.json.return_value = {"code": 202, "data": {"parseId": "parse-1", "version": 1}}
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result, {"status": "submitted", "parseId": "parse-1", "version": 1})
        kwargs = session.post.call_args.kwargs
        self.assertEqual([field for field, _ in kwargs["files"]], ["scyj", "sqwj", "dbwj"])
        self.assertEqual(kwargs["data"]["caseNo"], self.item["project"])
        self.assertEqual(kwargs["headers"]["X-Api-Token"], "test-token")

        ref_text.side_effect = ValueError("wrong patent")
        session.post.reset_mock()
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result["status"], "skipped")
        session.post.assert_not_called()

        ref_text.side_effect = None
        session.post.return_value.status_code = 200
        session.post.return_value.json.return_value = {"code": 202, "data": {"parseId": "parse-2"}}
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result["status"], "failed")

    @patch.dict(os.environ, {"QDFX_API_TOKEN": "test-token"})
    @patch("oa_report_ai.find_application_files", return_value={"spec": None})
    @patch("oa_report_ai._docx_text", return_value="")
    def test_missing_application_skips_before_fetch(self, docx, find_app):
        session = Mock()
        result = submit_oa_analysis(self.item, "OA text", self.refs, session=session)
        self.assertEqual(result["status"], "skipped")
        session.get.assert_not_called()
        session.post.assert_not_called()

    @patch.dict(os.environ, {"QDFX_API_TOKEN": "test-token"})
    @patch("oa_report_ai.find_application_files", side_effect=AssertionError("不应读取 NAS 申请文件"))
    @patch("qdfx_external._reference_markdown", return_value="# 对比文件\n全文")
    def test_manual_application_text_uses_formal_submit(self, ref_text, find_app):
        session = Mock()
        session.post.return_value.status_code = 202
        session.post.return_value.json.return_value = {"code": 202, "data": {"parseId": "parse-manual"}}
        result = submit_oa_analysis(self.item, "审查意见", self.refs, session=session,
                                    application_text="手工指定的申请文件正文")
        self.assertEqual(result["status"], "submitted")
        find_app.assert_not_called()
        self.assertIn("手工指定的申请文件正文", session.post.call_args.kwargs["files"][1][1][1].decode())

    def test_ep_inline_reference_and_unrecognized_reference(self):
        self.assertEqual(_ep_reference_numbers("D1: EP 1234567 A1; D2: WO2020123456A1"),
                         [{"doc_no": "EP1234567A1"}, {"doc_no": "WO2020123456A1"}])
        with patch.dict(os.environ, {"QDFX_API_TOKEN": "test-token"}), \
             patch("oa_report_ai.find_application_files", return_value={"spec": "/tmp/spec.docx"}), \
             patch("oa_report_ai._docx_text", return_value="Application text"):
            session = Mock()
            result = submit_oa_analysis(self.item, "OA text", [{"doc_no": "conference paper"}], session=session)
            self.assertEqual(result["status"], "skipped")
            session.post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
