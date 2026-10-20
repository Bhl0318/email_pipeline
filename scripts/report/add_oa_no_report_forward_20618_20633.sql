-- 已识别的 OA 官文最终不分配汇报信（无模板或命中 ignore）时的转发兜底。
-- * 是法域内的「无汇报信」规则键；明确的官文类型 assign/skip 规则仍优先。
-- 在 atw 库执行一次；可重复执行，不会新增重复规则。
START TRANSACTION;

INSERT INTO report_rule
    (rule_domain, region, rule_key, rule_variant, customer_code, action,
     preparer, forward_to, forward_cc, seq, status, remark)
VALUES
    ('oa', 'CN', '*', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, '无汇报信兜底转发'),
    ('oa', 'CN', '*', '', '20633', 'skip', '', '["report@metis-ip.com"]', '["patent8@metis-ip.com"]', 1, 1, '无汇报信兜底转发'),
    ('oa', 'US', '*', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, '无汇报信兜底转发'),
    ('oa', 'US', '*', '', '20633', 'skip', '', '["report@metis-ip.com"]', '["patent8@metis-ip.com"]', 1, 1, '无汇报信兜底转发'),
    ('oa', 'EP', '*', '', '20618', 'skip', '', '["report@metis-ip.com"]', '["ui_pa@metis-ip.com"]', 0, 1, '无汇报信兜底转发'),
    ('oa', 'EP', '*', '', '20633', 'skip', '', '["report@metis-ip.com"]', '["patent8@metis-ip.com"]', 1, 1, '无汇报信兜底转发')
ON DUPLICATE KEY UPDATE
    action = VALUES(action), preparer = VALUES(preparer),
    forward_to = VALUES(forward_to), forward_cc = VALUES(forward_cc),
    status = VALUES(status), remark = VALUES(remark);

COMMIT;
