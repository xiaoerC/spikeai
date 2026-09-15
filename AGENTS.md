# SpikeAI / NaroAI 工程与 Agent 协作指南

本文档定义了本项目（Narratium / 叙梦 Naro 1:1 复刻全栈系统）的工程规范、行为准则以及前后端隔离版 Agent Skills 自动路由机制。

---

## 一、 核心行为守则 (Karpathy Guidelines & User Global Rules)

在进行任何代码编写或修改时，Agent 必须严格遵守以下 6 项铁律：

1. **中文交互**：全流程使用中文与用户交流与回答。
2. **思考先行与宁问勿猜 (Think Before Coding)**：遇到需求模糊、接口设计分歧或关键架构权衡时，必须主动向用户提问澄清，达成共识后再编码；严禁盲目猜想与静默做决定。
3. **极简主义 (Simplicity First)**：优先编写最直接、最简洁的代码，严禁无意义的过度设计与多余抽象。
4. **防御编程 (Defensive Programming)**：严禁静默捕获异常（如空 `except:` / `catch {}`），所有错误必须显式抛出或记录日志。
5. **最小侵入与精准修改 (Surgical Changes)**：非任务相关的历史代码和注释必须完整保留，严禁大面积无意义重构或格式化；变更范围必须精准对应用户需求。
6. **强类型与详尽注释 (Type Hints & Docs)**：所有新增与修改的 Python/TypeScript 代码，必须包含完整类型标注（Type Hints）与详尽的文档注释（含 Usage 示例）。包管理严格遵循前端 `pnpm`、后端 `uv` 虚拟环境。

---

## 二、 核心技术栈与作用域隔离规范

本项目采用前后端分层架构，并实行 **严格的工程隔离机制**：

*   **前端工程 (`frontend/`)**：
    *   **技术栈**：Vue 3.5 + TypeScript + Vite 6 + UnoCSS + Pinia + Vue Flow + Reka UI (无头组件) + Vaul Vue (手势抽屉)。
    *   **设计语言**：黑金奢华暗黑玻璃拟物（Obsidian Gold Glassmorphism），Mobile-First 移动端优先（Safe Area 与软键盘避让）。
    *   **排版、架构、组件库与交互 9 大铁律**：
        1. **UnoCSS 绝对优先**：能用 UnoCSS 原子类解决的严禁写原生 `<style>` 或内联样式。
        2. **现代布局铁律**：排版一律使用 `Flexbox` 与 `Grid`，禁用 `float` / `inline-block`。
        3. **Gap 主导间距**：元素间距一律在父级使用 `gap`，严格杜绝子元素 `margin` 间距。
        4. **组件库规范**：统一使用 `@/components/common` 下的 `AppButton`、`AppModal`、`AppDrawer`、`AppTabs`，严禁手写 Ad-hoc 的简陋 fixed 遮罩弹窗。
        5. **绝对禁止原生 Alert 弹窗 (Zero Native Dialogs)**：严禁在任何业务逻辑中调用 `window.alert()` / `confirm()` / `prompt()` 原生弹窗，所有反馈必须使用 Toast 轻提示或 `<AppModal>`。
        6. **特性内聚与就近原则 (Colocation & Feature-First)**：页面私有组件、composables、constants、utils 就近存放在 `views/{feature}/` 内；主入口 `index.vue` 仅作为容器胶水层（~100行）。
        7. **公共组件严格升格机制 (Promotion Rule)**：全局 `src/components/common/` 仅放无业务绑定的 UI 基础设施，仅当逻辑被 ≥ 2 个业务域复用时才允许升格至全局。
        8. **Composition API 组织与 Composable 4 大铁律**：小组件内使用【注释功能域】将变量/方法/watch/mounted 物理聚拢；抽离 composable 时遵循 `MaybeRefOrGetter` 入参、普通对象包裹 ref 安全解构、`onUnmounted` 自动清理以及 `readonly()` 状态单向流保护。
        9. **强类型 API 契约与 SSE 流式状态**：所有请求经 `src/services/` 强类型包装，SSE 打字机流消费带 `AbortController` 优雅中止与 60fps 帧率保护，Pinia 状态单向流及 IndexedDB 异步持久化。
    *   **包管理器**：`pnpm`。
