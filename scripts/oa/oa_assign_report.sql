-- OA 分配 AI 案件报告表（atw）。每件立项一行，存立项时生成的 markdown 报告。
-- report_md：分配页中栏渲染的 markdown 正文（前四大类：基础/权项/技术/审意）。
-- schemes_json：人员安排建议(≥3组方案)结构化 JSON，供前端点选填人；本轮先空，下一步接 DB 人事后补。
CREATE TABLE IF NOT EXISTS oa_assign_report (
  id           VARCHAR(64) NOT NULL COMMENT '立项唯一id(=projects.row_id / oa_assign_task.id)',
  report_md    LONGTEXT    NULL COMMENT 'AI 生成的 markdown 案件分析报告正文',
  schemes_json TEXT        NULL COMMENT '人员安排建议方案 JSON [{responder,qc,alternates,reason}]',
  submit_json  TEXT        NULL COMMENT '提交的分配结果+附言 JSON {scheme_id,responder,qc,postscript,reason,submitted_at}',
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OA分配AI案件报告';

-- 已有表升级（新增 submit_json 字段；旧库执行一次）：
-- ALTER TABLE oa_assign_report ADD COLUMN submit_json TEXT NULL
--   COMMENT '提交的分配结果+附言 JSON {scheme_id,responder,qc,postscript,reason,submitted_at}';
