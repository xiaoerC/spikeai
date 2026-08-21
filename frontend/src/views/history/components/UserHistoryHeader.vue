<script setup lang="ts">
/**
 * 个人历史记录顶部 Header (1:1 原型高保真)
 *
 * @packageDocumentation
 */

const emit = defineEmits<(e: "backup") => void>();
</script>

<template>
  <header class="w-full flex items-center justify-between pt-6 pb-2">
    <!-- 左侧大标题 -->
    <h1 class="text-xl font-semibold text-[#F5F5F4] tracking-wide">
      历史记录
    </h1>

    <!-- 右侧云端备份金边按钮 -->
    <button
      type="button"
      @click="emit('backup')"
      class="px-3 py-1.5 rounded-lg border border-[#F9C86D] text-xs font-medium text-[#A8A29E] hover:text-[#F9C86D] hover:bg-[#F9C86D]/10 active:scale-95 transition-all shadow-[0_0_15px_rgba(249,200,109,0.08)] cursor-pointer select-none"
    >
      云端备份
    </button>
  </header>
</template>
