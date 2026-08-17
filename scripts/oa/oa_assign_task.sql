-- OA 分配 待分配/分配结果表（atw）。每件立项一行。
-- ★ 表名/字段待确认(C2)；若已有"立项人员分配数据表"，改 oa_assign_store.py 的 TABLE 与列名即可。
CREATE TABLE IF NOT EXISTS oa_assign_task (
  id               VARCHAR(64)  NOT NULL COMMENT '立项唯一id(=projects.row_id / Wiki行data-oa-id)',
  case_volume      VARCHAR(64)  DEFAULT NULL COMMENT '案号',
  project_name     VARCHAR(255) DEFAULT NULL COMMENT '立项类型/名称',
  customer         VARCHAR(128) DEFAULT NULL COMMENT '客户简称',
  region           VARCHAR(8)   DEFAULT NULL COMMENT '国别 CN/US/EP',
  oa_doc_date      VARCHAR(20)  DEFAULT NULL COMMENT 'OA发文日',
  entrust_date     VARCHAR(20)  DEFAULT NULL COMMENT '收文日',
  project_deadline VARCHAR(20)  DEFAULT NULL COMMENT '答复期限',
  designee         VARCHAR(128) DEFAULT NULL COMMENT '指定人(链接发给谁, C4待确认)',
  responder        VARCHAR(128) DEFAULT NULL COMMENT '答复负责人(分配结果)',
  qc               VARCHAR(128) DEFAULT NULL COMMENT '答复QC(分配结果)',
  submitted        TINYINT      NOT NULL DEFAULT 0 COMMENT '0待分配 1已分配',
  created_at       DATETIME     DEFAULT NULL COMMENT '立项落库时间',
  assigned_at      DATETIME     DEFAULT NULL COMMENT '分配提交时间',
  PRIMARY KEY (id),
  KEY idx_submitted (submitted),
  KEY idx_case (case_volume)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OA分配待分配/分配结果';
