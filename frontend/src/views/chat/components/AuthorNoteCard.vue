<script setup lang="ts">
/**
 * AI 聊天界面 - 「作者的话」卡片 (1:1 Figma 原型高保真)
 *
 * @packageDocumentation
 */

defineProps<{
  note: string;
}>();
</script>

<template>
  <div class="w-full flex flex-col items-center px-4 py-2 select-none relative">
    
    <!-- 1. 居中药丸徽标: 💬 作者的话 (#3B82F6) -->
    <div class="px-4 py-1.5 rounded-full border border-white/18 bg-black/40 backdrop-blur-md flex items-center gap-1.5 z-10 -mb-3 shadow-md">
      <!-- 💬 矢量气泡图标 -->
      <svg width="14" height="14" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M5.33333 6.66666H5.34M8 6.66666H8.00667M10.6667 6.66666H10.6733M6 10.6667H3.33333C2.97971 10.6667 2.64057 10.5262 2.39052 10.2761C2.14048 10.0261 2 9.68695 2 9.33332V3.99999C2 3.64637 2.14048 3.30723 2.39052 3.05718C2.64057 2.80713 2.97971 2.66666 3.33333 2.66666H12.6667C13.0203 2.66666 13.3594 2.80713 13.6095 3.05718C13.8595 3.30723 14 3.64637 14 3.99999V9.33332C14 9.68695 13.8595 10.0261 13.6095 10.2761C13.3594 10.5262 13.0203 10.6667 12.6667 10.6667H9.33333L6 13.3333V10.6667Z" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="text-[13px] font-medium text-[#3B82F6]">
        作者的话
      </span>
    </div>

    <!-- 2. 微光发光磨砂卡片主体 (border: 0.667px solid rgba(255, 255, 255, 0.85); background: linear-gradient(135deg, rgba(249, 200, 109, 0.08) ...)) -->
    <div class="w-full rounded-lg border border-white/85 bg-gradient-to-br from-[#F9C86D]/[0.08] to-[#F9C86D]/[0.08] p-4 pt-5 shadow-[0_2px_8px_rgba(0,0,0,0.1)] backdrop-blur-md">
      <div class="text-[14px] text-white/90 leading-[1.65] font-sans whitespace-pre-line tracking-tight">
        {{ note }}
      </div>
    </div>

  </div>
</template>
