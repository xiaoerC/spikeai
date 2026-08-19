<script setup lang="ts">
/**
 * 全局底部 5-Tab Bar 导航栏组件 (公共导航基础设施)
 *
 * @packageDocumentation
 */

import MoreDrawer from "@/components/navigation/MoreDrawer.vue";
import { useAppStore } from "@/stores/app";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const appStore = useAppStore();
const router = useRouter();
const route = useRoute();

const currentActiveTab = computed(() => {
  if (appStore.isMoreDrawerOpen) return "more";
  if (route.path === "/history") return "history";
  if (route.path === "/create") return "create";
  if (route.path === "/") return "community";
  return appStore.activeTab;
});

function handleNavigate(tab: "community" | "history" | "create" | "more") {
  if (tab === "more") {
    appStore.toggleMoreDrawer();
    return;
  }

  appStore.closeMoreDrawer();
  appStore.setActiveTab(tab);
  if (tab === "community" && route.path !== "/") {
    router.push("/");
  } else if (tab === "history" && route.path !== "/history") {
    router.push("/history");
  } else if (tab === "create" && route.path !== "/create") {
    router.push("/create");
  }
}
</script>

<template>
  <!-- 底部“更多”抽屉弹窗 -->
  <MoreDrawer />

  <!-- 底部固定容器与 iOS/Android 安全区: height: 68px; border-top: 0.667px solid rgba(83,71,65,0.50); background: rgba(26,23,20,0.95); -->
  <nav class="fixed bottom-0 left-0 right-0 z-50 pb-safe bg-[rgba(26,23,20,0.95)] border-t border-[rgba(83,71,65,0.50)] backdrop-blur-xl">
    <!-- 桌面端居中与 440px 移动视口宽度对齐 -->
    <div class="max-w-[440px] mx-auto h-[68px] px-2 flex items-center justify-between relative bg-transparent">
      
      <!-- 1. 角色社区 -->
      <button
        type="button"
        @click="handleNavigate('community')"
        :class="[
          'flex flex-col items-center justify-center w-[84.8px] p-1 rounded-lg transition-all duration-150 cursor-pointer select-none',
          currentActiveTab === 'community'
            ? 'text-[#F9C86D] bg-[rgba(42,35,28,0.30)]'
            : 'text-[#78716C] bg-transparent hover:text-[#A8A29E]'
        ]"
      >
        <div class="flex items-center justify-center w-6 h-[26px] pb-[2px]">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M4 1.33334L2 4.00001V13.3333C2 13.687 2.14048 14.0261 2.39052 14.2762C2.64057 14.5262 2.97971 14.6667 3.33333 14.6667H12.6667C13.0203 14.6667 13.3594 14.5262 13.6095 14.2762C13.8595 14.0261 14 13.687 14 13.3333V4.00001L12 1.33334H4Z" :stroke="currentActiveTab === 'community' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 4H14" :stroke="currentActiveTab === 'community' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.6667 6.66666C10.6667 7.3739 10.3857 8.05218 9.88561 8.55227C9.38552 9.05237 8.70724 9.33332 7.99999 9.33332C7.29275 9.33332 6.61447 9.05237 6.11438 8.55227C5.61428 8.05218 5.33333 7.3739 5.33333 6.66666" :stroke="currentActiveTab === 'community' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="text-[9px] leading-[11.25px] tracking-[-0.176px]">角色社区</span>
      </button>

      <!-- 2. 历史记录 -->
      <button
        type="button"
        @click="handleNavigate('history')"
        :class="[
          'flex flex-col items-center justify-center w-[84.8px] p-1 rounded-lg transition-all duration-150 cursor-pointer select-none',
          currentActiveTab === 'history'
            ? 'text-[#F9C86D] bg-[rgba(42,35,28,0.30)]'
            : 'text-[#78716C] bg-transparent hover:text-[#A8A29E]'
        ]"
      >
        <div class="flex items-center justify-center w-6 h-[26px] pb-[2px]">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 14.6667C11.6819 14.6667 14.6667 11.6819 14.6667 8.00001C14.6667 4.31811 11.6819 1.33334 8 1.33334C4.3181 1.33334 1.33334 4.31811 1.33334 8.00001C1.33334 11.6819 4.3181 14.6667 8 14.6667Z" :stroke="currentActiveTab === 'history' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 4V8L10.6667 9.33333" :stroke="currentActiveTab === 'history' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="text-[9px] leading-[11.25px] tracking-[-0.176px]">历史记录</span>
      </button>

      <!-- 3. 中间圆形暗黑高奢登录徽章 (完全深黑底座，严禁白色) -->
      <button
        type="button"
        @click="appStore.openLoginModal()"
        class="flex flex-col items-center justify-center w-[76.8px] bg-transparent cursor-pointer select-none"
      >
        <div class="flex items-center justify-center w-9 h-9 rounded-full border-2 border-[rgba(83,71,65,0.50)] bg-gradient-to-br from-[rgba(83,71,65,0.40)] to-[rgba(30,25,20,0.90)] mb-[2px] shadow-md overflow-hidden">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 4c1.93 0 3.5 1.57 3.5 3.5S13.93 13 12 13s-3.5-1.57-3.5-3.5S10.07 6 12 6zm0 14c-2.03 0-4.43-.82-6.14-2.88C7.55 15.8 9.68 15 12 15s4.45.8 6.14 2.12C16.43 19.18 14.03 20 12 20z" fill="#F9C86D"/>
          </svg>
        </div>
        <span class="text-[8px] leading-[10px] text-[#78716C] tracking-[-0.176px]">登录</span>
      </button>

      <!-- 4. 创建角色 -->
      <button
        type="button"
        @click="handleNavigate('create')"
        :class="[
          'flex flex-col items-center justify-center w-[84.8px] p-1 rounded-lg transition-all duration-150 cursor-pointer select-none',
          currentActiveTab === 'create'
            ? 'text-[#F9C86D] bg-[rgba(42,35,28,0.30)]'
            : 'text-[#78716C] bg-transparent hover:text-[#A8A29E]'
        ]"
      >
        <div class="flex items-center justify-center w-6 h-[26px] pb-[2px]">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.6667 14V12.6667C10.6667 11.9594 10.3857 11.2811 9.88562 10.781C9.38552 10.281 8.70724 10 8 10H3.33333C2.62609 10 1.94781 10.281 1.44771 10.781C0.947616 11.2811 0.666664 11.9594 0.666664 12.6667V14" :stroke="currentActiveTab === 'create' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.66667 7.33333C7.13943 7.33333 8.33333 6.13943 8.33333 4.66667C8.33333 3.19391 7.13943 2 5.66667 2C4.19391 2 3 3.19391 3 4.66667C3 6.13943 4.19391 7.33333 5.66667 7.33333Z" :stroke="currentActiveTab === 'create' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13.3333 5.33334V9.33334" :stroke="currentActiveTab === 'create' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M15.3333 7.33334H11.3333" :stroke="currentActiveTab === 'create' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="text-[9px] leading-[11.25px] tracking-[-0.176px]">创建角色</span>
      </button>

      <!-- 5. 更多 -->
      <button
        type="button"
        @click="handleNavigate('more')"
        :class="[
          'flex flex-col items-center justify-center w-[84.8px] p-1 rounded-lg transition-all duration-150 cursor-pointer select-none',
          currentActiveTab === 'more'
            ? 'text-[#F9C86D] bg-[rgba(42,35,28,0.30)]'
            : 'text-[#78716C] bg-transparent hover:text-[#A8A29E]'
        ]"
      >
        <div class="flex items-center justify-center w-6 h-[26px] pb-[2px]">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 4.33334C8.55228 4.33334 9 3.88563 9 3.33334C9 2.78106 8.55228 2.33334 8 2.33334C7.44772 2.33334 7 2.78106 7 3.33334C7 3.88563 7.44772 4.33334 8 4.33334Z" :stroke="currentActiveTab === 'more' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 9C8.55228 9 9 8.55228 9 8C9 7.44772 8.55228 7 8 7C7.44772 7 7 7.44772 7 8C7 8.55228 7.44772 9 8 9Z" :stroke="currentActiveTab === 'more' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 13.6667C8.55228 13.6667 9 13.2189 9 12.6667C9 12.1144 8.55228 11.6667 8 11.6667C7.44772 11.6667 7 12.1144 7 12.6667C7 13.2189 7.44772 13.6667 8 13.6667Z" :stroke="currentActiveTab === 'more' ? '#F9C86D' : '#78716C'" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="text-[9px] leading-[11.25px] tracking-[-0.176px]">更多</span>
      </button>

    </div>
  </nav>
</template>
