-- US结项：续案、部分续案、分案分别命中独立规则及模板；客户处理规则复制执行时US补正的有效规则。
-- 只生成SQL，不在此处执行。执行前确认 report_rule 中 close/US/补正 有有效客户规则。
START TRANSACTION;

-- 模板正文：以用户提供的三份内容为准。
INSERT INTO report_template (name, content, format, status, remark) VALUES (
  'US_续案递交_V2.md', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请续案递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{本申请递交日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述续案申请已于{{递交日期}}向美国专利商标局递交，申请号为{{申请号}}，附件为递交的申请文件及收到的官方文件。

待完成事项

1. 信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a) 发明人/申请人/代理人已知的相关文献

b) 发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c) 如果有除美国之外的国家或地区的与本申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, 'US结项续案递交独立模板')
ON DUPLICATE KEY UPDATE content=VALUES(content), format=VALUES(format), status=1, remark=VALUES(remark);

INSERT INTO report_template (name, content, format, status, remark) VALUES (
  'US_部分续案递交_V2.md', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请部分续案递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{本申请递交日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述部分续案申请已于{{递交日期}}向美国专利商标局递交，申请号为{{申请号}}，附件为递交的申请文件及收到的官方文件。

待完成事项

1. 信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a) 发明人/申请人/代理人已知的相关文献

b) 发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c) 如果有除美国之外的国家或地区的与本申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, 'US结项部分续案递交独立模板')
ON DUPLICATE KEY UPDATE content=VALUES(content), format=VALUES(format), status=1, remark=VALUES(remark);

INSERT INTO report_template (name, content, format, status, remark) VALUES (
  'US_分案递交_V2.md', '***机密并受律师客户通讯特权保护***
***Privileged and Confidential; Attorney-Client Communication***

**关于：美国申请分案递交**

|  |  |
| --- | --- |
| 专利申请号： | {{申请号}} |
| 专利申请名称： | {{申请名称}} |
| 本申请递交日： | {{本申请递交日}} |
| 委托方案号： | {{客户案号}} |
| 代理所案号： | {{代理所案号}} |

|  |  |
| --- | --- |
| 待完成事项： | 递交信息披露声明（Information Disclosure Statement） |
| 完成期限： | 尽快 |

尊敬的{{客户名称}}：

题述分案申请已于{{递交日期}}向美国专利商标局递交，申请号为{{申请号}}，附件为递交的申请文件及收到的官方文件。

待完成事项

1. 信息披露声明（Information Disclosure Statement）

根据美国专利法的规定，在专利申请过程中，发明人、申请人、及他们在美国专利商标局的代理人中任何一方知晓的与本申请的可专利性有重要关联（material to patentability）的文献资料，必须以information disclosure statement（IDS）的形式向美国专利商标局提交。IDS文件通常包括几个方面：

a) 发明人/申请人/代理人已知的相关文献

b) 发明人/申请人/代理人对相关领域检索获得的文献（但发明人/申请人/代理人并没有义务去做检索）

c) 如果有除美国之外的国家或地区的与本申请相关的专利申请，相应专利局反馈给发明人/申请人的相关文献及审查意见

如果存在上述文献，请贵司立即提供给我方，以便我方及时准备并向美国专利商标局提交IDS。

请注意，该强制性的披露义务一直持续到申请获批，专利授权为止。而且，根据申请在审查过程所处的阶段，递交IDS的时限会有不同，在有些情况下还可能产生官费。未能履行该强制性的披露义务（mandatory duty of disclosure）可能会被视为不正当行为（inequitable conduct），导致整份专利无效且不能执行。所以在专利授权前，如果发明人/申请人获悉上述文献，请立即通知我方。并发送到IDS@metis-ip.com / IDS@zhycoip.com 邮箱，以便我方在递交美国非临时专利申请时一并向美国专利商标局提交IDS。

如题述美国专利申请有任何进一步来自官方的消息，我们将随即通知贵方。对上述事宜倘有任何疑问，欢迎随时垂询。

谨致问候

{{签名品牌}}
', 'md', 1, 'US结项分案递交独立模板')
ON DUPLICATE KEY UPDATE content=VALUES(content), format=VALUES(format), status=1, remark=VALUES(remark);

