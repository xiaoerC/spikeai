<script setup lang="ts">
/**
 * 问卷分类切换 Tabs 组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { SurveyTabType } from "@/views/survey/types";

defineProps<{
  activeTab: SurveyTabType;
}>();

const emit = defineEmits<(e: "change-tab", tab: SurveyTabType) => void>();
</script>

<template>
  <div class="w-full flex items-center justify-center border-b border-[#44403C] gap-1 px-4 mt-4">
    <!-- 1. 问卷列表 Tab -->
    <button
      type="button"
      @click="emit('change-tab', 'list')"
      :class="[
        'flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition-all cursor-pointer select-none relative pb-2.5',
        activeTab === 'list'
          ? 'text-[#F9C86D] border-b-2 border-[#F9C86D]'
          : 'text-[#78716C] hover:text-[#A8A29E] border-b-2 border-transparent'
      ]"
    >
      <!-- 剪贴板 SVG 图标 -->
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="flex-shrink-0">
        <path d="M10 1.33334H6C5.63181 1.33334 5.33334 1.63182 5.33334 2.00001V3.33334C5.33334 3.70153 5.63181 4.00001 6 4.00001H10C10.3682 4.00001 10.6667 3.70153 10.6667 3.33334V2.00001C10.6667 1.63182 10.3682 1.33334 10 1.33334Z" :stroke="activeTab === 'list' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M10.6667 2.66666H12C12.3536 2.66666 12.6928 2.80713 12.9428 3.05718C13.1929 3.30723 13.3333 3.64637 13.3333 3.99999V13.3333C13.3333 13.6869 13.1929 14.0261 12.9428 14.2761C12.6928 14.5262 12.3536 14.6667 12 14.6667H4C3.64638 14.6667 3.30724 14.5262 3.05719 14.2761C2.80714 14.0261 2.66666 13.6869 2.66666 13.3333V3.99999C2.66666 3.64637 2.80714 3.30723 3.05719 3.05718C3.30724 2.80713 3.64638 2.66666 4 2.66666H5.33333" :stroke="activeTab === 'list' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M8 7.33334H10.6667" :stroke="activeTab === 'list' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M8 10.6667H10.6667" :stroke="activeTab === 'list' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>问卷列表</span>
    </button>

    <!-- 2. 我的记录 Tab -->
    <button
      type="button"
      @click="emit('change-tab', 'records')"
      :class="[
        'flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition-all cursor-pointer select-none relative pb-2.5',
        activeTab === 'records'
          ? 'text-[#F9C86D] border-b-2 border-[#F9C86D]'
          : 'text-[#78716C] hover:text-[#A8A29E] border-b-2 border-transparent'
      ]"
    >
      <!-- 打勾圆形 SVG 图标 -->
      <svg width="16" height="16" viewBox="0 0 16 16" fill="none" class="flex-shrink-0">
        <path d="M8 14.6667C11.6819 14.6667 14.6667 11.6819 14.6667 8.00001C14.6667 4.31811 11.6819 1.33334 8 1.33334C4.3181 1.33334 1.33334 4.31811 1.33334 8.00001C1.33334 11.6819 4.3181 14.6667 8 14.6667Z" :stroke="activeTab === 'records' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M6 7.99999L7.33333 9.33332L10 6.66666" :stroke="activeTab === 'records' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span>我的记录</span>
    </button>
  </div>
</template>
