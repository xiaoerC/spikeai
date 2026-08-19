<script setup lang="ts">
/**
 * 个人中心顶部 Header (渐变金标题 + 公告/聊天/动态/设置 4操作按钮)
 *
 * @packageDocumentation
 */

defineProps<{
  unreadCount?: number;
}>();

const emit = defineEmits<{
  (e: "openNotice"): void;
  (e: "openChat"): void;
  (e: "openActivity"): void;
  (e: "openSettings"): void;
}>();
</script>

<template>
  <header class="flex items-center justify-between w-full px-3 pt-4 pb-2">
    <!-- 1. 左侧标题区 -->
    <div class="flex flex-col">
      <h1 class="text-[20px] font-semibold tracking-[-0.4px] leading-6 bg-gradient-to-r from-[#F9C86D] via-[#FFD475] to-[#F9C86D] bg-clip-text text-transparent select-none drop-shadow-[0_0_20px_rgba(249,200,109,0.15)]">
        用户中心
      </h1>
      <p class="text-xs text-[#78716C] tracking-[-0.176px] mt-0.5 select-none">
        管理您的账户和设置
      </p>
    </div>

    <!-- 2. 右侧 4 个快捷图标按钮组 -->
    <div class="flex items-center gap-2">
      <!-- (1) 公告 -->
      <button
        type="button"
        @click="emit('openNotice')"
        title="公告"
        class="w-8 h-8 rounded-lg border border-[#44403C] bg-[#292524] shadow-inner flex items-center justify-center text-[#A8A29E] hover:text-[#F9C86D] hover:border-[#F9C86D]/50 transition-all cursor-pointer"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 8V12M12 16H12.01M22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 6.47715 6.47715 2 12 2C17.5228 2 22 6.47715 22 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- (2) 聊天室 -->
      <button
        type="button"
        @click="emit('openChat')"
        title="聊天室"
        class="w-8 h-8 rounded-lg border border-[#44403C] bg-[#292524] shadow-inner flex items-center justify-center text-[#A8A29E] hover:text-[#F9C86D] hover:border-[#F9C86D]/50 transition-all cursor-pointer"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- (3) 关注动态 (带未读角标) -->
      <button
        type="button"
        @click="emit('openActivity')"
        title="关注动态"
        class="relative w-8 h-8 rounded-lg border border-[#44403C] bg-[#292524] shadow-inner flex items-center justify-center text-[#A8A29E] hover:text-[#F9C86D] hover:border-[#F9C86D]/50 transition-all cursor-pointer"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M18 8A6 6 0 0 0 6 8C6 15 3 17 3 17H21S18 15 18 8ZM13.73 21A2 2 0 0 1 10.27 21" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <!-- 未读红点微章 -->
        <span
          v-if="(unreadCount ?? 0) > 0"
          class="absolute -top-1 -right-1 px-1 min-w-4 h-4 rounded-full bg-[#EF4444] text-[10px] font-bold text-white flex items-center justify-center shadow-md border border-[#1C1917]"
        >
          {{ unreadCount }}
        </span>
      </button>

      <!-- (4) 设置 -->
      <button
        type="button"
        @click="emit('openSettings')"
        title="设置"
        class="w-8 h-8 rounded-lg border border-[#44403C] bg-[#292524] shadow-inner flex items-center justify-center text-[#A8A29E] hover:text-[#F9C86D] hover:border-[#F9C86D]/50 transition-all cursor-pointer"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M12 15C13.6569 15 15 13.6569 15 12C15 10.3431 13.6569 9 12 9C10.3431 9 9 10.3431 9 12C9 13.6569 10.3431 15 12 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M19.4 15A1.65 1.65 0 0 0 20 16.3A2 2 0 0 1 18.3 19A1.65 1.65 0 0 0 17 19.4A1.65 1.65 0 0 0 16.3 20A2 2 0 0 1 13.7 20A1.65 1.65 0 0 0 13 19.4A1.65 1.65 0 0 0 11.7 19.4A1.65 1.65 0 0 0 11 20A2 2 0 0 1 8.3 19A1.65 1.65 0 0 0 7 19.4A1.65 1.65 0 0 0 6.3 18.7A2 2 0 0 1 6.3 15.3A1.65 1.65 0 0 0 7 14A1.65 1.65 0 0 0 6.3 12.7A2 2 0 0 1 8 10A1.65 1.65 0 0 0 9.3 10A1.65 1.65 0 0 0 10 8.7A2 2 0 0 1 12.7 8.7A1.65 1.65 0 0 0 13.4 10A1.65 1.65 0 0 0 14.7 10A2 2 0 0 1 17.4 12.7A1.65 1.65 0 0 0 18 14A1.65 1.65 0 0 0 19.4 15Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </div>
  </header>
</template>
