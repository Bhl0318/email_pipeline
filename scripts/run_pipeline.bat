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
python main.py --interval 30

REM 若循环意外退出，保留窗口查看报错
pause
