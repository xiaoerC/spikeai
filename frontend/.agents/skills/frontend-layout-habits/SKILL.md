---
name: frontend-layout-habits
description: 前端核心编码习惯与架构铁律：① 100% UnoCSS 优先；② 全面使用 Flex 与 Grid 现代布局；③ 元素间距使用 gap 主导；④ 领域/特性内聚 (Feature-First) 与就近原则 (Colocation)；⑤ 公共组件升格机制 (Promotion Rule)。仅在处理 frontend/ 目录代码时生效。
license: MIT
file_patterns:
  - "frontend/**/*.vue"
  - "frontend/**/*.ts"
  - "frontend/**/*.css"
  - "frontend/uno.config.ts"
triggers:
  - "Vue template layout"
  - "UnoCSS styling"
  - "Flexbox grid layout"
  - "Gap spacing"
  - "Feature colocation"
  - "Frontend directory structure"
---

# 大型前端项目工程结构与排版编码规范指南

本规范定义了 `frontend/` 工程在 **UI 排版习惯** 与 **大型项目架构组织 (Feature-First & Colocation)** 上的 5 大黄金法则。

---

## 铁律一：CSS 能使用 UnoCSS 就要使用 (UnoCSS First)

1. **零原生 `<style>` 原则**：
   - 凡是 UnoCSS 原子类能够表达的样式，**严禁写原生 `<style>` 块或内联 `style="..."`**。
   - 模板中直接使用原子化工具类（如 `bg-[#0a0b0e] text-amber-200 rounded-2xl`）。
2. **高频样式走 Shortcuts**：
   - 多处复用的黑金暗黑玻璃拟物卡片、操作按钮、发光徽章，统一在 `uno.config.ts` 的 `shortcuts` 中定义并复用，禁止散落编写复杂重复类名。
3. **纯 CSS 图标方案**：
   - 图标一律使用 `@unocss/preset-icons`（如 `<div class="i-carbon-chat text-xl" />`），禁止引入冗余的外部 icon 库。

---

## 铁律二：布局一律使用 Flex 与 Grid (Modern Layout Only)

1. **禁用过时与 Hack 布局**：
   - 严禁使用 `float: left/right`、`display: inline-block`、`display: table` 等陈旧排版方式。
   - 严禁使用 `position: absolute` 配合 `top/left` 偏移来模拟本该正常流式排列的列表或卡片。
2. **场景分工标准**：
   - **一维线性排列（导航栏、消息条目、按钮组、标签栏）**：必须使用 **Flexbox**（`flex flex-col` / `flex items-center justify-between`）。
   - **二维网格与卡片列表（首页双列角色卡、勋章墙、多色板）**：必须使用 **Grid**（`grid grid-cols-2` / `grid grid-cols-[repeat(auto-fit,minmax(160px,1fr))]`）。

---

## 铁律三：元素间距使用 Gap 主导，少用 Margin 与 Padding (Gap-Driven Spacing)

1. **父容器 `gap` 统领一切子元素间距**：
   - 兄弟元素之间的间隙，**一律在父级 Flex / Grid 容器上使用 `gap-*`、`gap-x-*`、`gap-y-*` 控制**。
   - ❌ **严禁反模式**：在子元素上写 `mr-3`、`mb-4` 然后使用 `:last-child` 处理多余边距。
   - ✅ **标准模式**：`<div class="flex flex-col gap-3"><div>A</div><div>B</div></div>`。
2. **Padding 与 Margin 的精准边界**：
   - **`padding` 的唯一用途**：容器自身的**内部内嵌呼吸区**（如卡片内边距 `p-4`、按钮内边距 `px-4 py-2`、Safe Area 安全区内边距 `pb-[env(safe-area-inset-bottom)]`）。
   - **`margin` 的克制使用**：仅用于极端场景（如 Flex 中的自动推移 `ml-auto` / `mt-auto`，或根容器的外层独立定位），禁止用于列表条目之间的常规间隔。

---

## 铁律四：特性/领域内聚与就近原则 (Feature-First & Colocation)

传统“按技术分层 (Layer-First)”把所有组件塞进全局 `components/` 会导致空间距离远、心智负担重、僵尸代码横生。

### 1. 核心准则：谁拥有，谁维护
只属于特定业务页面的代码（私有组件、Hooks、工具、常量、类型），必须**就近收敛**存放在该业务页面的目录树内：

