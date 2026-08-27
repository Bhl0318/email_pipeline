@echo off
rem ============================================================
rem  Warm-generate US filing previews (confirmation/assignment/declaration)
rem  Must run on the SAME machine as report_server (needs LibreOffice for docx->PDF).
rem  Clears proxy for THIS window only; does NOT change system settings.
rem
rem  Usage:
rem    double-click            -> default: --loop 300  (every 5 min)
rem    start_warm_preview.bat --loop 600
rem    start_warm_preview.bat                 (single run, no loop)
rem ============================================================
setlocal

rem --- UTF-8 console so the Chinese window title / python output render correctly ---
chcp 65001 >nul
title 递交预览热生成

rem --- clear proxy: empty proxy vars + NO_PROXY=* so python/requests go direct ---
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set NO_PROXY=*

rem --- cd to this bat's own folder (scripts\report) so relative imports work ---
cd /d "%~dp0"

echo [proxy] HTTP_PROXY/HTTPS_PROXY cleared, NO_PROXY=*
echo [cwd]   %CD%

if "%~1"=="" (
    echo [run]   python warm_preview.py --loop 300
    python warm_preview.py --loop 300
) else (
    echo [run]   python warm_preview.py %*
    python warm_preview.py %*
)

echo.
echo [exit]  script finished. Press any key to close...
pause >nul
endlocal
