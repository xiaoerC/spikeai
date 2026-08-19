---
name: naro-ui-components
description: SpikeAI / 叙梦 Naro 前端通用基础组件库 (AppButton, AppModal, AppDrawer, AppTabs) 与无头原语 (Reka UI + Vaul Vue + UnoCSS) 使用指南与大厂级最佳实践。
license: MIT
file_patterns:
  - "frontend/src/components/common/**/*"
  - "frontend/src/views/**/*.vue"
  - "frontend/uno.config.ts"
triggers:
  - "AppButton"
  - "AppModal"
  - "AppDrawer"
  - "AppTabs"
  - "Reka UI"
  - "Vaul Vue"
  - "BottomSheet"
  - "Dialog"
  - "Common UI components"
---

# 叙梦 Naro 前端组件库与无头交互体系最佳实践指南 (Naro UI Components)

本指南针对项目已封装的通用黑金暗黑玻璃拟物组件库（位于 `@/components/common`），结合大厂级设计系统（Design System）规范与无头交互原语（Reka UI + Vaul Vue + UnoCSS），提供标准化的使用范式与扩展原则。

---

## 一、 核心架构与引入规范

组件库基于 **“无头状态机 + UnoCSS 黑金拟物皮肤”** 模式构建。所有基础组件均支持从 `@/components/common` 统一解构引入：

```ts
import { AppButton, AppModal, AppDrawer, AppTabs } from '@/components/common'
import type { ButtonVariant, ButtonSize, TabItem, TabsVariant } from '@/components/common'
```

---

## 二、 基础组件详细 API 与实战范式

### 1. `AppDrawer` —— 移动端 iOS 物理阻尼手势抽屉 (基于 Vaul Vue)

专为 Mobile-First 设计的半屏/多档位下拉手势抽屉。自带黑金磨砂玻璃面板（`#1A1714`）、Safe Area 底部避让与触控阻尼。

#### Props & Emits
| 属性名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `v-model:open` | `boolean` | **必填** | 抽屉显隐状态 |
| `title` | `string` | `""` | 顶部标题文本 |
| `description` | `string` | `""` | 辅助描述文本 |
| `showHandle` | `boolean` | `true` | 是否展示顶部拖拽指示条 (Handle) |
| `showClose` | `boolean` | `false` | 是否展示右上角关闭 X 按钮 |
| `snapPoints` | `(string \| number)[]` | `undefined` | 多档位吸附高度（如 `['320px', '640px', 1]`） |
| `customClass` | `string` | `""` | 注入内容面板的额外 UnoCSS 类名 |

#### 插槽 (Slots)
- `default`: 抽屉主滚动内容区（自动包裹 `overflow-y-auto` 与 `pb-safe`）。
- `#header`: 自定义顶部栏（替换默认标题与描述）。
- `#footer`: 底部固定操作区（自带 `border-t` 与 `pb-safe`）。

#### 💡 实操范式：模型选择与过滤抽屉
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { AppDrawer, AppButton } from '@/components/common'

const isModelDrawerOpen = ref(false)
const selectedModel = ref('deepseek-v3')

function handleConfirm() {
  // 业务逻辑
  isModelDrawerOpen.value = false
}
</script>

<template>
  <AppDrawer
    v-model:open="isModelDrawerOpen"
    title="模型渠道切换"
    description="选择适合当前角色对话的底层大语言模型"
    :snap-points="['380px', '700px', 1]"
    show-close
  >
    <!-- 抽屉滚动内容 -->
    <div class="flex flex-col gap-2.5">
      <div 
        v-for="model in ['deepseek-v3', 'claude-3-7-sonnet', 'gpt-4o']" 
        :key="model"
        class="p-3.5 rounded-xl border border-obsidian-border bg-obsidian-surface hover:border-naro-gold/50 cursor-pointer flex items-center justify-between"
        :class="{ 'border-naro-gold bg-naro-gold/10': selectedModel === model }"
        @click="selectedModel = model"
      >
        <span class="font-medium text-gray-200">{{ model }}</span>
        <span v-if="selectedModel === model" class="i-carbon-checkmark text-naro-gold text-lg" />
      </div>
    </div>

    <!-- 底部固定吸底操作区 -->
    <template #footer>
      <div class="flex items-center gap-3">
        <AppButton variant="ghost" class="flex-1" @click="isModelDrawerOpen = false">取消</AppButton>
        <AppButton variant="gold" class="flex-1" @click="handleConfirm">应用切换</AppButton>
      </div>
    </template>
  </AppDrawer>
</template>
```

---

### 2. `AppModal` —— 黑金暗黑玻璃模态对话框 (基于 Reka UI Dialog)

具备完整的 A11y 无障碍支持、键盘 ESC 监听、焦点锁定（Focus Trap）与居中自适应定位。

#### Props & Emits
| 属性名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `v-model:open` | `boolean` | **必填** | 模态框显隐状态 |
| `title` | `string` | `""` | 弹窗标题 |
| `description` | `string` | `""` | 弹窗辅助描述 |
| `showClose` | `boolean` | `true` | 是否展示右上角关闭按钮 |
| `customClass` | `string` | `""` | 弹窗卡片额外类名 (如 `max-w-md`) |

#### 💡 实操范式：登录授权与关键操作确认
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { AppModal, AppButton } from '@/components/common'

const isLoginModalOpen = ref(false)
const isLoading = ref(false)

async function submitLogin() {
  isLoading.value = true
  try {
    // 登录 API
    isLoginModalOpen.value = false
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <AppModal
    v-model:open="isLoginModalOpen"
    title="欢迎回到叙梦 Naro"
    description="登录以同步您的云端角色卡、剧情分支与星元月华资产"
  >
    <div class="flex flex-col gap-3 py-2">
      <input 
        type="text" 
        placeholder="请输入邮箱 / 账号" 
        class="w-full px-4 py-2.5 rounded-xl bg-obsidian-surface border border-obsidian-border text-gray-200 placeholder-naro-muted text-sm focus:border-naro-gold focus:outline-none"
      />
    </div>

    <template #footer>
      <AppButton variant="ghost" @click="isLoginModalOpen = false">稍后体验</AppButton>
      <AppButton variant="gold" :loading="isLoading" @click="submitLogin">立即进入</AppButton>
    </template>
  </AppModal>
</template>
```

