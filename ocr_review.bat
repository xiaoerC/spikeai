@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\ocr-review.ps1"
if %ERRORLEVEL% neq 0 (
    echo.
    pause
)
