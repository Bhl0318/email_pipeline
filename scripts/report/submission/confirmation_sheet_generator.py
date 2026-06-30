# -*- coding: utf-8 -*-
"""confirmation-sheet-generator

输入合并好的著录项 JSON（case-bibliography-lookup 输出 + parent_applications），
生成确认函（Application Information Sheet）docx，stdout 输出结果 JSON。
移植自 old_submission/original/patent_application_form_generator.py，生成逻辑保持一致。
"""
import argparse
import datetime
import json
import os
import re
import sys

from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.table import WD_ROW_HEIGHT_RULE


class PatentApplicationFormGenerator:
    def __init__(self, case_info, output_path):
        self.case_info = case_info
        self.output_path = output_path

    def _set_cell_shading(self, cell, fill_color="acb9ca"):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        for shd in tcPr.findall(qn('w:shd')):
            tcPr.remove(shd)
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), fill_color)
        tcPr.append(shd)

    def _set_cell_vertical_center(self, cell):
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        for child in tcPr.findall(qn('w:vAlign')):
            tcPr.remove(child)
        vAlign = OxmlElement('w:vAlign')
        vAlign.set(qn('w:val'), 'center')
        tcPr.append(vAlign)

    def _format_cell(self, cell, text=None, font_size=10.5, bold=False, valign_center=False):
        """
        自动拆分中英文字符，每个 run 分别设置字体
        中文 → 等线
        英文 → Times New Roman
        """
        if text is not None:
            cell.text = ''
            para = cell.paragraphs[0]

            # 按中文和英文分段
            pattern = re.compile(r'([\u4e00-\u9fff]+|[^\u4e00-\u9fff]+)')
            for chunk in pattern.findall(text):
                run = para.add_run(chunk)
                run.font.size = Pt(font_size)
                run.bold = bold
                if re.search(r'[\u4e00-\u9fff]', chunk):
                    run.font.name = 'DengXian'
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'DengXian')
                else:
                    run.font.name = 'Times New Roman'
                    r = run._element
                    r.rPr.rFonts.set(qn('w:ascii'), 'Times New Roman')
                    r.rPr.rFonts.set(qn('w:hAnsi'), 'Times New Roman')
        else:
            para = cell.paragraphs[0]
            if not para.runs:
                para.add_run()

        if valign_center:
            self._set_cell_vertical_center(cell)

    def normalize_keys(self, d):
        if isinstance(d, dict):
            return {str(k): self.normalize_keys(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [self.normalize_keys(i) for i in d]
        else:
            return d

    def validate_required_fields(self, case_info):
        """
        验证必填字段，返回缺失字段的列表
        """
        missing_fields = []

        # 1. 验证方案号
        if not case_info.get('case_volume'):
            missing_fields.append({
                'field': 'case_volume',
                'field_name': '方案号',
                'path': 'case_info["case_volume"]',
                'description': '必填字段：方案号不能为空'
            })

        # 2. 验证案件名称（英文）
        case_info_data = case_info.get('case_info', {})
        if not case_info_data.get('case_name_en'):
            missing_fields.append({
                'field': 'case_info.case_name_en',
                'field_name': '案件名称（英文）',
                'path': 'case_info["case_info"]["case_name_en"]',
                'description': '必填字段：案件英文名称不能为空'
            })

        # 3. 验证发明人（至少一个）
        inventors = case_info.get('inventors', [])
        if not inventors or len(inventors) == 0:
            missing_fields.append({
                'field': 'inventors',
                'field_name': '发明人',
                'path': 'case_info["inventors"]',
                'description': '必填字段：至少需要一个发明人'
            })
        else:
            # 验证第一个发明人的姓名
            first_inventor = inventors[0]
            if not first_inventor.get('first_name_en') or '':
                missing_fields.append({
                    'field': 'inventors[0].first_name_en',
                    'field_name': '发明人名（First Name）',
                    'path': 'case_info["inventors"][0]["first_name_en"]',
                    'description': '必填字段：第一个发明人的名（First Name）不能为空'
                })
            if not first_inventor.get('last_name_en') or '':
                missing_fields.append({
                    'field': 'inventors[0].last_name_en',
                    'field_name': '发明人姓（Last Name）',
                    'path': 'case_info["inventors"][0]["last_name_en"]',
                    'description': '必填字段：第一个发明人的姓（Last Name）不能为空'
                })

        # 4. 验证申请人（至少一个）
        applicants = case_info.get('applicants', [])
        if not applicants or len(applicants) == 0:
            missing_fields.append({
                'field': 'applicants',
                'field_name': '申请人',
                'path': 'case_info["applicants"]',
                'description': '必填字段：至少需要一个申请人'
            })
        else:
            # 验证第一个申请人的信息
            first_applicant = applicants[0]
            if not first_applicant.get('applicant_name_en'):
                missing_fields.append({
                    'field': 'applicants[0].applicant_name_en',
                    'field_name': '申请人英文名称',
                    'path': 'case_info["applicants"][0]["applicant_name_en"]',
                    'description': '必填字段：第一个申请人的英文名称不能为空'
                })

            # 验证地址信息
            if not first_applicant.get('address1') or '':
                missing_fields.append({
                    'field': 'applicants[0].address1',
                    'field_name': '申请人地址1',
                    'path': 'case_info["applicants"][0]["address1"]',
                    'description': '必填字段：申请人地址1不能为空'
                })

            if not first_applicant.get('city_en'):
                missing_fields.append({
                    'field': 'applicants[0].city_en',
                    'field_name': '申请人城市（英文）',
                    'path': 'case_info["applicants"][0]["city_en"]',
                    'description': '必填字段：申请人城市（英文）不能为空'
                })

            if not first_applicant.get('province_city_en_us'):
                missing_fields.append({
                    'field': 'applicants[0].province_city_en_us',
                    'field_name': '申请人州/省（英文）',
                    'path': 'case_info["applicants"][0]["province_city_en_us"]',
                    'description': '必填字段：申请人州/省（英文）不能为空'
                })

            if not first_applicant.get('postcode'):
                missing_fields.append({
                    'field': 'applicants[0].postcode',
                    'field_name': '申请人邮编',
                    'path': 'case_info["applicants"][0]["postcode"]',
                    'description': '必填字段：申请人邮编不能为空'
                })

            if not first_applicant.get('country_en_us'):
                missing_fields.append({
                    'field': 'applicants[0].country_en_us',
                    'field_name': '申请人国家（英文）',
                    'path': 'case_info["applicants"][0]["country_en_us"]',
                    'description': '必填字段：申请人国家（英文）不能为空'
                })

        # 5. 验证落地方式
        if not case_info.get('filing_route'):
            missing_fields.append({
                'field': 'filing_route',
                'field_name': '落地方式',
                'path': 'case_info["filing_route"]',
                'description': '必填字段：落地方式不能为空'
            })

        # 6. 验证加速方式
        if not case_info.get('ae_methods'):
            missing_fields.append({
                'field': 'ae_methods',
                'field_name': '加速方式',
                'path': 'case_info["加速方式"]',
                'description': '必填字段：加速方式不能为空'
            })

        return missing_fields

    def validate_optional_fields(self, case_info):
        """
        验证非必填字段（可选信息），返回缺失字段的列表
        这些字段缺失不会阻止文档生成
        """
        missing_optional_fields = []

        # 获取业务类型
        business_type_zh_cn = case_info.get('business_type_zh_cn', '')

        # 定义不需要PCT信息的业务类型
        no_pct_required_types = ['普通新申请', '临时申请', '巴黎公约新申请']
        # 定义需要US母案信息的业务类型
        parent_required_types = ['续案', '分案', '部分续案']

        # 1. 验证母案信息（仅当 business_type_zh_cn 是 续案、分案、部分续案 时才提醒）
        if business_type_zh_cn in parent_required_types:
            parent_applications = case_info.get('parent_applications', []) or []
            if not parent_applications or len(parent_applications) == 0:
                missing_optional_fields.append({
                    'field': 'parent_applications',
                    'field_name': 'US母案信息',
                    'path': 'case_info["parent_applications"]',
                    'description': '可选字段：未提供US母案信息'
                })
            else:
                # 检查母案信息的完整性
                for idx, parent in enumerate(parent_applications):
                    if not parent.get('Application No'):
                        missing_optional_fields.append({
                            'field': f'parent_applications[{idx}].Application No',
                            'field_name': f'US母案申请号',
                            'path': f'case_info["parent_applications"][{idx}]["Application No"]',
                            'description': f'可选字段：US母案缺少申请号'
                        })
                    if not parent.get('Filing Date'):
                        missing_optional_fields.append({
                            'field': f'parent_applications[{idx}].Filing Date',
                            'field_name': f'US母案申请日',
                            'path': f'case_info["parent_applications"][{idx}]["Filing Date"]',
                            'description': f'可选字段：US母案缺少申请日'
                        })

        # 2. 验证PCT信息（仅当 business_type_zh_cn 不是 普通新申请、临时申请、巴黎公约新申请 时才提醒）
        if business_type_zh_cn not in no_pct_required_types:
            case_advance_info = case_info.get('case_advance_info', {})
            if not case_advance_info:
                missing_optional_fields.append({
                    'field': 'case_advance_info',
                    'field_name': 'PCT信息',
                    'path': 'case_info["case_advance_info"]',
                    'description': '可选字段：未提供PCT信息'
                })
            else:
                if not case_advance_info.get('pct_app_no'):
                    missing_optional_fields.append({
                        'field': 'case_advance_info.pct_app_no',
                        'field_name': 'PCT申请号',
                        'path': 'case_info["case_advance_info"]["pct_app_no"]',
                        'description': '可选字段：未提供PCT申请号'
                    })
                if not case_advance_info.get('pct_app_date'):
                    missing_optional_fields.append({
                        'field': 'case_advance_info.pct_app_date',
                        'field_name': 'PCT申请日',
                        'path': 'case_info["case_advance_info"]["pct_app_date"]',
                        'description': '可选字段：未提供PCT申请日'
                    })
                if not case_advance_info.get('pct_pub_no'):
                    missing_optional_fields.append({
                        'field': 'case_advance_info.pct_pub_no',
                        'field_name': 'PCT公开号',
                        'path': 'case_info["case_advance_info"]["pct_pub_no"]',
                        'description': '可选字段：未提供PCT公开号'
                    })
                if not case_advance_info.get('pct_pub_date'):
                    missing_optional_fields.append({
                        'field': 'case_advance_info.pct_pub_date',
                        'field_name': 'PCT公开日',
                        'path': 'case_info["case_advance_info"]["pct_pub_date"]',
                        'description': '可选字段：未提供PCT公开日'
                    })

        # 3. 验证优先权信息
        priorities = case_info.get('priorities', [])
        if not priorities or len(priorities) == 0:
            missing_optional_fields.append({
                'field': 'priorities',
                'field_name': '优先权信息',
                'path': 'case_info["priorities"]',
                'description': '可选字段：未提供优先权信息'
            })
        else:
            # 检查优先权信息的完整性
            for idx, priority in enumerate(priorities):
                if not priority.get('priority_num'):
                    missing_optional_fields.append({
                        'field': f'priorities[{idx}].priority_num',
                        'field_name': f'优先权号',
                        'path': f'case_info["priorities"][{idx}]["priority_num"]',
                        'description': f'可选字段：优先权缺少优先权号'
                    })
                if not priority.get('priority_date'):
                    missing_optional_fields.append({
                        'field': f'priorities[{idx}].priority_date',
                        'field_name': f'优先权日期',
                        'path': f'case_info["priorities"][{idx}]["priority_date"]',
                        'description': f'可选字段：优先权缺少优先权日期'
                    })

        # 4. 验证其他中文信息
        case_info_data = case_info.get('case_info', {})
        if not case_info_data.get('case_name'):
            missing_optional_fields.append({
                'field': 'case_info.case_name',
                'field_name': '案件名称（中文）',
                'path': 'case_info["case_info"]["case_name"]',
                'description': '可选字段：未提供案件中文名称'
            })

        # 验证申请人中文信息
        applicants = case_info.get('applicants', []) or []
        if applicants and len(applicants) > 0:
            for idx, applicant in enumerate(applicants):
                if not applicant.get('applicant_name_cn'):
                    missing_optional_fields.append({
                        'field': f'applicants[{idx}].applicant_name_cn',
                        'field_name': f'申请人中文名称',
                        'path': f'case_info["applicants"][{idx}]["applicant_name_cn"]',
                        'description': f'可选字段：申请人未提供中文名称'
                    })
                if not applicant.get('contact_address_cn'):
                    missing_optional_fields.append({
                        'field': f'applicants[{idx}].contact_address_cn',
                        'field_name': f'申请人中文地址',
                        'path': f'case_info["applicants"][{idx}]["contact_address_cn"]',
                        'description': f'可选字段：申请人未提供中文地址'
                    })
                if not applicant.get('city_cn'):
                    missing_optional_fields.append({
                        'field': f'applicants[{idx}].city_cn',
                        'field_name': f'申请人城市（中文）',
                        'path': f'case_info["applicants"][{idx}]["city_cn"]',
                        'description': f'可选字段：申请人未提供中文城市'
                    })
                if not applicant.get('province_city_zh_cn'):
                    missing_optional_fields.append({
                        'field': f'applicants[{idx}].province_city_zh_cn',
                        'field_name': f'申请人省市（中文）',
                        'path': f'case_info["applicants"][{idx}]["province_city_zh_cn"]',
                        'description': f'可选字段：申请人未提供中文省市'
                    })
                if not applicant.get('country_zh_cn'):
                    missing_optional_fields.append({
                        'field': f'applicants[{idx}].country_zh_cn',
                        'field_name': f'申请人国家（中文）',
                        'path': f'case_info["applicants"][{idx}]["country_zh_cn"]',
                        'description': f'可选字段：申请人未提供中文国家'
                    })
                if not applicant.get('entity_cn'):
                    missing_optional_fields.append({
                        'field': f'applicants[{idx}].entity_cn',
                        'field_name': f'申请人实体类型（中文）',
                        'path': f'case_info["applicants"][{idx}]["entity_cn"]',
                        'description': f'可选字段：申请人未提供中文实体类型'
                    })
                if not applicant.get('entity_en'):
                    missing_optional_fields.append({
                        'field': f'applicants[{idx}].entity_en',
                        'field_name': f'申请人实体类型（英文）',
                        'path': f'case_info["applicants"][{idx}]["entity_en"]',
                        'description': f'可选字段：申请人未提供英文实体类型'
                    })

        return missing_optional_fields

    def generate(self):
        case_info = self.normalize_keys(self.case_info)

        # 验证必填字段
        missing_fields = self.validate_required_fields(case_info)
        missing_optional_fields = self.validate_optional_fields(case_info)
        if missing_fields:
            error_message = "\n========== 必填字段缺失 ==========\n"
            error_message += f"共缺失 {len(missing_fields)} 个必填字段：\n\n"
            for idx, field in enumerate(missing_fields, 1):
                error_message += f"{idx}. {field['field_name']} ({field['field']})\n"
                error_message += f"   路径: {field['path']}\n"
                error_message += f"   说明: {field['description']}\n\n"
            error_message += "================================\n"
            print(error_message, file=sys.stderr)

        case_info_data = case_info.get("case_info", {})
        # 发明地：审核页可覆盖，留空回退默认 中国/CN
        loc_en = case_info_data.get("location_invention_en") or "People's Republic of China (CN)"
        loc_cn = case_info_data.get("location_invention_cn") or "中国"
        data_rows1 = [
            ['Title发明名称', case_info_data.get("case_name_en", ""), case_info_data.get("case_name", "")],
            ['Foreign Filing License/保密审查'],
            ['Location of Invention/Design / 发明/设计地', loc_en, loc_cn],
        ]

        # 美国母案：无母案数据则整段不渲染（不显示空的标题行）
        Parent_applications = case_info.get('parent_applications', []) or []
        data_rows6 = []
        if Parent_applications:
            data_rows6 = [['Parent Application/美国母案信息']]
            for parent in Parent_applications:
                data_rows6.append(['Application No/申请号:', parent.get('Application No', '') or ''])
                data_rows6.append(['Filing Date/申请日:', parent.get('Filing Date', '') or ''])

        # PCT：无任何 PCT 数据则整段不渲染
        PCT_applications = case_info.get('case_advance_info', {}) or {}
        data_rows7 = []
        if any((PCT_applications.get(k) or '').strip() for k in ('pct_app_no', 'pct_app_date', 'pct_pub_no', 'pct_pub_date')):
            data_rows7 = [
                ['PCT Application/PCT申请'],
                ['Application No/申请号:', PCT_applications.get('pct_app_no', '') or ''],
                ['Filing Date/申请日:', PCT_applications.get('pct_app_date', '') or ''],
                ['Publication No/公开号:', PCT_applications.get('pct_pub_no', '') or ''],
                ['Publication Date/公开日:', PCT_applications.get('pct_pub_date', '') or ''],
            ]

        inventors = case_info.get('inventors', []) or []
        applicants_list = case_info.get("applicants", []) or []
        _EMPTY_APP = {k: "" for k in (
            "applicant_name_en", "applicant_name_cn", "address1", "address2", "city_en", "city_cn",
            "province_city_en_us", "province_city_zh_cn", "postcode", "country_en_us", "country_zh_cn",
            "contact_address_cn")}
        LaborInfo = applicants_list[0] if applicants_list else _EMPTY_APP

        def _norm(s):
            return (s or "").strip().lower()

        # 申请人按英文名索引，供按 employer 取地址
        _app_by_name = {_norm(a.get("applicant_name_en")): a for a in applicants_list}

        def _app_for_employer(key, emp):
            """employer 命中申请人则取该申请人；否则（如前雇主，不在申请人列表）
            从 assignments.assigning_company 兜底取其地址（company_address 按逗号拆 address1/2）。"""
            app = _app_by_name.get(key)
            if app:
                return app
            for a in (case_info.get("assignments") or []):
                if _norm(a.get("assigning_company")) == key and (a.get("company_address") or "").strip():
                    ca = a["company_address"].strip()
                    parts = [p.strip() for p in re.split(r"[，,]", ca) if p.strip()]
                    return {**_EMPTY_APP, "applicant_name_en": emp,
                            "address1": parts[0] if parts else ca,
                            "address2": ", ".join(parts[1:]) if len(parts) > 1 else "",
                            "contact_address_en": ca}
            return _EMPTY_APP

        def _residence(app):
            res_en = ", ".join([x for x in [app.get("address1", ""), app.get("address2", ""), app.get("city_en", ""),
                                            app.get("province_city_en_us", ""), app.get("postcode", ""), app.get("country_en_us", "")] if x])
            res_cn = ", ".join([x for x in [app.get("contact_address_cn", ""), app.get("city_cn", ""),
                                            app.get("province_city_zh_cn", ""), app.get("country_zh_cn", "")] if x])
            return res_en, res_cn

        def _detail_rows(app):
            return [
                ["Address1/地址1:", app.get("address1", ""), app.get("contact_address_cn", "")],
                ["Address2/地址2:", app.get("address2", ""), ''],
                ["City/城市:", app.get("city_en", ""), app.get("city_cn", "")],
                ["State/Province/州/省", app.get("province_city_en_us", ""), app.get("province_city_zh_cn", "")],
                ["Post/邮编:", app.get("postcode", ""), ''],
                ["Nationality/国家:", app.get("country_en_us", ""), app.get("country_zh_cn", "")],
            ]

        def _fmt_idxs(idxs):
            """连续序号压成区间：[1,2,3]→1-3、[4,5,6,7]→4-7、[1,3,5]→1、3、5。"""
            parts, i = [], 0
            while i < len(idxs):
                j = i
                while j + 1 < len(idxs) and idxs[j + 1] == idxs[j] + 1:
                    j += 1
                parts.append(f"{idxs[i]}-{idxs[j]}" if j > i else str(idxs[i]))
                i = j + 1
            return "、".join(parts)

        # 按 employer 分组（保留发明人全局序号）。无 employer（存量）→ 全部归一组、公司取 applicants[0]。
        _all_have_emp = bool(inventors) and all((inv.get("employer") or "").strip() for inv in inventors)
        _groups = []  # 每组 {emp, app, members:[(全局序号, inventor)]}
        if _all_have_emp:
            _seen = {}
            for i, inv in enumerate(inventors, 1):
                emp = (inv.get("employer") or "").strip()
                key = _norm(emp)
                if key not in _seen:
                    _seen[key] = len(_groups)
                    _groups.append({"emp": emp, "app": _app_for_employer(key, emp), "members": []})
                _groups[_seen[key]]["members"].append((i, inv))
        else:
            _groups.append({"emp": LaborInfo.get("applicant_name_en", ""), "app": LaborInfo,
                            "members": [(i, inv) for i, inv in enumerate(inventors, 1)]})

        _single = len(_groups) == 1
        # 交叉布局：每组先列本组发明人（全局序号），紧跟该组劳动合同归属/住址；
        # 单公司(N=1) 用 "for all inventors"；多公司每组用 "for inventors<序号>"。
        data_rows2 = [['Inventor(s)/发明人 (Given name - Family name)']]
        for g in _groups:
            app = g["app"]
            for idx, inv in g["members"]:
                data_rows2.append([f'Inventor{idx}', inv.get('first_name_en', ''), inv.get('last_name_en', '')])
            # 仅单组时允许审核页全局覆盖（labor_contract_*/inventor_residence_*）
            labor_en = (case_info.get("labor_contract_en") if _single else "") or app.get("applicant_name_en", "") or g["emp"]
            labor_cn = (case_info.get("labor_contract_cn") if _single else "") or app.get("applicant_name_cn", "")
            _res_en, _res_cn = _residence(app)
            res_en = (case_info.get("inventor_residence_en") if _single else "") or _res_en
            res_cn = (case_info.get("inventor_residence_cn") if _single else "") or _res_cn
            if _single:
                labor_label = "Labor Contract for all inventors/劳动合同归属:"
                res_label = "Residence/Mailing Address for all inventors/所有发明人住址"
            else:
                tag = _fmt_idxs([idx for idx, _ in g["members"]])
                labor_label = f"Labor Contract for inventors{tag}/劳动合同归属:"
                res_label = f"Residence/Mailing Address for inventors{tag}/发明人{tag}住址"
            data_rows2.append([labor_label, labor_en, labor_cn])
            data_rows2.append([res_label, res_en, res_cn])
            for r in _detail_rows(app):
                data_rows2.append(r)

        applicants = case_info.get("applicants", []) or []
        data_rows3 = [['Applicant(s)/申请人']]
        applicant_index = 0
        for applicant in applicants:
            applicant_index += 1
            data_rows3.append([f'Name{str(applicant_index)}/申请人{str(applicant_index)}:', applicant.get('applicant_name_en', ''), applicant.get('applicant_name_cn', '')])
            data_rows3.append(['Address1/地址1:', applicant.get('address1', ''), applicant.get('contact_address_cn', '')])
            data_rows3.append(['Address2/地址2:', applicant.get('address2', ''), ''])
            data_rows3.append(['City/城市:', applicant.get('city_en', ''), applicant.get('city_cn', '')])
            data_rows3.append(['State/Province/州/省:', applicant.get('province_city_en_us', ''), applicant.get('province_city_zh_cn', '')])
            data_rows3.append(['Post/邮编：', applicant.get('postcode', '')])
            data_rows3.append(['Nationality/国家:', applicant.get('country_en_us', ''), applicant.get('country_zh_cn', '')])
            data_rows3.append(['Entity/实体', applicant.get('entity_en', ''), applicant.get('entity_cn', '')])

        # 优先权：无优先权数据则整段不渲染
        priorities = case_info.get('priorities', []) or []
        data_rows4 = []
        if priorities:
            data_rows4 = [['Priority Application (s)/优先权']]
            for prioritie in priorities:
                data_rows4.append(['Priority No./优先权号', prioritie.get('priority_num', '')])
                data_rows4.append(['Priority Date/优先权日:', prioritie.get('priority_date', '')])
                data_rows4.append(['DAS code/DAS码', prioritie.get('access_code', '')])
        data_rows5 = [
            ['Filing Route/落地方式'],
            ['Filing Route/落地方式', case_info.get('filing_route', '')] if case_info.get('filing_route') else ['Filing Route/落地方式', "371 Route (PCT national stage) \nBy pass continuation \nNew \nContinuation of \nContinuation in part of \nDivision of /nParis"],
            ['Expedited Examination Route/加速方式', case_info.get('ae_methods', '')] if case_info.get('ae_methods') else ['Expedited Examination Route/加速方式', "None \nTrack One prioritized examination(Track One) \nPatent Prosecution Highway (PPH)"],
        ]

        data_rows = data_rows1 + data_rows6 + data_rows7 + data_rows2 + data_rows3 + data_rows4 + data_rows5

        doc = Document()

        # 标题
        title = doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_run = title.add_run("Application Information Sheet")
        title_run.bold = True
        title_run.font.size = Pt(14)

        doc.add_paragraph()

        ref_paragraph = doc.add_paragraph()
        ref_text = f"Our Ref./我司案号: {case_info.get('case_volume', '')}"

        # 正则拆分中英文
        pattern = re.compile(r'([\u4e00-\u9fff]+|[^\u4e00-\u9fff]+)')
        for chunk in pattern.findall(ref_text):
            run = ref_paragraph.add_run(chunk)
            run.bold = True
            run.font.size = Pt(10.5)
            if re.search(r'[\u4e00-\u9fff]', chunk):  # 中文
                run.font.name = 'DengXian'
                run._element.rPr.rFonts.set(qn('w:eastAsia'), 'DengXian')
            else:  # 英文
                run.font.name = 'Times New Roman'
                r = run._element
                r.rPr.rFonts.set(qn('w:ascii'), 'Times New Roman')
                r.rPr.rFonts.set(qn('w:hAnsi'), 'Times New Roman')

        ref_paragraph_format = ref_paragraph.paragraph_format
        ref_paragraph_format.space_after = Pt(0)

        table = doc.add_table(rows=0, cols=3)
        table.style = "Table Grid"

        for row in data_rows:
            tr = table.add_row()
            cells = tr.cells

            if len(row) == 1:
                merged = cells[0].merge(cells[1])
                merged = merged.merge(cells[2])
                self._set_cell_shading(merged)
                self._format_cell(merged, row[0], bold=True, valign_center=True)
            elif len(row) == 2:
                cells[0].text = row[0]
                cells[1].text = row[1]
                cells[2].merge(cells[1])
                self._format_cell(cells[0], row[0], bold=True, valign_center=True)
                self._format_cell(cells[1], row[1], bold=False, valign_center=True)
            elif len(row) == 3:
                for i in range(3):
                    self._format_cell(cells[i], row[i], bold=(i == 0), valign_center=(i == 0))

        col_widths = [Cm(3.24), Cm((14.63 - 3.24) / 2), Cm((14.63 - 3.24) / 2)]
        for idx, width in enumerate(col_widths):
            for cell in table.columns[idx].cells:
                cell.width = width
                tcPr = cell._tc.get_or_add_tcPr()
                no_wraps = tcPr.findall(qn('w:noWrap'))
                for nw in no_wraps:
                    tcPr.remove(nw)

        for row in table.rows:
            row.height = Cm(0.6)
            row.height_rule = WD_ROW_HEIGHT_RULE.AT_LEAST

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        doc.save(self.output_path)
        print(f"文档已保存到 {self.output_path}", file=sys.stderr)
        return missing_fields, missing_optional_fields


def main():
    parser = argparse.ArgumentParser(description='生成确认函（Application Information Sheet）docx')
    parser.add_argument('--input', required=True, help='著录项 JSON 文件路径（case-bibliography-lookup 输出 + parent_applications）')
    parser.add_argument('--output', help='输出 docx 完整路径（指定则覆盖自动命名）')
    parser.add_argument('--output-dir', default='.', help='输出目录，配合自动命名使用（默认当前目录）')
    args = parser.parse_args()

    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            case_info = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"读取输入 JSON 失败: {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        output_path = os.path.abspath(args.output)
    else:
        case_volume = case_info.get('case_volume') or 'UNKNOWN'
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        file_name = f"{current_date}-Application Information Sheet-{case_volume}.docx"
        output_path = os.path.abspath(os.path.join(args.output_dir, file_name))

    try:
        missing_fields, missing_optional_fields = PatentApplicationFormGenerator(case_info, output_path).generate()
    except Exception as e:
        print(f"生成确认函失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps({
        "docx_path": output_path,
        "missing_fields": missing_fields,
        "missing_optional_fields": missing_optional_fields
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
