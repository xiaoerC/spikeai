# 叙梦 Naro 全栈系统：后端与全栈技术架构及开发实现指南

> **版本**：v1.0.0  
> **适用对象**：后端开发工程师、全栈架构师、DevOps 运维工程师  
> **技术栈基线**：Python 3.12 (`uv`) + FastAPI + SQLAlchemy 2.0 Async + PostgreSQL 16 (pgvector) + Redis 7 + Pillow + SSE  

---

## 一、 系统架构与技术选型

### 1.1 技术架构图

```mermaid
graph TB
    subgraph Client [前端客户端 (Vue 3.5 + Vite 6 + UnoCSS)]
        UI[Mobile-First 440px 黑金 UI]
        Router[Vue Router 4]
        Store[Pinia 状态管理]
        SSE_Client[EventSource / Fetch SSE 流式客户端]
    end

    subgraph Gateway [FastAPI 异步 API 网关]
        Auth_Middleware[JWT 鉴权 & Redis Token 黑名单]
        CORS_Limiter[CORS & Redis 令牌桶限流]
        SSE_Gateway[SSE text/event-stream 流式引擎]
        Router_V1[RESTful API Router v1]
    end

    subgraph Service_Core [核心业务领域服务层]
        Auth_Service[认证与用户服务]
        Wallet_Service[钱包资金与悲观锁事务 (CSO)]
        Card_Codec[SillyTavern PNG tEXt 编解码器]
        Tree_Service[DAG 剧情分支树状态机]
        Prompt_Engine[Mod 优先级 Prompt 组装引擎]
        RAG_Service[世界书 pgvector 混合向量召回]
        LLM_Adapter[多模型适配器 (OpenAI/Anthropic/DeepSeek/GLM)]
    end

    subgraph Storage [持久化与缓存层]
        PG[(PostgreSQL 16 + pgvector)]
        R[(Redis 7 Cluster)]
        S3[(OSS / S3 角色立绘与背景存储)]
    end

    UI --> SSE_Client
    UI --> Router
    SSE_Client --> SSE_Gateway
    Router --> Router_V1
    Router_V1 --> Auth_Middleware
    Auth_Middleware --> Service_Core
    SSE_Gateway --> LLM_Adapter
    Service_Core --> PG
    Service_Core --> R
    Service_Core --> S3
```

### 1.2 工程目录结构与代码组织规范

```
spikeai/
├── backend/
│   ├── pyproject.toml              # uv 包管理器依赖清单
│   ├── alembic.ini                 # 数据库迁移配置
│   ├── alembic/                    # 数据库版本迁移脚本
│   │   ├── env.py
│   │   └── versions/
│   ├── src/
│   │   └── app/
│   │       ├── main.py             # FastAPI 应用主入口与生命周期 (Lifespan)
│   │       ├── config.py           # Pydantic Settings 配置中枢
│   │       ├── core/               # 核心底层基础设施
│   │       │   ├── database.py     # SQLAlchemy 2.0 异步引擎与会话
│   │       │   ├── redis.py        # Redis 连接池与工具函数
│   │       │   └── exceptions.py   # 全局统一异常与拦截器
│   │       ├── models/             # SQLAlchemy 声明式 ORM 实体
│   │       │   ├── user.py         # User, Profile, Wallet, Transaction
│   │       │   ├── character.py    # Character, Metrics, WorldBook
│   │       │   ├── chat.py         # ChatSession, StoryBranch, Message, ControlPanel, NarrativeState
│   │       │   ├── mod.py          # ModItem, UserActiveMod, ModCollection, Custom
│   │       │   └── ops.py          # Activity, Notice, Survey
│   │       ├── schemas/            # Pydantic v2 DTO 强类型契约
│   │       ├── services/           # 核心领域业务逻辑
│   │       │   ├── auth_service.py
│   │       │   ├── wallet_service.py
│   │       │   ├── card_codec_service.py
│   │       │   ├── tree_service.py
│   │       │   ├── prompt_assembly.py
│   │       │   ├── worldbook_rag.py
│   │       │   └── llm_gateway.py
│   │       └── api/
│   │           └── v1/             # RESTful & SSE 路由控制层
│   └── tests/                      # pytest 异步单元测试套件
└── frontend/                       # 前端独立工程
```

