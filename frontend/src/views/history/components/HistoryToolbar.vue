<script setup lang="ts">
/**
 * 历史记录操作工具栏组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { HistoryViewMode } from "@/views/history/types";

defineProps<{
  /** 当前视图布局模式 */
  viewMode: HistoryViewMode;
  /** 是否处于批量删除管理模式 */
  isBatchMode: boolean;
}>();

const emit = defineEmits<{
  (e: "toggle-view"): void;
  (e: "toggle-batch"): void;
}>();
</script>

<template>
  <div class="flex items-center justify-end gap-2.5 w-full px-4 pt-6 pb-3">
    <!-- 1. 视图切换按钮 (四宫格原生 SVG, border: 0.667px solid #44403C) -->
    <button
      type="button"
      @click="emit('toggle-view')"
      class="p-[6px_8px] rounded-md border border-[#44403C] bg-transparent text-[#A8A29E] hover:text-white hover:border-[#666] active:scale-95 transition-all duration-150 cursor-pointer select-none flex items-center justify-center"
      title="切换网格/列表视图"
    >
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5 1H2C1.44772 1 1 1.44772 1 2V5C1 5.55228 1.44772 6 2 6H5C5.55228 6 6 5.55228 6 5V2C6 1.44772 5.55228 1 5 1Z" stroke="#A8A29E" stroke-width="1.5"/>
        <path d="M12 1H9C8.44772 1 8 1.44772 8 2V5C8 5.55228 8.44772 6 9 6H12C12.5523 6 13 5.55228 13 5V2C13 1.44772 12.5523 1 12 1Z" stroke="#A8A29E" stroke-width="1.5"/>
        <path d="M5 8H2C1.44772 8 1 8.44772 1 9V12C1 12.5523 1.44772 13 2 13H5C5.55228 13 6 12.5523 6 12V9C6 8.44772 5.55228 8 5 8Z" stroke="#A8A29E" stroke-width="1.5"/>
        <path d="M12 8H9C8.44772 8 8 8.44772 8 9V12C8 12.5523 8.44772 13 9 13H12C12.5523 13 13 12.5523 13 12V9C13 8.44772 12.5523 8 12 8Z" stroke="#A8A29E" stroke-width="1.5"/>
      </svg>
    </button>

    <!-- 2. 批量删除触发按钮 -->
    <button
      type="button"
      @click="emit('toggle-batch')"
      :class="[
        'px-3 py-[6px] rounded-md border text-xs leading-[16px] tracking-[-0.176px] transition-all duration-150 cursor-pointer select-none flex items-center justify-center',
        isBatchMode
          ? 'border-[#F9C86D] text-[#F9C86D] bg-[#F9C86D]/15 font-medium'
          : 'border-[#44403C] text-[#A8A29E] bg-transparent hover:border-[#666] hover:text-white active:scale-95'
      ]"
    >
      <span>{{ isBatchMode ? "退出管理" : "批量删除" }}</span>
    </button>
  </div>
</template>
