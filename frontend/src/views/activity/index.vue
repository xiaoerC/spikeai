<script setup lang="ts">
/**
 * 叙梦 Naro - 活动中心 / 官方活动 (Smart Container 主入口)
 *
 * 1:1 像素级还原活动中心页面，展示推广招募、提示词征集、画师串征集与长期福利。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import ActivityCard from "@/views/activity/components/ActivityCard.vue";
import ActivityHeader from "@/views/activity/components/ActivityHeader.vue";
import { useActivityList } from "@/views/activity/composables/useActivityList";
import LoginModal from "@/views/login/components/LoginModal.vue";

const appStore = useAppStore();
const { activities, currentCategory, expandedCardIds, toggleExpand, setCategory } =
  useActivityList();
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] md:bg-none md:bg-[#15120E] text-gray-100 relative">
    
    <!-- 1. 顶部 Header 与分类切换 -->
    <ActivityHeader
      :current-category="currentCategory"
      @select-category="setCategory"
    />

    <!-- 2. 主内容区: 官方活动卡片流 (桌面端双列网格) -->
    <main class="w-full max-w-[440px] md:max-w-[1200px] mx-auto px-3 md:px-6 pt-3 md:pt-6 pb-24 md:pb-12 flex flex-col md:grid md:grid-cols-2 gap-4">
      <ActivityCard
        v-for="act in activities"
        :key="act.id"
        :activity="act"
        :is-expanded="expandedCardIds.has(act.id)"
        @toggle-expand="toggleExpand"
      />
    </main>

    <!-- 3. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 4. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
