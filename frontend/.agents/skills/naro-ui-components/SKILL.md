---
name: naro-ui-components
description: SpikeAI / 叙梦 Naro 前端通用基础组件库 (AppButton, AppModal, AppDrawer, AppTabs) 与无头原语 (Reka UI + Vaul Vue + UnoCSS) 使用指南。包含绝对禁止原生 alert/confirm、杜绝 Ad-hoc 弹窗与大厂级最佳实践。
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
  - "Toast feedback"
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

#### 💡 实操范式：登录授权与关键确认
```vue
<script setup lang="ts">
import { ref } from 'vue'
import { AppModal, AppButton } from '@/components/common'

const isLogoutModalOpen = ref(false)

function handleLogout() {
  // 执行退出逻辑，绝不弹原生 alert！
  isLogoutModalOpen.value = false
}
</script>

<template>
  <AppModal
    v-model:open="isLogoutModalOpen"
    title="确认退出登录"
    description="退出后将无法同步云端剧情分支与资产记录，确定退出吗？"
  >
    <template #footer>
      <AppButton variant="ghost" @click="isLogoutModalOpen = false">取消</AppButton>
      <AppButton variant="danger" @click="handleLogout">确认退出</AppButton>
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

---

### 4. `AppTabs` —— 黑金分栏切换组件 (基于 Reka UI Tabs)

支持左右方向键键盘漫游、胶囊态（`pills`）与下划线态（`line`），支持角标（Badge）。

---

## 三、 大厂级开发铁律与反模式（Forbidden Anti-Patterns）

在编写前端业务组件与交互时，必须严格遵守以下 6 条铁律：

1. ❌ **绝对禁止调用浏览器原生 `alert()` / `confirm()` / `prompt()` (Zero Native Dialogs)**：
   - 严禁出现诸如 `alert('已退出登录')` 或 `confirm('确认删除吗？')` 的原生白底弹窗！原生弹窗会破坏黑金玻璃拟物沉浸感、阻塞 JS 线程且样式无法定制。
   - **正确做法**：轻量提示使用 **Toast 轻提示**，破坏性/二次确认操作使用 **`<AppModal>`** 或 **`<AppDrawer>`**。
2. ❌ **严禁手写 Ad-hoc 的 `position: fixed` 遮罩与弹窗**：
   - 必须统一使用 `AppModal` 或 `AppDrawer`。手写遮罩容易丢失 iOS 滚动穿透防护、A11y 焦点管理和 ESC 键盘关闭能力。
3. ❌ **严禁移动端硬套居中 Modal**：
   - 在手机端（`< 768px`），复杂筛选、长表单、多选项列表一律使用 **`AppDrawer` (BottomSheet)**，只有极简确认提示（如 1~2 行文案）才使用居中 `AppModal`。
4. ❌ **严禁内联硬编码颜色与按钮类名**：
   - 按钮必须使用 `<AppButton>`，杜绝在 `<div>` 或 `<button>` 上随意手写 `bg-[#f9c86d]` 或硬编码样式。
5. ❌ **严格遵循 UnoCSS 配色 Token**：
   - 背景使用 `bg-obsidian-bg` (`#0F0D0C`) 或 `bg-obsidian-surface` (`#1A1714`)。
   - 边框使用 `border-obsidian-border` (`#44403C`)。
   - 金色文字/高光使用 `text-naro-gold` (`#F9C86D`)。
6. ❌ **严格保证 Safe Area 底部留白**：
   - 任何涉及移动端底部吸底的面板或抽屉，必须带有 `pb-safe`（已内置在 `AppDrawer` 的 content/footer 中）。
