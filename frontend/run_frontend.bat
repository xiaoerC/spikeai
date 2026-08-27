@echo off
chcp 65001 > nul
title SpikeAI Frontend (Vite :5173)
cd /d "%~dp0"
echo 正在启动前端 Vue 3.5 + Vite 6 服务 (端口 5173)...
pnpm run dev
pause