-- 每个组合单独绑定模板。
INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark)
VALUES ('close', 'US', '新申请递交_续案', 'US_续案递交_V2.md', 0, 1, '客户规则同US补正')
ON DUPLICATE KEY UPDATE template=VALUES(template), attach_pdf=VALUES(attach_pdf), status=1, remark=VALUES(remark);

INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark)
VALUES ('close', 'US', '新申请递交_部分续案', 'US_部分续案递交_V2.md', 0, 1, '客户规则同US补正')
ON DUPLICATE KEY UPDATE template=VALUES(template), attach_pdf=VALUES(attach_pdf), status=1, remark=VALUES(remark);

INSERT INTO report_rule_template (rule_domain, region, rule_key, template, attach_pdf, status, remark)
VALUES ('close', 'US', '新申请递交_分案', 'US_分案递交_V2.md', 0, 1, '客户规则同US补正')
ON DUPLICATE KEY UPDATE template=VALUES(template), attach_pdf=VALUES(attach_pdf), status=1, remark=VALUES(remark);

-- 清理三个独立键可能存在的旧客户规则，再复制当前US补正的全部有效客户规则。
UPDATE report_rule SET status=0 WHERE rule_domain='close' AND region='US'
  AND rule_key IN ('新申请递交_续案', '新申请递交_部分续案', '新申请递交_分案');
INSERT INTO report_rule
  (rule_domain, region, rule_key, rule_variant, customer_code, action, preparer,
   forward_to, forward_cc, extra_json, seq, status, remark)
SELECT
  'close', 'US', r_dst.rule_key, r_src.rule_variant, r_src.customer_code, r_src.action, r_src.preparer,
  r_src.forward_to, r_src.forward_cc, r_src.extra_json, r_src.seq, 1, '客户规则同US补正'
FROM report_rule AS r_src
CROSS JOIN (
  SELECT '新申请递交_续案' AS rule_key
  UNION ALL SELECT '新申请递交_部分续案'
  UNION ALL SELECT '新申请递交_分案'
) AS r_dst
WHERE r_src.rule_domain='close' AND r_src.region='US' AND r_src.rule_key='补正' AND r_src.status=1
ON DUPLICATE KEY UPDATE
  action=VALUES(action), preparer=VALUES(preparer), forward_to=VALUES(forward_to),
  forward_cc=VALUES(forward_cc), extra_json=VALUES(extra_json), seq=VALUES(seq),
  status=1, remark=VALUES(remark);

-- 精确组合映射；原有合并项保持不变。
INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark)
VALUES ('close', 'US', '新申请递交_续案', '新申请递交_续案', 1, '独立组合，客户规则同US补正')
ON DUPLICATE KEY UPDATE rule_key=VALUES(rule_key), status=1, remark=VALUES(remark);

INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark)
VALUES ('close', 'US', '新申请递交_部分续案', '新申请递交_部分续案', 1, '独立组合，客户规则同US补正')
ON DUPLICATE KEY UPDATE rule_key=VALUES(rule_key), status=1, remark=VALUES(remark);

INSERT INTO report_rule_map (rule_domain, region, match_key, rule_key, status, remark)
VALUES ('close', 'US', '新申请递交_分案', '新申请递交_分案', 1, '独立组合，客户规则同US补正')
ON DUPLICATE KEY UPDATE rule_key=VALUES(rule_key), status=1, remark=VALUES(remark);

COMMIT;

-- 核对：三组均应有映射、模板，以及与US补正相同的有效客户规则数量。
SELECT m.match_key, m.rule_key, t.template, t.attach_pdf, COUNT(r.id) AS active_customer_rules
FROM report_rule_map AS m
LEFT JOIN report_rule_template AS t ON t.rule_domain=m.rule_domain AND t.region=m.region AND t.rule_key=m.rule_key AND t.status=1
LEFT JOIN report_rule AS r ON r.rule_domain=m.rule_domain AND r.region=m.region AND r.rule_key=m.rule_key AND r.status=1
WHERE m.rule_domain='close' AND m.region='US' AND m.status=1
  AND m.match_key IN ('新申请递交_续案', '新申请递交_部分续案', '新申请递交_分案')
GROUP BY m.match_key, m.rule_key, t.template, t.attach_pdf
ORDER BY m.match_key;
