# ADS 本地 XFA 预览部署

从 [PDF.js 官方发布页](https://github.com/mozilla/pdf.js/releases)下载稳定版的预构建 `dist.zip`，解压后确认其中有 `web/viewer.html` 和 `build/`。

部署时二选一：

- 将解压内容放到 `scripts/web/pdfjs/`，使 `scripts/web/pdfjs/web/viewer.html` 存在。
- 将 `SUBMISSION_PDFJS_DIR` 设为解压目录，例如在启动审核服务的同一个 CMD 窗口运行 `set "SUBMISSION_PDFJS_DIR=D:\pdfjs-dist"`。

重启 `report_server.py` 后，在递交页 ADS 标签点击「在线看 XFA 版」。预览器和 ADS 文件都从审核服务的同一域名提供，不需要另开 8888 端口，也不会调用 pdfRest。正式 XFA 的下载、发送和归档不变。

部署前应以实际 ADS 核对申请人、发明人、母案/PCT、Patented 区块等动态内容与 Adobe 是否一致；预览不一致时以正式 XFA 文件和 Adobe 核对结果为准。