---

## 二、 全量数据库设计 (PostgreSQL 16 + pgvector)

### 2.1 核心数据表结构 DDL 与索引规划

```sql
-- 1. 启用 pgvector 向量扩展与 UUID 扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. 用户与认证表 (users)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    invite_code VARCHAR(32) UNIQUE NOT NULL,
    invited_by UUID REFERENCES users(id),
    status VARCHAR(32) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_invite_code ON users(invite_code);

-- 3. 用户资料表 (user_profiles)
CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    username VARCHAR(64) NOT NULL,
    avatar_url TEXT DEFAULT '',
    vip_level INT DEFAULT 0,
    player_level INT DEFAULT 1,
    player_xp BIGINT DEFAULT 0,
    creator_level INT DEFAULT 1,
    creator_xp BIGINT DEFAULT 0,
    badges JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 钱包表 (user_wallets - 悲观锁事务保障)
CREATE TABLE user_wallets (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    star_coins INT DEFAULT 100 CHECK (star_coins >= 0),
    moon_gems INT DEFAULT 50 CHECK (moon_gems >= 0),
    version INT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 钱包流水明细表 (wallet_transactions)
CREATE TABLE wallet_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(32) NOT NULL, -- recharge, chat_star, chat_moon, daily_reward, mod_buy, creator_share
    currency VARCHAR(16) NOT NULL, -- star, moon
    amount INT NOT NULL,
    balance_after INT NOT NULL,
    model_id VARCHAR(64),
    target_character_id UUID,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_wallet_tx_user_created ON wallet_transactions(user_id, created_at DESC);

-- 6. 角色卡主表 (characters)
CREATE TABLE characters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id UUID NOT NULL REFERENCES users(id),
    name VARCHAR(128) NOT NULL,
    avatar_url TEXT NOT NULL,
    banner_url TEXT,
    category VARCHAR(32) NOT NULL DEFAULT 'story', -- story, nsfw, rpg
    description TEXT NOT NULL,
    personality TEXT DEFAULT '',
    scenario TEXT DEFAULT '',
    first_mes TEXT NOT NULL,
    alternate_greetings JSONB DEFAULT '[]'::jsonb,
    system_prompt TEXT DEFAULT '',
    post_history_instructions TEXT DEFAULT '',
    prologue_title VARCHAR(128) DEFAULT '序幕',
    prologue_html TEXT DEFAULT '',
    tags TEXT[] DEFAULT ARRAY[]::TEXT[],
    status VARCHAR(32) DEFAULT 'published', -- draft, published, private
    settings_word_count INT DEFAULT 0,
    version VARCHAR(32) DEFAULT '1.0.0',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_characters_category_status ON characters(category, status);
CREATE INDEX idx_characters_tags ON characters USING GIN(tags);

-- 7. 角色卡指标表 (character_metrics)
CREATE TABLE character_metrics (
    character_id UUID PRIMARY KEY REFERENCES characters(id) ON DELETE CASCADE,
    hotness FLOAT DEFAULT 0.0,
    trend_score FLOAT DEFAULT 0.0,
    chat_count BIGINT DEFAULT 0,
    like_count INT DEFAULT 0,
    favorite_count INT DEFAULT 0,
    import_count INT DEFAULT 0,
    rating FLOAT DEFAULT 5.0,
    rating_count INT DEFAULT 0,
    total_tokens BIGINT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_character_metrics_hotness ON character_metrics(hotness DESC);
CREATE INDEX idx_character_metrics_trend ON character_metrics(trend_score DESC);

-- 8. 世界书语义向量表 (character_worldbooks - pgvector HNSW)
CREATE TABLE character_worldbooks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    keys TEXT[] NOT NULL,
    content TEXT NOT NULL,
    constant BOOLEAN DEFAULT FALSE,
    position VARCHAR(32) DEFAULT 'after_char', -- before_char, after_char, system_top
    embedding vector(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_worldbooks_keys ON character_worldbooks USING GIN(keys);
CREATE INDEX idx_worldbooks_embedding ON character_worldbooks USING hnsw (embedding vector_cosine_ops);

-- 9. 对话会话表 (chat_sessions)
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    character_id UUID NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    current_branch_id UUID,
    current_model_id VARCHAR(64) DEFAULT 'glm-5.2-o1',
    mode VARCHAR(32) DEFAULT 'story', -- story, room
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id, updated_at DESC);

-- 10. 剧情分支表 (story_branches)
CREATE TABLE story_branches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    name VARCHAR(128) NOT NULL,
    parent_branch_id UUID REFERENCES story_branches(id),
    fork_message_id UUID,
    is_main BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_story_branches_session ON story_branches(session_id);

-- 11. 消息表 (chat_messages - DAG 节点链)
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    branch_id UUID NOT NULL REFERENCES story_branches(id) ON DELETE CASCADE,
    sender VARCHAR(16) NOT NULL, -- user, ai, system
    character_name VARCHAR(128),
    avatar_url TEXT,
    content TEXT NOT NULL,
    thinking_content TEXT DEFAULT '',
    input_tokens INT DEFAULT 0,
    output_tokens INT DEFAULT 0,
    parent_message_id UUID REFERENCES chat_messages(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_chat_messages_session_branch ON chat_messages(session_id, branch_id, created_at ASC);

-- 12. 主控面板状态表 (chat_control_panels)
CREATE TABLE chat_control_panels (
    session_id UUID PRIMARY KEY REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_name VARCHAR(64) DEFAULT '{{user}}',
    user_persona TEXT DEFAULT '',
    custom_prompt TEXT DEFAULT '',
    variables JSONB DEFAULT '{}'::jsonb, -- 38个变量 variable_1 ~ variable_38
    memory_blocks JSONB DEFAULT '[]'::jsonb,
    text_replacements JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 13. 叙梦面板状态表 (chat_narrative_states)
CREATE TABLE chat_narrative_states (
    session_id UUID PRIMARY KEY REFERENCES chat_sessions(id) ON DELETE CASCADE,
    date_text VARCHAR(64) DEFAULT '',
    time_text VARCHAR(32) DEFAULT '',
    location VARCHAR(128) DEFAULT '',
    present_characters TEXT[] DEFAULT ARRAY[]::TEXT[],
    player_states JSONB DEFAULT '[]'::jsonb,
    consumables JSONB DEFAULT '[]'::jsonb,
    important_items JSONB DEFAULT '[]'::jsonb,
    skills JSONB DEFAULT '[]'::jsonb,
    social_relations JSONB DEFAULT '[]'::jsonb,
    tasks JSONB DEFAULT '[]'::jsonb,
    history_events JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 14. Mod 模组表 (mods)
CREATE TABLE mods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    author_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    category_tag VARCHAR(32) NOT NULL, -- worldbook, system, command, regex, author
    price INT DEFAULT 0,
    status VARCHAR(32) DEFAULT 'published', -- draft, published
    entries JSONB DEFAULT '[]'::jsonb,
    downloads INT DEFAULT 0,
    likes INT DEFAULT 0,
    rating FLOAT DEFAULT 5.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 15. 用户激活 Mod 优先级矩阵表 (user_active_mods)
CREATE TABLE user_active_mods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    mod_id UUID NOT NULL REFERENCES mods(id) ON DELETE CASCADE,
    priority_order INT NOT NULL DEFAULT 0, -- 数字越大优先级越高
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_user_mod UNIQUE (user_id, mod_id)
);
CREATE INDEX idx_user_active_mods_order ON user_active_mods(user_id, priority_order ASC);
```

