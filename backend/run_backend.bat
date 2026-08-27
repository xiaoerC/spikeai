@echo off
chcp 65001 > nul
title SpikeAI Backend (FastAPI :8000)
cd /d "%~dp0"
echo 正在启动后端 FastAPI 服务 (端口 8000)...
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
pause