*   **后台管理工程 (`admin/`)**：
    *   **技术栈**：Vue 3.5 + TypeScript + Vite 6 + UnoCSS + Element Plus + VXE-Table + Pinia。
    *   **排版与规范 8 大铁律**：
        1. **UnoCSS 绝对优先**：排版与样式原子类化，减少深层 CSS/SCSS 嵌套。
        2. **Flexbox & Grid 现代布局**：淘汰浮动布局，页面结构清晰。
        3. **Gap 主导间距**：父容器一律使用 `gap` 管理子元素间隙。
        4. **统一 Biome 门禁**：全面对齐 `@biomejs/biome` 1.9.4，极速检查与格式化。
        5. **零原生弹窗**：严禁 `alert()`/`confirm()`，统一使用 Element Plus `ElMessage` 与 `ElMessageBox`。
        6. **强类型 API 契约**：接口与数据模型提供显式 TypeScript 类型定义。
        7. **现代 Composition API**：新写及重构组件采用 `<script setup>` 语法。
        8. **轻量化依赖**：拒绝老旧 Polyfill 与冗余组件全量注册。
    *   **包管理器**：`pnpm`。
*   **后端工程 (`backend/`)**：
    *   **技术栈**：FastAPI (Python 3.12, `uv` 管理) + SQLAlchemy 2.0 Async + PostgreSQL 16 (pgvector) + Redis 7 + Pillow (PNG tEXt/iTXt 编解码) + SSE 流式网关。
    *   **包管理器**：`uv`。


---

## 三、 Skills 架构与前后端隔离路由表

本项目 Skills 分为 **全局通用与协议层**（位于根目录 `.agents/skills/`）、**前端专属层**（位于 `frontend/.agents/skills/`）、**后台专属层**（位于 `admin/.agents/skills/`）与 **后端专属层**（位于 `backend/.agents/skills/`）：

```
spikeai/
├── AGENTS.md                                # 全局协作规范与路由总表
├── .agents/skills/                          # 【全局通用与协议层】
│   ├── karpathy-guidelines/                 # 底层行为守则基线
│   ├── grill-me/                            # 需求与接口设计极限追问
│   ├── tdd/                                 # 核心算法与纯逻辑单测驱动
│   ├── diagnose/                            # 6步疑难排错闭查
│   ├── cso/                                 # 资金流水与 JWT 安全审计
│   ├── qa/                                  # 真机视口渲染与端到端回归
│   ├── design-review/                       # 视觉与交互专项审查
│   ├── setup-pre-commit/                    # 提交前门禁配置 (Biome + uv)
│   └── sillytavern-card-spec/               # SillyTavern V2/V3 协议 + PNG tEXt 编解码标准
│
├── frontend/.agents/                        # 【前端专属隔离层】(仅在 frontend/ 作用域生效)
│   ├── rules/
│   │   └── frontend_habits.md               # 🌟 前端 9 大排版、架构、组件库、状态与禁止原生弹窗铁律
│   └── skills/
│       ├── naro-ui-components/              # 🌟 黑金基础组件库 (AppButton/Modal/Drawer/Tabs/禁止alert)
│       ├── frontend-api-sse-state/          # 🌟 API 契约、SSE 流式打字机与 Pinia 状态专家
│       ├── frontend-layout-habits/          # 🌟 前端布局、就近内聚与架构习惯专家
│       ├── antfu-vue-unocss/                # 🌟 Vue 3.5 + UnoCSS + Composition API 规范专家
│       ├── ui-ux-pro-max/                   # 黑金暗黑拟物 + 移动端手势与安全区规范
│       └── vue-flow-dag/                    # Vue Flow 剧情分支拓扑与自适应排版
│
├── admin/.agents/                           # 【后台专属隔离层】(仅在 admin/ 作用域生效)
│   ├── rules/
│   │   └── admin_habits.md                  # 🌟 后台 8 大排版、组件、规范与零原生弹窗铁律
│   └── skills/
│       └── admin-element-pro/               # 🌟 Element Plus + VXE-Table + UnoCSS 中后台开发专家
│
└── backend/.agents/skills/                  # 【后端专属隔离层】(仅在 backend/ 作用域生效)
    ├── fastapi-async-sqlalchemy/            # FastAPI + SQLAlchemy 2.0 Async + 事务行锁
    └── pgvector-worldbook-rag/              # PostgreSQL pgvector + 世界书语义混合召回
```

