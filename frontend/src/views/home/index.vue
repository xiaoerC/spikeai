<script setup lang="ts">
/**
 * 叙梦 Naro - AI 角色市场首页 (Smart Container 页面主入口)
 *
 * 遵循 Vue 3.5 + UnoCSS + Reka UI / Vaul Vue 规范架构，
 * 点击角色卡直接路由跳转至对应角色详情页 `/character/:id`。
 *
 * @packageDocumentation
 */

import { AppButton } from "@/components/common";
import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useMarketStore } from "@/stores/market";
import type { MarketCard } from "@/types";
import CharacterCard from "@/views/home/components/CharacterCard.vue";
import FilterPanel from "@/views/home/components/FilterPanel.vue";
import HeaderModeTabs from "@/views/home/components/HeaderModeTabs.vue";
import { Sparkles } from "lucide-vue-next";
import { useRouter } from "vue-router";

const marketStore = useMarketStore();
const router = useRouter();

/**
 * 点击角色卡直接跳转至角色详情页
 * @param card - 目标角色卡
 */
function handleCardClick(card: MarketCard): void {
  router.push(`/character/${card.id}`);
}
</script>

<template>
  <!-- 主容器: 440px 基准移动视口, 黑金渐变主色 -->
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部主模式切换 (剧情卡 / 绅士卡) -->
    <header class="w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] pt-safe">
      <HeaderModeTabs />
    </header>

    <!-- 2. 复合筛选控制面板 (排序Tab、搜索、日/周/月趋势、热门标签) -->
    <FilterPanel />

    <!-- 3. 双列角色卡片网格阵列 (1:1 黑金高奢卡片流, 点击直接跳转详情) -->
    <main class="flex-1 p-2 pb-24 w-full">
      <div
        v-if="marketStore.filteredCards.length > 0"
        class="grid grid-cols-2 gap-2 w-full animate-fade-in"
      >
        <CharacterCard
          v-for="card in marketStore.filteredCards"
          :key="card.id"
          :card="card"
          @select="handleCardClick"
        />
      </div>

      <!-- 空状态 -->
      <div
        v-else
        class="flex flex-col items-center justify-center py-16 gap-3 text-center"
      >
        <div class="w-12 h-12 rounded-full bg-[rgba(26,23,20,0.95)] border border-[#44403C] flex items-center justify-center text-[#F9C86D] shadow-gold">
          <Sparkles class="w-6 h-6" />
        </div>
        <div class="flex flex-col gap-1">
          <p class="text-sm font-semibold text-gray-300">暂无匹配的角色卡</p>
          <p class="text-xs text-[#78716C]">尝试更换筛选标签或清除搜索关键词</p>
        </div>
        <AppButton
          variant="ghost"
          size="sm"
          @click="marketStore.setSearchKeyword(''); marketStore.setSelectedTag('')"
          class="mt-2"
        >
          重置筛选条件
        </AppButton>
      </div>
    </main>

    <!-- 4. 全局底部导航栏 -->
    <BottomTabBar />

  </div>
</template>
