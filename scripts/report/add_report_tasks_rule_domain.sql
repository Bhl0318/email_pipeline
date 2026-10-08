-- 先在 atw 数据库执行本迁移，再部署包含 rule_domain 写入的 read_email.py。
-- 现有 report_tasks 记录由默认值归为 OA 官文；结项任务创建时需显式写入 close。
ALTER TABLE report_tasks
    ADD COLUMN rule_domain VARCHAR(16) NOT NULL DEFAULT 'oa'
    COMMENT '汇报信来源：oa=OA官文，close=结项';
