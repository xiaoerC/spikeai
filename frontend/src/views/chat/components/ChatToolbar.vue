<script setup lang="ts">
/**
 * AI 聊天界面 - 模型与模式工具条 (1:1 Figma 原型高保真)
 *
 * @packageDocumentation
 */

import type { AiModelItem } from "@/views/chat/constants/mockChatData";

defineProps<{
  currentModel: AiModelItem;
  currentMode: "story" | "room";
}>();

const emit = defineEmits<{
  (e: "openModelSelector"): void;
  (e: "switchMode", mode: "story" | "room"): void;
}>();
</script>

<template>
  <div class="w-full flex items-center justify-between z-20 select-none bg-transparent">

    
    <!-- 1. 左侧模型选择胶囊 (border: 0.667px solid rgba(255, 255, 255, 0.18); background: rgba(0, 0, 0, 0.25)) -->
    <button
      type="button"
      @click="emit('openModelSelector')"
      class="h-[29.3px] px-2 rounded-full border border-white/18 bg-black/40 backdrop-blur-md flex items-center gap-1.5 text-xs text-white/90 hover:border-[#F9C86D]/50 transition-all cursor-pointer truncate max-w-[270px] shadow-sm"
    >
      <!-- 蓝色竖条指示器 -->
      <div class="w-1 h-3 rounded-full bg-[#3B82F6] shrink-0" />

      <!-- 双子星 AI 渐变四角星光辉图标 -->
      <svg width="15" height="15" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
        <path d="M10 20C9.61883 17.4841 8.44253 15.1561 6.6432 13.3568C4.84386 11.5575 2.51593 10.3812 0 10C2.51593 9.61883 4.84386 8.44253 6.6432 6.6432C8.44253 4.84386 9.61883 2.51593 10 0C10.3813 2.51588 11.5576 4.84374 13.3569 6.64306C15.1563 8.44237 17.4841 9.61871 20 10C17.4841 10.3813 15.1563 11.5576 13.3569 13.3569C11.5576 15.1563 10.3813 17.4841 10 20Z" fill="url(#gemini_grad)"/>
        <defs>
          <linearGradient id="gemini_grad" x1="0" y1="20" x2="14" y2="6" gradientUnits="userSpaceOnUse">
            <stop stop-color="#1C7DFF"/>
            <stop offset="0.52" stop-color="#1C69FF"/>
            <stop offset="1" stop-color="#F0DCD6"/>
          </linearGradient>
        </defs>
      </svg>

      <!-- 模型名: 快速双子星3（关流 -->
      <span class="text-[10px] text-white/90 truncate max-w-[85px]">
        {{ currentModel.name }}
      </span>

      <!-- ★ 15 -->
      <div class="flex items-center gap-0.5">
        <svg width="9" height="9" viewBox="0 0 10 10" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4.99998 0.833344L6.28748 3.44168L9.16665 3.86251L7.08331 5.89168L7.57498 8.75834L4.99998 7.40418L2.42498 8.75834L2.91665 5.89168L0.833313 3.86251L3.71248 3.44168L4.99998 0.833344Z" fill="#EAB308"/>
        </svg>
        <span class="text-[11px] font-mono text-white/90">{{ currentModel.cost }}</span>
      </div>

      <!-- 会员免费(30/30) 橙色微标签 -->
      <span class="text-[10px] text-[#FF9F43] bg-[#FF9F43]/10 px-1 rounded-sm shrink-0">
        {{ currentModel.freeCountText }}
      </span>

      <!-- 下拉小箭头 ∨ -->
      <svg width="8" height="8" viewBox="0 0 8 8" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0 opacity-80">
        <path d="M6.33335 3L4.00002 5.33333L1.66669 3" stroke="white" stroke-opacity="0.9" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <!-- 2. 右侧模式切换药丸按钮组 (剧情 / 聊天室) -->
    <div class="flex items-center gap-1.5">
      
      <!-- 剧情模式 (带卷轴图标) -->
      <button
        type="button"
        @click="emit('switchMode', 'story')"
        :class="[
          'h-[29.3px] px-2.5 rounded-full border flex items-center gap-1 text-[10px] backdrop-blur-md transition-all cursor-pointer shadow-sm',
          currentMode === 'story'
            ? 'border-[#F9C86D]/60 bg-[#F9C86D]/20 text-white font-medium'
            : 'border-white/18 bg-black/40 text-white/80 hover:text-white'
        ]"
      >
        <svg width="11" height="11" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M7.5 6H5" stroke="white" stroke-opacity="0.9" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M7.5 4H5" stroke="white" stroke-opacity="0.9" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M9.5 8.5V2.5C9.5 2.23478 9.39464 1.98043 9.20711 1.79289C9.01957 1.60536 8.76522 1.5 8.5 1.5H2" stroke="white" stroke-opacity="0.9" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M4 10.5H10C10.2652 10.5 10.5196 10.3946 10.7071 10.2071C10.8946 10.0196 11 9.76522 11 9.5V9C11 8.86739 10.9473 8.74021 10.8536 8.64645C10.7598 8.55268 10.6326 8.5 10.5 8.5H5.5C5.36739 8.5 5.24021 8.55268 5.14645 8.64645C5.05268 8.74021 5 8.86739 5 9V9.5C5 9.76522 4.89464 10.0196 4.70711 10.2071C4.51957 10.3946 4.26522 10.5 4 10.5ZM4 10.5C3.73478 10.5 3.48043 10.3946 3.29289 10.2071C3.10536 10.0196 3 9.76522 3 9.5V2.5C3 2.23478 2.89464 1.98043 2.70711 1.79289C2.51957 1.60536 2.26522 1.5 2 1.5C1.73478 1.5 1.48043 1.60536 1.29289 1.79289C1.10536 1.98043 1 2.23478 1 2.5V3.5C1 3.63261 1.05268 3.75979 1.14645 3.85355C1.24021 3.94732 1.36739 4 1.5 4H3" stroke="white" stroke-opacity="0.9" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>剧情</span>
      </button>

      <!-- 聊天室模式 -->
      <button
        type="button"
        @click="emit('switchMode', 'room')"
        :class="[
          'h-[29.3px] px-2.5 rounded-full border flex items-center gap-1 text-[10px] backdrop-blur-md transition-all cursor-pointer shadow-sm',
          currentMode === 'room'
            ? 'border-[#F9C86D]/60 bg-[#F9C86D]/20 text-white font-medium'
            : 'border-white/18 bg-black/40 text-white/80 hover:text-white'
        ]"
      >
        <span>聊天室</span>
      </button>

    </div>

  </div>
</template>
