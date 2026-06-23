# 原始文档目录（测试用）

US 递交审核页「原始页」按钮读取的目录。原始文档 = 系统最初提取数据、
写入 IPEasy 的源文件（正式环境存于 **NAS**）。

## 目录约定

```
<SOURCE_DOC_DIR>/<case_volume>/<任意文件名>
```

- 一级子目录名 = 案件方案号（`case_volume`，与 submission_tasks 一致）
- 子目录下的所有文件即该案原始页，审核页按钮会逐个在新标签打开
- 后端接口：`GET /api/submission/tasks/{task_id}/source-docs`
- 静态访问：`/source-docs/<case_volume>/<filename>`

## 切换到正式 NAS

代码不用改，NAS 挂载好后设置环境变量指向挂载点即可：

```bash
export SOURCE_DOC_DIR=/mnt/nas/patent_docs   # 改成实际挂载路径
# 重启 report_server
```

> 注意：正式 NAS 上的目录/命名规则若与「<case_volume>/」不同，
> 需调整 report_server.py 中 get_submission_source_docs 的路径拼接逻辑。