---

### 3. `AppButton` —— 通用高质感原子按钮

支持 4 种视觉层级变体、尺寸调节、原生触感微缩放与加载态旋转图标。

#### Props & Emits
| 属性名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `variant` | `'gold' \| 'ghost' \| 'danger' \| 'outline'` | `'gold'` | 视觉层级变体 |
| `size` | `'sm' \| 'md' \| 'lg' \| 'icon'` | `'md'` | 尺寸控制 |
| `loading` | `boolean` | `false` | 异步加载旋转态 (自动阻止点击) |
| `disabled` | `boolean` | `false` | 禁用态 |
| `type` | `'button' \| 'submit' \| 'reset'` | `'button'` | 原生按钮类型 |
| `@click` | `(event: MouseEvent) => void` | - | 点击事件回调 |

#### 💡 变体使用准则
```vue
<!-- 主要高亮操作 (香槟金渐变高光) -->
<AppButton variant="gold" size="md">创建新角色</AppButton>

<!-- 次级幽暗操作 (黑曜石面板边框) -->
<AppButton variant="ghost" size="md">取消 / 返回</AppButton>

<!-- 危险警告操作 (暗红半透光晕) -->
<AppButton variant="danger" size="sm">删除此分支</AppButton>

<!-- 描边轻量操作 (金线通透) -->
<AppButton variant="outline" size="sm">导出 PNG 角色卡</AppButton>

<!-- 图标专属按钮 -->
<AppButton variant="ghost" size="icon">
  <span class="i-carbon-settings text-lg" />
</AppButton>
```

---

### 4. `AppTabs` —— 黑金分栏切换组件 (基于 Reka UI Tabs)

支持左右方向键键盘漫游、胶囊态（`pills`）与下划线态（`line`），支持角标（Badge）。

#### Props & Emits
| 属性名 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `v-model` | `string` | **必填** | 当前选中的 Tab Key |
| `items` | `TabItem[]` | **必填** | `[{ value: 'all', label: '全部', badge: 12 }]` |
| `variant` | `'pills' \| 'line'` | `'pills'` | `pills` 胶囊悬浮 / `line` 底部金线 |
| `customClass` | `string` | `""` | 容器扩展类名 |

#### 💡 实操范式
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { AppTabs } from '@/components/common'
import type { TabItem } from '@/components/common'

const currentTab = ref('all')
const tabs: TabItem[] = [
  { value: 'all', label: '全部推荐' },
  { value: 'story', label: '深度剧情卡', badge: 'HOT' },
  { value: 'gentleman', label: '绅士秘境', badge: 8 }
]
</script>

<template>
  <AppTabs v-model="currentTab" :items="tabs" variant="pills" />
</template>
```

---

## 三、 大厂级开发铁律与反模式（Forbidden Anti-Patterns）

在编写前端业务组件时，必须严格遵守以下 5 条铁律：

1. ❌ **严禁手写 Ad-hoc 的 `position: fixed` 遮罩与弹窗**：
   - 必须统一使用 `AppModal` 或 `AppDrawer`。手写遮罩容易丢失 iOS 滚动穿透防护、A11y 焦点管理和 ESC 键盘关闭能力。
2. ❌ **严禁移动端硬套居中 Modal**：
   - 在手机端（`< 768px`），复杂筛选、长表单、多选项列表一律使用 **`AppDrawer` (BottomSheet)**，只有极简确认提示（如 1~2 行文案）才使用居中 `AppModal`。
3. ❌ **严禁内联硬编码颜色与按钮类名**：
   - 按钮必须使用 `<AppButton>`，杜绝在 `<div>` 或 `<button>` 上随意手写 `bg-[#f9c86d]` 或硬编码样式。
4. ❌ **严格遵循 UnoCSS 配色 Token**：
   - 背景使用 `bg-obsidian-bg` (`#0F0D0C`) 或 `bg-obsidian-surface` (`#1A1714`)。
   - 边框使用 `border-obsidian-border` (`#44403C`)。
   - 金色文字/高光使用 `text-naro-gold` (`#F9C86D`)。
5. ❌ **严格保证 Safe Area 底部留白**：
   - 任何涉及移动端底部吸底的面板或抽屉，必须带有 `pb-safe`（已内置在 `AppDrawer` 的 content/footer 中）。

---

## 四、 扩展新无头组件的方法 (Using Reka UI)

如需增加下拉菜单（DropdownMenu）、下拉选择器（Select）、开关（Switch）等新组件：
1. 从 `reka-ui` 引入无头原语（如 `DropdownMenuRoot`, `DropdownMenuTrigger`, `DropdownMenuContent`, `DropdownMenuItem`）。
2. 在 `src/components/common/` 封装新组件，仅挂载 UnoCSS 黑金设计类（`bg-obsidian-surface border border-obsidian-border shadow-gold-card text-gray-200`）。
3. 在 `src/components/common/index.ts` 统一导出。
