-- OA 分配 批量分享批次表（atw）。一次「分享全部已分配」= 一批次一行。
-- 只读分享页 /oa-assign/share?batch=<batch_id> 据此取本批次的 oaid 列表 + 分享时间；
-- 各案报告/人员仍按 oaid JOIN oa_assign_report/projects 现取（不冗余）。
-- 注：oa_assign_store.save_share_batch 会 CREATE TABLE IF NOT EXISTS 幂等自建；
--     本文件供 DBA 预建（当运行账号无建表权限时）。
CREATE TABLE IF NOT EXISTS oa_assign_share_batch (
  batch_id   VARCHAR(32) NOT NULL COMMENT '分享批次id(uuid 前12位)',
  oaids_json TEXT        NULL COMMENT '本批次 oaid 列表(JSON 数组，=projects.id)',
  shared_at  VARCHAR(32) NULL COMMENT '分享时间(批次标记，页面头部显示)，如 2026-09-21 15:30',
  PRIMARY KEY (batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OA分配批量分享批次';
