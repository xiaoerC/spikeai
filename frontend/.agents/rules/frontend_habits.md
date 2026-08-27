---
description: 前端工程专属排版、架构、组件库、状态与流式交互铁律 (自动生效)
always_on: true
---

# 前端核心排版、架构、组件库、状态与流式交互铁律

在编写或修改 `frontend/` 目录下的任何 Vue / TypeScript / CSS / HTML 代码时，强制执行以下 9 项规范：

1. **UnoCSS 绝对优先 (UnoCSS First)**：
   - 能使用 UnoCSS 原子类解决的，严禁使用原生 `<style>` 标签或内联 `style=""`。
   - 高频/复杂暗黑玻璃拟物样式统一通过 `uno.config.ts` shortcuts 抽象复用。
2. **现代布局铁律 (Flex & Grid Only)**：
   - 布局排版一律使用 **Flexbox**（一维流式）与 **Grid**（二维网格/卡片阵列）。
   - 严禁使用 `float`、`display: inline-block`、`display: table` 或多余的绝对定位偏移来模拟流式排列。
3. **间距由 Gap 主导 (Gap-Driven Spacing)**：
   - 兄弟元素/列表条目之间的间距，一律在父容器上使用 `gap-*`、`gap-x-*`、`gap-y-*` 控制。
   - 严禁在子元素上写 `mr-*`、`mb-*` 然后用 `:last-child` 擦屁股；`padding` 仅用于内嵌呼吸留白，`margin` 保持极度克制。
4. **组件库优先与杜绝 Ad-hoc (UI Component Standards)**：
   - 交互按钮一律使用 `@/components/common` 下的 `<AppButton>`。
   - 移动端多选项/长表单/筛选一律使用 `<AppDrawer>` (BottomSheet 手势抽屉)。
   - 关键居中确认/登录弹窗一律使用 `<AppModal>`。
5. **绝对禁止浏览器原生 Alert/Confirm/Prompt (Zero Native Dialogs)**：
   - ❌ **严禁在任何业务代码、退出登录、异常捕获或调试逻辑中调用 `window.alert()`、`confirm()` 或 `prompt()`**。原生白框弹窗严重破坏黑金沉浸感与移动端体验。
   - ✅ 所有用户通知、操作结果反馈（如“已退出登录”、“复制成功”、“保存成功”）必须使用非阻塞的 **Toast 轻提示**，或统一调用 `<AppModal>` / `<AppDrawer>` 进行确认交互。
6. **特性/领域内聚与就近原则 (Feature-First & Colocation)**：
   - 拒绝扁平分层（Layer-First）。属于特定页面的私有组件、业务 composables、constants、utils、types 必须**就近收敛**在对应的 `src/views/{feature}/` 自治目录内。
   - 页面主入口 `index.vue` 遵循**容器模式 (Smart Container)**：只做状态与组件的装配分发（保持在 ~100 行内）。
7. **公共组件严格升格机制 (Promotion Rule)**：
   - 全局 `src/components/common/` 仅存放纯粹、无业务绑定的通用 UI 基础设施（如 `AppButton`, `AppModal`, `AppDrawer`, `AppTabs`）。
   - 仅当某逻辑/组件被 **≥ 2 个独立业务页面** 共同引用时，才允许“升格”提取到全局目录。
8. **大厂级 Composition API 组织与 Composable 4 大铁律**：
   - **组件内注释功能域**：小组件内代码按 `/** 功能域 */` 注释分块，将专属的 `ref + computed + methods + watch/mounted` 物理就近聚拢，禁止按技术类型上下分散。
   - **Composable 入参**：灵活支持 `MaybeRefOrGetter<T>` 配合 `toValue()`。
   - **Composable 返回值**：普通对象包裹 `ref`（`{ count, inc }`），严禁返回裸 `reactive` 导致解构丢响应。
   - **自闭环清理与状态保护**：内部监听器在 `onUnmounted` 自动清理；对外暴露的状态使用 `readonly()` 保护。
9. **强类型 API 契约与 SSE 流式状态流转 (API & SSE Streaming)**：
   - 所有网络请求必须收敛在 `src/services/` 经泛型统一包装，严禁在组件中写裸 `fetch` 或 `axios`。
   - 对话剧场 SSE 消费必须具备 `AbortController` 取消机制与 `requestAnimationFrame` 60fps 平滑打字机调度。
   - Pinia 状态严格遵循单向数据流变更；大型离线角色卡及分支历史禁止挤占 LocalStorage，统一采用异步 IndexedDB 持久化。
