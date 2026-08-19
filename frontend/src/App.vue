<script setup lang="ts">
import { useAppStore } from "@/stores/app";
import { checkIsMobileViewport, setupVisualViewportListener } from "@/utils/viewport";
import ForgotPasswordModal from "@/views/login/components/ForgotPasswordModal.vue";
import LoginModal from "@/views/login/components/LoginModal.vue";
import RegisterModal from "@/views/login/components/RegisterModal.vue";
import { onMounted, onUnmounted } from "vue";
import { RouterView } from "vue-router";

const appStore = useAppStore();

let cleanupViewport: (() => void) | null = null;

onMounted(() => {
  appStore.isMobile = checkIsMobileViewport();

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
  <!-- 桌面端居中容器包装器 (Mobile-First 架构，基准 440px) -->
  <div class="min-h-screen w-full bg-[#050508] flex justify-center font-sans antialiased selection:bg-naro-gold selection:text-black">
    <!-- 主移动端视窗画布 (严格 440px，自适应小屏) -->
    <div class="w-full max-w-[440px] min-h-screen bg-[#1A1511] shadow-2xl relative flex flex-col overflow-x-hidden">
      <RouterView />

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
    </div>
  </div>
</template>

<style>
/* 彻底清除所有浏览器原生组件的默认丑陋样式 */
*, *::before, *::after {
  box-sizing: border-box;
  -webkit-tap-highlight-color: transparent;
}

html, body {
  margin: 0;
  padding: 0;
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
</style>

