<script lang="ts" setup>
import {
  type IDepartmentFormData,
  type IDepartmentNode,
  createDepartment,
  updateDepartment,
} from '@/api/rbac';
import { OP_TYPE } from '@/constant';
import type { FormInstance, FormRules } from 'element-plus';
import { ElMessage } from 'element-plus';

const props = withDefaults(
  defineProps<{
    isVisible: boolean;
    data: Partial<IDepartmentNode>;
    type: OP_TYPE;
    treeData: IDepartmentNode[];
  }>(),
  {},
);

const emits = defineEmits(['update:isVisible', 'onRefresh']);

const title = computed(() => {
  return props.type === OP_TYPE.ADD ? '新增部门组织' : '编辑部门信息';
});

const loading = ref(false);
const formRef = ref<FormInstance>();

const form = ref<IDepartmentFormData & { id?: string }>({
  id: '',
  parent_id: undefined,
  name: '',
  leader: '',
  phone: '',
  sort: 0,
  status: 'active',
});

const rules = reactive<FormRules>({
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
});

// 可选父部门选项树 (根部门选项)
const deptTreeOptions = computed(() => {
  return [
    {
      id: null,
      name: '顶级组织 (无上级)',
      children: props.treeData,
    },
  ];
});

watch(
  () => props.isVisible,
  (val) => {
    if (val) {
      if (props.type === OP_TYPE.EDIT && props.data) {
        form.value = {
          id: props.data.id || '',
          parent_id: props.data.parent_id || undefined,
          name: props.data.name || '',
          leader: props.data.leader || '',
          phone: props.data.phone || '',
          sort: props.data.sort || 0,
          status: props.data.status || 'active',
        };
      } else {
        form.value = {
          id: '',
          parent_id: props.data?.parent_id || undefined,
          name: '',
          leader: '',
          phone: '',
          sort: 0,
          status: 'active',
        };
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

  try {
    loading.value = true;
    if (props.type === OP_TYPE.ADD) {
      await createDepartment(form.value);
      ElMessage.success('部门创建成功');
    } else if (props.type === OP_TYPE.EDIT && form.value.id) {
      await updateDepartment(form.value.id, {
        parent_id: form.value.parent_id || null,
        name: form.value.name,
        leader: form.value.leader,
        phone: form.value.phone,
        sort: form.value.sort,
        status: form.value.status,
      });
      ElMessage.success('部门更新成功');
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
    width="550px"
    destroy-on-close
    @close="close"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="上级部门" prop="parent_id">
        <el-tree-select
          v-model="form.parent_id"
          :data="deptTreeOptions"
          :props="{ label: 'name', children: 'children' }"
          node-key="id"
          value-key="id"
          placeholder="选择上级部门 (不选则为顶级组织)"
          check-strictly
          clearable
          class="w-full"
        />

      </el-form-item>

      <el-form-item label="部门名称" prop="name">
        <el-input v-model="form.name" placeholder="如 算法工程研发组" />
      </el-form-item>

      <el-form-item label="负责人" prop="leader">
        <el-input v-model="form.leader" placeholder="部门团队负责人姓名" />
      </el-form-item>

      <el-form-item label="联系电话" prop="phone">
        <el-input v-model="form.phone" placeholder="联系电话或办公分机" />
      </el-form-item>

      <div class="grid grid-cols-2 gap-x-4">
        <el-form-item label="显示排序" prop="sort">
          <el-input-number v-model="form.sort" :min="0" :max="999" class="w-full" />
        </el-form-item>

        <el-form-item label="状态" prop="status">
          <el-radio-group v-model="form.status">
            <el-radio value="active">启用</el-radio>
            <el-radio value="disabled">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="close">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submit">确定保存</el-button>
      </div>
    </template>
  </el-dialog>
</template>
