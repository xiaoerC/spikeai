# 叙梦 Naro (SpikeAI) 深度工程交接文档 (Agent Handoff Guide)

> **版本**：v5.0.0 (Phase 6 世界书全面交付更新)  
> **适用对象**：接棒本项目的后续 Agent / 工程师  
> **工程规范**：严格遵循 `AGENTS.md` 铁律（中文交流、强类型 Type Hints、防御编程、极简主义、最小侵入、零原生 alert 弹窗、前端 UnoCSS 优先、后端 SQLAlchemy 2.0 Async 隔离）。

---

## 一、 项目定位与当前完成状态全览

本项目是 **Narratium / 叙梦 Naro 的 1:1 全栈复刻工程**，采用前后端分层架构：
- **前端 (`frontend/`)**：Vue 3.5 + TypeScript + Vite 6 + UnoCSS + Pinia + Vue Flow + Reka UI + Vaul Vue，高奢黑金曜石（Obsidian Gold Glassmorphism）视觉，Mobile-First 移动端手势与安全区适配。
- **后端 (`backend/`)**：FastAPI (Python 3.12, `uv` 管理) + SQLAlchemy 2.0 Async + PostgreSQL 16 (pgvector) + Redis 7 + Pillow (PNG tEXt 编解码) + SSE 流式网关。

### 阶段完成状态 (Phase 0 ~ Phase 6 全部 100% 交付)
- **Phase 0: 基础页面与组件库**：17 个高保真黑金页面骨架、黑金组件库（`AppButton`, `AppModal`, `AppDrawer`, `AppTabs`）。
- **Phase 1: 钱包与资金系统 (CSO)**：`UserWallet` 双币流水，`with_for_update` 行级排他悲观锁，原子幂等防穿透。
- **Phase 2: SillyTavern 角色卡协议**：PNG `tEXt`/`iTXt` 编解码引擎，V2/V3 角色卡与世界书互转。
- **Phase 3: 统一 LLM 网关与 SSE 对话**：Xiaomi mimo / DeepSeek / OpenAI / Claude / Gemini 适配，`thinking` 深度思考分离与流式打字机。
- **Phase 4: DAG 剧情树与独立分支派生**：Git 级别 Parent-Pointer 状态机、分支抽屉与 Vue Flow 拓扑全景画布。
- **Phase 5: RPG 主控 38 变量矩阵与叙梦 6-Tab 状态机**：38 变量持久化插桩、状态/背包/技能/社交四宫格/任务/历史时间轴、两段式并发网络流水线（提速 300%+）。
- **Phase 6: 世界书 (World Book) 双模 RAG 引擎与管理面板**：
  - ORM 模型：`WorldBook` 与 `WorldBookEntry`；
  - 算法：`Aho-Corasick` 极速关键词扫描 + 次级关键词逻辑过滤（`selectiveLogic` 0/1/2）；
  - 智能置顶：当前发言显式命中关键词绝对置顶，指纹去重，Token 预算动态扩容与软跳过；
  - SillyTavern V2/V3 JSON 格式双向无损导入导出；
  - 前端抽屉：`WorldBookDrawer.vue` 挂载于顶栏 📖 按钮，抽屉内原生滑入编辑面板。

---

## 二、 服务启动与运行命令

### 1. 前端工程 (`frontend/`)
```bash
cd d:\AI\spikeai\frontend
pnpm dev --host 127.0.0.1 --port 5173
# 构建检查
pnpm build # (vue-tsc --noEmit && vite build)
```

### 2. 后端工程 (`backend/`)
```bash
cd d:\AI\spikeai\backend
uv run uvicorn src.app.main:app --host 127.0.0.1 --port 8000 --reload
# 运行全量单元测试
uv run pytest -q # 当前 29 个单测 100% 全部通过
```

---

## 三、 核心数据模型导览 (PostgreSQL 16)

1. **用户与钱包**：`User` (`users`), `UserProfile` (`user_profiles`), `UserWallet` (`user_wallets`), `WalletTransaction` (`wallet_transactions`)；
2. **角色卡体系**：`Character` (`characters`), `CharacterMetrics` (`character_metrics`), `CharacterWorldBook` (`character_worldbooks`);
3. **聊天会话与 DAG 分支**：`ChatSession` (`chat_sessions`), `ChatMessage` (`chat_messages`), `StoryBranch` (`story_branches`), `ControlPanel` (`control_panels`), `NarrativeState` (`narrative_states`);
4. **世界书 (Phase 6)**：`WorldBook` (`world_books`), `WorldBookEntry` (`world_book_entries`).

