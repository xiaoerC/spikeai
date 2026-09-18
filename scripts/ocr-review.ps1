<#
.SYNOPSIS
    SpikeAI 本地代码审查快捷脚本 (Alibaba Open Code Review CLI 封装)

.DESCRIPTION
    便捷封装 Alibaba Open Code Review (ocr) 工具，结合项目根目录 .opencodereview/rule.json 
    中定义的前后端 17 项铁律，提供对暂存区、提交历史、工作区的精准审查与可视化查看。
    双击或直接运行提供交互式菜单，带参数时直接执行对应功能，彻底杜绝闪退。

.PARAMETER Staged
    仅审查 Git 暂存区 (git diff --cached) 的变更代码。

.PARAMETER Commit
    审查指定的 Git Commit Hash (例如: -Commit abc1234)。

.PARAMETER Delegate
    以委托模式 (Delegation Mode) 运行，输出待审文件元数据与匹配的项目规约，无需配置 API Key。

.PARAMETER Scan
    全量扫描指定目录或文件 (无需依赖 Git Diff，例如: -Scan backend/src/app/core)。

.PARAMETER Viewer
    启动本地 WebUI 查看器 (ocr viewer)，在浏览器中交互式回放审查记录并打标。

.PARAMETER Config
    启动 OCR 模型端点配置向导 (ocr config provider/model)。

.PARAMETER NoPause
    执行完毕后不等待按键，直接退出 (适用于自动化脚本调用)。
#>

[CmdletBinding(DefaultParameterSetName = 'Default')]
param(
    [Parameter(ParameterSetName = 'Staged')]
    [Alias('s')]
    [switch]$Staged,

    [Parameter(ParameterSetName = 'Commit')]
    [Alias('c')]
    [string]$Commit,

    [Parameter(ParameterSetName = 'Delegate')]
    [Alias('d')]
    [switch]$Delegate,

    [Parameter(ParameterSetName = 'Scan')]
    [string]$Scan,

    [Parameter(ParameterSetName = 'Viewer')]
    [Alias('v')]
    [switch]$Viewer,

    [Parameter(ParameterSetName = 'Config')]
    [switch]$Config,

    [switch]$NoPause
)

# 强制输出编码为 UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Write-BrandHeader {
    Write-Host "==================================================================" -ForegroundColor DarkYellow
    Write-Host "     🌌 SpikeAI (叙梦全栈) x Alibaba OpenCodeReview 代码审查控制台" -ForegroundColor Yellow
    Write-Host "==================================================================" -ForegroundColor DarkYellow
}

function Write-Info {
    param([string]$Message)
    Write-Host "[SpikeAI OCR] $Message" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SpikeAI OCR] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[SpikeAI OCR] $Message" -ForegroundColor Yellow
}

function Write-Err {
    param([string]$Message)
    Write-Host "[SpikeAI OCR] $Message" -ForegroundColor Red
}

function Test-OcrInstalled {
    if (-not (Get-Command ocr -ErrorAction SilentlyContinue)) {
        Write-Err "未找到 'ocr' 命令行工具！"
        Write-Info "正在尝试自动检测全局 npm 路径..."
        $npmPrefix = (npm config get prefix 2>$null)
        if ($npmPrefix -and (Test-Path (Join-Path $npmPrefix "ocr.cmd"))) {
            $env:Path += ";$npmPrefix"
            Write-Success "已临时补齐 OCR 路径: $npmPrefix"
            return $true
        }
        Write-Warn "请先在终端运行以下命令全局安装: npm install -g @alibaba-group/open-code-review"
        return $false
    }
    return $true
}

function Invoke-ReviewSafely {
    param([string[]]$OcrArgs)
    try {
        & ocr @OcrArgs
        if ($LASTEXITCODE -ne 0) {
            Write-Warn "`n[提示] 若提示 'no valid LLM endpoint configured'，说明本地尚未配置大模型端点。"
            Write-Info "建议方案："
            Write-Info "1. 使用【委托模式】(Delegation Mode)，由 Antigravity 宿主 Agent 直接审查，免配置 API Key；"
            Write-Info "2. 或运行配置向导: ocr config provider 设置您的 DeepSeek/OpenAI/Qwen API Key。"
        } else {
            Write-Success "`n审查指令执行完毕！"
        }
    }
    catch {
        Write-Err "执行异常: $_"
    }
}

