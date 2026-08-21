@echo off
rem ============================================================
rem  env6 fetch agent-signed reply attachments launcher
rem  Clears proxy (bypass VPN/system proxy) for THIS window only,
rem  then starts the polling fetcher. Does NOT change system settings.
rem
rem  Usage:
rem    double-click            -> default: --loop 300  (every 5 min)
rem    start_fetch_attachments.bat --loop 300
rem    start_fetch_attachments.bat FilingSignatures agent uspto_upload --loop 300
rem    start_fetch_attachments.bat                    (single run, no loop)
rem ============================================================
setlocal

rem --- UTF-8 console so the Chinese window title / python output render correctly ---
chcp 65001 >nul
title 保存代理人回邮附件

rem --- clear proxy: empty proxy vars + NO_PROXY=* so python/requests go direct ---
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set NO_PROXY=*

rem --- cd to this bat's own folder so relative paths (scripts/) work ---
cd /d "%~dp0"

echo [proxy] HTTP_PROXY/HTTPS_PROXY cleared, NO_PROXY=*
echo [cwd]   %CD%

if "%~1"=="" (
    echo [run]   python fetch_uspto_upload_attachments.py --loop 300
    python fetch_uspto_upload_attachments.py --loop 300
) else (
    echo [run]   python fetch_uspto_upload_attachments.py %*
    python fetch_uspto_upload_attachments.py %*
)

echo.
echo [exit]  script finished. Press any key to close...
pause >nul
endlocal
