-- OA 分配 待分配状态表（atw）。每件立项一行，只记 id + 是否已分配。
-- 案件展示字段按 id JOIN projects 现取；分配结果回写 projects.project_qc/project_leader/project_participant。
CREATE TABLE IF NOT EXISTS oa_assign_task (
  id           VARCHAR(64) NOT NULL COMMENT '立项唯一id(=projects.row_id / Wiki行data-oa-id)',
  status       TINYINT     NOT NULL DEFAULT 0 COMMENT '0待分配 1已分配',
  link_sent_at DATETIME    NULL COMMENT '立项/发分配链接时刻(=该案要求分配的时间)，分配页展示',
  PRIMARY KEY (id),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OA分配待分配状态';

-- 已有表升级（新增 link_sent_at；旧库执行一次）：
-- ALTER TABLE oa_assign_task ADD COLUMN link_sent_at DATETIME NULL
--   COMMENT '立项/发分配链接时刻(=该案要求分配的时间)，分配页展示';
