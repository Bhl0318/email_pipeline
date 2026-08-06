@echo off
rem ============================================================
rem  env7 USPTO 上传常驻启动脚本
rem  作用：先在本窗口关掉所有代理（VPN/系统代理都不走），再启动轮询上传。
rem  这些 set 只影响本窗口，不改系统设置。
rem  用法：
rem    双击本文件            -> 默认每 30 秒轮询 + 真上传（--loop 30 --live）
rem    命令行带参数覆盖，例如：
rem      start_uspto_upload.bat                （默认 --loop 30 --live）
rem      start_uspto_upload.bat --loop 60 --live
rem      start_uspto_upload.bat                （去掉 --live 只 dry-run 请手敲：--loop 30）
rem ============================================================
setlocal

rem --- 关代理：清空代理变量 + NO_PROXY=* 让 python/pip/requests 全部直连 ---
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set NO_PROXY=*

rem --- 切到本 bat 所在目录（即 D:\up_uspto），确保相对路径正确 ---
cd /d "%~dp0"

echo [proxy] HTTP_PROXY/HTTPS_PROXY cleared, NO_PROXY=*
echo [cwd]   %CD%

if "%~1"=="" (
    echo [run]   python run_uspto_upload.py --loop 30 --live
    python run_uspto_upload.py --loop 30 --live
) else (
    echo [run]   python run_uspto_upload.py %*
    python run_uspto_upload.py %*
)

echo.
echo [exit]  script finished. Press any key to close...
pause >nul
endlocal
