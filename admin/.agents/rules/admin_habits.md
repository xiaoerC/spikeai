---
description: 后台管理系统 (admin/) 专属排版、架构、组件库、状态与质量门禁铁律 (自动生效)
always_on: true
---

# 后台管理工程核心排版、架构、组件库与质量门禁铁律

在编写或修改 `admin/` 目录下的任何 Vue / TypeScript / SCSS / HTML 代码时，强制执行以下 8 项铁律：

1. **UnoCSS 绝对优先与去 SCSS/CSS (UnoCSS First & Minimal SCSS)**：
   - 能使用 UnoCSS 原子类（Flexbox/Grid/Gap/Padding/Color/Dark/Border）解决的样式，**严禁写原生 `<style>` 或内联样式**。
   - 彻底减少和消除历史遗留的深层 SCSS 嵌套，高频卡片、表格容器、筛选表单优先使用 `uno.config.ts` 中的 shortcuts（如 `table-page-container`、`filter-form-wrap`、`card-base`、`flex-between` 等）。

2. **现代布局铁律 (Flex & Grid Only)**：
   - 页面排版一律使用 **Flexbox**（一维弹性伸缩）与 **Grid**（二维看板/统计卡片陈列）。
   - 严禁使用 `float`、`display: inline-block`、`display: table` 或硬编码的绝对定位来模拟页面布局。

3. **间距由 Gap 主导 (Gap-Driven Spacing)**：
   - 搜索筛选表单、操作按钮组、看板统计栅格、信息行一律在父级容器上使用 `gap-*`、`gap-x-*`、`gap-y-*` 控制元素间距。
   - 严格杜绝在子元素上滥写 `margin-right` / `margin-bottom`。

4. **统一使用 Biome 质量门禁 (Biome Only)**：
   - 本项目全面淘汰 ESLint 9 / Stylelint / Prettier。
   - 代码检查与格式化统一遵循项目根目录的 `biome.json`，提交或验证前运行 `pnpm check` 与 `pnpm format`。

5. **Element Plus 与 VXE-Table 规范使用 (Standard Components)**：
   - 中后台表单输入、选择器、开关、标签、分页一律使用 Element Plus 2.x 标准组件；
   - 复杂多列、动态列显隐控制、拖拽排序、批量选择的大型数据表统一使用 `@/components/DataTable`（基于 `vxe-table`）；
   - 严禁手写 Ad-hoc 的原生蒙版弹窗，统一使用 `<el-dialog>` 或 `<el-drawer>`。

6. **绝对禁止浏览器原生弹窗与安全操作确认 (Zero Native Dialogs & Safe Confirmation)**：
   - ❌ **严禁调用 `window.alert()` / `confirm()` / `prompt()` 原生弹窗**。
   - 删除、批量删除、重置密码、修改用户状态等敏感与破坏性操作，必须使用 `ElMessageBox.confirm` 进行二次弹窗确认；
   - 操作成功或失败必须使用非阻塞的 `ElMessage.success()` / `ElMessage.error()` 提示。

7. **强类型 API 契约与防御编程 (Type Hints & Zero Silent Failures)**：
   - 所有接口请求入参（`PageQuery` / 表单参数）与返回值（`PageResult<T>`）必须定义完整的 TypeScript 接口，严禁大面积写裸 `any`。
   - 严禁空 `try...catch` 静默吞掉异常；发生网络或业务异常时必须显式由 `ElMessage` 报错或向外抛出。

8. **特性内聚与就近原则 (Colocation & Feature-First)**：
   - 业务页面的私有弹窗组件（如 `*OpDialog.vue`）、专有类型定义就近存放在 `views/{feature}/components/` 目录下；
   - 页面主入口 `index.vue` 保持轻量，专注于筛选表单、表格装配与分页调度。
