<script setup lang="ts">
/**
 * 个人历史记录顶部 Header (1:1 原型像素级高保真)
 *
 * @packageDocumentation
 */

const emit = defineEmits<(e: "backup") => void>();
</script>

<template>
  <header class="w-full flex items-center justify-between pt-8 px-4 pb-0">
    <!-- 左侧大标题 -->
    <h1 class="text-[20px] font-semibold text-[#F5F5F4] leading-[24px] tracking-[1px]">
      历史记录
    </h1>

    <!-- 右侧云端备份金边按钮 (72.6px * 36px) -->
    <button
      type="button"
      @click="emit('backup')"
      class="w-[72.6px] h-[36px] px-3 flex items-center justify-center rounded-[8px] border border-[#F9C86D] bg-transparent text-[12px] font-medium text-[#A8A29E] hover:text-[#F9C86D] hover:bg-[#F9C86D]/10 active:scale-95 transition-all shadow-[0_0_15px_rgba(249,200,109,0.08)] cursor-pointer select-none"
    >
      云端备份
    </button>
  </header>
</template>
