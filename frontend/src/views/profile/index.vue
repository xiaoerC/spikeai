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
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] md:bg-none md:bg-[#15120E] text-[#F5F5F4] relative">
    
    <!-- 桌面端顶部标题 (仅在 md: 及以上显示，1:1 对齐截图 5) -->
    <div class="hidden md:flex flex-col px-8 pt-6 pb-2 max-w-[1600px] mx-auto w-full">
      <h1 class="text-xl font-bold text-[#F5F5F4]">用户中心</h1>
      <p class="text-xs text-[#78716C] mt-0.5">整理您的账户和设置</p>
    </div>

    <!-- 移动端顶部 Header -->
    <div class="md:hidden">
      <ProfileHeader
        :unread-count="noticeCount"
        @open-settings="handleOpenSettings"
      />
    </div>

    <!-- 主体区域: 移动端单列, 桌面端双列大屏仪表盘 (对齐截图 5) -->
    <main class="flex-1 px-3 md:px-8 pb-28 md:pb-12 w-full max-w-[440px] md:max-w-[1600px] mx-auto">
      
      <!-- 移动端单列线性布局 -->
      <div class="flex md:hidden flex-col gap-4">
        <UserProfileCard
          :user-data="userData"
          @recharge="handleRecharge"
          @daily-reward="handleDailyReward"
          @navigate="handleNavigate"
          @logout="handleLogout"
        />
        <ProfileBadgesCard :badges="badges" />
        <PlayerLevelCard :player-data="playerLevelData" />
        <CreatorLevelCard :creator-data="creatorLevelData" />
        <InviteBannerCard :invite-data="inviteInfo" />
        <UserBackpackCard />
        <AssetUsageHistoryCard
          :transactions="transactionsState"
          @change-page="fetchTransactions"
        />
      </div>

      <!-- PC 桌面端双列仪表盘布局 (1:1 还原截图 5) -->
      <div class="hidden md:grid grid-cols-[340px_1fr] gap-6 items-start mt-2">
        <!-- 左栏: 个人名片与勋章展示柜 -->
        <div class="flex flex-col gap-5">
          <UserProfileCard
            :user-data="userData"
            @recharge="handleRecharge"
            @daily-reward="handleDailyReward"
            @navigate="handleNavigate"
            @logout="handleLogout"
          />
          <ProfileBadgesCard :badges="badges" />
        </div>

        <!-- 右栏: 等级、活动、背包与使用记录流水表 -->
        <div class="flex flex-col gap-5 min-w-0">
          <!-- 上部: 玩家等级 + 创作者等级 并列 -->
          <div class="grid grid-cols-2 gap-5">
            <PlayerLevelCard :player-data="playerLevelData" />
            <CreatorLevelCard :creator-data="creatorLevelData" />
          </div>

          <!-- 中部: 邀请活动 + 我的背包 并列 -->
          <div class="grid grid-cols-[1.4fr_1fr] gap-5">
            <InviteBannerCard :invite-data="inviteInfo" />
            <UserBackpackCard />
          </div>

          <!-- 下部: 资产流水记录宽表 -->
          <AssetUsageHistoryCard
            :transactions="transactionsState"
            @change-page="fetchTransactions"
          />
        </div>
      </div>

    </main>

    <!-- 底部导航栏 (自动在桌面端隐藏) -->
    <BottomTabBar />

  </div>
</template>
