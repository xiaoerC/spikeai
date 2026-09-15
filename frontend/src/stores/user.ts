/**
 * 用户与资产状态管理 Store
 *
 * @packageDocumentation
 */

import { type UserProfileData, authService } from "@/services/auth";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

export const useUserStore = defineStore("user", () => {
  const token = ref<string | null>(localStorage.getItem("naro_access_token"));
  const profile = ref<UserProfileData | null>(null);
  const isLoading = ref(false);
  const errorMessage = ref<string | null>(null);

  const isLoggedIn = computed(() => !!token.value);
  const starCoins = computed(() => profile.value?.wallet.star_coins ?? 0);
  const moonGems = computed(() => profile.value?.wallet.moon_gems ?? 0);

  /** 判定是否需要首次强制设置用户名 */
  const needsUsername = computed(() => {
    if (!isLoggedIn.value || !profile.value) return false;
    return !profile.value.username || profile.value.is_custom_username === false;
  });

  /** 登录 */
  async function login(email: string, password: string): Promise<boolean> {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const res = await authService.login({ email, password });
      if (res.code === 0 && res.data) {
        token.value = res.data.access_token;
        profile.value = res.data.user;
        localStorage.setItem("naro_access_token", res.data.access_token);
        return true;
      }
      errorMessage.value = res.message || "登录失败";
      return false;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || err.message || "登录异常";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /** 注册 */
  async function register(email: string, password: string, inviteCode?: string): Promise<boolean> {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const res = await authService.register({ email, password, invite_code: inviteCode });
      if (res.code === 0 && res.data) {
        token.value = res.data.access_token;
        profile.value = res.data.user;
        localStorage.setItem("naro_access_token", res.data.access_token);
        return true;
      }
      errorMessage.value = res.message || "注册失败";
      return false;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || err.message || "注册异常";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /** 获取/刷新资料 */
  async function fetchProfile(): Promise<void> {
    if (!token.value) return;
    try {
      const res = await authService.getProfile();
      if (res.code === 0 && res.data) {
        profile.value = res.data;
      }
    } catch (err) {
      console.warn("拉取用户资料失败", err);
    }
  }

  /** 每日签到 */
  async function claimDailyReward(): Promise<{ success: boolean; message: string }> {
    try {
      const res = await authService.claimDailyReward();
      if (res.code === 0 && res.data) {
        if (profile.value) {
          profile.value.wallet.star_coins = res.data.new_balance;
        }
        return {
          success: true,
          message: res.data.message || `签到成功，获得 ${res.data.reward_star_coins} 星元！`,
        };
      }
      return { success: false, message: res.message || "签到失败" };
    } catch (err: any) {
      return {
        success: false,
        message: err.response?.data?.detail || err.message || "今日已完成签到",
      };
    }
  }

  /** 更新用户资料（昵称、头像） */
  async function updateProfile(payload: { username: string; avatar_url?: string }): Promise<boolean> {
    isLoading.value = true;
    errorMessage.value = null;
    try {
      const res = await authService.updateProfile(payload);
      if (res.code === 0 && res.data) {
        profile.value = res.data;
        return true;
      }
      errorMessage.value = res.message || "更新资料失败";
      return false;
    } catch (err: any) {
      errorMessage.value = err.response?.data?.detail || err.message || "更新资料异常";
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  /** 退出登录 */
  async function logout(): Promise<void> {
    try {
      await authService.logout();
    } catch {
      // 忽略登出异常
    } finally {
      resetState();
    }
  }

  /** 重置用户状态与凭据 */
  function resetState(): void {
    token.value = null;
    profile.value = null;
    errorMessage.value = null;
    localStorage.removeItem("naro_access_token");
  }

  return {
    token,
    profile,
    isLoading,
    errorMessage,
    isLoggedIn,
    needsUsername,
    starCoins,
    moonGems,
    login,
    register,
    fetchProfile,
    updateProfile,
    claimDailyReward,
    logout,
    resetState,
  };
});
