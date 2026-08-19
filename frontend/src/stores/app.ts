import type { AppState, ThemeMode, UserProfile } from "@/types";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export type AuthModalType = "none" | "login" | "register" | "forgot";

export const useAppStore = defineStore("app", () => {
  // 视口与键盘状态
  const isMobile = ref<boolean>(true);
  const viewportHeight = ref<number>(typeof window !== "undefined" ? window.innerHeight : 844);
  const keyboardHeight = ref<number>(0);
  const isKeyboardOpen = ref<boolean>(false);

  // 导航与主题
  const activeTab = ref<AppState["activeTab"]>("community");
  const currentTheme = ref<ThemeMode>("obsidian-gold");

  // 认证模态弹窗全局状态机 ("none" | "login" | "register" | "forgot")
  const authModalState = ref<AuthModalType>("none");

  const isLoginModalOpen = computed({
    get: () => authModalState.value === "login",
    set: (val: boolean) => {
      authModalState.value = val ? "login" : "none";
    },
  });

  const isRegisterModalOpen = computed({
    get: () => authModalState.value === "register",
    set: (val: boolean) => {
      authModalState.value = val ? "register" : "none";
    },
  });

  const isForgotModalOpen = computed({
    get: () => authModalState.value === "forgot",
    set: (val: boolean) => {
      authModalState.value = val ? "forgot" : "none";
    },
  });

  function openLoginModal(): void {
    authModalState.value = "login";
  }

  function openRegisterModal(): void {
    authModalState.value = "register";
  }

  function openForgotModal(): void {
    authModalState.value = "forgot";
  }

  function closeAuthModal(): void {
    authModalState.value = "none";
  }

  // 更多抽屉全局状态
  const isMoreDrawerOpen = ref<boolean>(false);

  function openMoreDrawer(): void {
    isMoreDrawerOpen.value = true;
  }

  function closeMoreDrawer(): void {
    isMoreDrawerOpen.value = false;
  }

  function toggleMoreDrawer(): void {
    isMoreDrawerOpen.value = !isMoreDrawerOpen.value;
  }

  // 用户资产与状态
  const currentUser = ref<UserProfile>({
    id: "user_guest_001",
    username: "旅行者",
    avatarUrl: "/default-avatar.png",
    starCoins: 120,
    moonGems: 15,
    vipLevel: 1,
    creatorLevel: 0,
    badges: ["开拓者", "夜之城居民"],
  });

  // 更新软键盘高度
  function updateKeyboard(height: number, isOpen: boolean) {
    keyboardHeight.value = height;
    isKeyboardOpen.value = isOpen;
  }

  // 切换底部 Tab
  function setActiveTab(tab: AppState["activeTab"]) {
    activeTab.value = tab;
  }

  return {
    isMobile,
    viewportHeight,
    keyboardHeight,
    isKeyboardOpen,
    activeTab,
    currentTheme,
    authModalState,
    isLoginModalOpen,
    isRegisterModalOpen,
    isForgotModalOpen,
    openLoginModal,
    openRegisterModal,
    openForgotModal,
    closeAuthModal,
    isMoreDrawerOpen,
    openMoreDrawer,
    closeMoreDrawer,
    toggleMoreDrawer,
    currentUser,
    updateKeyboard,
    setActiveTab,
  };
});
