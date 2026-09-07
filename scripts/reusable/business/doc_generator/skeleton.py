"""文档生成器骨架（业务支撑层）。

范式抽象自 report/submission/：把"按数据生成表单"拆成三步分离——
① 字段映射（原始数据 → 生成器要的结构）② 模板选择（按条件挑模板）
③ 生成器编排（跑一组生成器、各自返回统一结果、逐个兜底、汇总）。

骨架只管这三步的通用机制；每个生成器怎么填模板是业务（填 PDF 表单可用
doc_utils.fill_pdf_form，填 docx 用 python-docx）。生成器契约见下。

生成器契约：callable(data, **kwargs) -> dict，至少含
    {"file_path": 路径, "file_name": 文件名, "type": 类型}，可含 "warnings": [str]。
"""
import sys


def map_fields(raw, spec):
    """按映射规格把原始数据转成生成器要的结构（字段映射层）。

    输入：raw: dict（原始数据）；spec: dict {目标键: 来源}，来源可为
          源键名 str（取 raw[源键]）或 callable(raw)->值（自定义派生）。
    输出：dict（映射后的结构）。
    """
    out = {}
    for target, src in spec.items():
        out[target] = src(raw) if callable(src) else raw.get(src)
    return out


def select_template(templates, key, default=None):
    """按 key 从候选里挑模板（模板选择层）。

    输入：templates: dict {条件键: 模板路径}；key: 条件键；default: 未命中时的返回（可选）。
    输出：命中的模板路径；未命中→default。
    （"大小写/别名归一"这类判断由调用方在算 key 时处理。）
    """
    return templates.get(key, default)


def build_documents(data, jobs):
    """跑一组生成器，逐个兜底，汇总结果（生成器编排层）。

    输入：
      data: dict（各生成器共享的输入，即映射后的结构）
      jobs: 列表，每项为 (生成器callable, kwargs字典)；生成器按上面的契约返回 dict
    输出：{"documents": [成功的结果 dict...], "warnings": [str...]}
          某生成器抛异常不中断，记一条 warning 继续；各结果自带的 warnings 也汇总进来。
    """
    documents, warnings = [], []
    for gen, kw in jobs:
        try:
            doc = gen(data, **(kw or {}))
            documents.append(doc)
            if isinstance(doc, dict):
                warnings.extend(doc.get("warnings", []) or [])
        except Exception as e:  # noqa: BLE001
            name = getattr(gen, "__name__", str(gen))
            warnings.append(f"{name} 生成失败: {e}")
            print(f"[doc_generator] {name} 生成失败: {e}", file=sys.stderr)
    return {"documents": documents, "warnings": warnings}
