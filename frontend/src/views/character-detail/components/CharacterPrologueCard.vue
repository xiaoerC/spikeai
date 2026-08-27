<script setup lang="ts">
/**
 * 角色卡详情 - 序幕剧情卡片 (支持创作者自定义富文本 HTML 与黑金拟物优雅降级)
 *
 * @packageDocumentation
 */

import { ChevronDown, ChevronUp, Plus } from "lucide-vue-next";
import { ref } from "vue";

defineProps<{
  prologue: {
    title: string;
    description: string;
    html?: string;
    worldInfo: string;
    charactersInfo: string;
  };
}>();

const isWorldOpen = ref(false);
const isCharactersOpen = ref(false);
</script>

<template>
  <div class="w-full flex flex-col gap-2 px-3 pt-4 select-none">
    <!-- 1. 标题: • 序幕 -->
    <div class="flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-[#F9C86D]" />
      <h2 class="text-[18px] font-semibold text-[#F9C86D] tracking-[-0.36px] leading-6 font-sans">
        序幕
      </h2>
    </div>

    <!-- 2. 黑金曜石质感拟物卡片主体 -->
    <div class="w-full rounded-2xl bg-gradient-to-b from-[#241F1A]/95 via-[#1A1713]/95 to-[#14120F]/98 text-[#E7E5E4] p-5 shadow-2xl flex flex-col justify-between min-h-[260px] border border-[rgba(249,200,109,0.25)] relative overflow-hidden">
      
      <!-- 柔和微光渐变 -->
      <div class="absolute inset-0 bg-gradient-to-b from-[#F9C86D]/5 via-transparent to-transparent pointer-events-none" />

      <!-- (1) 艺术大标题 -->
      <div class="w-full flex flex-col items-center pt-2 pb-3 z-10">
        <h3 class="text-2xl font-serif font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-[#FFE5A3] via-[#F9C86D] to-[#D4AF37] drop-shadow-sm text-center italic">
          {{ prologue.title || "序幕" }}
        </h3>
      </div>

      <!-- (2) 自定义 HTML 序幕内容 (优先渲染) -->
      <div
        v-if="prologue.html"
        class="prologue-content w-full text-xs text-[#D6D3D1] leading-relaxed z-10 my-2"
        v-html="prologue.html"
      />

      <!-- (3) 默认降级展示 (当未提供富文本 HTML 时展示简介与折叠卡片) -->
      <template v-else>
        <!-- 手写风副标题 / 诗意导语 -->
        <p class="text-[14px] text-[#C4B5A5] font-serif tracking-wide text-center leading-relaxed mb-4 z-10">
          {{ prologue.description || "藏在老街区深处的一间不太好找的店。" }}
        </p>

        <!-- 底部折叠卡片 (关于世界 / 主要角色) -->
        <div class="w-full flex flex-col gap-2.5 pb-2 z-10">
          <!-- 关于世界 -->
          <div class="w-full rounded-xl bg-black/40 backdrop-blur-md border border-[rgba(249,200,109,0.15)] shadow-sm overflow-hidden transition-all">
            <button
              type="button"
              @click="isWorldOpen = !isWorldOpen"
              class="w-full px-4 py-3 flex items-center justify-between text-left cursor-pointer hover:bg-white/5 transition-colors"
            >
              <span class="text-[13px] font-serif font-bold text-[#F9C86D]">
                关于世界
              </span>
              <div class="w-5 h-5 rounded-full bg-[#2A231C] flex items-center justify-center text-[#F9C86D]">
                <ChevronUp v-if="isWorldOpen" class="w-3.5 h-3.5" />
                <Plus v-else class="w-3.5 h-3.5" />
              </div>
            </button>

            <!-- 展开内容 -->
            <div v-if="isWorldOpen" class="px-4 pb-3 text-xs text-[#A8A29E] leading-relaxed animate-fade-in font-sans">
              {{ prologue.worldInfo }}
            </div>
          </div>

          <!-- 主要角色 -->
          <div class="w-full rounded-xl bg-black/40 backdrop-blur-md border border-[rgba(249,200,109,0.15)] shadow-sm overflow-hidden transition-all">
            <button
              type="button"
              @click="isCharactersOpen = !isCharactersOpen"
              class="w-full px-4 py-3 flex items-center justify-between text-left cursor-pointer hover:bg-white/5 transition-colors"
            >
              <span class="text-[13px] font-serif font-bold text-[#F9C86D]">
                主要角色
              </span>
              <div class="w-5 h-5 rounded-full bg-[#2A231C] flex items-center justify-center text-[#F9C86D]">
                <ChevronUp v-if="isCharactersOpen" class="w-3.5 h-3.5" />
                <Plus v-else class="w-3.5 h-3.5" />
              </div>
            </button>

            <!-- 展开内容 -->
            <div v-if="isCharactersOpen" class="px-4 pb-3 text-xs text-[#A8A29E] leading-relaxed animate-fade-in font-sans">
              {{ prologue.charactersInfo }}
            </div>
          </div>
        </div>
      </template>

    </div>
  </div>
</template>

<style scoped>
.prologue-content :deep(p) {
  margin-bottom: 0.75rem;
  line-height: 1.65;
}
.prologue-content :deep(p:last-child) {
  margin-bottom: 0;
}
.prologue-content :deep(blockquote),
.prologue-content :deep(.border-l-2) {
  border-left-width: 2px;
  border-left-color: #F9C86D;
  padding-left: 0.75rem;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
</style>
