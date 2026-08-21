<script setup lang="ts">
/**
 * 问卷右下角 🐦 悬浮反馈按钮组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

const emit = defineEmits<(e: "click") => void>();
</script>

<template>
  <button
    type="button"
    @click="emit('click')"
    class="fixed right-5 bottom-24 z-30 w-14 h-14 rounded-full flex items-center justify-center bg-[#292524] border-2 border-[#F9C86D] shadow-[0_4px_16px_rgba(0,0,0,0.20),0_0_0_3px_rgba(249,200,109,0.15)] active:scale-95 transition-all cursor-pointer select-none"
  >
    <span class="text-2xl text-[#C0A480]">🐦</span>
  </button>
</template>
