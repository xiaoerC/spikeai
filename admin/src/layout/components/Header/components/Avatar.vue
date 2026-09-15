<template>
  <el-dropdown trigger="click">
    <div class="flex items-center gap-2 cursor-pointer select-none py-1 px-2 rounded-lg hover:bg-[var(--el-fill-color-light)] transition-colors">
      <!-- 账号第一个字符大写文字头像 -->
      <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-amber-500 to-amber-600 dark:from-amber-600 dark:to-yellow-500 text-white font-bold text-sm flex items-center justify-center shadow-xs border border-amber-400/30 font-mono">
        {{ initialChar }}
      </div>
      <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
        {{ userInfo?.username || '管理员' }}
      </span>
      <el-icon class="text-xs text-[var(--el-text-color-secondary)]">
        <arrow-down />
      </el-icon>
    </div>

    <template #dropdown>
      <el-dropdown-menu class="min-w-44">
        <!-- 用户身份标识头 -->
        <div class="px-3 py-2 border-b border-[var(--el-border-color-lighter)] flex flex-col gap-1">
          <span class="text-xs font-bold text-[var(--el-text-color-primary)]">
            {{ userInfo?.real_name || userInfo?.username || '管理员' }}
          </span>
          <div class="flex items-center gap-1.5 flex-wrap">
            <el-tag
              v-for="role in roleTags"
              :key="role"
              size="small"
              type="warning"
              effect="plain"
              class="!text-[10px] !h-5 !px-1.5"
            >
              {{ role }}
            </el-tag>
          </div>
        </div>

        <el-dropdown-item @click="modifyPassword" class="!py-2 text-xs">
          <el-icon class="mr-1.5 text-sm"><Edit /></el-icon>
          修改密码
        </el-dropdown-item>

        <el-dropdown-item divided @click="logOut" class="!py-2 text-xs !text-rose-500">
          <el-icon class="mr-1.5 text-sm"><SwitchButton /></el-icon>
          退出登录
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>

  <PersonalDialog ref="person" />
</template>

<script lang="ts" setup>
import { useUserStore } from '@/store/modules/user';
import { ElMessageBox } from 'element-plus';
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import PersonalDialog from './PersonalDialog.vue';

const router = useRouter();
const userStore = useUserStore();

const userInfo = computed(() => userStore.userInfo);

// 提取账号第一个字符大写作为个性化头像
const initialChar = computed(() => {
  const name = userStore.userInfo?.username || 'A';
  return name.trim().slice(0, 1).toUpperCase();
});

// 解析展示的角色标签
const roleTags = computed(() => {
  const roles = userStore.roles || [];
  if (roles.includes('super_admin')) return ['超级管理员'];
  const roleNameMap: Record<string, string> = {
    super_admin: '超级管理员',
    content_auditor: '内容审核员',
    ops_specialist: '运营专员',
    finance_auditor: '财务审核员',
  };
  return roles.map((r) => roleNameMap[r] || r);
});

const person = ref();

function modifyPassword() {
  person.value?.show();
}

async function logOut() {
  try {
    await ElMessageBox.confirm('您是否确认退出当前管理后台?', '温馨提示', {
      confirmButtonText: '确定退出',
      cancelButtonText: '取消',
      type: 'warning',
    });
    await userStore.logout(router);
  } catch {
    // 用户取消
  }
}
</script>