---

## 三、 5 大核心业务算法与架构实现

### 3.1 SillyTavern V2/V3 与 PNG tEXt 无损编解码器
遵循 SillyTavern Card Specification 规范：
- **写入算法**：
  1. 将角色卡序列化为标准 `chara_card_v2` JSON 格式；
  2. 扩展属性写入 `data.extensions.naro_prologue_html` 与 `data.creator_notes`；
  3. 使用 Base64 编码为字符串；
  4. 利用 Pillow 将 `chara` 关键字写入 PNG 图片的 `tEXt` / `iTXt` Chunk 中保存。
- **解析算法**：
  1. 打开上传的图片，读取 `img.info["chara"]` 或 `img.info["ccv3"]`；
  2. Base64 解码并反序列化为 Pydantic DTO；
  3. 自动适配 V2 与 V3 差异，提取并注入为叙梦标准角色模型。

### 3.2 DAG 剧情分支树状态机与时间轴回溯算法
- **树结构遍历**：
  - 客户端请求 `GET /chat/sessions/{id}/branches` 时，后端根据当前选中的 `branch_id`，自底向上递归查询 `parent_message_id`，拼接出线性时间轴；
- **零破坏回溯 (`Rollback`)**：
  - 当用户回溯至历史节点 $M_{target}$ 时，不删除任何后续消息，仅将 `chat_sessions.current_branch_id` 更新为目标分支，并在该节点生成下一次回复时创建子分支 $B_{new}$，实现 Git 级别的剧情版本控制。

