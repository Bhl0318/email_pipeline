-- 结项 V2 替换草案（仅 close 域）；本文件默认 ROLLBACK，不会实际替换。
-- 无需修改现有表结构：rule_key 最长 128 字符，超长 Excel 匹配键用可读摘要。
-- 结项模板键取 Excel「模板」原文；「无需做」不分配汇报信，只随结项邮件抄送。
-- 「待填模板（仅表头版）」正文来自 待填模板-仅表头版-示例.docx。
-- 本草案先为 Excel 模板名补 report_template 正文，再替换 close 域规则。
-- 正文仍需校对：CN 复审请求旧 MD 措辞有误，部分 US 草稿含固定日期。
-- 地区码取自案号；完整 Excel 原键在规范化草表中；仍需确认 TIP 类型1回退匹配和模板正文。
-- 规则表清理范围：report_rule / report_rule_map / report_rule_template 的 close 域。
-- 不删除或覆盖已有 report_template、report_tasks 或 OA 域数据。
START TRANSACTION;
INSERT INTO report_template (name, content, format, status, remark) SELECT '【106表补正提交】106表补正', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请补正答复**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

针对题述 PCT 申请，我们收到了《PCT/RO/106 表》补正通知，并于 20XX年XX 月 XX进行了补正答复。附件为相关递交文件和官方文件。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_106表补正提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【106表补正提交】106表补正');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【132表补正提交】132表补正', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请补正答复**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

针对题述 PCT 申请，我们收到了《PCT/RO/132 表》补正通知，并于 20XX年XX 月 XX 日进行了补正答复。附件为相关递交文件和官方文件。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_132表补正提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【132表补正提交】132表补正');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【206表补正提交】206表补正', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请补正答复**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

针对题述 PCT 申请，我们收到了PCT/ISA/206表（缴纳附加费和适用时异议费通知），根据贵方的答复指示，我司于20XX年XX月XX日提交了申请人信函。以下为递交相关文件。

1.电子提交收据（Receipt of Electronic Submission）

该收据确认上述国际申请答复已提交至国家知识产权局。

2. 申请人的信函（Letter）

信函指出申请人同意缴纳附加检索费，未提出异议。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_206表补正提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【206表补正提交】206表补正');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【AA答复递交】2026-08-31-美国申请AA答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请Advisory Action答复递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 是否需提交补充信息披露声明（Supplementary Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，根据贵方提供的答复指示，我方已将本次Advisory Action答复文件递交至美国专利商标局（USPTO）。附件为递交的答复文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_AA答复递交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请上诉理由书（Appeal Brief）递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

题述美国申请，根据贵方提供的答复指示，我方已将上诉理由书（Appeal Brief）递交至美国专利商标局（USPTO）。附件为递交的答复文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_AppealBrief提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请Ex Parte Quayle Action答复递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 是否需提交补充信息披露声明（Supplementary Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，根据贵方提供的答复指示，我方已将本次Ex Parte Quayle Action答复文件递交至美国专利商标局（USPTO）。附件为递交的答复文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_ExParteQuayleAction答复递交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【IDS递交】2026-08-31-IDS递交转达', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：IDS递交转达**

|  |  |
| --- | --- |
| 美国专利申请号： | {{申请号}} |
| 美国专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

我方于{{完成日期}}将题述申请的相关文献向美国专利商标局披露。请查收随信附上的递交收据。

递交IDS是一项强制性的披露义务（mandatory duty of disclosure），该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务可能会被视为不正当行为（inequitable conduct），导致整件专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请贵方立即提供给我方，并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_IDS递交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请缴纳授权费**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

题述美国申请，我方已缴纳了授权费，附件为递交的文件及收到的官方文件。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_NOA缴纳授权费_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【OA答复递交】2026-08-31-美国申请OA答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请OA答复递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 是否需提交补充信息披露声明（Supplementary Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，根据贵方提供的答复指示，我方已将本次OA答复文件递交至美国专利商标局（USPTO）。附件为递交的答复文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_OA答复递交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【OA答复递交】中国申请审查意见答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请答复审查意见递交**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 中国专利申请日 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

题述中国申请，根据贵方{{递交日期}}提供的答复指示，我方已于{{完成日期}}将本次审查意见答复文件递交至中国专利局。随附递交的申请文件及收到的官方文件。

如题述中国申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_OA答复递交.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【PPH提交】2026-08-31-PPH递交请求', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请PPH递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，我方已将本次PPH请求文件递交至美国专利商标局（USPTO）。附件为递交的PPH请求文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_PPH提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【RR答复递交】2026-08-31-美国申请RR答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请Requirement for Restriction Election答复递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 是否需提交补充信息披露声明（Supplementary Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，根据贵方提供的答复指示，我方已将本次Requirement for Restriction Election答复文件递交至美国专利商标局（USPTO）。附件为递交的答复文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_RR答复递交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【TD提交】2026-08-31-美国申请TD提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请TD递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，根据贵方提供的答复指示，我方已将本次TD文件递交至美国专利商标局（USPTO）。附件为递交的TD文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_TD提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【临时申请递交】2026-08-31-美国临时申请递交', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国临时专利申请递交**

|  |  |
| --- | --- |
| 临时专利申请号： | {{申请号}} |
| 临时专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |  |
| --- | --- | --- |
| 待完成事项： | 待完成事项： | 递交美国非临时专利申请 |
| 完成期限： | 完成期限： | {{临时申请到期日}} |

尊敬的{{客户名称}}：

题述美国临时专利申请已于{{递交日期}}已向美国专利商标局递交，申请号为{{申请号}}，附件为递交的申请文件及收到的官方文件。

待完成事项

基于该美国临时专利申请递交美国非临时专利申请的期限为{{临时申请到期日}}。

如题述美国临时专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_临时申请递交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【主动撤回】撤回国际申请', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

PRIVILEGED AND CONFIDENTIAL; ATTORNEY CLIENT COMMUNICATION

**关于：撤回国际申请**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

针对题述PCT申请，我方已于20XX年XX 月 XX 日申请撤回，附件为相关递交文件和官方文件。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_撤回申请提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【主动撤回】撤回国际申请');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【主动补正提交】国际申请主动补正', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请补正答复**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

针对题述 PCT 申请，我方已于 2026年XX 月 XX 日将本次补正文件递交至国家知识产权局。附件为相关递交文件和官方文件。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_主动补正提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【主动补正提交】国际申请主动补正');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【变更发明人】2026-08-31-美国申请变更发明人', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请变更发明人**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明<br>（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，我方于 2025 年 01 月 13 日递交了变更发明人的文件。附件为递交的文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_变更发明人_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【变更发明人提交】国际申请变更发明人汇报信', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请变更发明人信息**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

根据贵方指示，我方已于20XX年XX 月 XX向中国受理局递交了题述申请的发明人变更请求，现随函附上我方递交的发明人变更信函及国际局发出的306表格，请贵方存档。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_变更发明人提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【变更实体】2026-08-31-美国申请变更实体', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请变更实体**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 是否需提交补充信息披露声明（Supplementary Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，我方已于2024年10月31日提交了变更实体的请求。附件为递交的文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_变更实体_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请变更申请人、发明人地址信息**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

