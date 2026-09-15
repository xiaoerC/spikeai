/**
 * 个人中心全量业务状态与真实数据绑定 Composable
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { type InviteInfoData, type WalletTransactionItem, authService } from "@/services/auth";
import { useUserStore } from "@/stores/user";
import { computed, onMounted, reactive, readonly, ref } from "vue";

export function useUserProfile() {
  const userStore = useUserStore();
  const { warning } = useToast();
  const isDailyRewardOpen = ref(false);
  const isRechargeModalOpen = ref(false);
  const isSettingsModalOpen = ref(false);
  const noticeCount = ref(0);

  const inviteInfo = reactive<InviteInfoData>({
    invite_code: "",
    invite_url: "",
    invited_count: 0,
    reward_earned_star: 0,
  });

  const transactionsState = reactive<{
    items: WalletTransactionItem[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
    isLoading: boolean;
  }>({
    items: [],
    total: 0,
    page: 1,
    pageSize: 10,
    totalPages: 1,
    isLoading: false,
  });

  async function loadInitialData(): Promise<void> {
    if (userStore.isLoggedIn) {
      await Promise.all([userStore.fetchProfile(), fetchInviteInfo(), fetchTransactions(1)]);
    }
  }

  async function fetchInviteInfo(): Promise<void> {
    try {
      const res = await authService.getInviteInfo();
      if (res.code === 0 && res.data) {
        inviteInfo.invite_code = res.data.invite_code;
        inviteInfo.invite_url = res.data.invite_url;
        inviteInfo.invited_count = res.data.invited_count;
        inviteInfo.reward_earned_star = res.data.reward_earned_star;
      }
    } catch {
      // 降级使用 profile 内的邀请码
      if (userStore.profile) {
        inviteInfo.invite_code = userStore.profile.invite_code;
      }
    }
  }

  async function fetchTransactions(page = 1): Promise<void> {
    transactionsState.isLoading = true;
    transactionsState.page = page;
    try {
      const res = await authService.getTransactions(page, transactionsState.pageSize);
      if (res.code === 0 && res.data) {
        transactionsState.items = res.data.items;
        transactionsState.total = res.data.total;
        transactionsState.totalPages = res.data.total_pages || 1;
      }
    } catch {
      transactionsState.items = [];
      transactionsState.total = 0;
      transactionsState.totalPages = 1;
    } finally {
      transactionsState.isLoading = false;
    }
  }

  onMounted(() => {
    loadInitialData();
  });

  // 1. 用户核心资料卡片数据
  const userData = computed(() => {
    if (userStore.profile) {
      const p = userStore.profile;
      return {
        id: p.id,
        shortId: `ID: ${p.id.slice(0, 8)}...`,
        username: p.username,
        email: p.email,
        avatarUrl: p.avatar_url || `https://api.dicebear.com/7.x/bottts/svg?seed=${p.username}`,
        isOnline: true,
        vipLevel: p.vip_level === 0 ? "普通 naro" : `VIP ${p.vip_level}`,
        starCoins: p.wallet.star_coins,
        moonGems: p.wallet.moon_gems,
        inviteCode: p.invite_code,
        unreadNotices: 0,
      };
    }
    return {
      id: "",
      shortId: "ID: --",
      username: "未登录",
      email: "--",
      avatarUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=guest",
      isOnline: false,
      vipLevel: "普通 naro",
      starCoins: 0,
      moonGems: 0,
      inviteCode: "",
      unreadNotices: 0,
    };
  });

  // 2. 真实勋章列表
  const badges = computed(() => userStore.profile?.badges ?? []);

  // 3. 玩家等级计算与指标
  const playerLevelData = computed(() => {
    const level = userStore.profile?.player_level ?? 1;
    const currentXp = userStore.profile?.player_xp ?? 0;
    const nextLevelXp = level * 100;
    const progressPercentage = Math.min(100, Math.round((currentXp / nextLevelXp) * 100));

    return {
      level,
      title: level >= 10 ? "梦境行者" : "梦境初行者",
      currentXp,
      nextLevelXp,
      progressPercentage,
      totalXp: currentXp,
      moonGemsUsed: 0,
      starCoinsUsed: 0,
      vipUsage: 0,
      totalRecharged: 0,
    };
  });

  // 4. 创作者等级计算与指标
  const creatorLevelData = computed(() => {
    const level = userStore.profile?.creator_level ?? 1;
    const currentXp = userStore.profile?.creator_xp ?? 0;
    const nextLevelXp = level * 100;
    const progressPercentage = Math.min(100, Math.round((currentXp / nextLevelXp) * 100));

    return {
      level,
      title: "见习创作者",
      currentXp,
      nextLevelXp,
      progressPercentage,
      totalXp: currentXp,
      originalWorks: 0,
      worksUsage: 0,
      rewardStars: 0,
      rewardMoons: 0,
    };
  });

  function handleRecharge(): void {
    isRechargeModalOpen.value = true;
  }

  async function handleDailyReward(): Promise<void> {
    if (!userStore.isLoggedIn) {
      warning("请先登录后再领取每日奖励！");
      return;
    }
    const res = await userStore.claimDailyReward();
    if (res.success) {
      // 签到成功后刷新流水
      await fetchTransactions(1);
    }
  }

  function handleOpenSettings(): void {
    isSettingsModalOpen.value = true;
  }

  async function handleLogout(): Promise<void> {
    await userStore.logout();
  }

  return {
    userData,
    badges,
    playerLevelData,
    creatorLevelData,
    inviteInfo: readonly(inviteInfo),
    transactionsState,
    noticeCount: readonly(noticeCount),
    isDailyRewardOpen,
    isRechargeModalOpen,
    isSettingsModalOpen,
    handleRecharge,
    handleDailyReward,
    handleOpenSettings,
    handleLogout,
    fetchTransactions,
  };
}
