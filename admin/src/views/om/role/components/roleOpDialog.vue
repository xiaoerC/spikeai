<script lang="ts" setup>
import {
  type IPermissionTreeNode,
  type IRoleFormData,
  type IRoleItem,
  createAdminRole,
  getPermissionsTree,
  updateAdminRole,
} from '@/api/rbac';
import { OP_TYPE } from '@/constant';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage, type ElTree } from 'element-plus';

const props = withDefaults(
  defineProps<{ isVisible: boolean; data: Partial<IRoleItem>; type: OP_TYPE }>(),
  {},
);

const emits = defineEmits(['update:isVisible', 'onRefresh']);

const title = computed(() => {
  return props.type === OP_TYPE.ADD ? '新增角色' : '编辑角色与分配权限';
});

const loading = ref(false);
const formRef = ref<FormInstance>();
const treeRef = ref<InstanceType<typeof ElTree>>();

const permTreeData = ref<IPermissionTreeNode[]>([]);
const permTreeLoading = ref(false);

const form = ref<IRoleFormData & { id?: string }>({
  id: '',
  role_key: '',
  name: '',
  description: '',
  sort: 0,
  status: 'active',
  permission_ids: [],
});

const rules = reactive<FormRules>({
  role_key: [
    { required: true, message: '请输入角色英文唯一标识', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z0-9_]{2,32}$/,
      message: '由 2-32 位字母、数字或下划线组成',
      trigger: 'blur',
    },
  ],
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
});

// 加载全量系统权限树
const fetchPermTree = async () => {
  permTreeLoading.value = true;
  try {
    const res = await getPermissionsTree();
    permTreeData.value = res;
  } catch (e) {
    console.error('加载权限树异常:', e);
  } finally {
    permTreeLoading.value = false;
  }
};

watch(
  () => props.isVisible,
  async (val) => {
    if (val) {
      if (!permTreeData.value.length) {
        await fetchPermTree();
      }
      if (props.type === OP_TYPE.EDIT && props.data) {
        form.value = {
          id: props.data.id || '',
          role_key: props.data.role_key || '',
          name: props.data.name || '',
          description: props.data.description || '',
          sort: props.data.sort || 0,
          status: props.data.status || 'active',
          permission_ids: props.data.permission_ids || [],
        };
        // 勾选已有权限
        nextTick(() => {
          treeRef.value?.setCheckedKeys(props.data.permission_ids || []);
        });
      } else {
        form.value = {
          id: '',
          role_key: '',
          name: '',
          description: '',
          sort: 0,
          status: 'active',
          permission_ids: [],
        };
        nextTick(() => {
          treeRef.value?.setCheckedKeys([]);
        });
      }
      formRef.value?.clearValidate();
    }
  },
);

const close = () => {
  emits('update:isVisible', false);
};

const submit = async () => {
  if (!formRef.value) return;
  const valid = await formRef.value.validate();
  if (!valid) return;

  // 获取勾选的权限 ID 列表 (包含全选和半选节点)
  const checkedKeys = (treeRef.value?.getCheckedKeys() as string[]) || [];
  const halfCheckedKeys = (treeRef.value?.getHalfCheckedKeys() as string[]) || [];
  const allSelectedPermIds = Array.from(new Set([...checkedKeys, ...halfCheckedKeys]));

  try {
    loading.value = true;
    if (props.type === OP_TYPE.ADD) {
      await createAdminRole({
        ...form.value,
        permission_ids: allSelectedPermIds,
      });
      ElMessage.success('角色创建成功');
    } else if (props.type === OP_TYPE.EDIT && form.value.id) {
      await updateAdminRole(form.value.id, {
        name: form.value.name,
        description: form.value.description,
        sort: form.value.sort,
        status: form.value.status,
        permission_ids: allSelectedPermIds,
      });
      ElMessage.success('角色与权限已更新');
    }
    emits('onRefresh');
    close();
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <el-dialog
    :title="title"
    :model-value="isVisible"
    width="650px"
    destroy-on-close
    @close="close"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="110px"
      label-position="right"
    >
      <div class="grid grid-cols-2 gap-x-4">
        <el-form-item label="角色标识" prop="role_key">
          <el-input
            v-model="form.role_key"
            placeholder="如 content_auditor"
            :disabled="type === OP_TYPE.EDIT"
          />
        </el-form-item>

        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="如 内容审核专员" />
        </el-form-item>

        <el-form-item label="显示排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" :max="999" class="w-full" />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="disabled">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </div>

      <el-form-item label="职责描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
          placeholder="说明该角色的业务职能与系统操作范围"
        />

      </el-form-item>

      <el-form-item label="菜单与权限">
        <div class="w-full border border-gray-200 dark:border-zinc-700 rounded p-3 max-h-60 overflow-y-auto">
          <el-tree
            ref="treeRef"
            v-loading="permTreeLoading"
            :data="permTreeData"
            :props="{ label: 'title', children: 'children' }"
            show-checkbox
            node-key="id"
            default-expand-all
            highlight-current
          >
            <template #default="{ data }">
              <div class="flex items-center gap-2">
                <span>{{ data.title }}</span>
                <el-tag
                  size="small"
                  :type="data.type === 'directory' ? 'info' : data.type === 'menu' ? 'primary' : 'success'"
                >
                  {{ data.type === 'directory' ? '目录' : data.type === 'menu' ? '菜单' : '按钮' }}
                </el-tag>
                <span class="text-xs text-gray-400">{{ data.code }}</span>
              </div>
            </template>
          </el-tree>
        </div>
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submit">确定保存</el-button>
      </div>
    </template>
  </el-dialog>
</template>