```
frontend/src/
├── components/                # 🌟 全局公共 UI 基础设施 (纯展示、无业务状态、高复用)
│   ├── base/                  # 原子基础组件 (NaroButton, NaroInput, NaroAvatar, NaroBadge)
│   ├── feedback/              # 反馈类组件 (GlassModal, Toast, Skeleton, Drawer)
│   └── navigation/            # 全局导航框架 (GlobalTabBar, SafeTopBar)
│
├── composables/               # 🌟 全局组合式逻辑 (useTheme, useViewport, useSSE, useAuth)
├── constants/                 # 🌟 全局系统级常量 (API_ENDPOINTS, STORAGE_KEYS, ROUTE_NAMES)
├── layouts/                   # 页面布局骨架 (MobileAppLayout, DesktopCenterLayout, BlankLayout)
├── plugins/                   # 第三方插件配置与初始化
├── router/                    # 路由中心网关
├── services/                  # 🌟 全局网络请求与 API 客户端
├── stores/                    # 🌟 全局核心共享状态 (Pinia: 用户会话、钱包余额、系统设置)
├── styles/                    # 全局样式入口 (reset, tokens, glassmorphism.css)
├── types/                     # 🌟 全局通用领域契约/实体类型 (User, CharacterCardSpec, DAGNode)
├── utils/                     # 🌟 全局纯通用纯函数 (date, formatters, crypto, clipboard)
│
└── views/                     # 🚀 业务领域与页面集合 (每个都是高度内聚的自治单元)
    │
    ├── home/                  # 🏠 叙梦首页/角色市场模块 (内聚自治)
    │   ├── components/        # 🔒 该页面私有组件 (不对外暴露)
    │   │   ├── HeaderModeTabs.vue
    │   │   ├── FilterPanel.vue
    │   │   ├── CharacterCard.vue
    │   │   └── CardDetailDrawer.vue
    │   ├── composables/       # 🔒 该页面私有的组合式业务逻辑
    │   │   ├── useCardFilter.ts
    │   │   └── useInfiniteCardList.ts
    │   ├── constants/         # 🔒 该页面私有的静态配置与标签
    │   │   ├── marketTags.ts
    │   │   └── defaultFilters.ts
    │   ├── utils/             # 🔒 该页面私有的数据转换与计算
    │   │   └── cardMetricFormatter.ts
    │   ├── types/             # 🔒 该页面私有的视图状态类型
    │   │   └── index.ts
    │   ├── index.vue          # 🌟 页面视图主装配入口 (Container, 胶水层 ~100行)
    │   └── routes.ts          # (可选) 页面私有路由定义
    │
    ├── chat/                  # 💬 沉浸式对话与分支剧情画布模块
    │   ├── components/
    │   ├── composables/
    │   └── index.vue
    │
    ├── card-editor/           # 🎨 角色卡/世界书编辑器模块
    │   ├── components/
    │   ├── composables/
    │   └── index.vue
    │
    └── profile/               # 👤 个人中心与历史记录模块
        ├── components/
        └── index.vue
```

### 2. 容器模式 (Smart Container)
- `views/{feature}/index.vue` 只负责**胶水装配**：从当前目录的 `composables/` 获取状态与行为，分发给当前目录的 `components/`。主文件不写庞杂逻辑，代码保持在 ~100 行。

---

## 铁律五：公共组件严格升格机制 (Promotion Rule)

1. **升格判定门槛**：
   - 严禁将单页面独占的业务组件直接写进全局 `src/components/`。
   - **只有当一段逻辑/组件被 ≥ 2 个独立业务页面共同复用时**，才允许“升格”提取到全局根目录。
2. **全局组件库的标准 (Design System)**：
   - `src/components/` 中的组件必须是**纯净无业务绑定**的（例如 `<NaroGlassCard>` 只提供暗黑拟物和玻璃光晕，不关心里面展示的是角色还是订单）。

---

## 六、 正反模式对比

### 示例 1: 标签与操作栏排版
```vue
<!-- ❌ 错误反模式：margin、style 与非 flex -->
<div style="display: block;">
  <span class="inline-block mr-2" style="background: red;">标签A</span>
  <span class="inline-block" style="background: red;">标签B</span>
</div>

<!-- ✅ 正确规范：UnoCSS + Flex + gap-2 -->
<div class="flex items-center gap-2">
  <span class="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 text-xs border border-amber-500/20">标签A</span>
  <span class="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-300 text-xs border border-amber-500/20">标签B</span>
</div>
```

### 示例 2: 页面业务拆分
```vue
<!-- ❌ 错误反模式：在 views/home.vue 中堆砌 800 行代码，包含所有子弹窗、请求与过滤计算 -->

<!-- ✅ 正确规范：views/home/index.vue 保持 ~100 行容器胶水装配 -->
<script setup lang="ts">
import { useCardFilter } from './composables/useCardFilter'
import { useInfiniteCardList } from './composables/useInfiniteCardList'
import HeaderModeTabs from './components/HeaderModeTabs.vue'
import FilterPanel from './components/FilterPanel.vue'
import CharacterCard from './components/CharacterCard.vue'

const { activeTab, setTab } = useCardFilter()
const { cards, isLoading, loadMore } = useInfiniteCardList(activeTab)
</script>

<template>
  <div class="flex flex-col gap-3 p-4 min-h-screen">
    <HeaderModeTabs :active="activeTab" @change="setTab" />
    <FilterPanel />
    <div class="grid grid-cols-2 gap-3">
      <CharacterCard v-for="card in cards" :key="card.id" :card="card" />
    </div>
  </div>
</template>
```
