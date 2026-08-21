<script setup lang="ts">
/**
 * 个人历史记录批量操作悬浮底部栏 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

defineProps<{
  selectedCount: number;
}>();

const emit = defineEmits<{
  (e: "cancel"): void;
  (e: "delete"): void;
}>();
</script>

<template>
  <div class="fixed bottom-20 left-1/2 -translate-x-1/2 z-40 w-[90%] max-w-[400px] px-4 py-3 rounded-2xl bg-[rgba(26,23,20,0.95)] border border-[#F9C86D]/30 shadow-2xl backdrop-blur-xl flex items-center justify-between animate-in slide-in-from-bottom-5 duration-200">
    <span class="text-xs text-[#F5F5F4] font-medium">
      已选择 <strong class="text-[#F9C86D]">{{ selectedCount }}</strong> 项
    </span>

    <div class="flex items-center gap-2">
      <button
        type="button"
        @click="emit('cancel')"
        class="px-3 py-1.5 rounded-lg bg-[#292524] text-xs text-[#A8A29E] hover:text-white transition-colors cursor-pointer"
      >
        取消
      </button>
      <button
        type="button"
        @click="emit('delete')"
        :disabled="selectedCount === 0"
        :class="[
          'px-4 py-1.5 rounded-lg text-xs font-bold transition-all cursor-pointer select-none',
          selectedCount > 0
            ? 'bg-[#EF4444] text-white active:scale-95 shadow-md'
            : 'bg-[#383330] text-[#78716C] cursor-not-allowed'
        ]"
      >
        确认删除
      </button>
    </div>
  </div>
</template>
