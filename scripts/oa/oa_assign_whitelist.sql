-- OA 分配白名单（atw）。一行 = 某人在某(业务类型×档位×领域×梯队)下可安排。
-- 维度值用 VARCHAR 开放值域（新档位/领域/梯队/业务类型直接插新值，免改表）；
-- attrs 兜底未来新维度；source 支持多来源并存。
CREATE TABLE IF NOT EXISTS oa_assign_whitelist (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  biz_type    VARCHAR(16)  NOT NULL COMMENT '业务类型: OA实质|OA形式|(未来:复审/无效/检索…)',
  tier        VARCHAR(16)  NOT NULL COMMENT 'QC|梯队1|梯队2|梯队3|(未来其他)',
  tier_level  TINYINT      NOT NULL DEFAULT 99 COMMENT '排序: QC=0 梯队1=1 梯队2=2 梯队3=3',
  grade       VARCHAR(16)  NULL COMMENT '档位: 普及|标准|海外|CN|(未来)',
  field       VARCHAR(16)  NULL COMMENT '领域: 通用|结构|生化|通用/结构|通用/结构/生化|(未来)',
  name_raw    VARCHAR(64)  NOT NULL COMMENT '白名单原始写法(常为简称/名)',
  username_zn VARCHAR(64)  NULL COMMENT '解析到的 users.username_zn(全名); 解析不到留空',
  note        VARCHAR(255) NULL COMMENT '备注(化学/生物/试试/特殊情况再考虑/CN答复可不QC 等)',
  flag        VARCHAR(16)  NULL COMMENT '标记(blue/red 等颜色语义, 若有)',
  attrs       JSON         NULL COMMENT '未来新增维度(不改表): {"axis":"value",…}',
  source      VARCHAR(64)  NULL COMMENT '来源标识(如 Confluence pageId), 支持多来源',
  synced_at   DATETIME     NULL COMMENT '最近更新时间',
  KEY idx_lookup (biz_type, grade, field, tier_level),
  KEY idx_user (username_zn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OA分配白名单(梯队×档位×领域→人员)';

-- 梯队说明（每业务类型每梯队一段描述）
CREATE TABLE IF NOT EXISTS oa_assign_tier_desc (
  biz_type    VARCHAR(16)  NOT NULL COMMENT '业务类型: OA实质|OA形式|…',
  tier        VARCHAR(16)  NOT NULL COMMENT 'QC|梯队1|梯队2|梯队3',
  tier_level  TINYINT      NOT NULL DEFAULT 99,
  description VARCHAR(500) NULL COMMENT '该梯队评价说明',
  PRIMARY KEY (biz_type, tier)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='OA分配白名单-梯队说明';
