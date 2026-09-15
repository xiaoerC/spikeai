<script setup lang="ts">
/**
 * AI 聊天界面 - 顶部导航栏 (1:1 Figma 原型高保真)
 *
 * 包含左侧返回/侧边栏，右侧 BGM、Naro助手、叙梦面板、主控面板以及右上角设置菜单。
 *
 * @packageDocumentation
 */

import ChatSettingsMenu from "@/views/chat/components/ChatSettingsMenu.vue";
import { ref } from "vue";

const emit = defineEmits<{
  (e: "back"): void;
  (e: "forward"): void;
  (e: "openSidebar"): void;
  (e: "openMusic"): void;
  (e: "openAssistant"): void;
  (e: "openNarrativePanel"): void;
  (e: "openWorldbook"): void;
  (e: "openCanvas"): void;
  (e: "openApps"): void;
  (e: "openControlPanel"): void;
  (e: "settingsAction", action: string): void;
}>();

// 设置菜单展开状态
const isSettingsMenuOpen = ref(false);

function toggleSettingsMenu(): void {
  isSettingsMenuOpen.value = !isSettingsMenuOpen.value;
}

function handleSettingsAction(action: string): void {
  emit("settingsAction", action);
}
</script>

<template>
  <header class="w-full px-3 py-2 flex items-center justify-between z-30 select-none bg-transparent relative">
    
    <!-- 1. 左侧: [←] 返回 与 [→] 展开侧边栏 两个磨砂玻璃按钮 -->
    <div class="flex items-center gap-2">
      <!-- (1) [←] 返回按钮 -->
      <button
        type="button"
        @click="emit('back')"
        class="w-[33.3px] h-[29.3px] rounded-lg border border-white/18 bg-black/25 flex items-center justify-center relative overflow-hidden group hover:border-[#F9C86D]/50 transition-all cursor-pointer shadow-sm"
        title="返回"
      >
        <!-- 微弱黑金流光底层 -->
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-[#F9C86D]/10 to-transparent opacity-30 pointer-events-none" />
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="relative z-10">
          <path d="M12.6667 8H3.33334" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8.00001 12.6666L3.33334 7.99998L8.00001 3.33331" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- (2) [→] 展开侧边栏按钮 -->
      <button
        type="button"
        @click="emit('openSidebar')"
        class="w-[33.3px] h-[29.3px] rounded-lg border border-white/18 bg-black/25 flex items-center justify-center relative overflow-hidden group hover:border-[#F9C86D]/50 transition-all cursor-pointer shadow-sm"
        title="展开侧边栏"
      >
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-[#F9C86D]/10 to-transparent opacity-30 pointer-events-none" />

        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="relative z-10">
          <path d="M3.33331 8H12.6666" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M8 3.33331L12.6667 7.99998L8 12.6666" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>

    <!-- 2. 中间弹性留白，凸显背景人物插画 -->
    <div class="flex-1" />

    <!-- 3. 右侧 5 个磨砂玻璃霓虹色彩功能按钮 -->
    <div class="flex items-center gap-1.5">
      
      <!-- (1) 🎵 音乐/BGM (粉红高光) -->
      <button
        type="button"
        @click="emit('openMusic')"
        class="w-[33.3px] h-[29.3px] rounded-lg border border-white/18 bg-black/25 flex items-center justify-center relative overflow-hidden hover:border-[#FF69B4]/60 transition-all cursor-pointer shadow-sm"
        title="背景音乐"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6 12C7.10457 12 8 11.1046 8 10V3L13 2V6" stroke="#FF69B4" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="5" cy="11" r="2" stroke="#FF69B4" stroke-width="1.33333"/>
        </svg>
      </button>

      <!-- (2) 🏷️ Naro助手 (金色高光) -->
      <button
        type="button"
        @click="emit('openAssistant')"
        class="w-[33.3px] h-[29.3px] rounded-lg border border-white/18 bg-black/25 flex items-center justify-center relative overflow-hidden hover:border-[#D1A35C]/60 transition-all cursor-pointer shadow-sm"
        title="Naro助手"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 1.33331C8.35362 1.33331 8.69276 1.47379 8.94281 1.72384C9.19286 1.97389 9.33333 2.31302 9.33333 2.66665C9.33333 3.15998 9.06667 3.59331 8.66667 3.81998V4.66665H9.33333C10.571 4.66665 11.758 5.15831 12.6332 6.03348C13.5083 6.90865 14 8.09564 14 9.33331H12.6667C12.6667 8.44926 12.3155 7.60141 11.6904 6.97629C11.0652 6.35117 10.2174 5.99998 9.33333 5.99998H8.66667V6.84665C9.06667 7.07331 9.33333 7.50665 9.33333 7.99998C9.33333 8.73331 8.73333 9.33331 8 9.33331C7.26667 9.33331 6.66667 8.73331 6.66667 7.99998C6.66667 7.50665 6.93333 7.07331 7.33333 6.84665V5.99998H6.66667C5.78261 5.99998 4.93477 6.35117 4.30964 6.97629C3.68452 7.60141 3.33333 8.44926 3.33333 9.33331H2C2 8.09564 2.49167 6.90865 3.36683 6.03348C4.242 5.15831 5.42899 4.66665 6.66667 4.66665H7.33333V3.81998C6.93333 3.59331 6.66667 3.15998 6.66667 2.66665C6.66667 2.31302 6.80714 1.97389 7.05719 1.72384C7.30724 1.47379 7.64638 1.33331 8 1.33331Z" stroke="#D1A35C" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- (3) 📺 叙梦面板 (天蓝高光) -->
      <button
        type="button"
        @click="emit('openNarrativePanel')"
        class="w-[33.3px] h-[29.3px] rounded-lg border border-white/18 bg-black/25 flex items-center justify-center relative overflow-hidden hover:border-[#3B82F6]/60 transition-all cursor-pointer shadow-sm"
        title="叙梦面板"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M4 1.33331V3.99998" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12 1.33331V3.99998" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M4 12V14.6667" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12 12V14.6667" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M13.3333 4H2.66665C1.93027 4 1.33331 4.59695 1.33331 5.33333V10.6667C1.33331 11.403 1.93027 12 2.66665 12H13.3333C14.0697 12 14.6666 11.403 14.6666 10.6667V5.33333C14.6666 4.59695 14.0697 4 13.3333 4Z" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M5.33333 9.33335C6.06971 9.33335 6.66667 8.7364 6.66667 8.00002C6.66667 7.26364 6.06971 6.66669 5.33333 6.66669C4.59695 6.66669 4 7.26364 4 8.00002C4 8.7364 4.59695 9.33335 5.33333 9.33335Z" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M9.33331 6.66669L10.6666 8.00002L9.33331 9.33335" stroke="#3B82F6" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- (4) ⊞ 主控面板 (浅绿高光) -->
      <button
        type="button"
        @click="emit('openControlPanel')"
        class="w-[33.3px] h-[29.3px] rounded-lg border border-white/18 bg-black/25 flex items-center justify-center relative overflow-hidden hover:border-[#22C55E]/60 transition-all cursor-pointer shadow-sm"
        title="主控面板"
      >
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M6.66667 2H2V6.66667H6.66667V2Z" stroke="#22C55E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M14 2H9.33331V6.66667H14V2Z" stroke="#22C55E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M14 9.33331H9.33331V14H14V9.33331Z" stroke="#22C55E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M6.66667 9.33331H2V14H6.66667V9.33331Z" stroke="#22C55E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- (4.5) 📖 世界书设定集 (琥珀金高光) -->
      <button
        type="button"
        @click="emit('openWorldbook')"
        class="w-[33.3px] h-[29.3px] rounded-lg border border-white/18 bg-black/25 flex items-center justify-center relative overflow-hidden hover:border-[#F59E0B]/60 transition-all cursor-pointer shadow-sm"
        title="世界书设定集 (World Book)"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
          <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
        </svg>
      </button>

      <!-- (5) ⚙️ 设置 (白色/暗黑深色基座) -->
      <div class="relative">
        <button
          type="button"
          @click="toggleSettingsMenu"
          :class="[
            'w-8 h-8 rounded-lg border shadow-inner flex items-center justify-center transition-all cursor-pointer',
            isSettingsMenuOpen
              ? 'border-[#F9C86D] bg-[#292524] text-[#F9C86D] shadow-[0_0_8px_rgba(249,200,109,0.3)]'
              : 'border-[#44403C] bg-[#292524] text-[#F5F5F4] hover:text-[#F9C86D] hover:border-[#F9C86D]/50'
          ]"
          title="设置"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 10C9.10457 10 10 9.10457 10 8C10 6.89543 9.10457 6 8 6C6.89543 6 6 6.89543 6 8C6 9.10457 6.89543 10 8 10Z" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.9334 10C12.8446 10.2011 12.8181 10.4241 12.8574 10.6404C12.8966 10.8567 12.9997 11.0562 13.1534 11.2134L13.1934 11.2534C13.3173 11.3772 13.4157 11.5242 13.4828 11.6861C13.5499 11.848 13.5844 12.0215 13.5844 12.1967C13.5844 12.3719 13.5499 12.5454 13.4828 12.7073C13.4157 12.8691 13.3173 13.0162 13.1934 13.14C13.0695 13.264 12.9225 13.3623 12.7606 13.4294C12.5987 13.4965 12.4252 13.5311 12.25 13.5311C12.0748 13.5311 11.9013 13.4965 11.7394 13.4294C11.5776 13.3623 11.4305 13.264 11.3067 13.14L11.2667 13.1C11.1096 12.9463 10.91 12.8432 10.6937 12.804C10.4775 12.7648 10.2544 12.7913 10.0534 12.88C9.85617 12.9645 9.68801 13.1049 9.56956 13.2837C9.45111 13.4626 9.38754 13.6722 9.38669 13.8867V14C9.38669 14.3536 9.24621 14.6928 8.99616 14.9428C8.74611 15.1929 8.40698 15.3334 8.05335 15.3334C7.69973 15.3334 7.36059 15.1929 7.11055 14.9428C6.8605 14.6928 6.72002 14.3536 6.72002 14V13.94C6.71486 13.7194 6.64343 13.5054 6.51503 13.3258C6.38662 13.1463 6.20718 13.0095 6.00002 12.9334C5.79894 12.8446 5.57589 12.8181 5.35963 12.8574C5.14336 12.8966 4.94381 12.9997 4.78669 13.1534L4.74669 13.1934C4.62286 13.3173 4.4758 13.4157 4.31394 13.4828C4.15208 13.5499 3.97857 13.5844 3.80335 13.5844C3.62813 13.5844 3.45463 13.5499 3.29277 13.4828C3.1309 13.4157 2.98385 13.3173 2.86002 13.1934C2.73605 13.0695 2.63771 12.9225 2.57061 12.7606C2.50351 12.5987 2.46897 12.4252 2.46897 12.25C2.46897 12.0748 2.50351 11.9013 2.57061 11.7394C2.63771 11.5776 2.73605 11.4305 2.86002 11.3067L2.90002 11.2667C3.05371 11.1096 3.15681 10.91 3.19602 10.6937C3.23524 10.4775 3.20876 10.2544 3.12002 10.0534C3.03551 9.85617 2.89519 9.68801 2.71633 9.56956C2.53747 9.45111 2.32788 9.38754 2.11335 9.38669H2.00002C1.6464 9.38669 1.30726 9.24621 1.05721 8.99616C0.807163 8.74611 0.666687 8.40698 0.666687 8.05335C0.666687 7.69973 0.807163 7.36059 1.05721 7.11055C1.30726 6.8605 1.6464 6.72002 2.00002 6.72002H2.06002C2.28068 6.71486 2.49469 6.64343 2.67422 6.51503C2.85375 6.38662 2.9905 6.20718 3.06669 6.00002C3.15543 5.79894 3.1819 5.57589 3.14269 5.35963C3.10348 5.14336 3.00038 4.94381 2.84669 4.78669L2.80669 4.74669C2.68272 4.62286 2.58437 4.4758 2.51727 4.31394C2.45018 4.15208 2.41564 3.97857 2.41564 3.80335C2.41564 3.62813 2.45018 3.45463 2.51727 3.29277C2.58437 3.1309 2.68272 2.98385 2.80669 2.86002C2.93052 2.73605 3.07757 2.63771 3.23943 2.57061C3.4013 2.50351 3.5748 2.46897 3.75002 2.46897C3.92524 2.46897 4.09874 2.50351 4.26061 2.57061C4.42247 2.63771 4.56952 2.73605 4.69335 2.86002L4.73335 2.90002C4.89047 3.05371 5.09003 3.15681 5.30629 3.19602C5.52256 3.23524 5.74561 3.20876 5.94669 3.12002H6.00002C6.1972 3.03551 6.36537 2.89519 6.48382 2.71633C6.60227 2.53747 6.66583 2.32788 6.66669 2.11335V2.00002C6.66669 1.6464 6.80716 1.30726 7.05721 1.05721C7.30726 0.807163 7.6464 0.666687 8.00002 0.666687C8.35364 0.666687 8.69278 0.807163 8.94283 1.05721C9.19288 1.30726 9.33335 1.6464 9.33335 2.00002V2.06002C9.33421 2.27454 9.39778 2.48414 9.51623 2.663C9.63468 2.84186 9.80284 2.98218 10 3.06669C10.2011 3.15543 10.4241 3.1819 10.6404 3.14269C10.8567 3.10348 11.0562 3.00038 11.2134 2.84669L11.2534 2.80669C11.3772 2.68272 11.5242 2.58437 11.6861 2.51727C11.848 2.45018 12.0215 2.41564 12.1967 2.41564C12.3719 2.41564 12.5454 2.45018 12.7073 2.51727C12.8691 2.58437 13.0162 2.68272 13.14 2.80669C13.264 2.93052 13.3623 3.07757 13.4294 3.23943C13.4965 3.4013 13.5311 3.5748 13.5311 3.75002C13.5311 3.92524 13.4965 4.09874 13.4294 4.26061C13.3623 4.42247 13.264 4.56952 13.14 4.69335L13.1 4.73335C12.9463 4.89047 12.8432 5.09003 12.804 5.30629C12.7648 5.52256 12.7913 5.74561 12.88 5.94669V6.00002C12.9645 6.1972 13.1049 6.36537 13.2837 6.48382C13.4626 6.60227 13.6722 6.66583 13.8867 6.66669H14C14.3536 6.66669 14.6928 6.80716 14.9428 7.05721C15.1929 7.30726 15.3334 7.6464 15.3334 8.00002C15.3334 8.35364 15.1929 8.69278 14.9428 8.94283C14.6928 9.19288 14.3536 9.33335 14 9.33335H13.94C13.7255 9.33421 13.5159 9.39778 13.337 9.51623C13.1582 9.63468 13.0179 9.80284 12.9334 10Z" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 1:1 设置下拉菜单 -->
        <ChatSettingsMenu
          v-model:open="isSettingsMenuOpen"
          @select="handleSettingsAction"
        />
      </div>

    </div>

  </header>
</template>
