<script setup lang="ts">
/**
 * 叙梦 Naro - 独立登录/认证中心页面 (views/login/index.vue)
 *
 * @packageDocumentation
 */

import ForgotPasswordModal from "@/views/login/components/ForgotPasswordModal.vue";
import LoginModal from "@/views/login/components/LoginModal.vue";
import RegisterModal from "@/views/login/components/RegisterModal.vue";
import { useAuthModal } from "@/views/login/composables/useAuthModal";
import { onMounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const { isOpen, currentView, openLogin, openRegister, openForgot, close } = useAuthModal();

onMounted(() => {
  openLogin();
});

function handleSuccess() {
  router.push("/");
}
</script>

<template>
  <div class="min-h-screen w-full bg-[#0C0A09] flex items-center justify-center relative overflow-hidden">
    <!-- 背景流光与羽化光晕 -->
    <div class="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-[#F9C86D]/10 blur-3xl pointer-events-none" />
    <div class="absolute -bottom-32 -right-32 w-96 h-96 rounded-full bg-[#F9C86D]/10 blur-3xl pointer-events-none" />

    <!-- 登录模态弹窗 -->
    <LoginModal
      :open="isOpen && currentView === 'login'"
      @update:open="isOpen = $event"
      @success="handleSuccess"
      @switch-to-register="openRegister"
      @switch-to-forgot="openForgot"
    />

    <!-- 注册模态弹窗 -->
    <RegisterModal
      :open="isOpen && currentView === 'register'"
      @update:open="isOpen = $event"
      @switch-to-login="openLogin"
    />

    <!-- 找回密码模态弹窗 -->
    <ForgotPasswordModal
      :open="isOpen && currentView === 'forgot'"
      @update:open="isOpen = $event"
      @switch-to-login="openLogin"
    />
  </div>
</template>
