#!/usr/bin/env python3
"""实测：Prior Application Status=Patented 的 ADS 走 pdfRest 扁平化后，专利块/专利号是否被渲染出来。

结论（2026-09-01 实测）：**pdfRest 也不行**——扁平版只渲染默认可见的 Pending 块（Patented 时为空），
状态显示 "Patented" 但专利号/授权日/母案号都不显示；数据在隐藏的专利子表单里，任何"按数据渲染"的
服务（Adobe / pdfRest）都不会替你切到专利块（可见性绑在用户 change 交互上，非脚本）。
→ 现实办法：ADS 打开后对 Patented 母案手动重选一次状态即渲染（数据已预填）。

用法（在 scripts/report 目录下）：
  python test_pdfrest_patented.py
⚠ 会把一份测试 ADS 数据上传到 pdfRest 云（收费一次调用）。
"""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))   # 让 submission.* 可导入
from submission.common import normalize_parents            # noqa: E402
from submission.fields_mapping import fields_to_case_info   # noqa: E402
from submission.ads_generator import generate_ads, generate_ads_flat  # noqa: E402


def main():
    # 一份 Patented 母案的测试数据（专利号 11999999 / 授权日 2025-06-10 / 母案 18/621,052）
    base = {"applicants": [{"applicant_name_en": "ACME CORP", "address1": "1 Main", "city_en": "NYC",
                            "country_en_us": "US", "postcode": "10001"}],
            "inventors": [{"first_name_en": "John", "last_name_en": "Smith"}]}
    f = {**base, "case_info": {"case_name_en": "TEST INVENTION"},
         "parent_applications": [{"Prior Application Number": "18/621,052", "Filing Date": "2023-01-01",
                                  "Continuity Type": "Continuation of", "Prior Application Status": "Patented",
                                  "Patent Number": "11999999", "Issue Date": "2025-06-10"}]}
    normalize_parents(f)
    ci = fields_to_case_info(f, {})

    out = tempfile.mkdtemp()
    print("生成本地 XFA ADS…")
    xfa = generate_ads(ci, out)
    print("  XFA:", xfa["file_path"])

    print("走 pdfRest 扁平化（上传云端）…")
    try:
        flat = generate_ads_flat(ci, out)
        print("  扁平结果 type:", flat.get("type"), "file:", flat.get("file_name"), "warn:", flat.get("warnings"))
    except Exception as e:  # noqa: BLE001
        print("  ❌ 扁平化失败:", type(e).__name__, e)
        return

    flat_path = flat.get("file_path")
    if not flat_path or flat.get("type") != "ADS-flat":
        print("  ⚠ 未拿到扁平版（回退了数据核对版），pdfRest 未成功渲染，无法判定。")
        return

    import fitz
    txt = "".join(p.get_text() for p in fitz.open(flat_path))
    print("\n=== 扁平 PDF 文本里查关键值 ===")
    checks = {
        "专利号 11999999": "11999999" in txt,
        "授权日 2025-06-10": ("2025-06-10" in txt) or ("06/10/2025" in txt),
        "母案号 18621052/18/621,052": ("18621052" in txt) or ("621,052" in txt),
        "出现 Patented 字样": "Patented" in txt,
        "出现 Patent Number 标签": "Patent Number" in txt,
        "出现 Pending 字样": "Pending" in txt,
    }
    for k, v in checks.items():
        print(f"  {'✅' if v else '❌'} {k}: {v}")
    print("\n=== 结论 ===")
    if checks["专利号 11999999"]:
        print(">>> pdfRest 扁平版出现了专利号 → 渲染出了【专利块】，这条路可行。")
    else:
        print(">>> 扁平版没有专利号 → pdfRest 也只渲染 Pending 块，这条路不行。")
    print("扁平 PDF:", flat_path)


if __name__ == "__main__":
    main()
