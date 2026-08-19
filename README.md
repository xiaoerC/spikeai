# SpikeAI (叙梦 Naro 全栈复刻系统)

> 沉浸式 AI 角色互动与分支剧情社区全栈系统，1:1 像素级复刻叙梦 (Narratium / Naro)。

---

## 🌟 项目简介

SpikeAI 是基于现代化全栈技术构建的沉浸式 AI 角色互动与叙事社区平台。系统融合了黑金奢华暗黑玻璃拟物视觉设计（Obsidian Gold Glassmorphism）、SillyTavern V2/V3 角色卡与世界书规范、向量语义混合检索（RAG）、分支剧情树画布以及高并发流式对话能力。

---

## 🛠️ 技术栈

### 前端工程 (`frontend/`)
- **核心框架**：Vue 3.5 + TypeScript + Vite 6
- **样式引擎**：UnoCSS (Tailwind CSS 兼容原子类预设 + 自定义黑金主题)
- **状态管理与路由**：Pinia + Vue Router 4
- **无头 UI / 交互库**：Reka UI + Vaul Vue (移动端手势抽屉 BottomSheet) + Lucide Icons
- **剧情分支可视化**：Vue Flow (DAG 自适应剧情拓扑排版)
- **代码规范**：Biome + vue-tsc (零报错强类型保证)
- **包管理器**：`pnpm`

### 后端工程 (`backend/`)
- **Web 框架**：FastAPI (Python 3.12, 异步 ASGI 网关)
- **ORM & 数据库**：SQLAlchemy 2.0 (Async) + asyncpg + PostgreSQL 16
- **向量检索与世界书**：PostgreSQL `pgvector` (HNSW 索引语义混合召回)
- **缓存与并发控制**：Redis 7 (分布式锁与状态缓存)
- **角色卡编解码**：Pillow (SillyTavern PNG tEXt/iTXt 元数据无损解析与生成)
- **包管理器**：`uv`

---

## 📁 目录结构

```text
spikeai/
├── frontend/                     # 前端工程 (Vue 3.5 + UnoCSS + Vite)
│   ├── src/
│   │   ├── components/common/   # 纯净基础 UI 组件 (AppButton, AppModal, AppDrawer, AppTabs)
│   │   ├── components/navigation/# 导航栏与全局抽屉
│   │   ├── views/               # 业务域内聚页面 (home, chat, login, profile, ranking...)
│   │   ├── stores/              # Pinia 状态管理
│   │   └── types/               # 全局 TypeScript 类型定义
│   └── uno.config.ts            # UnoCSS 黑金主题与样式配置
│
├── backend/                      # 后端工程 (FastAPI + SQLAlchemy Async)
│   ├── src/app/
│   │   ├── api/v1/              # 业务路由入口 (RESTful & SSE 流式)
│   │   ├── core/                # 数据库连接池、Redis、异常与安全中间件
│   │   └── config.py            # Pydantic Settings 类型安全配置
│   └── pyproject.toml           # 后端依赖配置 (uv)
│
├── .agents/                      # 全局协作规范与技能库 (Agent Skills)
├── AGENTS.md                     # 工程行为守则与前后端隔离路由指南
├── docker-compose.yml            # 容器化基础设施 (PostgreSQL + pgvector + Redis)
└── .env.example                  # 环境变量模板
```

---

## 🚀 快速启动

### 1. 启动基础设施
```bash
# 使用 Docker Compose 一键启动 PostgreSQL 16 (含 pgvector) 与 Redis 7
docker-compose up -d
```

### 2. 启动前端服务
```bash
cd frontend
pnpm install
pnpm dev
# 访问 http://localhost:5173
```

### 3. 启动后端服务
```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
# 访问 http://localhost:8000/docs 查看 API Swagger 文档
```

---

## 📜 许可协议

本项目遵循 [MIT License](LICENSE) 协议开源。
