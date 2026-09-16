<script setup lang="ts">
/**
 * 帮助中心顶部 Header 导航与官方文档标头 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { HelpTabType } from "@/views/help/types";
import { ArrowLeft } from "lucide-vue-next";
import { useRouter } from "vue-router";

defineProps<{
  currentTab: HelpTabType;
}>();

const emit = defineEmits<(e: "change-tab", tab: HelpTabType) => void>();

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
  <header class="sticky top-0 z-40 w-full max-w-[440px] md:max-w-none mx-auto flex flex-col bg-[rgba(26,21,16,0.95)] backdrop-blur-md border-b border-white/5 shadow-md">
    <!-- 顶部返回栏 -->
    <div class="px-4 pt-3 pb-1 flex items-center justify-between w-full max-w-[1000px] mx-auto">
      <button
        type="button"
        @click="handleBack"
        class="p-1 rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/10 active:scale-95 transition-all cursor-pointer"
      >
        <ArrowLeft class="w-5 h-5" />
      </button>

      <!-- OFFICIAL DOC 徽章 -->
      <span class="px-2 py-0.5 rounded bg-[#F9C86D]/15 border border-[#F9C86D]/30 text-[10px] font-bold text-[#F9C86D] tracking-wider">
        OFFICIAL DOC
      </span>

      <div class="w-5" />
    </div>

    <!-- 标题与副标题 -->
    <div class="px-4 pt-2 pb-3 flex flex-col w-full max-w-[1000px] mx-auto">
      <h1 class="text-lg font-bold text-[#F5F5F4] tracking-wide">
        Naro · 叙梦
      </h1>
      <p class="text-xs text-[#F9C86D] font-medium mt-0.5">
        FAQ 与官方指令集
      </p>
    </div>

    <!-- 3 大分类 Tabs (新手指南 / FAQ 常见问题 / 官方指令集) -->
    <div class="px-4 pb-3 flex items-center gap-2 overflow-x-auto no-scrollbar w-full max-w-[1000px] mx-auto">
      <button
        type="button"
        @click="emit('change-tab', 'guide')"
        :class="[
          'px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer select-none',
          currentTab === 'guide'
            ? 'bg-[#F9C86D] text-[#0C0A09] shadow-[0_0_12px_rgba(249,200,109,0.30)]'
            : 'bg-[#292524] text-[#A8A29E] hover:text-white hover:bg-[#383330] border border-white/5'
        ]"
      >
        新手指南
      </button>

      <button
        type="button"
        @click="emit('change-tab', 'faq')"
        :class="[
          'px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer select-none',
          currentTab === 'faq'
            ? 'bg-[#F9C86D] text-[#0C0A09] shadow-[0_0_12px_rgba(249,200,109,0.30)]'
            : 'bg-[#292524] text-[#A8A29E] hover:text-white hover:bg-[#383330] border border-white/5'
        ]"
      >
        FAQ 常见问题
      </button>

      <button
        type="button"
        @click="emit('change-tab', 'commands')"
        :class="[
          'px-3.5 py-1.5 rounded-full text-xs font-semibold transition-all cursor-pointer select-none',
          currentTab === 'commands'
            ? 'bg-[#F9C86D] text-[#0C0A09] shadow-[0_0_12px_rgba(249,200,109,0.30)]'
            : 'bg-[#292524] text-[#A8A29E] hover:text-white hover:bg-[#383330] border border-white/5'
        ]"
      >
        官方指令集
      </button>
    </div>

    <!-- 导言文本提示 -->
    <div v-if="currentTab === 'guide'" class="px-4 pb-3 text-xs text-[#A8A29E] leading-relaxed border-t border-white/5 pt-2.5 w-full max-w-[1000px] mx-auto">
      从第一次打开叙梦，到建立属于你的长期剧情记忆。按下面的步骤完成设置就能更顺畅地开始一段对话。
    </div>
  </header>
</template>
