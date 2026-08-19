<script setup lang="ts">
/**
 * AI 聊天界面 - 底部胶囊输入栏 (1:1 Figma 原型高保真)
 *
 * @packageDocumentation
 */

import { ref } from "vue";

defineProps<{
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: "send", text: string): void;
  (e: "aiAssist"): void;
  (e: "expand"): void;
  (e: "plus"): void;
}>();

const inputText = ref("");

function handleSend(): void {
  if (!inputText.value.trim()) return;
  emit("send", inputText.value.trim());
  inputText.value = "";
}

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}
</script>

<template>
  <div class="w-full z-30 select-none bg-transparent">



    
    <!-- 全圆角胶囊输入容器 (border: 0.667px solid #44403C, border-radius: 9999px, background: rgba(0,0,0,0.5), backdrop-blur) -->
    <div class="w-full h-11 px-2 rounded-full border border-[#44403C]/80 bg-black/50 backdrop-blur-xl flex items-center justify-between gap-2 shadow-2xl">
      
      <!-- 1. 左侧: ✦ AI 辅助/火花金色四角星图标 -->
      <button
        type="button"
        @click="emit('aiAssist')"
        class="w-7 h-7 rounded-full flex items-center justify-center text-[#F9C86D] hover:scale-110 active:scale-95 transition-all cursor-pointer shrink-0"
        title="AI 灵感辅助"
      >
        <svg width="18" height="18" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 2L6.72533 5.87533C6.6601 6.07367 6.5492 6.25392 6.40156 6.40156C6.25392 6.5492 6.07367 6.6601 5.87533 6.72533L2 8L5.87533 9.27467C6.07367 9.3399 6.25392 9.4508 6.40156 9.59844C6.5492 9.74608 6.6601 9.92633 6.72533 10.1247L8 14L9.27467 10.1247C9.3399 9.92633 9.4508 9.74608 9.59844 9.59844C9.74608 9.4508 9.92633 9.3399 10.1247 9.27467L14 8L10.1247 6.72533C9.92633 6.6601 9.74608 6.5492 9.59844 6.40156C9.4508 6.25392 9.3399 6.07367 9.27467 5.87533L8 2Z" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M3.33334 2V4.66667" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12.6667 11.3333V14" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 3.33334H4.66667" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M11.3333 12.6667H14" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- 2. 中间输入区 (带微圆角内框: background: rgba(42, 37, 32, 0.50); border: 0.667px solid rgba(83, 71, 65, 0.30); border-radius: 6px) -->
      <div class="flex-1 h-8 px-2.5 rounded-md border border-[#534741]/30 bg-[#2A2520]/50 flex items-center justify-between gap-1 focus-within:border-[#F9C86D]/50 transition-colors">
        <input
          v-model="inputText"
          type="text"
          :disabled="disabled"
          placeholder="发送消息..."
          @keydown="handleKeydown"
          class="flex-1 bg-transparent border-none outline-none text-xs text-white/95 placeholder-white/40 font-sans tracking-tight"
        />

        <!-- ⤢ 展开输入框按钮 -->
        <button
          type="button"
          @click="emit('expand')"
          class="w-5 h-5 flex items-center justify-center text-white/70 hover:text-white transition-colors cursor-pointer shrink-0"
          title="展开输入框"
        >
          <svg width="12" height="12" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8.75 1.75H12.25V5.25" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.25 1.75L8.16669 5.83333" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1.75 12.25L5.83333 8.16666" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.25 12.25H1.75V8.75" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- 3. 最右侧: ✚ 金色十字加号/发送按钮 -->
      <button
        type="button"
        @click="inputText.trim() ? handleSend() : emit('plus')"
        :class="[
          'w-7 h-7 rounded-full flex items-center justify-center transition-all cursor-pointer shrink-0',
          inputText.trim()
            ? 'bg-[#F9C86D] text-[#0C0A09] hover:scale-105 active:scale-95'
            : 'text-[#D1A35C] hover:bg-white/5 active:scale-95'
        ]"
        :title="inputText.trim() ? '发送' : '添加附件/世界书'"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M3.33331 8H12.6666" :stroke="inputText.trim() ? '#0C0A09' : '#D1A35C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8 3.33334V12.6667" :stroke="inputText.trim() ? '#0C0A09' : '#D1A35C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

    </div>
  </div>
</template>