# 1. 检查安装
if (-not (Test-OcrInstalled)) {
    if (-not $NoPause) {
        Write-Host "`n按回车键退出..." -ForegroundColor Gray
        [void][System.Console]::ReadLine()
    }
    exit 1
}

# 2. 定位到仓库根目录
$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

# 3. 模式判断：传参模式 vs 交互式菜单模式
$HasExplicitParam = $Staged -or $Commit -or $Delegate -or $Scan -or $Viewer -or $Config

if ($HasExplicitParam) {
    Write-BrandHeader
    if ($Viewer) {
        Write-Info "正在启动 OpenCodeReview 本地 Web 查看器 (http://localhost:5483)..."
        & ocr viewer
    }
    elseif ($Delegate) {
        Write-Info "运行委托模式 (Delegation Mode) 预览待审文件与注入规约..."
        & ocr delegate preview --format json
    }
    elseif ($Config) {
        Write-Info "启动 OCR 模型与渠道配置向导..."
        & ocr config provider
    }
    elseif ($Scan) {
        Write-Info "全量扫描指定文件/目录: $Scan ..."
        Invoke-ReviewSafely @('scan', $Scan)
    }
    elseif ($Commit) {
        Write-Info "审查指定的 Commit: $Commit ..."
        Invoke-ReviewSafely @('review', '-c', $Commit)
    }
    elseif ($Staged) {
        Write-Info "审查 Git 暂存区 (Staged Changes)..."
        Invoke-ReviewSafely @('review', '--staged')
    }
}
else {
    # 交互式菜单模式 (双击或无参数运行时)
    while ($true) {
        Clear-Host
        Write-BrandHeader
        Write-Host "当前仓库路径: $RepoRoot" -ForegroundColor DarkGray
        Write-Host "已加载规约: .opencodereview/rule.json (前端/后台/后端17项铁律)`n" -ForegroundColor DarkCyan

        Write-Host "请选择操作模式:" -ForegroundColor White
        Write-Host "  [1] 委托模式预览 (免 API Key - 查看待审清单与绑定的 SpikeAI 铁律)" -ForegroundColor Green
        Write-Host "  [2] 启动本地 WebUI 查看器 (ocr viewer - 回放会话/交互式标记)" -ForegroundColor Cyan
        Write-Host "  [3] 审查 Git 暂存区变更 (ocr review --staged - 需配置 LLM)" -ForegroundColor White
        Write-Host "  [4] 审查工作区全量变更 (ocr review - 需配置 LLM)" -ForegroundColor White
        Write-Host "  [5] 配置 OCR 大模型端点 (ocr config provider / model)" -ForegroundColor Yellow
        Write-Host "  [0] 退出控制台`n" -ForegroundColor Gray

        $choice = Read-Host "请输入选项编号 [0-5]"

        switch ($choice.Trim()) {
            '1' {
                Write-Host ""
                Write-Info "正在提取变更与匹配 SpikeAI 铁律规约..."
                & ocr delegate preview --format json
                Write-Host "`n提示: 您可以把上述清单与规则发给 Antigravity，由 Agent 直接帮您自检修复！" -ForegroundColor DarkCyan
                break
            }
            '2' {
                Write-Host ""
                Write-Info "正在启动 WebUI 会话查看器 (默认端口: 5483)..."
                Write-Info "按 Ctrl+C 可停止查看器服务。"
                & ocr viewer
                break
            }
            '3' {
                Write-Host ""
                Write-Info "正在执行 Git 暂存区代码审查..."
                Invoke-ReviewSafely @('review', '--staged')
                break
            }
            '4' {
                Write-Host ""
                Write-Info "正在执行工作区代码审查..."
                Invoke-ReviewSafely @('review')
                break
            }
            '5' {
                Write-Host ""
                Write-Info "进入 OCR 模型提供商交互式配置..."
                & ocr config provider
                break
            }
            '0' {
                Write-Host "`n感谢使用 SpikeAI 代码审查工具，再见！" -ForegroundColor Yellow
                exit 0
            }
            default {
                Write-Warn "无效的选择，请重新输入。"
                Start-Sleep -Seconds 1
                continue
            }
        }

        Write-Host "`n------------------------------------------------------------------" -ForegroundColor DarkGray
        $subChoice = Read-Host "按回车键返回主菜单，或输入 q 退出"
        if ($subChoice.Trim().ToLower() -eq 'q') {
            exit 0
        }
    }
}

if (-not $NoPause) {
    Write-Host "`n按回车键退出..." -ForegroundColor Gray
    [void][System.Console]::ReadLine()
}
