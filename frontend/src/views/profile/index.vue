<script setup lang="ts">
/**
 * 叙梦 Naro - 个人用户中心主页面 (Smart Container 主入口)
 *
 * 1:1 严格还原 Figma 原型全部功能与黑金高奢视觉规范。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import AssetUsageHistoryCard from "@/views/profile/components/AssetUsageHistoryCard.vue";
import CreatorLevelCard from "@/views/profile/components/CreatorLevelCard.vue";
import InviteBannerCard from "@/views/profile/components/InviteBannerCard.vue";
import PlayerLevelCard from "@/views/profile/components/PlayerLevelCard.vue";
import ProfileBadgesCard from "@/views/profile/components/ProfileBadgesCard.vue";
import ProfileHeader from "@/views/profile/components/ProfileHeader.vue";
import UserBackpackCard from "@/views/profile/components/UserBackpackCard.vue";
import UserProfileCard from "@/views/profile/components/UserProfileCard.vue";
import { useUserProfile } from "@/views/profile/composables/useUserProfile";
import { onMounted } from "vue";
import { useRouter } from "vue-router";

const appStore = useAppStore();
const router = useRouter();

const {
  userData,
  badges,
  playerLevelData,
  creatorLevelData,
  inviteInfo,
  transactionsState,
  noticeCount,
  handleRecharge,
  handleDailyReward,
  handleOpenSettings,
  handleLogout,
  fetchTransactions,
} = useUserProfile();

onMounted(() => {
  appStore.setActiveTab("more");
});

function handleNavigate(feature: string): void {
  if (feature === "home") {
    router.push("/");
  }
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full max-w-[440px] mx-auto bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-[#F5F5F4] relative shadow-2xl">
    
    <!-- 1. 顶部 Header -->
    <ProfileHeader
      :unread-count="noticeCount"
      @open-settings="handleOpenSettings"
    />

    <!-- 2. 主体可滚动区域 (包含全部 7 大业务卡片) -->
    <main class="flex-1 px-3 pb-28 w-full flex flex-col gap-4">
      <!-- (1) 用户核心资料卡片 -->
      <UserProfileCard
        :user-data="userData"
        @recharge="handleRecharge"
        @daily-reward="handleDailyReward"
        @navigate="handleNavigate"
        @logout="handleLogout"
      />

      <!-- (2) 我的勋章成就卡片 -->
      <ProfileBadgesCard :badges="badges" />

      <!-- (3) 玩家等级卡片 -->
      <PlayerLevelCard :player-data="playerLevelData" />

      <!-- (4) 创作者等级卡片 -->
      <CreatorLevelCard :creator-data="creatorLevelData" />

      <!-- (5) 邀请活动福利卡片 -->
      <InviteBannerCard :invite-data="inviteInfo" />

      <!-- (6) 我的背包卡片 -->
      <UserBackpackCard />

      <!-- (7) 资产使用记录流水卡片 -->
      <AssetUsageHistoryCard
        :transactions="transactionsState"
        @change-page="fetchTransactions"
      />
    </main>

    <!-- 3. 全局底部导航栏 -->
    <BottomTabBar />

  </div>
</template>
