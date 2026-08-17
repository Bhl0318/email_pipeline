-- US 递交质量埋点：种子表（服务端专用，前端永不返回）。
-- 在 atw 库执行（受控环境，人工跑）。env1 播种时 INSERT；report_server 出口 SELECT/UPDATE(resolved)。
-- 处理结果(caught/missed)另写 JSONL 日志；本表只存种子 + 是否已判定。
CREATE TABLE IF NOT EXISTS submission_qa_seeds (
  id           VARCHAR(36)  NOT NULL PRIMARY KEY,
  case_volume  VARCHAR(64)  NOT NULL,
  task_id      VARCHAR(36)  NOT NULL,
  stage        VARCHAR(24)  NOT NULL,               -- confirmation(env2)（本期只 env2）
  field_path   VARCHAR(128) NOT NULL,               -- 如 priorities.0.priority_no
  value_a      TEXT,                                -- 原/正确值（仅服务端，绝不进前端；供日志/核对）
  value_b      TEXT,                                -- 播种错值（已写进 fields_json；出口仍==此值＝漏检）
  resolved     TINYINT(1)   NOT NULL DEFAULT 0,     -- 出口是否已判定（一次性、防重判）
  seeded_at    DATETIME,
  resolved_at  DATETIME,
  KEY idx_case (case_volume),
  KEY idx_task (task_id),
  KEY idx_resolved (resolved)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
