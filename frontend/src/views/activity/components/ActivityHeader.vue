<script setup lang="ts">
/**
 * 活动中心顶部 Header 导航与分类筛选栏 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { ActivityCategory } from "@/views/activity/types";
import { ArrowLeft, Sparkles } from "lucide-vue-next";
import { useRouter } from "vue-router";

defineProps<{
  currentCategory: ActivityCategory;
}>();

const emit = defineEmits<(e: "select-category", cat: ActivityCategory) => void>();

const router = useRouter();

function handleBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
}
</script>

<template>
  <header class="sticky top-0 z-40 w-full max-w-[440px] md:max-w-none mx-auto flex flex-col bg-[rgba(26,21,16,0.92)] backdrop-blur-md border-b border-white/5 shadow-md">
    <!-- 顶部标题栏 -->
    <div class="px-4 py-3 flex items-center justify-between w-full max-w-[1200px] mx-auto">
      <!-- 左侧返回按钮 -->
      <button
        type="button"
        @click="handleBack"
        class="p-1 rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/10 active:scale-95 transition-all cursor-pointer"
      >
        <ArrowLeft class="w-5 h-5" />
      </button>

      <!-- 中间大标题 -->
      <div class="flex items-center gap-1.5 pr-6">
        <Sparkles class="w-4 h-4 text-[#F9C86D]" />
        <h1 class="text-base font-bold text-[#F5F5F4] tracking-wide">
          活动中心
        </h1>
      </div>

      <!-- 占位保持居中 -->
      <div class="w-5" />
    </div>

    <!-- 分类筛选切换胶囊 (全部活动 / 🎪 角色活动) -->
    <div class="px-4 pb-3 flex items-center gap-2 overflow-x-auto no-scrollbar w-full max-w-[1200px] mx-auto">
      <button
        type="button"
        @click="emit('select-category', 'all')"
        :class="[
          'px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer select-none',
          currentCategory === 'all'
            ? 'bg-[#F9C86D] text-[#0C0A09] shadow-[0_0_12px_rgba(249,200,109,0.30)]'
            : 'bg-[#292524] text-[#A8A29E] hover:text-white hover:bg-[#383330] border border-white/5'
        ]"
      >
        全部活动
      </button>

      <button
        type="button"
        @click="emit('select-category', 'character')"
        :class="[
          'px-3.5 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1 transition-all cursor-pointer select-none',
          currentCategory === 'character'
            ? 'bg-[#F9C86D] text-[#0C0A09] shadow-[0_0_12px_rgba(249,200,109,0.30)]'
            : 'bg-[#292524] text-[#A8A29E] hover:text-white hover:bg-[#383330] border border-white/5'
        ]"
      >
        <span>🎪</span>
        <span>角色活动</span>
      </button>
    </div>
  </header>
</template>