根据贵方指示，我方已于20XX年XX 月 XX向中国受理局递交了题述申请的申请人、发明人地址变更请求，现随函附上我方递交的申请人、发明人地址变更信函及国际局发出的306表格，请贵方存档。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_变更申请人、发明人地址提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【变更申请人】2026-08-31-美国申请变更申请人', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请变更申请人**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明<br>（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，我方于 2025 年 01 月 13 日递交了变更申请人的文件。附件为递交的文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_变更申请人_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【变更申请人提交】国际申请变更申请人汇报信', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请变更申请人信息**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

根据贵方指示，我方已于20XX年XX 月 XX向中国受理局递交了题述申请的申请人变更请求，现随函附上我方递交的申请人变更信函及国际局发出的306表格，请贵方存档。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_变更申请人提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【复审答复递交】-中国申请复审答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请复审答复递交**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 中国专利申请日 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

题述中国申请，根据贵方{{递交日期}}提供的答复指示，我方已于{{完成日期}}将本次复审答复文件递交至中国专利局。随附递交的申请文件及收到的官方文件。

如题述中国申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_复审答复递交.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【复审请求】中国申请复审请求提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请复审答复递交**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 中国专利申请日 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

题述中国申请，根据贵方{{递交日期}}提供的答复指示，我方已于{{递交日期}}将本次复审答复文件递交至中国专利局。现随附递交的申请文件及收到的官方文件。

如题述中国申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_复审请求.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【复审请求】中国申请复审请求提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【复审阶段优先审查】-中国申请复审优先审查提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请复审优先审查递交**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 中国专利申请日 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

题述中国申请，我方已于{{递交日期}}将本次复审优先审查文件递交至中国专利局。随附递交的申请文件及收到的官方文件。

如题述中国申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_复审阶段优先审查.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【撤回申请】中国申请撤回申请手续合格通知书', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请撤回专利申请提交及手续合格通知书**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 中国专利申请日 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

贵方于{{递交日期}}提供给我方的撤回专利申请文件，我方已于{{递交日期}}向中国专利局递交。以下为递交的申请文件及收到的官方文件。

1. 向中国专利局递交的文件

以下为我方向中国专利局递交文件的清单：

撤回专利申请声明

该文件列出撤回专利申请相关信息。

2. 针对本次文件递交收到的官方通知

电子申请回执

该通知书确认本申请撤回专利文件已提交至中国专利局。该通知书详细列出前述递交文件、递交时间等信息。

手续合格通知书

该通知书指出申请人于{{递交日期}}提出撤回专利申请声明，经审查，符合专利法第32条及其实施细则第36条的规定，同一撤回专利申请。

如题述中国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_撤回申请.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【新申请递交】2026-08-31-美国专利申请递交', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国专利申请递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明<br>（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述专利申请已向美国专利商标局递交，申请号为{{申请号}}。附件为递交的申请文件及收到的官方文件。

待完成事项

信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_新申请递交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【新申请递交】【接口用极简版】-中国新申请提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请递交**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 中国专利申请日 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

题述中国申请已于{{递交日期}}向中国专利局递交，详细申请文件及官方文件后续送达。

如题述中国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_新申请递交_接口用极简版.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【新申请递交】【无代办事项】-国际申请递交事宜', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

PRIVILEGED AND CONFIDENTIAL; ATTORNEY CLIENT COMMUNICATION

**关于：国际申请递交**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

题述PCT申请已于20XX年XX月XX日向国家知识产权局提交，国际申请号为{{申请号}}，以下为递交相关文件。

1.电子提交收据（Receipt of Electronic Submission）

该收据确认上述国际申请已于20XX年XX月XX日提交至国家知识产权局，并被分配上述申请号。

2. PCT请求书（PCT Request）

PCT请求书中指出上述国际申请的申请人、发明人及优先权等信息。

3.费用清单（Fee Transmittal）

费用清单里列出了收费项目及总额。

4.专利申请文件（Patent Application）

该文件是最终提交的专利申请文件，包括说明书和附图部分。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_新申请递交_无代办事项_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【申请人更名】2026-08-31-美国申请申请人更名', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请申请人更名**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明<br>（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，我方于 2025 年 01 月 13 日递交了申请人更名的文件。附件为递交的文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_申请人更名_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【申请人更名提交】国际申请申请人更名提交汇报信', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：国际申请申请人更名信息**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

根据贵方指示，我方已于20XX年XX 月 XX向中国受理局递交了题述申请的申请人更名请求，现随函附上我方递交的申请人更名信函及国际局发出的306表格，请贵方存档。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_申请人更名提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【翻译提交】2026-08-31-美国申请翻译文件递交', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国专利申请翻译文件递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明<br>（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述专利申请已向美国专利商标局递交，现补交了英文翻译文件。附件为本次递交的英文翻译文件及其他相关文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_翻译提交_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【补交DAS码】国际申请补交DAS码', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

PRIVILEGED AND CONFIDENTIAL; ATTORNEY CLIENT COMMUNICATION

**关于：补交DAS码**

|  |  |
| --- | --- |
| 申请号： | {{申请号}} |
| 申请名称： | {{申请名称}} |
| 申请日： | {{申请日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

尊敬的{{客户名称}}：

针对题述PCT申请，我方已于20XX年XX月XX日补交了DAS码，DAS码为XXXX，附件为相关递交文件。

如题述PCT申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

众慧优创
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/PCT_补交DAS码_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【补交DAS码】国际申请补交DAS码');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【补交Declaration】2026-08-31-美国申请补交Declaration转达', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：补交Declaration**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |
| 待完成事项： | 递交信息披露声明（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，我方已于{{完成日期}}向美国专利商标局补交Declaration。附件为递交的发明人签署的誓言及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_补交Declaration_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【补交POA】2026-08-31-美国申请补交POA', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请补交 POA**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 是否需提交补充信息披露声明（Supplementary Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，我方已将 POA 文件成功递交至美国专利商标局（USPTO）。 附件为递交的 POA 文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_补交POA_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【补正答复】2026-08-31-美国申请补正答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请补正答复递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 是否需提交补充信息披露声明（Supplementary Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述美国申请，根据贵方提供的答复指示，我方已将本次补正答复文件递交至美国专利商标局（USPTO）。附件为递交的答复文件及收到的官方文件。

待完成事项

补充信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本案申请的可专利性有重要关联（material to patentability）的文献资料，必须以Information Disclosure Statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a)	发明人/申请人/代理人已知的相关文献；

b)	发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）；

c)	如果有除美国之外的国家或地区的与本案申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见。

如果存在上述文献，请贵司整理之后提供给我方，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/US_补正答复_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【补正递交】-中国申请补正答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请补正答复递交**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 进入中国国家阶段日期 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

题述中国申请，根据贵方{{递交日期}}提供的答复指示，我方已于{{完成日期}}将本次补正答复文件递交至中国专利局。随附递交的申请文件及收到的官方文件。