### 3.3 Mod 模组优先级矩阵注入引擎 (Prompt Assembly Pipeline)
- **组装管道**：
  ```
  [System Base Prompt]
          │
          ▼
  [User Persona (主控)]
          │
          ▼
  [Low-Priority Active Mod (0)]
          │
          ▼
  [Mid-Priority Active Mod (1)]
          │
          ▼
  [Top-Priority Active Mod (N - 金色最高优先级)] ───> 最靠近对话历史与最新输入
          │
          ▼
  [Character WorldBook (RAG 召回条目)]
          │
          ▼
  [History Messages (带有正则替换)]
          │
          ▼
  [Latest User Input]
  ```
- **最高优先级生效原理**：列表最底部的 Mod 拥有最高的 `priority_order`，组装器将其词条最后插入 Prompt，从而在 Transformer Attention 注意力机制中获得最高权重响应。

### 3.4 世界书混合向量召回算法 (Hybrid WorldBook RAG)
1. **关键词扫描**：使用 Aho-Corasick 算法扫描用户最新输入，直接命中 `character_worldbooks.keys` 的词条作为必选上下文；
2. **向量语义相似度搜索**：
   ```sql
   SELECT id, content, position, 1 - (embedding <=> :query_vector) AS similarity
   FROM character_worldbooks
   WHERE character_id = :char_id
     AND 1 - (embedding <=> :query_vector) > 0.75
   ORDER BY embedding <=> :query_vector
   LIMIT 3;
   ```
3. **去重与动态注入**：合并关键词与向量召回结果，去重后按照 `position` 插入系统提示词中。

### 3.5 钱包悲观锁并发扣费事务 (CSO 资金安全规范)
```python
async with db.begin():
    # 1. 悲观行级排他锁，防止并发穿透
    stmt = select(UserWallet).where(UserWallet.user_id == user_id).with_for_update()
    result = await db.execute(stmt)
    wallet = result.scalar_one_or_none()
    
    if not wallet or wallet.star_coins < cost:
        raise InsufficientBalanceError("星元余额不足，请前往个人中心充值")
    
    # 2. 扣除余额并记录流水
    wallet.star_coins -= cost
    wallet.version += 1
    
    tx = WalletTransaction(
        user_id=user_id,
        type="chat_star",
        currency="star",
        amount=-cost,
        balance_after=wallet.star_coins,
        model_id=model_id,
        target_character_id=character_id,
        description=f"使用 {model_id} 模型对话消耗"
    )
    db.add(tx)
    # 事务自动提交
```

---

## 四、 全量 RESTful & SSE 流式 API 接口契约

### 4.1 统一请求响应与错误码规范
- 统一成功响应结构：
  ```json
  {
    "code": 0,
    "message": "success",
    "data": { ... }
  }
  ```
- 统一错误响应结构：
  ```json
  {
    "code": 40001,
    "message": "星元余额不足",
    "error_details": "Star coins balance is 9, required 30"
  }
  ```
- 业务错误码字典：
  - `0`: 成功
  - `40001`: 钱包余额不足 (`INSUFFICIENT_BALANCE`)
  - `40101`: 未登录或 Token 无效 (`UNAUTHORIZED`)
  - `40301`: 无权操作该资源 (`FORBIDDEN`)
  - `40401`: 资源未找到 (`NOT_FOUND`)
  - `50001`: LLM 上游网关超时或故障 (`MODEL_PROVIDER_ERROR`)

---

### 4.2 核心 API 路由清单

