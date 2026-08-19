<script setup lang="ts">
/**
 * 叙梦 Naro - 历史记录 / 周次历史回顾 (Smart Container 主入口)
 *
 * 1:1 像素级还原历史记录页面，展示周次筛选胶囊与双列历史角色卡片瀑布流。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import HistoryCharacterGrid from "@/views/history/components/HistoryCharacterGrid.vue";
import HistoryHeader from "@/views/history/components/HistoryHeader.vue";
import { useHistoryList } from "@/views/history/composables/useHistoryList";
import type { HistoryCharacterCard } from "@/views/history/types";
import LoginModal from "@/views/login/components/LoginModal.vue";
import { useRouter } from "vue-router";

const router = useRouter();
const appStore = useAppStore();
const {
  cards,
  weekOptions,
  selectedWeek,
  currentWeekLabel,
  isWeekSelectorOpen,
  setWeek,
  toggleWeekSelector,
  clearHistory,
} = useHistoryList();

function handleSelectCard(card: HistoryCharacterCard) {
  router.push(`/character/${card.id}`);
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部 Header 与周次筛选胶囊 -->
    <HistoryHeader
      :current-week-label="currentWeekLabel"
      :selected-week="selectedWeek"
      :week-options="weekOptions"
      :is-week-selector-open="isWeekSelectorOpen"
      @toggle-week="toggleWeekSelector"
      @select-week="setWeek"
      @clear-history="clearHistory"
    />

    <!-- 2. 主内容区: 2 列历史卡片瀑布流 -->
    <main class="w-full max-w-[440px] mx-auto px-3 pt-3 pb-24 flex flex-col gap-3">
      <!-- 若有卡片 -->
      <HistoryCharacterGrid
        v-if="cards.length > 0"
        :cards="cards"
        @select-card="handleSelectCard"
      />

      <!-- 空状态 -->
      <div
        v-else
        class="flex flex-col items-center justify-center py-24 text-center"
      >
        <div class="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-3">
          <svg class="w-8 h-8 text-[#78716C]" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" stroke-width="1.5"/>
            <path d="M12 6v6l4 2" stroke-width="1.5"/>
          </svg>
        </div>
        <p class="text-sm text-[#A8A29E] font-medium">暂无该周次的历史记录</p>
        <p class="text-xs text-[#78716C] mt-1">去社区探索并与喜欢的角色互动吧</p>
      </div>
    </main>

    <!-- 3. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 4. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
