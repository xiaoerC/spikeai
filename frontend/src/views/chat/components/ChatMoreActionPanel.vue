<script setup lang="ts">
/**
 * AI 聊天界面 - 底部更多操作功能拓展面板 (1:1 Figma 原型 Frame 99:7366)
 *
 * 包含:
 * 1. 顶部点数与月亮积分状态胶囊 (⭐ 184 / 🌙 2,122)
 * 2. 第一行双列卡片:
 *    - 对话增强 (青绿 #56B3B4)
 *    - 记忆增强 (高亮紫色 #A855F7 切换态)
 * 3. 第二行双列卡片:
 *    - Mod 管理 (金色 #F9C86D + 窗口图标)
 *    - 画师串 · 二次元 (金色 #F9C86D + 星球星轨图标)
 *
 * @packageDocumentation
 */

import { ref } from "vue";

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "action", actionName: string): void;
}>();

// 记忆增强激活状态 (默认开启)
const isMemoryEnhanced = ref(true);
// 对话增强激活状态
const isDialogueEnhanced = ref(false);

function toggleMemory(): void {
  isMemoryEnhanced.value = !isMemoryEnhanced.value;
  emit("action", isMemoryEnhanced.value ? "memoryOn" : "memoryOff");
}

function toggleDialogue(): void {
  isDialogueEnhanced.value = !isDialogueEnhanced.value;
  emit("action", isDialogueEnhanced.value ? "dialogueOn" : "dialogueOff");
}

function handleAction(name: string): void {
  emit("action", name);
}

function handleClose(): void {
  emit("update:open", false);
}
</script>

