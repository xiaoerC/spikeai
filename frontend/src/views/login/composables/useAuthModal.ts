/**
 * 认证模态弹窗状态机 Hook (views/login 私有)
 *
 * @packageDocumentation
 */

import { ref } from "vue";

export type AuthModalView = "login" | "register" | "forgot";

/**
 * 认证模态弹窗组合式状态管理
 */
export function useAuthModal() {
  const isOpen = ref(false);
  const currentView = ref<AuthModalView>("login");

  function openLogin() {
    currentView.value = "login";
    isOpen.value = true;
  }

  function openRegister() {
    currentView.value = "register";
    isOpen.value = true;
  }

  function openForgot() {
    currentView.value = "forgot";
    isOpen.value = true;
  }

  function close() {
    isOpen.value = false;
  }

  return {
    isOpen,
    currentView,
    openLogin,
    openRegister,
    openForgot,
    close,
  };
}
