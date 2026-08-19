<script setup lang="ts">
/**
 * 叙梦 Naro - 等级榜 / 排行榜 (Smart Container 主入口)
 *
 * 1:1 像素级还原等级榜，展示 Top 3 领奖台冠亚季军与第 4~N 名排行榜流。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import LoginModal from "@/views/login/components/LoginModal.vue";
import RankingHeader from "@/views/ranking/components/RankingHeader.vue";
import RankingListItem from "@/views/ranking/components/RankingListItem.vue";
import RankingPodiumTop3 from "@/views/ranking/components/RankingPodiumTop3.vue";
import { useRankingList } from "@/views/ranking/composables/useRankingList";

const appStore = useAppStore();
const { champion, runnerUp, thirdPlace, restUsers } = useRankingList();
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部 Header 导航栏 -->
    <RankingHeader />

    <!-- 2. 主内容区 -->
    <main class="w-full max-w-[440px] mx-auto px-3 pt-2 pb-24 flex flex-col gap-3">
      
      <!-- Top 3 冠亚季军领奖台 -->
      <RankingPodiumTop3
        :champion="champion"
        :runner-up="runnerUp"
        :third-place="thirdPlace"
      />

      <!-- 第 4 ~ N 名列表流 -->
      <div class="flex flex-col gap-2 mt-1">
        <RankingListItem
          v-for="user in restUsers"
          :key="user.rank"
          :user="user"
        />
      </div>

    </main>

    <!-- 3. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 4. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
