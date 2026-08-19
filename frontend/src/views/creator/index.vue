<script setup lang="ts">
/**
 * 叙梦 Naro - 创作者专区 / 创作者广场 (Smart Container 主入口)
 *
 * 1:1 像素级还原创作者专区，展示知名创作者资料、作品矩阵与关注互动。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import CreatorShowcaseCard from "@/views/creator/components/CreatorShowcaseCard.vue";
import { useCreatorList } from "@/views/creator/composables/useCreatorList";
import type { CreatorCharacterWork } from "@/views/creator/types";
import LoginModal from "@/views/login/components/LoginModal.vue";
import { ArrowLeft, Search, Sparkles } from "lucide-vue-next";
import { useRouter } from "vue-router";

const router = useRouter();
const appStore = useAppStore();
const { creators, toggleFollow } = useCreatorList();

function handleSelectWork(_work: CreatorCharacterWork) {
  // 跳转到角色详情或开始对话
}

function handleBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部 Header 导航栏 -->
    <header class="sticky top-0 z-40 w-full max-w-[440px] mx-auto px-3 py-3 flex items-center justify-between bg-[rgba(26,23,20,0.92)] backdrop-blur-md border-b border-white/5 shadow-md">
      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="handleBack"
          class="p-1.5 rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/10 active:scale-95 transition-all cursor-pointer"
        >
          <ArrowLeft class="w-5 h-5" />
        </button>
        <div class="flex items-center gap-1.5">
          <Sparkles class="w-4 h-4 text-[#F9C86D]" />
          <h1 class="text-base font-bold text-[#F5F5F4] tracking-wide">
            创作者专区
          </h1>
        </div>
      </div>

      <!-- 搜索或排序筛选图标 -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="p-1.5 rounded-lg text-[#A8A29E] hover:text-[#F9C86D] hover:bg-white/10 transition-colors cursor-pointer"
        >
          <Search class="w-4 h-4" />
        </button>
      </div>
    </header>

    <!-- 2. 创作者瀑布流内容区 -->
    <main class="w-full max-w-[440px] mx-auto px-3 pt-3 pb-24 flex flex-col gap-4">
      <CreatorShowcaseCard
        v-for="creator in creators"
        :key="creator.id"
        :creator="creator"
        @toggle-follow="toggleFollow"
        @select-work="handleSelectWork"
      />
    </main>

    <!-- 3. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 4. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
