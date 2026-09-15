<script lang="ts" setup>
import {
  type IAdminUserFormData,
  type IAdminUserItem,
  type IDepartmentNode,
  type IRoleItem,
  createAdminUser,
  updateAdminUser,
} from '@/api/rbac';
import { OP_TYPE } from '@/constant';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage } from 'element-plus';
import { type Ref, computed, inject, ref, watch } from 'vue';

const userGlobalData = inject('userGlobalData') as Ref<{
  roleList: IRoleItem[];
  deptList: IDepartmentNode[];
}>;

const props = withDefaults(
  defineProps<{ isVisible: boolean; data: Partial<IAdminUserItem>; type: OP_TYPE }>(),
  {},
);

const emits = defineEmits(['update:isVisible', 'onRefresh']);

const title = computed(() => {
  return props.type === OP_TYPE.ADD ? '新增管理员' : '修改管理员资料';
});

const loading = ref(false);
const formRef = ref<FormInstance>();

const form = ref<IAdminUserFormData & { id?: string }>({
  id: '',
  username: '',
  email: '',
  real_name: '',
  password: '',
  phone: '',
  job_number: '',
  department_id: '',
  role_ids: [],
  status: 'active',
});

// 是否为超级管理员账号
const isSuperAdmin = computed(() => {
  return form.value.username === 'superadmin' || props.data?.is_super_admin === true;
});

const rules = computed<FormRules>(() => ({
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  real_name: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入工作邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效邮箱格式', trigger: 'blur' },
  ],
  password: [
    { required: props.type === OP_TYPE.ADD, message: '请输入登录初始密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 位', trigger: 'blur' },
  ],
}));

// 获取超级管理员的角色 ID
const getSuperRoleId = () => {
  const superRole = userGlobalData.value?.roleList?.find((r) => r.role_key === 'super_admin');
  return superRole ? superRole.id : null;
};

watch(
  () => props.isVisible,
  (val) => {
    if (val) {
      if (props.type === OP_TYPE.EDIT && props.data) {
        const initialRoleIds = props.data.roles?.map((r) => r.id) || [];
        // 超管强制带上 super_admin 角色
        if (props.data.username === 'superadmin' || props.data.is_super_admin) {
          const superId = getSuperRoleId();
          if (superId && !initialRoleIds.includes(superId)) {
            initialRoleIds.unshift(superId);
          }
        }
        form.value = {
          id: props.data.id || '',
          username: props.data.username || '',
          email: props.data.email || '',
          real_name: props.data.real_name || '',
          password: '',
          phone: props.data.phone || '',
          job_number: props.data.job_number || '',
          department_id: props.data.department_id || '',
          role_ids: initialRoleIds,
          status: props.data.status || 'active',
        };
      } else {
        form.value = {
          id: '',
          username: '',
          email: '',
          real_name: '',
          password: '',
          phone: '',
          job_number: '',
          department_id: '',
          role_ids: [],
          status: 'active',
        };
      }
      formRef.value?.clearValidate();
    }
  },
);

// 监听角色变动，超管不可移除 super_admin
const handleRoleChange = (val: string[]) => {
  if (isSuperAdmin.value) {
    const superId = getSuperRoleId();
    if (superId && !val.includes(superId)) {
      ElMessage.warning('超级管理员必须保留【超级管理员】角色');
      form.value.role_ids.unshift(superId);
    }
  }
};

const close = () => {
  emits('update:isVisible', false);
};

const submit = async () => {
  if (!formRef.value) return;
  const valid = await formRef.value.validate();
  if (!valid) return;

  // 超管前置安全校验
  if (isSuperAdmin.value) {
    if (form.value.status === 'disabled') {
      ElMessage.error('超级管理员账号禁止禁用');
      form.value.status = 'active';
      return;
    }
    const superId = getSuperRoleId();
    if (superId && !form.value.role_ids.includes(superId)) {
      ElMessage.error('超级管理员账号必须拥有超级管理员角色 (super_admin)');
      form.value.role_ids.unshift(superId);
      return;
    }
  }

  try {
    loading.value = true;
    if (props.type === OP_TYPE.ADD) {
      await createAdminUser(form.value);
      ElMessage.success('管理员创建成功');
    } else if (props.type === OP_TYPE.EDIT && form.value.id) {
      await updateAdminUser(form.value.id, {
        email: form.value.email,
        real_name: form.value.real_name,
        phone: form.value.phone,
        job_number: form.value.job_number,
        department_id: form.value.department_id || null,
        role_ids: form.value.role_ids,
        status: form.value.status,
      });
      ElMessage.success('管理员资料更新成功');
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
        <el-form-item label="登录账号" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入管理员登录账号"
            :disabled="type === OP_TYPE.EDIT"
          />
        </el-form-item>

        <el-form-item label="真实姓名" prop="real_name">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>

        <el-form-item label="工作邮箱" prop="email">
          <el-input v-model="form.email" placeholder="如 admin@spikeai.internal" />
        </el-form-item>

        <el-form-item
          v-if="type === OP_TYPE.ADD"
          label="初始密码"
          prop="password"
        >
          <el-input
            v-model="form.password"
            type="password"
            show-password
            placeholder="不少于6位密码"
          />
        </el-form-item>

        <el-form-item label="员工工号" prop="job_number">
          <el-input v-model="form.job_number" placeholder="如 SA001" />
        </el-form-item>

        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="form.phone" placeholder="手机联系方式" />
        </el-form-item>

        <el-form-item label="所属部门" prop="department_id">
          <el-tree-select
            v-model="form.department_id"
            :data="userGlobalData.deptList"
            :props="{ label: 'name', children: 'children' }"
            node-key="id"
            value-key="id"
            placeholder="请选择所属部门"
            check-strictly
            clearable
            class="w-full"
          />
        </el-form-item>

        <el-form-item label="账号状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="disabled" :disabled="isSuperAdmin">
              禁用
              <span v-if="isSuperAdmin" class="text-[10px] text-[var(--el-text-color-placeholder)] ml-1">
                (超管不可禁用)
              </span>
            </el-radio>
          </el-radio-group>
        </el-form-item>
      </div>

      <el-form-item label="分配角色" prop="role_ids">
        <el-select
          v-model="form.role_ids"
          multiple
          placeholder="请选择赋予的管理角色"
          class="w-full"
          @change="handleRoleChange"
        >
          <el-option
            v-for="item in userGlobalData.roleList"
            :key="item.id"
            :label="item.name"
            :value="item.id"
            :disabled="isSuperAdmin && item.role_key === 'super_admin'"
          >
            <!-- 左右两端对齐，避免 float 破坏 element-plus 对勾布局 -->
            <div class="flex items-center justify-between w-full pr-5">
              <span class="text-xs font-medium text-[var(--el-text-color-primary)]">
                {{ item.name }}
              </span>
              <span class="text-[11px] font-mono text-[var(--el-text-color-placeholder)]">
                {{ item.role_key }}
              </span>
            </div>
          </el-option>
        </el-select>
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