<template>
  <!-- 点击外部透明遮罩 -->
  <div
    v-if="open"
    @click="handleClose"
    class="fixed inset-0 z-30 bg-transparent"
  />

  <!-- 1:1 更多操作扩展面板 -->
  <Transition name="panel-slide">
    <div
      v-if="open"
      class="w-full z-40 rounded-lg border border-[#44403C]/50 bg-[#1C1917]/95 backdrop-blur-2xl shadow-[0_10px_20px_0_rgba(0,0,0,0.60),0_6px_10px_0_rgba(0,0,0,0.50)] p-3 flex flex-col gap-2 select-none"
    >
      <!-- 1. 顶部资产胶囊 (⭐ 184 / 🌙 2,122) -->
      <div class="flex items-center">
        <div class="h-[29px] px-3.5 rounded-full border border-white/18 bg-black/25 backdrop-blur-md flex items-center gap-3 shadow-inner">
          <!-- 星星金币 -->
          <div class="flex items-center gap-1">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6 1L7.545 4.13L11 4.635L8.5 7.07L9.09 10.51L6 8.885L2.91 10.51L3.5 7.07L1 4.635L4.455 4.13L6 1Z" fill="#FFB900"/>
            </svg>
            <span class="text-xs text-white/90 font-mono leading-none">184</span>
          </div>

          <!-- 紫色弯月积分 -->
          <div class="flex items-center gap-1">
            <span class="text-xs leading-none">🌙</span>
            <span class="text-xs text-[#A855F7] font-mono font-medium leading-none">2,122</span>
          </div>
        </div>
      </div>

      <!-- 2. 第一行功能双列卡片 (对话增强 + 记忆增强) -->
      <div class="grid grid-cols-2 gap-2">
        <!-- (1) 对话增强 -->
        <button
          type="button"
          @click="toggleDialogue"
          :class="[
            'p-2.5 rounded-[6px] border flex items-center justify-between transition-all cursor-pointer group',
            isDialogueEnhanced
              ? 'border-[#56B3B4] bg-[#56B3B4] text-[#2A261F]'
              : 'border-[#44403C] bg-[#2A261F] text-[#56B3B4] hover:border-[#56B3B4]/50'
          ]"
        >
          <span class="text-xs font-medium">对话增强</span>
          <!-- 铅笔带底横线 SVG -->
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M7 11.6667H12.25" :stroke="isDialogueEnhanced ? '#2A261F' : '#56B3B4'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.625 2.0417C9.85706 1.80963 10.1718 1.67926 10.5 1.67926C10.6625 1.67926 10.8234 1.71127 10.9735 1.77345C11.1237 1.83564 11.2601 1.92679 11.375 2.0417C11.4899 2.1566 11.5811 2.29302 11.6432 2.44315C11.7054 2.59328 11.7374 2.75419 11.7374 2.9167C11.7374 3.0792 11.7054 3.24011 11.6432 3.39024C11.5811 3.54038 11.4899 3.67679 11.375 3.7917L4.08333 11.0834L1.75 11.6667L2.33333 9.33336L9.625 2.0417Z" :stroke="isDialogueEnhanced ? '#2A261F' : '#56B3B4'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- (2) 记忆增强 (高亮紫色状态) -->
        <button
          type="button"
          @click="toggleMemory"
          :class="[
            'p-2.5 rounded-[6px] border flex items-center justify-between transition-all cursor-pointer group',
            isMemoryEnhanced
              ? 'border-[#A855F7] bg-[#A855F7] text-[#2A261F]'
              : 'border-[#44403C] bg-[#2A261F] text-[#A855F7] hover:border-[#A855F7]/50'
          ]"
        >
          <span class="text-xs font-medium">记忆增强</span>
          <!-- 书本 SVG -->
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M1.16667 1.75H4.66667C5.28551 1.75 5.879 1.99583 6.31659 2.43342C6.75417 2.871 7 3.46449 7 4.08333V12.25C7 11.7859 6.81563 11.3408 6.48744 11.0126C6.15925 10.6844 5.71413 10.5 5.25 10.5H1.16667V1.75Z" :stroke="isMemoryEnhanced ? '#2A261F' : '#A855F7'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.8333 1.75H9.33333C8.71449 1.75 8.121 1.99583 7.68342 2.43342C7.24583 2.871 7 3.46449 7 4.08333V12.25C7 11.7859 7.18437 11.3408 7.51256 11.0126C7.84075 10.6844 8.28587 10.5 8.75 10.5H12.8333V1.75Z" :stroke="isMemoryEnhanced ? '#2A261F' : '#A855F7'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- 3. 第二行功能双列卡片 (Mod 管理 + 画师串 · 二次元) -->
      <div class="grid grid-cols-2 gap-2">
        <!-- (3) Mod 管理 -->
        <button
          type="button"
          @click="handleAction('modManage')"
          class="p-2.5 rounded-[6px] border border-[#44403C] bg-[#2A261F] hover:border-[#F9C86D]/50 flex items-center justify-between transition-all cursor-pointer group"
        >
          <span class="text-xs font-medium text-[#F9C86D]">Mod 管理</span>
          <!-- 屏幕窗口 SVG -->
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M11.6667 1.75H2.33333C1.689 1.75 1.16667 2.27233 1.16667 2.91667V8.75C1.16667 9.39433 1.689 9.91667 2.33333 9.91667H11.6667C12.311 9.91667 12.8333 9.39433 12.8333 8.75V2.91667C12.8333 2.27233 12.311 1.75 11.6667 1.75Z" stroke="#F9C86D" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.66667 12.25H9.33333" stroke="#F9C86D" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 9.91669V12.25" stroke="#F9C86D" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- (4) 画师串 · 二次元 -->
        <button
          type="button"
          @click="handleAction('artistPrompt')"
          class="p-2.5 rounded-[6px] border border-[#44403C] bg-[#292524] hover:border-[#F9C86D]/50 flex items-center gap-1.5 transition-all cursor-pointer group"
        >
          <!-- 星球星轨 SVG -->
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M10.9047 8.42598C10.8637 8.42598 10.8227 8.42188 10.7803 8.41367C10.4494 8.34531 10.2375 8.02129 10.3059 7.6918C10.3523 7.46758 10.3756 7.23652 10.3756 7.00547C10.3756 5.15156 8.86758 3.64355 7.01367 3.64355C5.63008 3.64355 4.3668 4.51172 3.87188 5.80508C3.75156 6.1209 3.39746 6.27812 3.08301 6.15781C2.76719 6.0375 2.60996 5.6834 2.73027 5.36895C3.4043 3.60391 5.12559 2.41992 7.01367 2.41992C9.5416 2.41992 11.5979 4.47617 11.5979 7.0041C11.5979 7.31855 11.5664 7.63301 11.5021 7.93789C11.442 8.22773 11.1877 8.42598 10.9047 8.42598Z" fill="#F9C86D"/>
            <path d="M9.01113 7.46075C8.70078 7.46075 8.43418 7.22423 8.4041 6.90841C8.34668 6.30685 7.91738 5.79278 7.33633 5.62872C7.0123 5.53712 6.82227 5.19942 6.91523 4.87403C7.00684 4.55001 7.34453 4.36134 7.66992 4.45294C8.73086 4.75372 9.51563 5.69298 9.6209 6.79083C9.65371 7.12716 9.40762 7.4252 9.07129 7.45802C9.04941 7.45938 9.03027 7.46075 9.01113 7.46075ZM7.01367 11.5883C4.74414 11.5883 2.79316 9.89571 2.47461 7.65216C2.42676 7.31856 2.65918 7.00821 2.99414 6.96173C3.3291 6.91524 3.63809 7.14767 3.68457 7.48126C3.91836 9.12599 5.34844 10.366 7.01367 10.366C7.98984 10.366 8.91543 9.9422 9.55527 9.20528C9.77676 8.94962 10.1623 8.92364 10.418 9.14376C10.6736 9.36524 10.701 9.75079 10.4795 10.0065C9.60723 11.0113 8.34395 11.5883 7.01367 11.5883Z" fill="#F9C86D"/>
            <path d="M10.0748 10.1035C8.9209 10.1035 7.57559 9.88202 6.28223 9.50331C3.27168 8.62284 0.475781 6.87284 0.955664 5.23358C1.10605 4.71815 1.62559 4.07421 3.24707 3.92928C3.42754 3.91288 3.61758 3.90331 3.81309 3.90057C4.14805 3.891 4.42832 4.16581 4.43242 4.5035C4.43652 4.8412 4.16719 5.11874 3.82949 5.12284C3.66406 5.12557 3.50684 5.13241 3.35645 5.14608C2.53203 5.21991 2.16699 5.44823 2.12871 5.57538C2.0166 5.95956 3.45352 7.40057 6.62676 8.32889C9.8 9.25721 11.7865 8.81698 11.8986 8.43143C11.9383 8.29471 11.7113 7.80253 10.7502 7.15995C10.4699 6.97264 10.3947 6.59256 10.582 6.31229C10.7693 6.03202 11.1494 5.95682 11.4297 6.14413C13.0963 7.25975 13.2426 8.19081 13.0717 8.77596C12.7982 9.71112 11.6061 10.1035 10.0748 10.1035Z" fill="#F9C86D"/>
          </svg>
          <span class="text-xs font-medium text-[#F9C86D] truncate">画师串 · 二次元</span>
        </button>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.panel-slide-enter-active,
.panel-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: bottom right;
}
.panel-slide-enter-from,
.panel-slide-leave-to {
  opacity: 0;
  transform: translateY(8px) scale(0.98);
}
</style>