#### 1. 认证与个人中心
- `POST /api/v1/auth/register`：邮箱验证码注册，入参 `{email, password, code, invite_code?}`。
- `POST /api/v1/auth/login`：账号登录，返回 `{access_token, refresh_token, user_profile}`。
- `GET /api/v1/user/profile`：获取当前用户详细信息、等级、11 大勋章、钱包余额。
- `POST /api/v1/user/daily-reward`：每日签到领取星元 ★。
- `GET /api/v1/user/wallet/transactions`：分页获取资产使用流水。

#### 2. 角色市场与详情
- `GET /api/v1/market/cards`：多维复合筛选。
  - 参数：`mode=story|nsfw`, `sort=heat|recommend|trend|random|favorite`, `time_span=day|week|month`, `tag`, `keyword`, `page`, `page_size`。
- `GET /api/v1/characters/{id}`：获取角色详情（含 10 项数据指标、序幕、作者）。
- `POST /api/v1/characters`：创建/上传角色卡。
- `POST /api/v1/characters/{id}/like`：点赞 Toggle。
- `POST /api/v1/characters/{id}/favorite`：收藏 Toggle。
- `POST /api/v1/characters/{id}/reward`：使用星元/月华打赏角色。
- `GET/POST /api/v1/characters/{id}/comments`：获取/发表评论。

#### 3. AI 对话与分支剧情
- `POST /api/v1/chat/sessions`：初始化或读取会话 `{character_id}`。
- `POST /api/v1/chat/sessions/{id}/send`：**SSE 流式生成接口**。
  - 请求体：`{content: string, model_id: string, mode: "story"|"room"}`。
  - SSE 事件流：
    - `event: thinking` -> `data: {"chunk": "..."}`
    - `event: message` -> `data: {"chunk": "..."}`
    - `event: metrics` -> `data: {"inputTokens": 1200, "outputTokens": 450, "cost": 30}`
    - `event: done` -> `data: {"messageId": "msg-123"}`
- `POST /api/v1/chat/sessions/{id}/branch`：基于历史节点分叉平行分支 `{from_message_id, branch_name}`。
- `GET /api/v1/chat/sessions/{id}/branches`：获取平行分支与时间轴节点树。
- `POST /api/v1/chat/sessions/{id}/rollback`：回溯至历史节点 `{target_message_id}`。
- `GET/PUT /api/v1/chat/sessions/{id}/control-panel`：主控面板数据存取。
- `GET/PUT /api/v1/chat/sessions/{id}/narrative-panel`：叙梦面板 6 大 Tab 状态存取。

#### 4. 自定义与 Mod 模组
- `GET/POST/PUT/DELETE /api/v1/custom/personas`：用户人设 CRUD。
- `GET/POST/PUT/DELETE /api/v1/custom/commands`：快捷指令 CRUD。
- `GET/POST/PUT/DELETE /api/v1/custom/artists`：画师串 Prompt CRUD。
- `GET /api/v1/mods/square`：Mod 广场列表。
- `POST /api/v1/mods/{id}/buy`：购买 Mod。
- `GET/PUT /api/v1/mods/settings/priority`：获取/更新已激活 Mod 优先级排序与统计。

---

## 五、 部署、环境配置与质量保证

### 5.1 环境变量配置模板 (`.env`)
```bash
# 基础服务配置
PROJECT_NAME="Narratium Naro Backend"
DEBUG=False
SECRET_KEY="your-jwt-secret-key-replace-in-production"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# PostgreSQL 16 数据库连接串
DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/naro_db"

# Redis 7 连接串
REDIS_URL="redis://localhost:6379/0"

# LLM Providers API Keys
OPENAI_API_KEY="sk-..."
ANTHROPIC_API_KEY="sk-ant-..."
DEEPSEEK_API_KEY="sk-..."
ZHIPU_API_KEY="..."
```

### 5.2 质量门禁指标
- **静态类型与代码质量**：`ruff check .` 与 `mypy src` 0 警告 0 错误；
- **自动化测试覆盖率**：`pytest --cov=src tests/` 测试覆盖率 `> 85%`；
- **并发性能基线**：SSE 长连接并发数 $\ge 2000$，P95 响应延迟 $< 800ms$。
