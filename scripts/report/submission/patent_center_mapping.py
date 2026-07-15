#!/usr/bin/env python3
"""fields_json + 文件集 → Patent Center 新申请上传的 API 载荷（环节7 直调方案的确定性数据层）。

据《us_submission/PatentCenter申请上传接口时序-2026-07-15.md》逆向出的私有接口
（patentcenter.uspto.gov/filing/private/v1）整理。**纯确定性映射（严禁 AI）**，不碰网络/USPTO，
可离线单测；API 客户端消费本模块产出，按时序直调（tokens 由 Playwright 登录后注入）。

产出：
- submission_create：POST /submissions 的体（申请类型/主题/类别）
- filed_on_behalf_of：PATCH /submissions/{id} 的代表递交执业人（=代理所；userIdentifier 运行期从 /sponsors 匹配）
- documents：按上传顺序的文件清单，每项含 kind / 关联端点(ads|items) / document description（分类）
- needs：缺失或待确认项（不编造）
"""
from .common import infer_subject_matter

# subject_matter → (applicationTypeIdentifier, subjectMatterCategory)
# UTL 已由 HAR 确认（identifier=1, category="UTL"）；DES/371 的 identifier 待实测确认。
_SUBJECT_MAP = {
    "UTL": (1, "UTL"),
    "DES": (None, "DES"),   # applicationTypeIdentifier 待确认
    "371": (None, "UTL"),   # 371 国家阶段：category/submissionCategory 待确认
}

# 我们生成/签署的文件 kind → (关联端点, USPTO document description)
# ADS 走专用 /ads/file/associateScannedFile（认 AIA14 表单 PDF）；其余走 /items/associateScannedFile。
# description 不进 associate 请求体（Patent Center 按文件名自动识别 + UI 确认），此处作元数据供环节8 复审核对。
_DOC_MAP = {
    "ADS":           ("ads",   "Application Data Sheet"),
    "Specification": ("items", "Specification"),
    "Claims":        ("items", "Claims"),
    "Abstract":      ("items", "Abstract"),
    "Drawings":      ("items", "Drawings-only black and white line drawings"),
    "Declaration":   ("items", "Oath or Declaration filed"),
    "POA":           ("items", "Power of Attorney"),
    "Transmittal":   ("items", "Transmittal Letter"),
    "IDS":           ("items", "Information Disclosure Statement (IDS) Form (SB08)"),
}

# ADS 优先、其余按 USPTO 惯例顺序；未列 kind 排最后
_DOC_ORDER = ["ADS", "Specification", "Claims", "Abstract", "Drawings",
              "Transmittal", "POA", "Declaration", "IDS"]


def _subject(fields, needs):
    sm = infer_subject_matter(fields) or "UTL"
    app_id, cat = _SUBJECT_MAP.get(sm, (None, sm))
    if app_id is None:
        needs.append(f"subject_matter={sm}：applicationTypeIdentifier 待实测确认（仅 UTL 已确认=1）")
    return sm, app_id, cat


def fields_to_patent_center(fields, *, filed_on_behalf=None, documents=None):
    """fields_json + 文件集 → Patent Center 上传 API 载荷。

    :param fields: submission_tasks.fields_json
    :param filed_on_behalf: 代表递交执业人 dict {firstName, lastName}（=代理所；运行期传入，
        userIdentifier 由客户端从 GET /sponsors 按名匹配填入）
    :param documents: 待上传文件 [{"path":..., "kind":"ADS"/"Specification"/...}]（env4/5 产出 + 签署件）
    :return: {"submission_create","filed_on_behalf_of","documents","needs"}
    """
    fields = fields or {}
    needs = []

    sm, app_id, cat = _subject(fields, needs)
    submission_create = {
        "applicationTypeIdentifier": app_id if app_id is not None else 1,
        "guestIndicator": False,
        "subjectMatterCategory": cat,
        "submissionCategory": "New",
    }

    fob = dict(filed_on_behalf or {})
    first = (fob.get("firstName") or "").strip()
    last = (fob.get("lastName") or "").strip()
    if not (first and last):
        needs.append("缺代表递交执业人 filed_on_behalf（firstName/lastName；=代理所，运行期传入）")
    filed_on_behalf_of = {
        "filedOnBehalfOfFirstName": first,
        "filedOnBehalfOfLastName": last,
        # userIdentifier 运行期由客户端从 GET /sponsors 按名匹配后填入
        "filedOnBehalfOfUserIdentifier": fob.get("userIdentifier"),
        "pctNumberText": (fields.get("case_advance_info") or {}).get("pct_app_no") or None,
    }
    if not filed_on_behalf_of["filedOnBehalfOfUserIdentifier"]:
        needs.append("filedOnBehalfOfUserIdentifier 待运行期从 GET /sponsors 按执业人名匹配")

    docs_in = documents or []
    if not docs_in:
        needs.append("缺待上传文件集 documents（env4/5 产出的 ADS/说明书/权要/附图/POA/Declaration/Transmittal 等）")
    docs_out = []
    for d in docs_in:
        kind = (d.get("kind") or "").strip()
        path = (d.get("path") or "").strip()
        endpoint, desc = _DOC_MAP.get(kind, (None, None))
        if endpoint is None:
            needs.append(f"文件 kind「{kind}」未知，无法定关联端点/分类")
            endpoint, desc = "items", kind
        if not path:
            needs.append(f"文件 kind「{kind}」缺路径")
        docs_out.append({
            "kind": kind, "path": path,
            "associate": endpoint,          # "ads" → /ads/file/... ; "items" → /items/...
            "document_description": desc,    # 供环节8 复审核对；不进 associate 请求体
        })
    # 按 USPTO 惯例排序（ADS 优先），未知 kind 排最后
    docs_out.sort(key=lambda x: _DOC_ORDER.index(x["kind"]) if x["kind"] in _DOC_ORDER else len(_DOC_ORDER))

    return {
        "submission_create": submission_create,
        "filed_on_behalf_of": filed_on_behalf_of,
        "documents": docs_out,
        "needs": needs,
    }
