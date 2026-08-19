<script setup lang="ts">
/**
 * 历史记录角色卡片 2 列网格组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { HistoryCharacterCard } from "@/views/history/types";

defineProps<{
  cards: HistoryCharacterCard[];
}>();

const emit = defineEmits<(e: "select-card", card: HistoryCharacterCard) => void>();
</script>

<template>
  <div class="grid grid-cols-2 gap-3 w-full">
    <div
      v-for="card in cards"
      :key="card.id"
      @click="emit('select-card', card)"
      class="relative flex flex-col rounded-xl overflow-hidden bg-[rgba(26,21,16,0.97)] border border-white/5 hover:border-[#F9C86D]/40 transition-all duration-200 cursor-pointer group shadow-lg"
    >
      <!-- 1. 卡片立绘与悬浮标签层 (约 130px 高度) -->
      <div class="relative w-full h-32 overflow-hidden bg-[#292524]">
        <img
          :src="card.coverUrl"
          :alt="card.title"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <!-- 渐变遮罩 -->
        <div class="absolute inset-0 bg-gradient-to-t from-[rgba(26,21,16,0.97)] via-transparent to-black/30" />

        <!-- 顶部左侧: @作者微胶囊 Badge -->
        <div class="absolute top-2 left-2 z-10 px-2 py-0.5 rounded-full border border-[rgba(148,0,211,0.60)] bg-black/60 backdrop-blur-xs shadow-[0_0_6px_rgba(255,180,80,0.40)]">
          <span class="text-[11px] font-medium text-[#F9C86D]">
            {{ card.authorName }}
          </span>
        </div>

        <!-- 顶部右侧: 火热指数 -->
        <div class="absolute top-2 right-2 z-10 flex items-center gap-1 bg-black/50 px-1.5 py-0.5 rounded backdrop-blur-xs">
          <svg class="w-3.5 h-3.5 text-[#EAB308]" viewBox="0 0 16 16" fill="none">
            <path d="M11.77 12.44C10.77 13.44 9.41 14 8 14C6.59 14 5.23 13.44 4.23 12.44C3.23 11.44 2.67 10.08 2.67 8.67C2.67 7.25 3.23 5.9 4.23 4.9C4.23 4.9 4.67 6 6 6.67C6 5.33 6.33 3.33 8 2C9.33 3.33 10.73 3.85 11.77 4.9C12.27 5.39 12.66 5.98 12.93 6.63C13.2 7.27 13.33 7.97 13.33 8.67C13.33 9.37 13.2 10.06 12.93 10.71C12.66 11.36 12.27 11.94 11.77 12.44Z" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-xs font-bold text-[#EAB308]">{{ card.heat }}</span>
        </div>
      </div>

      <!-- 2. 卡片下方信息详情层 -->
      <div class="p-2.5 flex flex-col gap-1.5 justify-between flex-1">
        <!-- 标题 -->
        <h3 class="text-xs font-semibold text-[#F9C86D] line-clamp-1 leading-snug">
          {{ card.title }}
        </h3>

        <!-- 3 大指标: 评论 / Token / 评分 -->
        <div class="flex items-center gap-2 text-[10px] text-[#FF9F43]">
          <!-- 评论数 -->
          <div class="flex items-center gap-0.5">
            <svg class="w-3 h-3" viewBox="0 0 12 12" fill="none">
              <path d="M4 6H4.005M6 6H6.005M8 6H8.005M10.5 6C10.5 8.209 8.485 10 6 10C5.26432 10.0025 4.5374 9.84038 3.8725 9.5255L1.5 10L2.1975 8.14C1.756 7.521 1.5 6.787 1.5 6C1.5 3.791 3.515 2 6 2C8.485 2 10.5 3.791 10.5 6Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ card.commentsCount }}</span>
          </div>

          <!-- Token 数 -->
          <div class="flex items-center gap-0.5">
            <svg class="w-3 h-3" viewBox="0 0 12 12" fill="none">
              <path d="M6.5 5V1.5L2 7H5.5V10.5L10 5H6.5Z" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ card.tokenUsage }}</span>
          </div>

          <!-- 评分 (若有) -->
          <div v-if="card.rating" class="flex items-center gap-0.5 text-[#F9C86D]">
            <svg class="w-3 h-3 fill-current" viewBox="0 0 12 12">
              <path d="M5.74 1.75C5.76 1.7 5.8 1.65 5.84 1.62C5.89 1.59 5.94 1.58 6 1.58C6.06 1.58 6.11 1.59 6.16 1.62C6.2 1.65 6.24 1.7 6.26 1.75L7.32 4.31C7.34 4.35 7.38 4.39 7.42 4.42C7.46 4.46 7.51 4.47 7.56 4.48L10.32 4.7C10.57 4.72 10.67 5.03 10.48 5.19L8.38 6.99C8.34 7.03 8.31 7.07 8.29 7.12C8.28 7.17 8.27 7.22 8.29 7.27L8.93 9.96C8.94 10.02 8.94 10.08 8.92 10.13C8.9 10.18 8.87 10.22 8.82 10.26C8.78 10.29 8.72 10.31 8.67 10.31C8.61 10.31 8.56 10.3 8.51 10.27L6.15 8.83C6.1 8.8 6.05 8.79 6 8.79C5.95 8.79 5.9 8.8 5.85 8.83L3.49 10.27C3.44 10.3 3.39 10.31 3.33 10.31C3.28 10.31 3.22 10.29 3.18 10.26C3.13 10.23 3.1 10.18 3.08 10.13C3.06 10.08 3.06 10.02 3.07 9.96L3.71 7.27C3.73 7.22 3.72 7.17 3.71 7.12C3.69 7.07 3.66 7.03 3.62 6.99L1.52 5.19C1.48 5.16 1.45 5.11 1.43 5.06C1.42 5 1.42 4.94 1.44 4.89C1.45 4.84 1.49 4.79 1.53 4.76C1.57 4.72 1.63 4.7 1.68 4.7L4.44 4.48C4.49 4.47 4.54 4.46 4.58 4.42C4.62 4.39 4.66 4.35 4.68 4.31L5.74 1.75Z"/>
            </svg>
            <span class="font-bold">{{ card.rating }}</span>
          </div>
        </div>

        <!-- 摘要 (2行收敛) -->
        <p class="text-[10px] text-white/70 line-clamp-2 leading-tight">
          {{ card.summary }}
        </p>

        <!-- 标签组 -->
        <div class="flex items-center gap-1 overflow-x-hidden pt-0.5">
          <span
            v-for="tag in card.tags"
            :key="tag"
            class="px-1.5 py-0.5 rounded-full text-[9px] font-medium border border-white/20 bg-white/10 text-white/80"
          >
            {{ tag }}
          </span>
        </div>
      </div>

    </div>
  </div>
</template>
