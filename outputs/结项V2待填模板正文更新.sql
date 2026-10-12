-- 仅更新已存在的 report_template 正文；不新增模板或重导规则。
-- 适用对象：name = '待填模板（仅表头版）'。
-- 运行前后可用下方查询核对；UPDATE 结果应为 1 行。

SELECT name,
       LOCATE('关于题述申请，正文事项需要自己编辑', content) AS old_text_position,
       LOCATE('{{正文事项}}', content) AS placeholder_position
FROM report_template
WHERE name = '待填模板（仅表头版）';

START TRANSACTION;

UPDATE report_template
SET content = REPLACE(content,
                      '关于题述申请，正文事项需要自己编辑',
                      '{{正文事项}}')
WHERE name = '待填模板（仅表头版）'
  AND status = 1
  AND LOCATE('关于题述申请，正文事项需要自己编辑', content) > 0;

SELECT ROW_COUNT() AS updated_rows;

SELECT name,
       LOCATE('关于题述申请，正文事项需要自己编辑', content) AS old_text_position,
       LOCATE('{{正文事项}}', content) AS placeholder_position
FROM report_template
WHERE name = '待填模板（仅表头版）';

COMMIT;
