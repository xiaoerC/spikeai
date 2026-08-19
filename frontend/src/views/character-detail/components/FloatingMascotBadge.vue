<script setup lang="ts">
/**
 * 角色卡详情 - 右下角悬浮吉祥物小鸟微章 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

const emit = defineEmits<(e: "click") => void>();
</script>

<template>
  <button
    type="button"
    @click="emit('click')"
    class="fixed right-4 bottom-20 z-40 w-14 h-14 rounded-full border-2 border-[#F9C86D] bg-[#292524] shadow-[0_4px_16px_rgba(0,0,0,0.5),0_0_0_3px_rgba(249,200,109,0.15)] flex items-center justify-center hover:scale-105 active:scale-95 transition-all cursor-pointer select-none"
    title="叙梦助手"
  >
    <!-- 粉红吉祥物小鸟 SVG -->
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M16 4C13.5 4 11 6 11 8.5C11 9.5 11.5 10.5 12 11.5L4 16C3 16.5 2.5 17.5 3 18.5C3.5 19.5 4.5 20 5.5 20H15C18.5 20 21 17.5 21 14C21 8.5 18.5 4 16 4Z" fill="#FF69B4"/>
      <circle cx="16" cy="8" r="1.5" fill="#0C0A09"/>
      <path d="M21 9L23 10.5L21 12" stroke="#F9C86D" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  </button>
</template>