---

## 四、 核心服务与算法模块导览

- **`backend/src/app/services/world_book_service.py`**：
  - `WorldBookScanner.scan_keywords`：Aho-Corasick 多关键词扫描；
  - `WorldBookScanner.filter_secondary_keys`：Secondary Keys 逻辑过滤 (0: AND ANY, 1: NOT ALL, 2: NOT ANY)；
  - `WorldBookService.match_world_book_entries`：当前发言直接命中置顶、指纹去重、Token 软截断与结构化 Prompt 组装；
  - `WorldBookService.import_sillytavern_json` / `export_sillytavern_json`：SillyTavern 双向互转；
- **`backend/src/app/services/mod_service.py`**：
  - `ModService.ensure_seed_mods`：4 大官方精选 Mod 种子自动注入（画风镜头、深度微表情、自由创作、RPG 战斗）；
  - `ModService.get_active_mod_prompt_patches`：多锚点（`system_prefix`, `before_char`, `after_char`, `top_an`, `bottom_an`, `user_suffix`）Prompt 插桩按 priority 升序合并；
  - `ModService.update_user_mod_priorities`：批量调序与权重更新；
- **`backend/src/app/services/chat_service.py`**：
  - `send_message_stream`：SSE 流式组装（Mod 前置 -> 角色人设 -> Mod 画风 -> 主控 38 变量 -> 叙梦 6-Tab -> 世界书 RAG -> Mod 深度描写 -> 滑动历史窗口 -> Mod 用户后缀）。
- **`frontend/src/views/chat/components/ModManagerDrawer.vue`**：
  - 黑金 Obsidian Gold 抽屉、已激活矩阵（金色 Top 高光、升降序、启停）、Mod 广场、字数统计横幅与自定义 Mod 创建。

---

## 五、 关键 Gotchas 与避坑指南 (Pitfalls & Gotchas)

1. **SQLite NUMERIC 亲和性与纯数字 UUID**：
   - SQLite 会将纯数字 UUID 字符串（如 `11111111111111111111111111111101`）自动转为浮点数存储，并在超出 53 位精度时发生精度截断导致唯一约束冲突或读取返回 float；
   - **种子 Mod ID 必须包含十六进制字母（如 `a0000000-0000-0000-0000-000000000001`）**，确保在 SQLite 下以 TEXT 存储。
2. **SillyTavern JSON 枚举与类型兼容**：
   - 酒馆导出的条目 `position` 常为数值 `0, 1, 2, 3`，必须映射为安全的字符串 (`before_char`, `after_char`, `top_an`, `bottom_an`)；
   - 导入时必须校验 `character_id` 是否在数据库中真实存在，角色不存在时自动降级为全局公共世界书。
3. **前端 Token 存储 Key**：
   - 前端 Axios 拦截器从 `localStorage.getItem("naro_access_token")` 读取 Token。

---

## 六、 下一个 Agent 的立即行动指南 (Phase 8 执行计划)

Phase 0 ~ Phase 7 已全部圆满交付并 100% 通过 37/37 项后端单测与前端 build。
用户下一个阶段的目标是 **Phase 8: 60fps 平滑打字机与 IndexedDB 离线秒开加速引擎**。

### Phase 8 核心步骤：
1. **`requestAnimationFrame` 环形缓冲打字机 (`frontend/src/views/chat/composables/useRafTypewriter.ts`)**：
   - 基于帧率自适应平滑吐字，防止超高速大模型 SSE 流引发 DOM Markdown 解析频繁重排掉帧；
2. **IndexedDB 本地持久化快照 (`frontend/src/services/storage/chatStorage.ts`)**：
   - 缓存角色卡、会话分支与最新 1000 条消息，实现首屏 <50ms 秒开；
3. **长对话虚拟滚动优化 (`frontend/src/views/chat/components/ChatMessageList.vue`)**：
   - 超过 100 条消息自适应启用虚拟列表，保持 DOM 节点常驻 ≤ 30 个；
4. **单测与全链路回归验证**。