### 1. 前端任务路由规则 (Scope: `frontend/`)
- 当编写/修改 API 请求、SSE 流式打字机消费、Pinia 状态与前后端数据联调时：
  - 调用 `frontend-api-sse-state` 规范构建 Axios 泛型拦截器、`useChatStream` 打字机 Composable 与 Pinia 状态持久化。
- 当编写/修改 `.vue`、`.ts`、`uno.config.ts` 或调整移动端 UI 布局与页面开发时：
  - 调用 `naro-ui-components` 规范调用 `AppButton`、`AppModal`、`AppDrawer` (BottomSheet) 与 `AppTabs`，**绝对禁止调用原生 `alert()`/`confirm()`**。
  - 自动遵守 `frontend_habits.md` 规则与 `frontend-layout-habits`（UnoCSS优先、Flex/Grid排版、Gap间距、特性内聚、升格机制、无原生弹窗）。
  - 调用 `antfu-vue-unocss` 遵循 Anthony Fu 的 Vue 3.5 响应式解构、注释功能块聚拢与 Composable 4 大铁律。
  - 调用 `ui-ux-pro-max` 遵循 Obsidian Gold 调色板、磨砂玻璃模糊度、Safe Area 及软键盘防遮挡规范。
  - 调用 `vue-flow-dag` 构建分支剧情树画布与自适应 Dagre 排版。
  - 调用 `design-review` 审查最终界面视觉与手势交互。

### 2. 后端任务路由规则 (Scope: `backend/`)
- 当编写/修改 FastAPI 路由、SQLAlchemy ORM 模型、Alembic 迁移及 Redis 事务时：
  - **严禁加载或引用前端 UI/CSS 类库规则**，保持纯净的 Python 3.12 / uv 隔离环境。
  - 调用 `fastapi-async-sqlalchemy` 编写规范的异步 ORM 模型、`with_for_update` 行级锁与依赖注入。
  - 调用 `pgvector-worldbook-rag` 构建世界书 HNSW 向量索引与混合召回。
  - 核心编解码（`card_parser.py`）与 DAG 分支算法（`tree_service.py`）遵循 `sillytavern-card-spec` 与 `tdd` 驱动。
  - 遇到复杂逻辑异常时遵循 `diagnose` 6 步闭环。
  - 涉及钱包余额与权限校验时调用 `cso` 审查。

### 3. 后台管理任务路由规则 (Scope: `admin/`)
- 当编写/修改后台管理页面、DataTable 表格、Element Plus 表单、权限配置与报表看板时：
  - 严格遵守 `admin_habits.md` 8 大铁律（UnoCSS 绝对优先、Flex/Grid 排版、父级 Gap 间距、Biome 格式化、零原生弹窗）。
  - 调用 `admin-element-pro` 运用成熟的中后台 CRUD 范式、Dialog 异步提交闭环与 VXE-Table 虚拟滚动调优。
  - 保持与后端 API 的强类型契约，禁止引入未授权的过时老旧第三方依赖。


---

## 四、 代码知识图谱与智能检索 (CodeGraph)

本项目已全面接入 **CodeGraph (AST 代码知识图谱)**：
- **符号与架构探索**：优先使用 `codegraph_explore` 替代大面积无序 grep，一次性检索跨文件符号定义与调用拓扑；
- **重构影响分析 (Impact Analysis)**：在修改公共 DTO、Pinia 状态、数据库模型或核心 Service 前，使用 `codegraph_impact` 与 `codegraph_callers` 预先评估受影响组件与 API，杜绝破坏性重构；
- **知识库同步**：本地 SQLite 索引文件自动存放在 `.codegraph/` 目录，已加入 `.gitignore` 保护。
