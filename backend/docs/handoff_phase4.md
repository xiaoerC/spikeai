# 叙梦 Naro (SpikeAI) 全栈工程交接文档 (Phase 4 -> Phase 5 Handoff)

> **交接目标**：为接手的新 Agent 提供完整无损的系统上下文、已交付代码拓扑、测试验证方法、全局铁律与 Phase 5（RPG 主控面板 38 变量与叙梦 6 大 Tab 状态机）的具体实施指南。  
> **工程目录**：`d:\AI\spikeai` (前端 `frontend/`，后端 `backend/`)  
> **路线图参考**：[naro_full_roadmap_v3.md](file:///C:/Users/spike/.gemini/antigravity/brain/fd14b984-28bb-4db7-8696-efc9d78af398/naro_full_roadmap_v3.md)

---

## 一、 系统工程现状与已交付成果复盘 (Phase 0 ~ Phase 4)

### 1. 技术栈体系与隔离规范
*   **前端工程 (`frontend/`)**：
    *   **技术栈**：Vue 3.5 + TypeScript + Vite 6 + UnoCSS + Pinia + Vue Flow + Reka UI + Lucide Icons；
    *   **包管理**：`pnpm`；
    *   **设计语言**：黑金奢华暗黑拟物（Obsidian Gold Glassmorphism），Mobile-First 移动端优先，**绝对禁止使用原生 `alert()` / `confirm()` 弹窗**。
*   **后端工程 (`backend/`)**：
    *   **技术栈**：FastAPI (Python 3.12, `uv` 管理) + SQLAlchemy 2.0 Async + PostgreSQL 16 (pgvector) + Redis 7 + Pillow (PNG tEXt 编解码) + SSE 流式网关；
    *   **包管理**：`uv`。

### 2. 已交付阶段核心能力矩阵
1. **Phase 0 & 1（用户认证、钱包流水与 CSO 资金锁）**：
   - JWT 双 Token 无感刷新、`UserWallet` / `WalletTransaction` 流水审计、`with_for_update` 行级悲观锁保障代币扣费绝对一致。
2. **Phase 2（角色生态与 SillyTavern 编解码）**：
   - SillyTavern V2/V3 角色卡 PNG tEXt/iTXt 元数据无损双向编解码（`card_parser.py`）、角色创建器、上下架与草稿管理。
3. **Phase 3（沉浸式流式对话网关与双层看门狗）**：
   - Xiaomi MIMO (`mimo-v2.5`) 与 LongCat (`LongCat-2.0`) 真实大模型 SSE 流式网关对接；
   - `Thinking` 深度思考流与正文分离解包；
   - 25s TTFT 首字看门狗 + 15s 流式卡死看门狗；
   - 气泡失败态重试、2 列海报网格历史记录。
4. **Phase 4（DAG 剧情分支树、独立会话派生与自顶向下拓扑画布）**：
   - **Git 级别 Parent-Pointer 剧情树**：多平行分支独立消息链组装（`TreeService.get_branch_active_messages`）；
   - **独立会话分叉**：从任意 AI 节点深度克隆全新独立 `ChatSession`，同一角色支持多条独立历史会话并在历史记录网格中独立展示；
   - **时间线倒序**：`StoryBranchDrawer.vue` 最新消息与进度置于最顶部（第 N 幕）；
   - **自顶向下全景拓扑图**：`StoryBranchCanvasModal.vue` 垂直 Top-to-Bottom 时序流向，主线居左垂直排列，分支平滑右延；
   - **对话轮次控制**：仅在 AI 剧情节点开放分叉与回溯，用户发言节点不展示分叉按钮，杜绝连续两次用户发言；
   - **消息改写重跑**：支持原位修改（`edit_only`）与派生新分支重跑剧情（`edit_and_fork`），前后端统一采用 `crypto.randomUUID()` 强契约。

---

## 二、 核心代码资产与文件索引

### 1. 后端核心文件 (`backend/src/app/`)
- **模型层**：
  - [`models/chat.py`](file:///d:/AI/spikeai/backend/src/app/models/chat.py)：`ChatSession`, `StoryBranch`, `ChatMessage`, `ChatControlPanel`, `ChatNarrativeState`；
  - [`models/character.py`](file:///d:/AI/spikeai/backend/src/app/models/character.py)：`Character`, `WorldBookEntry`；
  - [`models/wallet.py`](file:///d:/AI/spikeai/backend/src/app/models/wallet.py)：`UserWallet`, `WalletTransaction`；
- **契约层**：
  - [`schemas/chat.py`](file:///d:/AI/spikeai/backend/src/app/schemas/chat.py)：`SendMessageRequest` (含 `client_message_id`), `ForkSessionRequest`, `ForkBranchRequest`, `RollbackRequest`, `EditMessageRequest`, `ControlPanelDTO`, `NarrativeStateDTO`；
- **服务层**：
  - [`services/chat_service.py`](file:///d:/AI/spikeai/backend/src/app/services/chat_service.py)：`stream_chat`, `fork_session_at_message`, `get_user_chat_sessions`；
  - [`services/tree_service.py`](file:///d:/AI/spikeai/backend/src/app/services/tree_service.py)：`fork_branch`, `switch_branch`, `rollback_to_message`, `edit_message`, `get_dag_graph`；
  - [`services/llm_gateway.py`](file:///d:/AI/spikeai/backend/src/app/services/llm_gateway.py)：小米 MIMO / LongCat 统一网关。

### 2. 前端核心文件 (`frontend/src/`)
- **聊天业务域 (`views/chat/`)**：
  - [`views/chat/index.vue`](file:///d:/AI/spikeai/frontend/src/views/chat/index.vue)：主容器胶水层；
  - [`views/chat/composables/useChatSession.ts`](file:///d:/AI/spikeai/frontend/src/views/chat/composables/useChatSession.ts)：会话初始化、流式消费、会话分叉、分支切换、消息改写重跑；
  - [`views/chat/components/ChatMessageItem.vue`](file:///d:/AI/spikeai/frontend/src/views/chat/components/ChatMessageItem.vue)：消息气泡（AI 气泡含「···」更多菜单，用户气泡仅含「修改」📝 按钮）；
  - [`views/chat/components/StoryBranchDrawer.vue`](file:///d:/AI/spikeai/frontend/src/views/chat/components/StoryBranchDrawer.vue)：倒序时间线抽屉（最新在最上，仅 AI 节点展示回溯/分叉）；
  - [`views/chat/components/StoryBranchCanvasModal.vue`](file:///d:/AI/spikeai/frontend/src/views/chat/components/StoryBranchCanvasModal.vue)：Vue Flow 自顶向下垂直拓扑图；
  - [`views/chat/components/ControlPanelDrawer.vue`](file:///d:/AI/spikeai/frontend/src/views/chat/components/ControlPanelDrawer.vue)：主控面板（38 变量矩阵与指令）；
  - [`views/chat/components/NarrativePanelDrawer.vue`](file:///d:/AI/spikeai/frontend/src/views/chat/components/NarrativePanelDrawer.vue)：叙梦面板（6 大子 Tab 状态机）。
- **历史记录业务域 (`views/history/`)**：
  - [`views/history/index.vue`](file:///d:/AI/spikeai/frontend/src/views/history/index.vue)：个人历史记录主容器（携带 `session_id` 跳转进入独立会话）；
  - [`views/history/composables/useUserHistory.ts`](file:///d:/AI/spikeai/frontend/src/views/history/composables/useUserHistory.ts)：多会话加载、封面立绘头像优先；
  - [`views/history/components/UserHistoryCardGrid.vue`](file:///d:/AI/spikeai/frontend/src/views/history/components/UserHistoryCardGrid.vue)：2 列网格卡片流。

---

## 三、 运行与验证指令备忘

### 1. 后端运行与单测
```powershell
# 运行后端所有自动化测试套件 (当前 23/23 100% 全部通过)
cd d:\AI\spikeai\backend
uv run pytest

# 启动后端开发服务器 (Port: 8080)
uv run uvicorn app.main:app --host 127.0.0.1 --port 8080 --reload
```

### 2. 前端类型检查与构建
```powershell
# 运行前端强类型检查与 Vite 生产构建 (0 错误)
cd d:\AI\spikeai\frontend
pnpm build

# 启动前端开发服务器 (Port: 5173)
pnpm dev --host 127.0.0.1 --port 5173
```

---

## 四、 下一阶段任务清单 (Phase 5: RPG 主控与叙梦 6 大 Tab 状态机持久化)

接手的新 Agent 请按以下步骤推进 Phase 5：

1. **后端数据持久化与接口开放**：
   - 检查并完善 `ChatControlPanel`（38 变量矩阵、指令、长期记忆）与 `ChatNarrativeState`（日期、时间、地点、在场角色、玩家状态、消耗品、重要物品、技能、NPC关系、任务、事件时间轴）的 CRUD API；
   - 开放 `GET /api/v1/chat/sessions/{session_id}/control-panel` 与 `PUT /api/v1/chat/sessions/{session_id}/control-panel`；
   - 开放 `GET /api/v1/chat/sessions/{session_id}/narrative-state` 与 `PUT /api/v1/chat/sessions/{session_id}/narrative-state`。
2. **Prompt 动态插桩流水线**：
   - 在 `chat_service.py` 组装 System Prompt 时，将 38 变量矩阵与叙梦状态机结构化序列化注入大模型上下文；
   - 支持大模型在回复中通过特殊标签（如 `<state_update>` 或 JSON 块）自动更新叙梦面板状态机。
3. **前端抽屉真实数据双向绑定**：
   - 在 `ControlPanelDrawer.vue` 中双向绑定真实 38 变量数值与自定义指令；
   - 在 `NarrativePanelDrawer.vue` 中实现 6 大子 Tab（状态、背包、技能、羁绊关系四宫格、任务、星期分组事件）与后端的无感同步保存。

---

## 五、 推荐给新 Agent 的 Skills (Suggested Skills)

新 Agent 在接手后续任务时，建议根据任务类型调用以下 Skills：

- **`antfu-vue-unocss`**：编写与重构 Vue 3.5 组件、UnoCSS 原子类及 Composable 4 大铁律；
- **`fastapi-async-sqlalchemy`**：编写 FastAPI 异步 ORM、Pydantic v2 契约与事务；
- **`frontend-api-sse-state`**：处理 SSE 流式消费、Axios 泛型请求与 Pinia 状态流；
- **`ui-ux-pro-max`**：黑金 Obsidian 拟物视觉、移动端安全区与手势交互审查；
- **`tdd`**：核心算法与状态机测试驱动开发；
- **`diagnose`**：遇到疑难异常时的 6 步闭环排错。
