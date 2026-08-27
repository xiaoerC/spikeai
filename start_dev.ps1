# ==============================================================================
# SpikeAI / Narratium 全栈一键启动 PowerShell 脚本
# ==============================================================================

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

Write-Host "==============================================================================" -ForegroundColor Cyan
Write-Host "            🌌 叙梦 Naro / SpikeAI 全栈一键启动 (开发模式)" -ForegroundColor Yellow
Write-Host "==============================================================================" -ForegroundColor Cyan

# 1. 启动后端 FastAPI
Write-Host "`n[1/3] 正在启动后端 FastAPI 服务 (端口 8000)..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$RootDir\backend`" && uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000 || pause"

Start-Sleep -Seconds 2

# 2. 启动前端 Vite
Write-Host "[2/3] 正在启动前端 Vue 3.5 + Vite 6 服务 (端口 5173)..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd /d `"$RootDir\frontend`" && pnpm run dev || pause"

Start-Sleep -Seconds 3

# 3. 自动打开浏览器
Write-Host "[3/3] 正在打开浏览器体验地址与 Swagger 文档..." -ForegroundColor Green
Start-Process "http://localhost:5173"
Start-Process "http://localhost:8000/docs"

Write-Host "`n==============================================================================" -ForegroundColor Cyan
Write-Host " ✅ 启动就绪！" -ForegroundColor Green
Write-Host "   - 前端体验地址 : http://localhost:5173" -ForegroundColor White
Write-Host "   - 后端 API 文档 : http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - 远程数据库   : PostgreSQL (140.143.87.234:5432)" -ForegroundColor Gray
Write-Host "   - 远程 Redis    : Redis 7 (140.143.87.234:6379)" -ForegroundColor Gray
Write-Host "==============================================================================`n" -ForegroundColor Cyan
