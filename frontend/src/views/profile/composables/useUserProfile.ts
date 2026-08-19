/**
 * 个人中心业务逻辑 Composable
 *
 * @packageDocumentation
 */

import { PROFILE_USER_DATA } from "@/views/profile/constants/profileMock";
import { readonly, ref } from "vue";

export function useUserProfile() {
  const isDailyRewardOpen = ref(false);
  const isRechargeModalOpen = ref(false);
  const isSettingsModalOpen = ref(false);
  const noticeCount = ref(PROFILE_USER_DATA.unreadNotices);

  function handleRecharge(): void {
    isRechargeModalOpen.value = true;
  }

  function handleDailyReward(): void {
    isDailyRewardOpen.value = true;
  }

  function handleOpenSettings(): void {
    isSettingsModalOpen.value = true;
  }

  function handleLogout(): void {
    // 退出登录触发
  }

  return {
    userData: readonly(ref(PROFILE_USER_DATA)),
    noticeCount: readonly(noticeCount),
    isDailyRewardOpen,
    isRechargeModalOpen,
    isSettingsModalOpen,
    handleRecharge,
    handleDailyReward,
    handleOpenSettings,
    handleLogout,
  };
}
