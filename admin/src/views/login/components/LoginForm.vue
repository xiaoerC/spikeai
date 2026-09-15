<template>
  <div class="flex flex-col items-center mb-6">
    <div class="w-14 h-14 rounded-2xl bg-amber-500/10 dark:bg-amber-400/10 border border-amber-500/20 flex items-center justify-center mb-3 shadow-inner">
      <img alt="SpikeAI Logo" class="w-9 h-9" src="@/assets/image/logo.svg" />
    </div>
    <h2 class="text-2xl font-bold tracking-tight text-slate-800 dark:text-zinc-100">
      SpikeAI 运营管理中心
    </h2>
    <p class="text-xs text-slate-500 dark:text-zinc-400 mt-1">
      智能体角色互动与平台运营管理系统
    </p>
  </div>

  <el-form ref="ruleFormRef" :model="ruleForm" :rules="rules" size="large" class="w-full">
    <el-form-item prop="username" class="mb-5">
      <el-input
        v-model="ruleForm.username"
        auto-complete="on"
        placeholder="请输入管理员账号"
        @keyup.enter="submitForm(ruleFormRef)"
      >
        <template #prefix>
          <el-icon class="text-slate-400 dark:text-zinc-500">
            <UserFilled />
          </el-icon>
        </template>
      </el-input>
    </el-form-item>

    <el-form-item prop="password" class="mb-6">
      <el-input
        v-model="ruleForm.password"
        :type="passwordType"
        auto-complete="on"
        placeholder="请输入登录密码"
        @keyup.enter="submitForm(ruleFormRef)"
      >
        <template #prefix>
          <el-icon class="text-slate-400 dark:text-zinc-500">
            <Lock />
          </el-icon>
        </template>
        <template #suffix>
          <div class="cursor-pointer text-slate-400 hover:text-slate-600 dark:hover:text-zinc-300 transition-colors" @click="showPwd">
            <svg-icon :icon-class="passwordType === 'password' ? 'eye' : 'eye-open'" />
          </div>
        </template>
      </el-input>
    </el-form-item>

    <el-form-item class="w-full mb-2">
      <el-button
        :loading="loading"
        type="primary"
        size="large"
        class="w-full !h-11 font-medium tracking-wide !rounded-lg"
        @click="submitForm(ruleFormRef)"
      >
        登 录
      </el-button>
    </el-form-item>
  </el-form>
</template>

<script lang="ts" setup>
import { useUserStore } from '@/store/modules/user';
import { getTimeStateStr } from '@/utils/index';
import type { FormInstance, FormRules } from 'element-plus';
import { ElNotification } from 'element-plus';
import { reactive, ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const UserStore = useUserStore();
const ruleFormRef = ref<FormInstance>();
const passwordType = ref('password');
const loading = ref(false);

const rules = reactive<FormRules>({
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入登录密码', trigger: 'blur' }],
});

// 默认不预填密码，满足正式商用上线安全规范
const ruleForm = reactive({
  username: '',
  password: '',
});

// 显示密码图标
const showPwd = () => {
  passwordType.value = passwordType.value === 'password' ? '' : 'password';
};

const submitForm = async (formEl: FormInstance | undefined) => {
  if (!formEl) return;
  const valid = await formEl.validate();
  if (!valid) return false;

  loading.value = true;
  try {
    await UserStore.login(ruleForm);
    await router.push({ path: '/' });
    ElNotification({
      title: getTimeStateStr(),
      message: '欢迎登录 SpikeAI 运营管理中心',
      type: 'success',
      duration: 3000,
    });
  } finally {
    loading.value = false;
  }
};
</script>
