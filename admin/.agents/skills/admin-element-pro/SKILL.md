---
name: admin-element-pro
description: Vue 3.5 + Element Plus 2.x + VXE-Table + UnoCSS 中后台管理系统开发专家规范
---

# Admin Element Pro — 中后台管理界面与路由开发规范

本 Skill 专门指导在 `admin/` 项目作用域下的中后台管理功能开发、动态权限路由扩展、DataTable 高级表格应用以及表单弹窗标准范式。

---

## 一、 页面开发标准结构范式 (Standard CRUD Pattern)

一个规范的中后台业务页面 (`src/views/{feature}/index.vue`) 必须具备以下结构：

```vue
<script lang="ts" setup>
import { ref, reactive } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import type { IItemInfo, ItemQueryParams } from '@/api/{feature}/type';
import { getItemListPage, deleteItem, updateItemStatus } from '@/api/{feature}';
import ItemOpDialog from './components/itemOpDialog.vue';

// 1. 表格列配置
const columns = ref([
  { field: 'id', title: 'ID', width: 80 },
  { field: 'name', title: '名称' },
  { field: 'status', title: '状态', slot: 'status' },
  { field: 'createTime', title: '创建时间' }
]);

// 2. 分页与查询状态
const tableQuery = reactive<PageQuery>({
  page: 1,
  size: 10,
  filter: '',
  order: ''
});

const filter = reactive({
  keyword: '',
  status: ''
});

const tableData = ref<PageResult<IItemInfo>>({
  totalPages: 0,
  total: 0,
  number: 1,
  size: 10,
  list: []
});

const loading = ref(false);

// 3. 核心加载逻辑
const search = async () => {
  loading.value = true;
  try {
    const res = await getItemListPage(tableQuery);
    tableData.value = res.data;
  } catch (error: any) {
    ElMessage.error(error.message || '加载列表失败');
  } finally {
    loading.value = false;
  }
};
search();

// 4. 操作确认
const handleDelete = (row: IItemInfo) => {
  ElMessageBox.confirm(`确认删除「${row.name}」吗？`, '安全警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    await deleteItem(row.id);
    ElMessage.success('删除成功');
    search();
  }).catch(() => {});
};
</script>

<template>
  <div class="table-page-container">
    <!-- 1. 筛选条件区 (UnoCSS Flex 优先，杜绝复杂 SCSS) -->
    <el-form inline :model="filter" class="filter-form-wrap" @submit.prevent="search">
      <el-form-item label="关键词：">
        <el-input v-model="filter.keyword" placeholder="请输入关键词" clearable />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="search">查询</el-button>
        <el-button @click="resetFilter">重置</el-button>
      </el-form-item>
    </el-form>

    <!-- 2. 数据表格主体 -->
    <DataTable
      :loading="loading"
      :table-data="tableData"
      :table-query="tableQuery"
      :columns="columns"
      @refresh="search"
      @current-change="((tableQuery.page = $event), search())"
      @size-change="((tableQuery.size = $event), search())"
    >
      <template #status="{ row }">
        <el-tag :type="row.status === 1 ? 'success' : 'info'">
          {{ row.status === 1 ? '启用' : '禁用' }}
        </el-tag>
      </template>
    </DataTable>
  </div>
</template>
```

---

## 二、 动态权限路由添加规范

在 `src/routers/modules/` 中新建或扩展模块路由：
1. 一级路由挂载 `Layout` 组件：`component: Layout`；
2. 子路由声明在 `children` 数组中，并在 `meta` 中定义：
   - `title`: 页面标题（用于侧边栏与页签显示）；
   - `icon`: 菜单图标（Element Plus 图标或 Remix 图标）；
   - `role`: 权限角色数组（可选，RBAC 授权匹配）；
3. 将模块导入并展开到 `src/routers/index.ts` 的 `asyncRoutes` 列表中。

---

## 三、 表单弹窗 (Dialog) 交互准则

1. 私有弹窗统一定义在当前页面的 `components/` 目录下；
2. 接收 `isVisible`（通过 `v-model:is-visible` 双向绑定）以及操作对象数据；
3. 表单必须配备 `rules` 规则与 `formRef.value.validate()` 校验；
4. 提交保存必须带 `submitLoading` 状态，防止表单重复提交；
5. 保存成功后 emit `'on-refresh'` 触发父组件列表无缝刷新。
