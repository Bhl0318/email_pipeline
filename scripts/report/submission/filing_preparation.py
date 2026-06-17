#!/usr/bin/env python3
"""环节4 组装：准备递交文件（映射 → 生成 POA/Transmittal/ADS → 拼给美代理邮件）。

纯确定性，不连库、不发信、不做定时触发——这些由调用方负责：
- 定稿文件（说明书/权要/附图终版）由人工上传（审核页），以 final_docs 传入，随递交件一并交美代理；
- 入队 submission_tasks(task_type='filing_preparation') 与发送，由审核页/定时 skill 处理。

输入 fields = submission_tasks.fields_json；签字人/Customer Number/Deposit 走 agent_config.json。
"""
from pathlib import Path

from .agent_email import build_agent_email
from .ads_generator import generate_ads
from .fields_mapping import fields_to_case_info, load_agent_info
from .poa_generator import generate_poa
from .transmittal_generator import generate_transmittal


def build_filing_documents(fields: dict, output_dir, final_docs=None,
                           agent_recipient: str = "X总/X律师",
                           transmittal_options: dict = None) -> dict:
    """生成递交三件 + 给美代理邮件。
    :param fields: submission_tasks.fields_json
    :param output_dir: 输出目录（建议 output/{案号}/filing/）
    :param final_docs: 人工上传的定稿文件路径列表（说明书/权要/附图），原样纳入清单
    :param transmittal_options: 递交清单（实体/页数/POA·IDS·序列表·PA·Assignment·ADS·备注），
           操作员在审核页填，见 transmittal_generator 模块 docstring
    :return: {case_volume, documents:[{file_path,file_name,type}], final_docs, agent_email, case_info, warnings}
    """
    case_volume = fields.get("case_volume", "")
    warnings = []

    agent_info = load_agent_info(case_volume)
    if not agent_info.get("Name"):
        warnings.append("未取到签字代理人（agent_config.json 缺该客户/默认条目）→ POA/Transmittal 签字栏将为空")
    case_info = fields_to_case_info(fields, agent_info)

    output_dir = Path(output_dir)
    documents = []
    # POA / ADS 无额外选项；Transmittal 吃递交清单 options
    jobs = [
        (generate_poa, {}),
        (generate_transmittal, {"options": transmittal_options}),
        (generate_ads, {}),
    ]
    for gen, kw in jobs:
        try:
            doc = gen(case_info, output_dir, **kw)
            documents.append(doc)
            warnings.extend(doc.get("warnings", []) if isinstance(doc, dict) else [])
        except Exception as e:
            warnings.append(f"{gen.__name__} 生成失败: {e}")

    return {
        "case_volume": case_volume,
        "documents": documents,
        "final_docs": list(final_docs or []),
        "agent_email": build_agent_email(case_volume, agent_recipient),
        "case_info": case_info,
        "warnings": warnings,
    }


if __name__ == "__main__":
    import json
    sample = {
        "case_volume": "64504-H006US00", "case_info": {"case_name_en": "SMART KNEE BRACE"},
        "subject_matter": "UTL",
        "applicants": [{"applicant_name_en": "Mebotx Co.", "address1": "9F", "city_en": "Suzhou",
                        "postcode": "215100", "country_en_us": "CN"}],
        "inventors": [{"full_name_en": "Wei LIN", "first_name_en": "Wei", "last_name_en": "LIN"}],
        "priorities": [], "parent_applications": [],
    }
    out = Path(__file__).resolve().parent.parent / "ads_test_out"
    r = build_filing_documents(sample, out, final_docs=["/path/to/说明书定稿.pdf"])
    print("案号:", r["case_volume"])
    for d in r["documents"]:
        print("  生成:", d.get("type"), d.get("file_name"))
    print("  定稿(人工上传):", r["final_docs"])
    print("  给美代理邮件 subject:", r["agent_email"]["subject"])
    print("  body:\n", r["agent_email"]["body"])
    if r["warnings"]:
        print("  warnings:", r["warnings"])
