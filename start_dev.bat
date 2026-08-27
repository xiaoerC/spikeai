@echo off
cd /d "%~dp0"
if exist "backend\.venv\Scripts\python.exe" (
    backend\.venv\Scripts\python.exe dev.py
) else (
    uv run python dev.py
)
pause