如题述中国申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_补正递交.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：中国申请答复视为未要求通知书递交**

|  |  |
|------|-----|
| 中国专利申请号 | {{申请号}} |
| 中国专利申请名称 | {{申请名称}} |
| 进入中国国家阶段日期 | {{申请日}} |
| 委托方案号 | {{客户案号}} |
| 代理所案号 | {{代理所案号}} |

---

尊敬的{{客户名称}}：

题述中国申请，根据贵方{{递交日期}}提供的答复指示，我方已于{{完成日期}}将本次视为未要求通知书答复文件递交至中国专利局。随附递交的申请文件及收到的官方文件。

如题述中国申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

如您对此案有流程方面的疑问，请联系{{联系人}}，电子邮件：{{联系人邮箱}}，手机：{{联系人手机}}。

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候
{{签名品牌}}
', 'md', 1, '结项V2；来源 scripts/templates/md/结项通知/CN_视为未要求优先权提交.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_template (name, content, format, status, remark) SELECT '待填模板（仅表头版）', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{递交日期}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 待填 |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

关于题述申请，正文事项需要自己编辑

对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, '结项V2；来源 outputs/结项V2模板草稿/结项_待填模板_V2.md；待校对' WHERE NOT EXISTS (SELECT 1 FROM report_template WHERE name='待填模板（仅表头版）');
DELETE FROM report_rule WHERE rule_domain='close';
DELETE FROM report_rule_map WHERE rule_domain='close';
DELETE FROM report_rule_template WHERE rule_domain='close';
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '新申请递交', '【新申请递交】【接口用极简版】-中国新申请提交报告', 0, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '新申请递交', '新申请递交', 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '新申请递交', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '新申请递交', '【新申请递交】【接口用极简版】-中国新申请提交报告', 0, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '新申请递交', '新申请递交', 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '新申请递交', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '新申请递交', '【新申请递交】【接口用极简版】-中国新申请提交报告', 0, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '新申请递交', '新申请递交', 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '新申请递交', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第2行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', 'PCT落地', '【新申请递交】【接口用极简版】-中国新申请提交报告', 0, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'PCT落地', 'PCT落地', 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'PCT落地', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', 'PCT落地', '【新申请递交】【接口用极简版】-中国新申请提交报告', 0, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'PCT落地', 'PCT落地', 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'PCT落地', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', 'PCT落地', '【新申请递交】【接口用极简版】-中国新申请提交报告', 0, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'PCT落地', 'PCT落地', 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'PCT落地', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第3行；【新申请递交】【接口用极简版】-中国新申请提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '【OA答复递交】中国申请审查意见答复提交报告', 0, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_第一次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_第二次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_第三次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_第四次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_第五次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_第一次答复-预审', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_第二次答复-预审', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '【OA答复递交】中国申请审查意见答复提交报告', 0, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_第一次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_第二次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_第三次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_第四次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_第五次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_第一次答复-预审', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_第二次答复-预审', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '【OA答复递交】中国申请审查意见答复提交报告', 0, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_第一次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_第二次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_第三次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_第四次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_第五次答复', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_第一次答复-预审', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_第二次答复-预审', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜第一次答复, 第二次答复, 第三次答复, 第四次答复, 第五次答复, 第一次答复-预审, 第二次答复-预审', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第4行；【OA答复递交】中国申请审查意见答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '【复审请求】中国申请复审请求提交报告', 0, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_驳回复审请求', 'OA答复｜驳回复审请求', 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜驳回复审请求', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '【复审请求】中国申请复审请求提交报告', 0, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_驳回复审请求', 'OA答复｜驳回复审请求', 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜驳回复审请求', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '【复审请求】中国申请复审请求提交报告', 0, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_驳回复审请求', 'OA答复｜驳回复审请求', 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜驳回复审请求', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第5行；【复审请求】中国申请复审请求提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '【复审答复递交】-中国申请复审答复提交报告', 0, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_复审答复', 'OA答复｜复审答复', 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜复审答复', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '【复审答复递交】-中国申请复审答复提交报告', 0, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_复审答复', 'OA答复｜复审答复', 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜复审答复', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '【复审答复递交】-中国申请复审答复提交报告', 0, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_复审答复', 'OA答复｜复审答复', 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜复审答复', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第6行；【复审答复递交】-中国申请复审答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', 'OA答复_口审答复', 'OA答复｜口审答复', 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', 'OA答复｜口审答复', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', 'OA答复_口审答复', 'OA答复｜口审答复', 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', 'OA答复｜口审答复', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', 'OA答复_口审答复', 'OA答复｜口审答复', 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', 'OA答复｜口审答复', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '补正', '【补正递交】-中国申请补正答复提交报告', 0, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '补正', '补正', 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '补正', '【补正递交】-中国申请补正答复提交报告', 0, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '补正', '补正', 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '补正', '【补正递交】-中国申请补正答复提交报告', 0, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '补正', '补正', 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第8行；【补正递交】-中国申请补正答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '著录项目', '', 0, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '著录项目', '著录项目', 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20615', 'skip', '', '["report@metis-ip.com"]', '["mei.hu@metis-ip.com"]', 2, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '著录项目', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '著录项目', '', 0, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '著录项目', '著录项目', 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20615', 'skip', '', '["report@metis-ip.com"]', '["mei.hu@metis-ip.com"]', 2, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '著录项目', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '著录项目', '', 0, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '著录项目', '著录项目', 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20615', 'skip', '', '["report@metis-ip.com"]', '["mei.hu@metis-ip.com"]', 2, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '著录项目', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第9行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '缴费', '', 0, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '缴费', '缴费', 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '缴费', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '缴费', '', 0, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '缴费', '缴费', 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '缴费', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '缴费', '', 0, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '缴费', '缴费', 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '缴费', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第10行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', 0, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '补正_内部项目结项', 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20615', 'skip', '', '["report@metis-ip.com"]', '["mei.hu@metis-ip.com"]', 2, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '补正_内部项目结项', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', 0, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '补正_内部项目结项', 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20615', 'skip', '', '["report@metis-ip.com"]', '["mei.hu@metis-ip.com"]', 2, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '补正_内部项目结项', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', 0, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '补正_内部项目结项', 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20615', 'skip', '', '["report@metis-ip.com"]', '["mei.hu@metis-ip.com"]', 2, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '补正_内部项目结项', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第11行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', 0, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_DAS交存', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_费用减缴请求', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_实审请求', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_请款退费', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_优先审查', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', 0, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_DAS交存', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_费用减缴请求', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_实审请求', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_请款退费', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_优先审查', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', 0, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_DAS交存', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_费用减缴请求', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_实审请求', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_请款退费', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_优先审查', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜DAS交存, 费用减缴请求, 实审请求, 请款退费, 优先审查', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第12行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_PPH提交', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_申请保密审查', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_主动修改', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_撤回提前公开', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_提前公开', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_恢复权利请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_延长期限请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_提交优先权副本', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_单一性恢复费', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_复审口审回执', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_复审口审补交证据', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_非正常案件申诉', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_分案通知书答复', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_分案申请视为未提出', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_行政复议请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_登记财政资助专利声明', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_专利权期限补偿请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜PPH提交等17项', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_PPH提交', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_申请保密审查', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_主动修改', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_撤回提前公开', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_提前公开', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_恢复权利请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_延长期限请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_提交优先权副本', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_单一性恢复费', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_复审口审回执', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_复审口审补交证据', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_非正常案件申诉', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_分案通知书答复', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_分案申请视为未提出', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_行政复议请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_登记财政资助专利声明', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_专利权期限补偿请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜PPH提交等17项', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_PPH提交', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_申请保密审查', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_主动修改', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_撤回提前公开', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_提前公开', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_恢复权利请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_延长期限请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_提交优先权副本', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_单一性恢复费', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_复审口审回执', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_复审口审补交证据', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_非正常案件申诉', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_分案通知书答复', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_分案申请视为未提出', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_行政复议请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_登记财政资助专利声明', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_专利权期限补偿请求', '其他｜PPH提交等17项', 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜PPH提交等17项', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第13行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '【撤回申请】中国申请撤回申请手续合格通知书', 0, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_撤回申请', '其他｜撤回申请', 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜撤回申请', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '【撤回申请】中国申请撤回申请手续合格通知书', 0, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_撤回申请', '其他｜撤回申请', 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜撤回申请', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '【撤回申请】中国申请撤回申请手续合格通知书', 0, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_撤回申请', '其他｜撤回申请', 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜撤回申请', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第14行；【撤回申请】中国申请撤回申请手续合格通知书');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告', 0, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_答复视为未要求优先权', '其他｜答复视为未要求优先权', 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜答复视为未要求优先权', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告', 0, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_答复视为未要求优先权', '其他｜答复视为未要求优先权', 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜答复视为未要求优先权', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告', 0, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_答复视为未要求优先权', '其他｜答复视为未要求优先权', 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜答复视为未要求优先权', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第15行；【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '【复审阶段优先审查】-中国申请复审优先审查提交报告', 0, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '其他_复审优先审查', '其他｜复审优先审查', 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '其他｜复审优先审查', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '【复审阶段优先审查】-中国申请复审优先审查提交报告', 0, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '其他_复审优先审查', '其他｜复审优先审查', 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '其他｜复审优先审查', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '【复审阶段优先审查】-中国申请复审优先审查提交报告', 0, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '其他_复审优先审查', '其他｜复审优先审查', 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '其他｜复审优先审查', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第16行；【复审阶段优先审查】-中国申请复审优先审查提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', 0, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_费减备案', '事务办理｜费减备案, 总委备案', 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_总委备案', '事务办理｜费减备案, 总委备案', 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜费减备案, 总委备案', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', 0, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_费减备案', '事务办理｜费减备案, 总委备案', 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_总委备案', '事务办理｜费减备案, 总委备案', 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜费减备案, 总委备案', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', 0, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_费减备案', '事务办理｜费减备案, 总委备案', 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_总委备案', '事务办理｜费减备案, 总委备案', 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20615', 'skip', '', '["mei.hu@metis-ip.com"]', '[]', 2, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜费减备案, 总委备案', '', '其他', 'ignore', '', '', '', 9, 1, 'V2 结项通知-CN 第17行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_办理文件副本', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_直接提交保密审查请求', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_递交US保密审查', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_专利权评估报告', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_专利文档查询复制', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_中止请求', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_办理专利登记簿副本', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CN', '事务办理_办理专利说明书', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CN', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_办理文件副本', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_直接提交保密审查请求', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_递交US保密审查', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_专利权评估报告', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_专利文档查询复制', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_中止请求', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_办理专利登记簿副本', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CM', '事务办理_办理专利说明书', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CM', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_办理文件副本', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_直接提交保密审查请求', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_递交US保密审查', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_专利权评估报告', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_专利文档查询复制', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_中止请求', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_办理专利登记簿副本', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'CS', '事务办理_办理专利说明书', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20615', 'assign', 'mei.hu@metis-ip.com', '', '', 2, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20608', 'ignore', '', '', '', 3, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20963', 'skip', '', '["mei.hu@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 5, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20735', 'ignore', '', '', '', 6, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 7, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '5开头', 'ignore', '', '', '', 8, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'CS', '事务办理｜办理文件副本, 直接提交保密审查请求, 递交US保密审查, 专利权评估报告, 专利文档查询复制, 中止请求, 办理专利登记簿副本, 办理专利说明书', '', '其他', 'assign', 'hui.ren@metis-ip.com', '', '', 9, 1, 'V2 结项通知-CN 第18行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '新申请递交｜临时申请', '【临时申请递交】2026-08-31-美国临时申请递交', 0, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '新申请递交_临时申请', '新申请递交｜临时申请', 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜临时申请', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜临时申请', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜临时申请', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜临时申请', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜临时申请', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜临时申请', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '新申请递交｜临时申请', '【临时申请递交】2026-08-31-美国临时申请递交', 0, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '新申请递交_临时申请', '新申请递交｜临时申请', 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜临时申请', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜临时申请', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜临时申请', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜临时申请', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜临时申请', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜临时申请', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'PR', '新申请递交｜临时申请', '【临时申请递交】2026-08-31-美国临时申请递交', 0, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '新申请递交_临时申请', '新申请递交｜临时申请', 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜临时申请', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜临时申请', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜临时申请', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜临时申请', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜临时申请', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜临时申请', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第2行；【临时申请递交】2026-08-31-美国临时申请递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '【新申请递交】2026-08-31-美国专利申请递交', 0, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '新申请递交_新申请发明', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '新申请递交_新申请外观', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '新申请递交_PCT落地', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '新申请递交_发明-巴黎公约', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '新申请递交_外观-巴黎公约', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '新申请递交_续案/分案/部分续案', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '【新申请递交】2026-08-31-美国专利申请递交', 0, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '新申请递交_新申请发明', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '新申请递交_新申请外观', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '新申请递交_PCT落地', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '新申请递交_发明-巴黎公约', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '新申请递交_外观-巴黎公约', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '新申请递交_续案/分案/部分续案', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'PR', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '【新申请递交】2026-08-31-美国专利申请递交', 0, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '新申请递交_新申请发明', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '新申请递交_新申请外观', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '新申请递交_PCT落地', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '新申请递交_发明-巴黎公约', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '新申请递交_外观-巴黎公约', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '新申请递交_续案/分案/部分续案', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', '新申请递交｜新申请发明, 新申请外观, PCT落地, 发明-巴黎公约, 外观-巴黎公约, 续案/分案/部分续案', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第3行；【新申请递交】2026-08-31-美国专利申请递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'OA答复｜Non-final, Final', '【OA答复递交】2026-08-31-美国申请OA答复提交报告', 0, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'OA答复_Non-final', 'OA答复｜Non-final, Final', 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'OA答复_Final', 'OA答复｜Non-final, Final', 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Non-final, Final', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Non-final, Final', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Non-final, Final', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Non-final, Final', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Non-final, Final', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Non-final, Final', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'OA答复｜Non-final, Final', '【OA答复递交】2026-08-31-美国申请OA答复提交报告', 0, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'OA答复_Non-final', 'OA答复｜Non-final, Final', 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'OA答复_Final', 'OA答复｜Non-final, Final', 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Non-final, Final', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Non-final, Final', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Non-final, Final', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Non-final, Final', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Non-final, Final', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Non-final, Final', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第4行；【OA答复递交】2026-08-31-美国申请OA答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'OA答复｜AA', '【AA答复递交】2026-08-31-美国申请AA答复提交报告', 0, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'OA答复_AA', 'OA答复｜AA', 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜AA', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜AA', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜AA', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜AA', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜AA', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜AA', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'OA答复｜AA', '【AA答复递交】2026-08-31-美国申请AA答复提交报告', 0, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'OA答复_AA', 'OA答复｜AA', 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜AA', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜AA', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜AA', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜AA', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜AA', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜AA', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第5行；【AA答复递交】2026-08-31-美国申请AA答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'OA答复｜RR', '【RR答复递交】2026-08-31-美国申请RR答复提交报告', 0, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'OA答复_RR', 'OA答复｜RR', 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'OA答复｜RR', '【RR答复递交】2026-08-31-美国申请RR答复提交报告', 0, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'OA答复_RR', 'OA答复｜RR', 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第6行；【RR答复递交】2026-08-31-美国申请RR答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'OA答复｜RR Petition', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'OA答复_RR Petition', 'OA答复｜RR Petition', 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR Petition', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR Petition', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR Petition', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR Petition', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR Petition', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜RR Petition', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'OA答复｜RR Petition', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'OA答复_RR Petition', 'OA答复｜RR Petition', 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR Petition', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR Petition', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR Petition', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR Petition', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR Petition', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜RR Petition', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第7行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'OA答复｜Ex Parte Quayle Action', '【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告', 0, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'OA答复_Ex Parte Quayle Action', 'OA答复｜Ex Parte Quayle Action', 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Ex Parte Quayle Action', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Ex Parte Quayle Action', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Ex Parte Quayle Action', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Ex Parte Quayle Action', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Ex Parte Quayle Action', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'OA答复｜Ex Parte Quayle Action', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'OA答复｜Ex Parte Quayle Action', '【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告', 0, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'OA答复_Ex Parte Quayle Action', 'OA答复｜Ex Parte Quayle Action', 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Ex Parte Quayle Action', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Ex Parte Quayle Action', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Ex Parte Quayle Action', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Ex Parte Quayle Action', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Ex Parte Quayle Action', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'OA答复｜Ex Parte Quayle Action', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第8行；【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'IDS', '【IDS递交】2026-08-31-IDS递交转达', 0, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'IDS', 'IDS', 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'IDS', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'IDS', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'IDS', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'IDS', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'IDS', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'IDS', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'IDS', '【IDS递交】2026-08-31-IDS递交转达', 0, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'IDS', 'IDS', 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'IDS', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'IDS', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'IDS', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'IDS', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'IDS', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'IDS', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第9行；【IDS递交】2026-08-31-IDS递交转达');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'NOA', '【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费', 0, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'NOA', 'NOA', 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'NOA', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'NOA', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'NOA', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'NOA', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'NOA', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'NOA', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'NOA', '【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费', 0, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'NOA', 'NOA', 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'NOA', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'NOA', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'NOA', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'NOA', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'NOA', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'NOA', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第10行；【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '补正', '【补正答复】2026-08-31-美国申请补正答复提交报告', 0, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '补正', '补正', 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '补正', '【补正答复】2026-08-31-美国申请补正答复提交报告', 0, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '补正', '补正', 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第11行；【补正答复】2026-08-31-美国申请补正答复提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '著录项目｜变更申请人', '【变更申请人】2026-08-31-美国申请变更申请人', 0, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '著录项目_变更申请人', '著录项目｜变更申请人', 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更申请人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更申请人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更申请人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更申请人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更申请人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更申请人', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '著录项目｜变更申请人', '【变更申请人】2026-08-31-美国申请变更申请人', 0, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '著录项目_变更申请人', '著录项目｜变更申请人', 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更申请人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更申请人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更申请人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更申请人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更申请人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更申请人', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第12行；【变更申请人】2026-08-31-美国申请变更申请人');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '著录项目｜申请人更名', '【申请人更名】2026-08-31-美国申请申请人更名', 0, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '著录项目_申请人更名', '著录项目｜申请人更名', 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜申请人更名', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜申请人更名', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜申请人更名', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜申请人更名', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜申请人更名', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜申请人更名', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '著录项目｜申请人更名', '【申请人更名】2026-08-31-美国申请申请人更名', 0, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '著录项目_申请人更名', '著录项目｜申请人更名', 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜申请人更名', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜申请人更名', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜申请人更名', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜申请人更名', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜申请人更名', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜申请人更名', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第13行；【申请人更名】2026-08-31-美国申请申请人更名');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '著录项目｜变更发明人', '【变更发明人】2026-08-31-美国申请变更发明人', 0, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '著录项目_变更发明人', '著录项目｜变更发明人', 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更发明人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更发明人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更发明人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更发明人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更发明人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜变更发明人', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '著录项目｜变更发明人', '【变更发明人】2026-08-31-美国申请变更发明人', 0, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '著录项目_变更发明人', '著录项目｜变更发明人', 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更发明人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更发明人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更发明人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更发明人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更发明人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜变更发明人', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第14行；【变更发明人】2026-08-31-美国申请变更发明人');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '著录项目｜POA递交/变更代理机构', '【补交POA】2026-08-31-美国申请补交POA', 0, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '著录项目_POA递交/变更代理机构', '著录项目｜POA递交/变更代理机构', 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜POA递交/变更代理机构', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜POA递交/变更代理机构', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜POA递交/变更代理机构', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜POA递交/变更代理机构', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜POA递交/变更代理机构', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '著录项目｜POA递交/变更代理机构', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '著录项目｜POA递交/变更代理机构', '【补交POA】2026-08-31-美国申请补交POA', 0, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '著录项目_POA递交/变更代理机构', '著录项目｜POA递交/变更代理机构', 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜POA递交/变更代理机构', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜POA递交/变更代理机构', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜POA递交/变更代理机构', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜POA递交/变更代理机构', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜POA递交/变更代理机构', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '著录项目｜POA递交/变更代理机构', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第15行；【补交POA】2026-08-31-美国申请补交POA');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '其他递交｜DAS/优先权副本递交等13项', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_DAS/优先权副本递交', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_递交US保密审查', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_递交CN保密审查', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_Preliminary Amendment递交', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_Amendment after NOA', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_petition for revival(复活)', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_Petition to restore恢复优先权', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_请求撤案', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_提交公众意见', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_递交confirmation', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_变更发明人/申请人地址', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_Streamlined Claim Set Pilot', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_RFI_PIER_Pilot答复', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜DAS/优先权副本递交等13项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜DAS/优先权副本递交等13项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜DAS/优先权副本递交等13项', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜DAS/优先权副本递交等13项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜DAS/优先权副本递交等13项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜DAS/优先权副本递交等13项', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '其他递交｜DAS/优先权副本递交等13项', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_DAS/优先权副本递交', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_递交US保密审查', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_递交CN保密审查', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_Preliminary Amendment递交', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_Amendment after NOA', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_petition for revival(复活)', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_Petition to restore恢复优先权', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_请求撤案', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_提交公众意见', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_递交confirmation', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_变更发明人/申请人地址', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_Streamlined Claim Set Pilot', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_RFI_PIER_Pilot答复', '其他递交｜DAS/优先权副本递交等13项', 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜DAS/优先权副本递交等13项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜DAS/优先权副本递交等13项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜DAS/优先权副本递交等13项', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜DAS/优先权副本递交等13项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜DAS/优先权副本递交等13项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜DAS/优先权副本递交等13项', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第16行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', 0, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_Assignment登记', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_request for refund(退款)', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_补缴费用/只缴费用', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_递交439表', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_咨询案件进展', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_购买申请副本', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_案件排查', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_递交Interview request', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', 0, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_Assignment登记', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_request for refund(退款)', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_补缴费用/只缴费用', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_递交439表', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_咨询案件进展', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_购买申请副本', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_案件排查', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_递交Interview request', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Assignment登记, request for refund(退款), 补缴费用/只缴费用, 递交439表, 咨询案件进展, 购买申请副本, 案件排查, 递交Interview request', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-US 第17行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '其他递交｜Declaration递交', '【补交Declaration】2026-08-31-美国申请补交Declaration转达', 0, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_Declaration递交', '其他递交｜Declaration递交', 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Declaration递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Declaration递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Declaration递交', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Declaration递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Declaration递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜Declaration递交', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '其他递交｜Declaration递交', '【补交Declaration】2026-08-31-美国申请补交Declaration转达', 0, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_Declaration递交', '其他递交｜Declaration递交', 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Declaration递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Declaration递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Declaration递交', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Declaration递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Declaration递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜Declaration递交', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第18行；【补交Declaration】2026-08-31-美国申请补交Declaration转达');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '其他递交｜变更实体', '【变更实体】2026-08-31-美国申请变更实体', 0, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_变更实体', '其他递交｜变更实体', 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜变更实体', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜变更实体', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜变更实体', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜变更实体', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜变更实体', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜变更实体', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '其他递交｜变更实体', '【变更实体】2026-08-31-美国申请变更实体', 0, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_变更实体', '其他递交｜变更实体', 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜变更实体', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜变更实体', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜变更实体', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜变更实体', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜变更实体', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜变更实体', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第19行；【变更实体】2026-08-31-美国申请变更实体');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '其他递交｜补交翻译稿', '【翻译提交】2026-08-31-美国申请翻译文件递交', 0, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_补交翻译稿', '其他递交｜补交翻译稿', 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜补交翻译稿', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜补交翻译稿', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜补交翻译稿', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜补交翻译稿', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜补交翻译稿', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜补交翻译稿', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '其他递交｜补交翻译稿', '【翻译提交】2026-08-31-美国申请翻译文件递交', 0, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_补交翻译稿', '其他递交｜补交翻译稿', 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜补交翻译稿', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜补交翻译稿', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜补交翻译稿', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜补交翻译稿', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜补交翻译稿', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜补交翻译稿', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第20行；【翻译提交】2026-08-31-美国申请翻译文件递交');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '其他递交｜TD', '【TD提交】2026-08-31-美国申请TD提交报告', 0, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_TD', '其他递交｜TD', 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜TD', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜TD', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜TD', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜TD', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜TD', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜TD', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '其他递交｜TD', '【TD提交】2026-08-31-美国申请TD提交报告', 0, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_TD', '其他递交｜TD', 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜TD', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜TD', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜TD', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜TD', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜TD', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜TD', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第21行；【TD提交】2026-08-31-美国申请TD提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '其他递交｜PPH', '【PPH提交】2026-08-31-PPH递交请求', 0, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '其他递交_PPH', '其他递交｜PPH', 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜PPH', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜PPH', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜PPH', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜PPH', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜PPH', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '其他递交｜PPH', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '其他递交｜PPH', '【PPH提交】2026-08-31-PPH递交请求', 0, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '其他递交_PPH', '其他递交｜PPH', 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜PPH', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜PPH', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜PPH', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜PPH', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜PPH', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '其他递交｜PPH', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第22行；【PPH提交】2026-08-31-PPH递交请求');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'Appeal递交｜递交Appeal Brief', '【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告', 0, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'Appeal递交_递交Appeal Brief', 'Appeal递交｜递交Appeal Brief', 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜递交Appeal Brief', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜递交Appeal Brief', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜递交Appeal Brief', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜递交Appeal Brief', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜递交Appeal Brief', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜递交Appeal Brief', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'Appeal递交｜递交Appeal Brief', '【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告', 0, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'Appeal递交_递交Appeal Brief', 'Appeal递交｜递交Appeal Brief', 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜递交Appeal Brief', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜递交Appeal Brief', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜递交Appeal Brief', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜递交Appeal Brief', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜递交Appeal Brief', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜递交Appeal Brief', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第23行；【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'Appeal递交_提交Notice of Appeal', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'Appeal递交_缴纳Appeal forwarding Fee', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', 'Appeal递交_答复Patent Board Decision', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'Appeal递交_提交Notice of Appeal', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'Appeal递交_缴纳Appeal forwarding Fee', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', 'Appeal递交_答复Patent Board Decision', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', 'Appeal递交｜提交Notice of Appeal, 缴纳Appeal forwarding Fee, 答复Patent Board Decision', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第24行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '', 0, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '补正_内部项目结项', 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '补正_内部项目结项', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '', 0, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '补正_内部项目结项', 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '补正_内部项目结项', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-US 第25行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '年费', '', 0, 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '年费', '年费', 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '年费', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '年费', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '年费', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '年费', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '年费', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '年费', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-US 第26行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'US', '附加', '', 0, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'US', '附加', '附加', 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '附加', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '附加', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '附加', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '附加', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '附加', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'US', '附加', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DS', '附加', '', 0, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DS', '附加', '附加', 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '附加', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '附加', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '附加', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '附加', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '附加', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DS', '附加', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-US 第27行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'PR', 'PR｜其他递交', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'PR', '其他递交', 'PR｜其他递交', 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', 'PR｜其他递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', 'PR｜其他递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', 'PR｜其他递交', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', 'PR｜其他递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', 'PR｜其他递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'PR', 'PR｜其他递交', '', '其他', 'assign', 'zhuqing.sun@metis-ip.com', '', '', 5, 1, 'V2 结项通知-US 第28行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '新申请递交｜PCT新申请递交', '【新申请递交】【无代办事项】-国际申请递交事宜', 0, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '新申请递交_PCT新申请递交', '新申请递交｜PCT新申请递交', 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜PCT新申请递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜PCT新申请递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜PCT新申请递交', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜PCT新申请递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜PCT新申请递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜PCT新申请递交', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '新申请递交｜PCT新申请递交', '【新申请递交】【无代办事项】-国际申请递交事宜', 0, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '新申请递交_PCT新申请递交', '新申请递交｜PCT新申请递交', 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜PCT新申请递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜PCT新申请递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜PCT新申请递交', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜PCT新申请递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜PCT新申请递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜PCT新申请递交', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第2行；【新申请递交】【无代办事项】-国际申请递交事宜');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '新申请递交｜海牙协定新申请递交', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '新申请递交_海牙协定新申请递交', '新申请递交｜海牙协定新申请递交', 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜海牙协定新申请递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜海牙协定新申请递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜海牙协定新申请递交', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜海牙协定新申请递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜海牙协定新申请递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '新申请递交｜海牙协定新申请递交', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '新申请递交｜海牙协定新申请递交', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '新申请递交_海牙协定新申请递交', '新申请递交｜海牙协定新申请递交', 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜海牙协定新申请递交', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜海牙协定新申请递交', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜海牙协定新申请递交', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜海牙协定新申请递交', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜海牙协定新申请递交', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '新申请递交｜海牙协定新申请递交', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第3行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '补正｜补交POA', '', 0, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_补交POA', '补正｜补交POA', 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交POA', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交POA', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交POA', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交POA', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交POA', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交POA', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '补正｜补交POA', '', 0, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_补交POA', '补正｜补交POA', 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交POA', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交POA', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交POA', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交POA', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交POA', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交POA', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-PCT 第4行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '补正｜补交DAS码', '【补交DAS码】国际申请补交DAS码', 0, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_补交DAS码', '补正｜补交DAS码', 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交DAS码', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交DAS码', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交DAS码', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交DAS码', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交DAS码', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补交DAS码', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '补正｜补交DAS码', '【补交DAS码】国际申请补交DAS码', 0, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_补交DAS码', '补正｜补交DAS码', 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交DAS码', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交DAS码', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交DAS码', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交DAS码', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交DAS码', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补交DAS码', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第5行；【补交DAS码】国际申请补交DAS码');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '【106表补正提交】106表补正', 0, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_106表-补正权利要求', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_106表-补正说明书附图', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_106表-申请人及发明人地址', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '【106表补正提交】106表补正', 0, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_106表-补正权利要求', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_106表-补正说明书附图', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_106表-申请人及发明人地址', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜106表-补正权利要求, 106表-补正说明书附图, 106表-申请人及发明人地址', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第6行；【106表补正提交】106表补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '【132表补正提交】132表补正', 0, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_132表-补正权利要求书', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_132表-补正申请人及发明人地址', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '【132表补正提交】132表补正', 0, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_132表-补正权利要求书', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_132表-补正申请人及发明人地址', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜132表-补正权利要求书, 132表-补正申请人及发明人地址', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第7行；【132表补正提交】132表补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '补正｜补正发明名称, 19条修改, 34条修改', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_补正发明名称', '补正｜补正发明名称, 19条修改, 34条修改', 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_19条修改', '补正｜补正发明名称, 19条修改, 34条修改', 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_34条修改', '补正｜补正发明名称, 19条修改, 34条修改', 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补正发明名称, 19条修改, 34条修改', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补正发明名称, 19条修改, 34条修改', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补正发明名称, 19条修改, 34条修改', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补正发明名称, 19条修改, 34条修改', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补正发明名称, 19条修改, 34条修改', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜补正发明名称, 19条修改, 34条修改', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '补正｜补正发明名称, 19条修改, 34条修改', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_补正发明名称', '补正｜补正发明名称, 19条修改, 34条修改', 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_19条修改', '补正｜补正发明名称, 19条修改, 34条修改', 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_34条修改', '补正｜补正发明名称, 19条修改, 34条修改', 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补正发明名称, 19条修改, 34条修改', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补正发明名称, 19条修改, 34条修改', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补正发明名称, 19条修改, 34条修改', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补正发明名称, 19条修改, 34条修改', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补正发明名称, 19条修改, 34条修改', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜补正发明名称, 19条修改, 34条修改', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第8行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '补正｜主动补正权利要求', '【主动补正提交】国际申请主动补正', 0, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '补正_主动补正权利要求', '补正｜主动补正权利要求', 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜主动补正权利要求', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜主动补正权利要求', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜主动补正权利要求', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜主动补正权利要求', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜主动补正权利要求', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '补正｜主动补正权利要求', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '补正｜主动补正权利要求', '【主动补正提交】国际申请主动补正', 0, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '补正_主动补正权利要求', '补正｜主动补正权利要求', 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜主动补正权利要求', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜主动补正权利要求', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜主动补正权利要求', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜主动补正权利要求', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜主动补正权利要求', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '补正｜主动补正权利要求', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第9行；【主动补正提交】国际申请主动补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_请求纸质优先权副本', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_DAS请求', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_办理优先权文件副本', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_递交US保密审查', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_递交海外其他保密审查', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '待填模板（仅表头版）', 0, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_请求纸质优先权副本', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_DAS请求', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_办理优先权文件副本', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_递交US保密审查', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_递交海外其他保密审查', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜请求纸质优先权副本, DAS请求, 办理优先权文件副本, 递交US保密审查, 递交海外其他保密审查', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第10行；待填模板（仅表头版）');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '其他｜主动撤回', '【主动撤回】撤回国际申请', 0, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_主动撤回', '其他｜主动撤回', 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜主动撤回', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜主动撤回', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜主动撤回', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜主动撤回', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜主动撤回', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜主动撤回', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '其他｜主动撤回', '【主动撤回】撤回国际申请', 0, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_主动撤回', '其他｜主动撤回', 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜主动撤回', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜主动撤回', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜主动撤回', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜主动撤回', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜主动撤回', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜主动撤回', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第11行；【主动撤回】撤回国际申请');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', 0, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_缴纳优先权要求费', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_缴纳申请费', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_缴费', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', 0, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_缴纳优先权要求费', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_缴纳申请费', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_缴费', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜缴纳优先权要求费, 缴纳申请费, 缴费', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-PCT 第12行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '其他｜答复206表', '【206表补正提交】206表补正', 0, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '其他_答复206表', '其他｜答复206表', 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜答复206表', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜答复206表', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜答复206表', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜答复206表', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜答复206表', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '其他｜答复206表', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '其他｜答复206表', '【206表补正提交】206表补正', 0, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '其他_答复206表', '其他｜答复206表', 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜答复206表', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜答复206表', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜答复206表', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜答复206表', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜答复206表', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '其他｜答复206表', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第13行；【206表补正提交】206表补正');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人', '【变更申请人提交】国际申请变更申请人汇报信', 0, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '著录项目_变更申请人', '著录项目｜变更申请人', 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人', '【变更申请人提交】国际申请变更申请人汇报信', 0, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '著录项目_变更申请人', '著录项目｜变更申请人', 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第14行；【变更申请人提交】国际申请变更申请人汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '著录项目｜申请人更名', '【申请人更名提交】国际申请申请人更名提交汇报信', 0, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '著录项目_申请人更名', '著录项目｜申请人更名', 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜申请人更名', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜申请人更名', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜申请人更名', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜申请人更名', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜申请人更名', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜申请人更名', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '著录项目｜申请人更名', '【申请人更名提交】国际申请申请人更名提交汇报信', 0, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '著录项目_申请人更名', '著录项目｜申请人更名', 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜申请人更名', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜申请人更名', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜申请人更名', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜申请人更名', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜申请人更名', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜申请人更名', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第15行；【申请人更名提交】国际申请申请人更名提交汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人地址, 变更发明人地址', '【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信', 0, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '著录项目_变更申请人地址', '著录项目｜变更申请人地址, 变更发明人地址', 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '著录项目_变更发明人地址', '著录项目｜变更申请人地址, 变更发明人地址', 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人地址, 变更发明人地址', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人地址, 变更发明人地址', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人地址, 变更发明人地址', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人地址, 变更发明人地址', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人地址, 变更发明人地址', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更申请人地址, 变更发明人地址', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人地址, 变更发明人地址', '【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信', 0, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '著录项目_变更申请人地址', '著录项目｜变更申请人地址, 变更发明人地址', 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '著录项目_变更发明人地址', '著录项目｜变更申请人地址, 变更发明人地址', 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人地址, 变更发明人地址', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人地址, 变更发明人地址', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人地址, 变更发明人地址', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人地址, 变更发明人地址', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人地址, 变更发明人地址', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更申请人地址, 变更发明人地址', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第16行；【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '著录项目｜变更发明人', '【变更发明人提交】国际申请变更发明人汇报信', 0, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '著录项目_变更发明人', '著录项目｜变更发明人', 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更发明人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更发明人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更发明人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更发明人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更发明人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更发明人', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '著录项目｜变更发明人', '【变更发明人提交】国际申请变更发明人汇报信', 0, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '著录项目_变更发明人', '著录项目｜变更发明人', 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更发明人', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更发明人', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更发明人', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更发明人', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更发明人', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更发明人', '', '其他', 'assign', 'yuan.wang@metis-ip.com', '', '', 5, 1, 'V2 结项通知-PCT 第17行；【变更发明人提交】国际申请变更发明人汇报信');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'WO', '著录项目｜变更代理机构, 变更代理机构案号', '', 0, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '著录项目_变更代理机构', '著录项目｜变更代理机构, 变更代理机构案号', 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'WO', '著录项目_变更代理机构案号', '著录项目｜变更代理机构, 变更代理机构案号', 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更代理机构, 变更代理机构案号', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更代理机构, 变更代理机构案号', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更代理机构, 变更代理机构案号', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更代理机构, 变更代理机构案号', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更代理机构, 变更代理机构案号', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'WO', '著录项目｜变更代理机构, 变更代理机构案号', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark) VALUES ('close', 'DM', '著录项目｜变更代理机构, 变更代理机构案号', '', 0, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '著录项目_变更代理机构', '著录项目｜变更代理机构, 变更代理机构案号', 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark) VALUES ('close', 'DM', '著录项目_变更代理机构案号', '著录项目｜变更代理机构, 变更代理机构案号', 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更代理机构, 变更代理机构案号', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更代理机构, 变更代理机构案号', '', '20633', 'skip', '', '["patent8@metis-ip.com"]', '[]', 1, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更代理机构, 变更代理机构案号', '', '20608', 'ignore', '', '', '', 2, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更代理机构, 变更代理机构案号', '', '20753', 'skip', '', '["xin.han@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 3, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更代理机构, 变更代理机构案号', '', '20664', 'skip', '', '["zhuqing.sun@metis-ip.com"]', '["patents_pa@metis-ip.com"]', 4, 1, 'V2 结项通知-PCT 第18行；无需做');
INSERT INTO report_rule (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer, forward_to, forward_cc, seq, status, remark) VALUES ('close', 'DM', '著录项目｜变更代理机构, 变更代理机构案号', '', '其他', 'ignore', '', '', '', 5, 1, 'V2 结项通知-PCT 第18行；无需做');
-- 校验模板及新增 close 域行数。确认所有前置条件后，单独审核 COMMIT 版本。
-- 应为 39；若不足，先核查已有同名但停用或正文为空的行。
SELECT COUNT(DISTINCT name) AS active_v2_template_rows FROM report_template WHERE status=1 AND content IS NOT NULL AND TRIM(content)<>'' AND name IN ('【106表补正提交】106表补正', '【132表补正提交】132表补正', '【206表补正提交】206表补正', '【AA答复递交】2026-08-31-美国申请AA答复提交报告', '【Appeal Brief提交】2026-08-31-美国申请Appeal Brief提交报告', '【Ex Parte Quayle Action答复递交】2026-08-31-美国申请Ex Parte Quayle Action答复提交报告', '【IDS递交】2026-08-31-IDS递交转达', '【NOA缴纳授权费】2026-08-31-美国申请缴纳授权费', '【OA答复递交】2026-08-31-美国申请OA答复提交报告', '【OA答复递交】中国申请审查意见答复提交报告', '【PPH提交】2026-08-31-PPH递交请求', '【RR答复递交】2026-08-31-美国申请RR答复提交报告', '【TD提交】2026-08-31-美国申请TD提交报告', '【临时申请递交】2026-08-31-美国临时申请递交', '【主动撤回】撤回国际申请', '【主动补正提交】国际申请主动补正', '【变更发明人】2026-08-31-美国申请变更发明人', '【变更发明人提交】国际申请变更发明人汇报信', '【变更实体】2026-08-31-美国申请变更实体', '【变更申请人、发明人地址提交】国际申请变更申请人、发明人地址汇报信', '【变更申请人】2026-08-31-美国申请变更申请人', '【变更申请人提交】国际申请变更申请人汇报信', '【复审答复递交】-中国申请复审答复提交报告', '【复审请求】中国申请复审请求提交报告', '【复审阶段优先审查】-中国申请复审优先审查提交报告', '【撤回申请】中国申请撤回申请手续合格通知书', '【新申请递交】2026-08-31-美国专利申请递交', '【新申请递交】【接口用极简版】-中国新申请提交报告', '【新申请递交】【无代办事项】-国际申请递交事宜', '【申请人更名】2026-08-31-美国申请申请人更名', '【申请人更名提交】国际申请申请人更名提交汇报信', '【翻译提交】2026-08-31-美国申请翻译文件递交', '【补交DAS码】国际申请补交DAS码', '【补交Declaration】2026-08-31-美国申请补交Declaration转达', '【补交POA】2026-08-31-美国申请补交POA', '【补正答复】2026-08-31-美国申请补正答复提交报告', '【补正递交】-中国申请补正答复提交报告', '【视为未要求优先权提交】中国申请视为未要求优先权答复提交报告', '待填模板（仅表头版）');
SELECT 'report_rule_template' AS table_name, COUNT(*) AS close_rows FROM report_rule_template WHERE rule_domain='close'
UNION ALL SELECT 'report_rule_map', COUNT(*) FROM report_rule_map WHERE rule_domain='close'
UNION ALL SELECT 'report_rule', COUNT(*) FROM report_rule WHERE rule_domain='close';
ROLLBACK;
