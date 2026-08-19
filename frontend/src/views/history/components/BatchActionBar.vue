<script setup lang="ts">
/**
 * 历史记录批量管理底部操作条
 *
 * @packageDocumentation
 */

import { AppButton } from "@/components/common";
import { CheckSquare, Trash2, X } from "lucide-vue-next";

defineProps<{
  /** 当前已选中的卡片数量 */
  selectedCount: number;
  /** 当前列表所有卡片总数 */
  totalCount: number;
}>();

const emit = defineEmits<{
  (e: "select-all"): void;
  (e: "clear-selection"): void;
  (e: "delete-selected"): void;
  (e: "exit"): void;
}>();
</script>

<template>
  <!-- 底部固定悬浮条: 位于 TabBar 上方 -->
  <div class="fixed bottom-[74px] left-0 right-0 z-40 px-3 pointer-events-none">
    <div class="max-w-[440px] mx-auto pointer-events-auto">
      <div class="flex items-center justify-between p-3 rounded-2xl border border-[#F9C86D]/40 bg-[rgba(26,23,20,0.96)] shadow-2xl backdrop-blur-xl animate-fade-in">
        
        <!-- 左侧信息与全选 -->
        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="emit('select-all')"
            class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-[#44403C] text-xs text-gray-200 hover:border-[#F9C86D] hover:text-[#F9C86D] transition-colors cursor-pointer select-none"
          >
            <CheckSquare class="w-3.5 h-3.5" />
            <span>全选</span>
          </button>

          <span class="text-xs text-[#A8A29E]">
            已选 <strong class="text-[#F9C86D]">{{ selectedCount }}</strong> / {{ totalCount }}
          </span>
        </div>

        <!-- 右侧删除与退出 -->
        <div class="flex items-center gap-2">
          <AppButton
            variant="danger"
            size="sm"
            :disabled="selectedCount === 0"
            @click="emit('delete-selected')"
          >
            <Trash2 class="w-3.5 h-3.5 mr-1" />
            <span>删除({{ selectedCount }})</span>
          </AppButton>

          <button
            type="button"
            @click="emit('exit')"
            class="p-1.5 rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/10 transition-colors cursor-pointer select-none"
            title="退出管理"
          >
            <X class="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  </div>
</template>
