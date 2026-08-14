-- US 递交质量埋点：种子表（seeded error 记录 + 出口判定结果）。
-- 在 atw 库执行（受控环境，人工跑）。value_a/value_b 保留供报表核对与复算。
CREATE TABLE IF NOT EXISTS submission_qa_seeds (
  id           VARCHAR(36)  NOT NULL PRIMARY KEY,
  case_volume  VARCHAR(64)  NOT NULL,
  task_id      VARCHAR(36)  NOT NULL,
  stage        VARCHAR(24)  NOT NULL,               -- confirmation(env2) | filing(env5)
  field_path   VARCHAR(128) NOT NULL,               -- 如 priorities.0.priority_no
  field_label  VARCHAR(64)  NOT NULL,               -- 人可读：优先权号 等
  value_a      TEXT,                                -- 原/正确值
  value_b      TEXT,                                -- 播种错值（出口仍==此值＝漏检）
  outcome      VARCHAR(16)  NOT NULL DEFAULT 'pending', -- pending | caught | missed
  reviewer     VARCHAR(128),                        -- 出口动作时的操作人（如有）
  seeded_at    DATETIME,
  resolved_at  DATETIME,
  KEY idx_case (case_volume),
  KEY idx_task (task_id),
  KEY idx_outcome (outcome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
