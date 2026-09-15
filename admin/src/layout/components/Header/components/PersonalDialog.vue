<template>
  <el-dialog
    v-model="dialogVisible"
    title="修改个人登录密码"
    width="460px"
    destroy-on-close
    :close-on-click-modal="false"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="96px"
      label-position="right"
      class="py-2"
    >
      <el-form-item label="当前账号">
        <span class="font-bold text-xs font-mono text-[var(--el-text-color-primary)]">
          {{ username }}
        </span>
      </el-form-item>

      <el-form-item label="当前旧密码" prop="old_password">
        <el-input
          v-model="formData.old_password"
          type="password"
          show-password
          placeholder="请输入当前生效的旧密码"
        />
      </el-form-item>

      <el-form-item label="新登录密码" prop="new_password">
        <el-input
          v-model="formData.new_password"
          type="password"
          show-password
          placeholder="请输入新密码 (不少于6位)"
        />
      </el-form-item>

      <el-form-item label="确认新密码" prop="confirm_password">
        <el-input
          v-model="formData.confirm_password"
          type="password"
          show-password
          placeholder="请再次输入新密码"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="submit">
          确定修改
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { changePasswordApi } from '@/api/auth';
import { useUserStore } from '@/store/modules/user';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { computed, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const userStore = useUserStore();

const dialogVisible = ref(false);
const loading = ref(false);
const formRef = ref<FormInstance>();

const username = computed(() => userStore.userInfo?.username || 'admin');

const formData = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
});

const validateConfirmPwd = (_rule: any, value: string, callback: any) => {
  if (value !== formData.new_password) {
    callback(new Error('两次输入的新密码不一致'));
  } else {
    callback();
  }
};

const rules: FormRules = {
  old_password: [{ required: true, message: '请输入当前旧密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新登录密码', trigger: 'blur' },
    { min: 6, message: '新密码长度不能少于 6 位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请确认新登录密码', trigger: 'blur' },
    { validator: validateConfirmPwd, trigger: 'blur' },
  ],
};

function show() {
  formData.old_password = '';
  formData.new_password = '';
  formData.confirm_password = '';
  dialogVisible.value = true;
  formRef.value?.clearValidate();
}

async function submit() {
  if (!formRef.value) return;
  const valid = await formRef.value.validate();
  if (!valid) return;

  try {
    loading.value = true;
    await changePasswordApi({
      old_password: formData.old_password,
      new_password: formData.new_password,
    });
    ElMessage.success('密码修改成功，请使用新密码重新登录');
    dialogVisible.value = false;
    // 强制登出并跳转登录页
    await userStore.logout(router);
  } catch (error: any) {
    ElMessage.error(error?.message || '修改密码失败');
  } finally {
    loading.value = false;
  }
}

defineExpose({
  show,
});
</script>
