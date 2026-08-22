<script setup lang="ts">
/**
 * 个人历史记录右侧操作工具栏 (1:1 原型高保真)
 *
 * 支持宫格/列表排版双态切换与批量多选模式。
 *
 * @packageDocumentation
 */

import type { HistoryViewMode } from "@/views/history/types";
import { LayoutGrid } from "lucide-vue-next";

defineProps<{
  viewMode: HistoryViewMode;
  isBatchMode: boolean;
}>();

const emit = defineEmits<{
  (e: "toggle-view"): void;
  (e: "toggle-batch"): void;
}>();
</script>

<template>
  <div class="w-full flex items-center justify-end gap-2 px-4 pt-6">
    <!-- 视图切换按钮 (宫格 田 / 列表 ☰) -->
    <button
      type="button"
      @click="emit('toggle-view')"
      title="切换视图排版"
      :class="[
        'p-1.5 rounded-[6px] border border-[#44403C] transition-all cursor-pointer select-none flex items-center justify-center',
        viewMode === 'list'
          ? 'bg-white/10 text-white border-[#F9C86D]/50 shadow-[0_0_8px_rgba(249,200,109,0.15)]'
          : 'text-[#A8A29E] hover:text-white hover:bg-white/5'
      ]"
    >
      <!-- 列表视图 ☰ 图标 (Figma 1:1 SVG) -->
      <svg
        v-if="viewMode === 'list'"
        width="14"
        height="14"
        viewBox="0 0 14 14"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path d="M12.25 2H1.75C1.33579 2 1 2.33579 1 2.75C1 3.16421 1.33579 3.5 1.75 3.5H12.25C12.6642 3.5 13 3.16421 13 2.75C13 2.33579 12.6642 2 12.25 2Z" fill="currentColor"/>
        <path d="M12.25 6.25H1.75C1.33579 6.25 1 6.58579 1 7C1 7.41421 1.33579 7.75 1.75 7.75H12.25C12.6642 7.75 13 7.41421 13 7C13 6.58579 12.6642 6.25 12.25 6.25Z" fill="currentColor"/>
        <path d="M12.25 10.5H1.75C1.33579 10.5 1 10.8358 1 11.25C1 11.6642 1.33579 12 1.75 12H12.25C12.6642 12 13 11.6642 13 11.25C13 10.8358 12.6642 10.5 12.25 10.5Z" fill="currentColor"/>
      </svg>
      <!-- 宫格视图 田 图标 -->
      <LayoutGrid v-else class="w-3.5 h-3.5" />
    </button>

    <!-- 批量删除按钮 -->
    <button
      type="button"
      @click="emit('toggle-batch')"
      :class="[
        'px-3 py-1.5 rounded-[6px] border text-[12px] font-normal leading-[16px] transition-all cursor-pointer select-none',
        isBatchMode
          ? 'border-[#EF4444] bg-[#EF4444]/15 text-[#EF4444]'
          : 'border-[#44403C] text-[#A8A29E] hover:text-white hover:bg-white/5'
      ]"
    >
      {{ isBatchMode ? "取消" : "批量删除" }}
    </button>
  </div>
</template>
