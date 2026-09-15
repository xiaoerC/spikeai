<script lang="ts" setup>
import { type IRoleItem, deleteAdminRole, getAdminRoleList, updateAdminRole } from '@/api/rbac';
import type { IColumnConfig } from '@/components/DataTable/index.vue';
import { OP_TYPE } from '@/constant';
import RoleOpDialog from '@/views/om/role/components/roleOpDialog.vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { onMounted, ref } from 'vue';

const loading = ref(false);
const roleList = ref<IRoleItem[]>([]);

const columns: IColumnConfig[] = [
  { field: 'name', title: '角色名称', minWidth: 150, slot: 'name' },
  { field: 'role_key', title: '英文标识 (Role Key)', minWidth: 160, slot: 'role_key' },
  { field: 'description', title: '职责与权限描述', minWidth: 220, showOverflow: true },
  { field: 'sort', title: '排序', width: 90, align: 'center' },
  { field: 'status', title: '状态', width: 100, align: 'center', slot: 'status' },
  { field: 'created_at', title: '创建时间', width: 170, align: 'center', slot: 'created_at' },
  { field: 'actions', title: '操作', width: 180, fixed: 'right', align: 'center', slot: 'actions' },
];

// 拉取角色列表
const fetchRoles = async () => {
  loading.value = true;
  try {
    const res = await getAdminRoleList();
    roleList.value = res;
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchRoles();
});

// 操作弹窗
const dialogVisible = ref(false);
const dialogType = ref<OP_TYPE>(OP_TYPE.ADD);
const currentRow = ref<Partial<IRoleItem>>({});

const handleCreate = () => {
  dialogType.value = OP_TYPE.ADD;
  currentRow.value = {};
  dialogVisible.value = true;
};

const handleEdit = (row: any) => {
  dialogType.value = OP_TYPE.EDIT;
  currentRow.value = { ...row };
  dialogVisible.value = true;
};

// 状态切换
const handleStatusChange = async (row: any) => {
  if (row.role_key === 'super_admin') {
    ElMessage.warning('超级管理员角色不允许禁用');
    row.status = 'active';
    return;
  }
  try {
    await updateAdminRole(row.id, { status: row.status });
    ElMessage.success('角色状态已更新');
  } catch {
    row.status = row.status === 'active' ? 'disabled' : 'active';
  }
};

// 删除角色
const handleDelete = (row: any) => {
  if (row.role_key === 'super_admin') {
    ElMessage.warning('系统内置超级管理员角色不允许删除');
    return;
  }

  ElMessageBox.confirm(
    `确认删除角色 [${row.name}] 吗？删除后拥有该角色的用户将失去相应权限！`,
    '删除警告',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    },
  ).then(async () => {
    await deleteAdminRole(row.id);
    ElMessage.success('角色已成功删除');
    fetchRoles();
  });
};
</script>

<template>
  <div class="w-full p-4 flex flex-col gap-4">
    <DataTable
      :table-data="roleList"
      :columns="columns"
      :loading="loading"
      :show-pager="false"
      table-title="系统角色与权限分配"
      @refresh="fetchRoles"
    >
      <template #options>
        <el-button
          v-auth="['system:role:create']"
          type="primary"
          icon="Plus"
          @click="handleCreate"
        >
          新增角色
        </el-button>
      </template>

      <template #name="{ row }">
        <div class="flex items-center gap-1.5 font-medium">
          <span>{{ row.name }}</span>
          <el-tag v-if="row.role_key === 'super_admin'" size="small" type="danger">内置超管</el-tag>
        </div>
      </template>

      <template #role_key="{ row }">
        <code class="text-xs bg-gray-100 dark:bg-zinc-800 px-1.5 py-0.5 rounded text-gray-700 dark:text-zinc-300">
          {{ row.role_key }}
        </code>
      </template>

      <template #status="{ row }">
        <el-switch
          v-model="row.status"
          active-value="active"
          inactive-value="disabled"
          :disabled="row.role_key === 'super_admin'"
          @change="handleStatusChange(row)"
        />
      </template>

      <template #created_at="{ row }">
        <span class="text-xs text-gray-500 font-mono">
          {{ row.created_at?.slice(0, 19).replace('T', ' ') }}
        </span>
      </template>

      <template #actions="{ row }">
        <div class="flex justify-center items-center gap-2">
          <el-button
            v-auth="['system:role:update', 'system:role:assign_perm']"
            type="primary"
            link
            size="small"
            @click="handleEdit(row)"
          >
            编辑与授权
          </el-button>
          <el-button
            v-if="row.role_key !== 'super_admin'"
            v-auth="['system:role:delete']"
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

    <!-- 角色操作弹窗 -->
    <RoleOpDialog
      v-model:is-visible="dialogVisible"
      :data="currentRow"
      :type="dialogType"
      @on-refresh="fetchRoles"
    />
  </div>
</template>
