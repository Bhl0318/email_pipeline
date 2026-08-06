@echo off
rem ============================================================
rem  env7 USPTO upload launcher
rem  Clears proxy (bypass VPN/system proxy) for THIS window only,
rem  then starts the polling uploader. Does NOT change system settings.
rem
rem  Usage:
rem    double-click            -> default: --loop 30 --live
rem    start_uspto_upload.bat --loop 60 --live
rem    start_uspto_upload.bat --loop 30          (dry-run, no --live)
rem ============================================================
setlocal

rem --- clear proxy: empty proxy vars + NO_PROXY=* so python/pip/requests go direct ---
set HTTP_PROXY=
set HTTPS_PROXY=
set ALL_PROXY=
set NO_PROXY=*

rem --- cd to this bat's own folder (D:\up_uspto) so relative paths work ---
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
