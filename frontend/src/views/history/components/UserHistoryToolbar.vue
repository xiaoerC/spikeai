<script setup lang="ts">
/**
 * 个人历史记录右侧操作工具栏 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { LayoutGrid } from "lucide-vue-next";

defineProps<{
  isBatchMode: boolean;
}>();

const emit = defineEmits<(e: "toggle-batch") => void>();
</script>

<template>
  <div class="w-full flex items-center justify-end gap-2 mt-4">
    <!-- 宫格视图按钮 -->
    <button
      type="button"
      class="p-1.5 rounded-md border border-[#44403C] text-[#A8A29E] hover:text-white hover:bg-white/5 active:scale-95 transition-all cursor-pointer select-none"
    >
      <LayoutGrid class="w-3.5 h-3.5" />
    </button>

    <!-- 批量删除按钮 -->
    <button
      type="button"
      @click="emit('toggle-batch')"
      :class="[
        'px-3 py-1 rounded-md border text-xs font-normal transition-all cursor-pointer select-none',
        isBatchMode
          ? 'border-[#EF4444] bg-[#EF4444]/15 text-[#EF4444]'
          : 'border-[#44403C] text-[#A8A29E] hover:text-white hover:bg-white/5'
      ]"
    >
      {{ isBatchMode ? "取消" : "批量删除" }}
    </button>
  </div>
</template>
