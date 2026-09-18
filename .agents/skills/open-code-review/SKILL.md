---
name: open-code-review
description: 阿里开源高精度 AI 代码审查技能（支持本地审查与免 API Key 的委托模式 Delegation Mode）。当用户或 Agent 需要对当前代码变更、Git 提交、暂存区或特定文件进行架构规约审计、并发安全检查、漏洞拦截时调用。
---

# Open Code Review (OCR) 代码审查技能

本技能基于阿里巴巴开源的高精度代码审查引擎 [open-code-review](https://github.com/alibaba/open-code-review) (`ocr` CLI)，结合 SpikeAI 独有的前后端 17 项工程铁律，为 Agent 与开发者提供确定性工程分块与语义级深度审查。

---

## 一、 核心工作模式

### 1. 委托模式 (Delegation Mode - 推荐)
- **特点**：**无需配置 OCR LLM API Key，零额外计费**。
- **机制**：由本地 `ocr` CLI 负责确定性工程处理（精准提取统一 Git Diff、排除无关静态资源、自动关联 `.opencodereview/rule.json` 项目铁律），由**宿主 Agent (Antigravity)** 自身的智能模型执行深度审查与修复建议。

#### 委托审查执行流程
```powershell
# 1. 探查待审文件清单与 Git 变动元数据 (JSON 格式)
ocr delegate preview --format json

# 2. 获取目标变更文件所绑定的 SpikeAI 铁律规约
ocr delegate rule <文件路径列表...>

# 3. 针对变更 Diff 与注入的规约进行深度自查，输出行级审查意见并按需实施修复
```

### 2. 独立模式 (Standalone OCR Mode)
- **特点**：由 `ocr` 自身调用配置的模型端点独立执行审查，支持断点续审与全量扫描。
```powershell
# 审查当前工作区 (未暂存 + 已暂存)
ocr review

# 仅审查暂存区 (Staged)
ocr review --staged

# 审查特定 Commit 或分支比对
ocr review -c <commit_hash>
ocr review --from main --to feat/branch

# 全量目录静态与架构安全审计 (无需 Git Diff)
ocr scan backend/src/app/core

# 启动本地 Web 交互审查控制台 (支持高亮 Diff 与意见已修复/忽略标记)
ocr viewer
```

---

## 二、 规约引擎与审查重点

审查过程自动加载根目录 [`.opencodereview/rule.json`](file:///d:/AI/spikeai/.opencodereview/rule.json)，重点拦截以下违规：

### 1. 前端与后台工程 (`frontend/`, `admin/`)
- ❌ **绝对禁止原生弹窗**：严禁 `window.alert()` / `confirm()` / `prompt()`；
- ❌ **严禁内联 style 与原生 `<style>`**：必须 UnoCSS 原子类优先；
- ❌ **严禁子元素 margin 擦屁股**：间距必须由父级容器 `gap-*` 主导；
- ❌ **组件规范**：必须使用 `<AppButton>`、`<AppModal>`、`<AppDrawer>` (前端) 或 Element Plus / VXE-Table (后台)；
- ❌ **严禁空 catch**：禁止空 `try-catch` 静默吞掉错误。

### 2. 后端工程 (`backend/`)
- ❌ **严禁同步阻塞 I/O**：必须 SQLAlchemy 2.0 Async 语法 (`select()`, `Mapped`)；
- ❌ **并发资产防超卖**：涉及钱包余额、货币增减必须使用 `with_for_update` 行级锁；
- ❌ **严禁空 `except:`**：禁止 `except Exception: pass` 静默捕获；
- ❌ **协议安全**：SillyTavern PNG tEXt/iTXt 编解码必须防范恶意构造的大 chunk 攻击。

---

## 三、 Agent 结对使用场景与建议

1. **功能完成后的自检 (Self-Review)**：
   在完成一次复杂开发（如修改了资产扣减逻辑或编写了新页面）后，调用 `ocr delegate preview` 检查是否有遗留的调试代码、未对齐的规约或并发隐患。
2. **重构回归审计**：
   在执行大幅代码优化后，配合 `ocr review --staged` 或运行 `.\scripts\ocr-review.ps1 -Staged` 确认没有破坏既有架构约束。
