<script lang="ts" setup>
import {
  type IDepartmentNode,
  deleteDepartment,
  getDepartmentTree,
  updateDepartment,
} from '@/api/rbac';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { OP_TYPE } from '@/constant';
import DeptOpDialog from '@/views/om/department/components/deptOpDialog.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { onMounted, ref } from 'vue';

const loading = ref(false);
const deptTree = ref<IDepartmentNode[]>([]);

const columns: IColumnConfig[] = [
  { field: 'name', title: '部门名称', minWidth: 220, treeNode: true },
  { field: 'leader', title: '团队负责人', minWidth: 120, slot: 'leader' },
  { field: 'phone', title: '联系电话', width: 140, align: 'center', slot: 'phone' },
  { field: 'sort', title: '排序权重', width: 100, align: 'center' },
  { field: 'status', title: '状态', width: 100, align: 'center', slot: 'status' },
  { field: 'created_at', title: '创建时间', width: 170, align: 'center', slot: 'created_at' },
  { field: 'actions', title: '操作', width: 220, fixed: 'right', align: 'center', slot: 'actions' },
];

// 拉取部门树
const fetchDeptTree = async () => {
  loading.value = true;
  try {
    const res = await getDepartmentTree();
    deptTree.value = res;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchDeptTree();
});

// 操作弹窗
const dialogVisible = ref(false);
const dialogType = ref<OP_TYPE>(OP_TYPE.ADD);
const currentRow = ref<Partial<IDepartmentNode>>({});

// 新增顶级或子部门
const handleCreate = (parentId?: string) => {
  dialogType.value = OP_TYPE.ADD;
  currentRow.value = { parent_id: parentId };
  dialogVisible.value = true;
};

// 编辑部门
const handleEdit = (row: any) => {
  dialogType.value = OP_TYPE.EDIT;
  currentRow.value = { ...row };
  dialogVisible.value = true;
};

// 状态切换
const handleStatusChange = async (row: any) => {
  try {
    await updateDepartment(row.id, { status: row.status });
    ElMessage.success('部门状态已更新');
  } catch {
    row.status = row.status === 'active' ? 'disabled' : 'active';
  }
};

// 删除部门
const handleDelete = (row: any) => {
  if (row.children && row.children.length > 0) {
    ElMessage.warning('该部门包含子部门，请先处理子部门后再删除');
    return;
  }

  ElMessageBox.confirm(`确认删除部门组织 [${row.name}] 吗？`, '删除警告', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  }).then(async () => {
    await deleteDepartment(row.id);
    ElMessage.success('部门已成功删除');
    fetchDeptTree();
  });
};
</script>

<template>
  <div class="w-full p-4 flex flex-col gap-4">
    <DataTable
      :table-data="deptTree"
      :columns="columns"
      :loading="loading"
      :show-pager="false"
      :show-index="false"
      :tree-default-node="{ childrenField: 'children' }"
      table-title="组织架构与部门管理"
      @refresh="fetchDeptTree"
    >
      <template #options>
        <el-button
          v-auth="['system:dept:create']"
          type="primary"
          icon="Plus"
          @click="handleCreate()"
        >
          新增顶级部门
        </el-button>
      </template>

      <template #leader="{ row }">
        <span>{{ row.leader || '-' }}</span>
      </template>

      <template #phone="{ row }">
        <span class="font-mono text-xs">{{ row.phone || '-' }}</span>
      </template>

      <template #status="{ row }">
        <el-switch
          v-model="row.status"
          active-value="active"
          inactive-value="disabled"
          @change="handleStatusChange(row)"
        />
      </template>

      <template #created_at="{ row }">
        <span class="text-xs text-gray-500 font-mono">
          {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
        </span>
      </template>

      <template #actions="{ row }">
        <div class="flex justify-center items-center gap-1">
          <el-button
            v-auth="['system:dept:create']"
            type="primary"
            link
            size="small"
            @click="handleCreate(row.id)"
          >
            添加子部门
          </el-button>
          <el-button
            v-auth="['system:dept:update']"
            type="primary"
            link
            size="small"
            @click="handleEdit(row)"
          >
            编辑
          </el-button>
          <el-button
            v-auth="['system:dept:delete']"
            type="danger"
            link
            size="small"
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </div>
      </template>
    </DataTable>

    <!-- 部门操作弹窗 -->
    <DeptOpDialog
      v-model:is-visible="dialogVisible"
      :data="currentRow"
      :type="dialogType"
      :tree-data="deptTree"
      @on-refresh="fetchDeptTree"
    />
  </div>
</template>
