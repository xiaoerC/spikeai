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
import DesktopHomeToolbar from "@/views/home/components/DesktopHomeToolbar.vue";
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
  <!-- 主容器: 移动端自适应小屏，桌面端宽屏自适应展开 -->
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] md:bg-none md:bg-[#15120E] text-gray-100 relative">
    
    <!-- 1. 桌面端顶部复合工具栏 (仅在 md: 及以上显示，1:1 对齐截图 1/2) -->
    <div class="hidden md:block w-full px-6 pt-5 pb-1 max-w-[1600px] mx-auto">
      <DesktopHomeToolbar />
    </div>

    <!-- 2. 移动端顶部模式切换与筛选面板 (仅在小屏显示) -->
    <header class="w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] pt-safe md:hidden">
      <HeaderModeTabs />
    </header>
    <div class="md:hidden">
      <FilterPanel />
    </div>

    <!-- 3. 角色卡片响应式网格阵列 (移动端双列, 桌面端 5 列标准流) -->
    <main class="flex-1 p-2 md:px-6 md:py-4 pb-24 md:pb-12 w-full max-w-[1600px] mx-auto">
      <div
        v-if="marketStore.filteredCards.length > 0"
        class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-5 2xl:grid-cols-6 gap-2.5 md:gap-4 w-full animate-fade-in"
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
        class="flex flex-col items-center justify-center py-20 gap-3 text-center"
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

    <!-- 4. 全局底部导航栏 (自动在桌面端隐藏) -->
    <BottomTabBar />

  </div>
</template>
