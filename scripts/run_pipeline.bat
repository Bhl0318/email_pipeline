@echo off
REM email_pipeline runner (Windows)
REM 放在 scripts\ 目录下，双击或计划任务运行。
REM %~dp0 = 本 bat 所在目录，切到该目录后运行 main.py。

chcp 65001 >nul
cd /d "%~dp0"

REM ── 激活虚拟环境 ──
call "C:\code\email_pipeline\venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [错误] 无法激活虚拟环境 C:\code\email_pipeline\venv，请确认路径。
    pause
    exit /b 1
)

REM ── 每 30 分钟循环运行一次（进程需保持前台，关窗口即停止） ──
REM 控制台输出（含 stderr 的 [审意分析]/[对比文件] 等日志）追加写入 pipeline.log（落在 scripts\ 下）。
REM 2>&1 把 stderr 并入同一文件；>> 追加不覆盖。日志只增不切割，体积过大时手动清理或改用 logging 方案。
echo [%DATE% %TIME%] 启动 email_pipeline，日志写入 "%~dp0pipeline.log"
python main.py --interval 30 >> pipeline.log 2>&1

REM 若循环意外退出，保留窗口查看报错
pause
