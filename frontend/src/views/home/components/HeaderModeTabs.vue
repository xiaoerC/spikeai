<script setup lang="ts">
/**
 * 顶部「剧情卡 / 绅士卡」主模式切换组件 (Home 页面私有)
 *
 * @packageDocumentation
 */

import { useMarketStore } from "@/stores/market";
import type { CardMode } from "@/types";

const marketStore = useMarketStore();

/**
 * 切换卡片模式
 * @param mode - 'story' | 'nsfw'
 */
function handleModeChange(mode: CardMode): void {
  marketStore.setMode(mode);
}
</script>

<template>
  <!-- 顶部主模式切换并排容器 -->
  <div class="flex items-center gap-[6px] w-full p-2">
    <!-- 剧情卡按钮 -->
    <button
      type="button"
      @click="handleModeChange('story')"
      :class="[
        'flex-1 h-10 flex items-center justify-center gap-[6px] rounded-lg border-[1.333px] transition-all duration-150 select-none cursor-pointer',
        marketStore.mode === 'story'
          ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09] font-bold'
          : 'bg-transparent border-[#44403C] text-[#78716C] font-semibold hover:border-gray-500'
      ]"
    >
      <svg
        class="w-[18px] h-[18px] flex-shrink-0"
        viewBox="0 0 18 18"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M9 5.25V15.75"
          :stroke="marketStore.mode === 'story' ? '#0C0A09' : '#78716C'"
          stroke-width="1.65"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <path
          d="M2.25 13.5C2.05109 13.5 1.86032 13.421 1.71967 13.2803C1.57902 13.1397 1.5 12.9489 1.5 12.75V3C1.5 2.80109 1.57902 2.61032 1.71967 2.46967C1.86032 2.32902 2.05109 2.25 2.25 2.25H6C6.79565 2.25 7.55871 2.56607 8.12132 3.12868C8.68393 3.69129 9 4.45435 9 5.25C9 4.45435 9.31607 3.69129 9.87868 3.12868C10.4413 2.56607 11.2044 2.25 12 2.25H15.75C15.9489 2.25 16.1397 2.32902 16.2803 2.46967C16.421 2.61032 16.5 2.80109 16.5 3V12.75C16.5 12.9489 16.421 13.1397 16.2803 13.2803C16.1397 13.421 15.9489 13.5 15.75 13.5H11.25C10.6533 13.5 10.081 13.7371 9.65901 14.159C9.23705 14.581 9 15.1533 9 15.75C9 15.1533 8.76295 14.581 8.34099 14.159C7.91903 13.7371 7.34674 13.5 6.75 13.5H2.25Z"
          :stroke="marketStore.mode === 'story' ? '#0C0A09' : '#78716C'"
          stroke-width="1.65"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <span class="text-[14px] leading-[20px] tracking-[-0.176px]">剧情卡</span>
    </button>

    <!-- 绅士卡按钮 -->
    <button
      type="button"
      @click="handleModeChange('nsfw')"
      :class="[
        'flex-1 h-10 flex items-center justify-center gap-[6px] rounded-lg border-[1.333px] transition-all duration-150 select-none cursor-pointer',
        marketStore.mode === 'nsfw'
          ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09] font-bold'
          : 'bg-transparent border-[#44403C] text-[#78716C] font-semibold hover:border-gray-500'
      ]"
    >
      <svg
        class="w-[18px] h-[18px] flex-shrink-0"
        viewBox="0 0 18 18"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M3 10.5C2.85808 10.5005 2.71893 10.4607 2.59872 10.3852C2.47851 10.3098 2.38218 10.2018 2.32091 10.0737C2.25965 9.94572 2.23597 9.80294 2.25263 9.66199C2.26928 9.52105 2.32559 9.38772 2.415 9.2775L9.84 1.6275C9.8957 1.56321 9.9716 1.51977 10.0552 1.5043C10.1389 1.48883 10.2253 1.50226 10.3003 1.54238C10.3753 1.5825 10.4344 1.64692 10.468 1.72508C10.5016 1.80324 10.5076 1.89049 10.485 1.9725L9.045 6.4875C9.00254 6.60114 8.98828 6.72339 9.00345 6.84376C9.01861 6.96412 9.06275 7.07901 9.13207 7.17857C9.20139 7.27813 9.29383 7.35939 9.40146 7.41537C9.50909 7.47135 9.62869 7.50039 9.75 7.5H15C15.1419 7.49952 15.2811 7.53931 15.4013 7.61477C15.5215 7.69022 15.6178 7.79823 15.6791 7.92626C15.7404 8.05428 15.764 8.19706 15.7474 8.33801C15.7307 8.47895 15.6744 8.61228 15.585 8.7225L8.16 16.3725C8.10431 16.4368 8.02841 16.4802 7.94477 16.4957C7.86112 16.5112 7.77471 16.4977 7.6997 16.4576C7.6247 16.4175 7.56556 16.3531 7.532 16.2749C7.49844 16.1968 7.49244 16.1095 7.515 16.0275L8.955 11.5125C8.99746 11.3989 9.01172 11.2766 8.99656 11.1562C8.98139 11.0359 8.93726 10.921 8.86793 10.8214C8.79861 10.7219 8.70617 10.6406 8.59855 10.5846C8.49092 10.5286 8.37132 10.4996 8.25 10.5H3Z"
          :stroke="marketStore.mode === 'nsfw' ? '#0C0A09' : '#78716C'"
          stroke-width="1.65"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <span class="text-[14px] leading-[20px] tracking-[-0.176px]">绅士卡</span>
    </button>
  </div>
</template>
