<script setup lang="ts">
import AppToast from "@/components/common/AppToast.vue";
import DesktopSidebar from "@/components/navigation/DesktopSidebar.vue";
import { useResponsiveLayout } from "@/composables/useResponsiveLayout";
import { useAppStore } from "@/stores/app";
import { useUserStore } from "@/stores/user";
import { checkIsMobileViewport, setupVisualViewportListener } from "@/utils/viewport";
import ForgotPasswordModal from "@/views/login/components/ForgotPasswordModal.vue";
import LoginModal from "@/views/login/components/LoginModal.vue";
import RegisterModal from "@/views/login/components/RegisterModal.vue";
import SetUsernameModal from "@/views/login/components/SetUsernameModal.vue";
import { onMounted, onUnmounted, ref, watch } from "vue";
import { RouterView, useRoute } from "vue-router";

const appStore = useAppStore();
const userStore = useUserStore();
const { isMobile } = useResponsiveLayout();
const route = useRoute();
const rightScrollContainer = ref<HTMLElement | null>(null);

// 路由切换时，重置右侧主滚动容器位置至顶部
watch(
  () => route.fullPath,
  () => {
    if (rightScrollContainer.value) {
      rightScrollContainer.value.scrollTop = 0;
    }
  },
);

let cleanupViewport: (() => void) | null = null;

onMounted(() => {
  appStore.isMobile = checkIsMobileViewport();

  // 初始化检查登录资料
  userStore.fetchProfile();

  const handleResize = () => {
    appStore.isMobile = checkIsMobileViewport();
    appStore.viewportHeight = window.innerHeight;
  };

  window.addEventListener("resize", handleResize);

  // 注册视口动态监听器
  cleanupViewport = setupVisualViewportListener((keyboardHeight, isKeyboardOpen) => {
    appStore.updateKeyboard(keyboardHeight, isKeyboardOpen);
  });
});

onUnmounted(() => {
  if (cleanupViewport) {
    cleanupViewport();
  }
});
</script>

<template>
  <!-- 全局 Toast 提示容器 -->
  <AppToast />

  <!-- 1. 移动端视口外壳 (< 768px): 保持基准 440px 居中安全画布 -->
  <div
    v-if="isMobile"
    :class="[
      'w-full bg-[#050508] flex justify-center font-sans antialiased selection:bg-naro-gold selection:text-black',
      route.path.startsWith('/chat') ? 'fixed inset-0 overflow-hidden' : 'min-h-screen'
    ]"
  >
    <div
      :class="[
        'w-full max-w-[440px] bg-[#1A1511] shadow-2xl relative flex flex-col',
        route.path.startsWith('/chat') ? 'h-full max-h-full overflow-hidden' : 'min-h-screen overflow-x-hidden'
      ]"
    >
      <RouterView />
    </div>
  </div>

  <!-- 2. PC 桌面端工作台外壳 (>= 768px): 左侧常驻固定侧边栏 + 右侧宽屏自适应独立滚动视窗 -->
  <div
    v-else
    class="h-screen w-full bg-[#120F0C] flex font-sans antialiased selection:bg-naro-gold selection:text-black text-[#F5F5F4] overflow-hidden"
  >
    <!-- 左侧常驻侧边栏 (绝对不随右侧内容滚动) -->
    <DesktopSidebar />

    <!-- 右侧自适应主内容独立滚动视窗 -->
    <div
      ref="rightScrollContainer"
      class="flex-1 h-full flex flex-col min-w-0 bg-[#15120E] overflow-y-auto overflow-x-hidden relative"
    >
      <RouterView />
    </div>
  </div>

  <!-- 全局认证模态弹窗系统 (登录 / 注册 / 找回密码 互切无缝响应) -->
  <LoginModal
    :open="appStore.authModalState === 'login'"
    @update:open="(val: boolean) => { if (!val) appStore.closeAuthModal(); }"
    @switch-to-register="appStore.openRegisterModal()"
    @switch-to-forgot="appStore.openForgotModal()"
  />

  <RegisterModal
    :open="appStore.authModalState === 'register'"
    @update:open="(val: boolean) => { if (!val) appStore.closeAuthModal(); }"
    @switch-to-login="appStore.openLoginModal()"
  />

  <ForgotPasswordModal
    :open="appStore.authModalState === 'forgot'"
    @update:open="(val: boolean) => { if (!val) appStore.closeAuthModal(); }"
    @switch-to-login="appStore.openLoginModal()"
  />

  <!-- 首次登录强制设置用户名弹窗 (强阻断) -->
  <SetUsernameModal :open="userStore.needsUsername" />
</template>

<style>
/* 彻底清除所有浏览器原生组件的默认丑陋样式 */
*, *::before, *::after {
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}

html, body {
  margin: 0 !important;
  padding: 0 !important;
  background-color: #050508;
  color: #F3F4F6;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

button {
  all: unset;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
  cursor: pointer;
  background: transparent;
  color: inherit;
  font: inherit;
  user-select: none;
  -webkit-user-select: none;
}

input {
  all: unset;
  box-sizing: border-box;
  font: inherit;
  color: inherit;
}

input::placeholder {
  color: #A18D6F;
}

/* 快速响应弹窗与遮罩动画 (150ms 极速丝滑) */
@keyframes modalFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes modalScaleIn {
  from { opacity: 0; transform: scale(0.96); }
  to { opacity: 1; transform: scale(1); }
}

.animate-fade-in {
  animation: modalFadeIn 150ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.animate-scale-in {
  animation: modalScaleIn 150ms cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

/* 自定义黑金极简滚动条，保持桌面端奢华暗黑质感 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(249, 200, 109, 0.2);
  border-radius: 9999px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(249, 200, 109, 0.4);
}
</style>

