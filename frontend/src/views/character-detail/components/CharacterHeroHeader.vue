<script setup lang="ts">
/**
 * 角色卡详情 - 顶部 Hero 与 10 项核心数据面板 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { CharacterDetailData } from "@/views/character-detail/constants/mockCharacterDetail";
import { BookOpen, FileText } from "lucide-vue-next";

defineProps<{
  character: CharacterDetailData;
}>();
</script>

<template>
  <div class="relative w-full overflow-hidden flex flex-col items-center pt-3 pb-2 select-none">
    
    <!-- 1. 顶部高斯模糊暗黑渐变大背景 -->
    <div
      class="absolute inset-0 z-0 bg-cover bg-center filter blur-xl scale-110 opacity-30 pointer-events-none"
      :style="{ backgroundImage: `url(${character.bannerUrl || character.avatarUrl})` }"
    />
    <div class="absolute inset-0 z-0 bg-gradient-to-b from-transparent via-[#1A1511]/80 to-[#1A1511] pointer-events-none" />

    <!-- 2. 居中立体卡片封面 (80px x 106.7px, border: 2px solid #292524, shadow) -->
    <div class="relative z-10 w-[80px] h-[106.7px] rounded-lg border-2 border-[#292524] shadow-[0_25px_50px_-12px_rgba(0,0,0,0.5)] overflow-hidden bg-black/40">
      <img
        :src="character.avatarUrl"
        :alt="character.name"
        class="w-full h-full object-cover"
      />
    </div>

    <!-- 3. 角色标题与状态标签 -->
    <div class="relative z-10 w-full flex flex-col items-center mt-3 px-3">
      <h1 class="text-[20px] font-semibold text-[#F5F5F4] tracking-[-0.4px] leading-6 text-center">
        {{ character.name }}
      </h1>

      <div class="flex items-center gap-2 mt-2">
        <!-- 🟢 已发布 -->
        <div class="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#22C55E]/10 border border-[#22C55E]/30">
          <span class="w-1.5 h-1.5 rounded-full bg-[#22C55E]" />
          <span class="text-xs text-[#22C55E]">已发布</span>
        </div>

        <!-- 原创作品 -->
        <span v-if="character.isOriginal" class="text-xs text-[#F9C86D]">
          原创作品
        </span>
      </div>
    </div>

    <!-- 4. 10 项数据指标网格 (2 行 x 5 列, Inter 14px 粗体金色 + 10px 浅灰说明) -->
    <div class="relative z-10 w-full flex flex-col gap-2 mt-4 px-2">
      <!-- 第一行 (5 列: 热度、点赞、收藏、导入、使用) -->
      <div class="grid grid-cols-5 gap-1 text-center">
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.hotness }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">热度</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.likes }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">点赞</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.favorites }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">收藏</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.imports }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">导入</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.uses }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">使用</span>
        </div>
      </div>

      <!-- 第二行 (5 列: 独立玩家、总对话、深度游玩、平均消耗、累计tokens) -->
      <div class="grid grid-cols-5 gap-1 text-center pt-1">
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.uniquePlayers }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">独立玩家</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.totalChats }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">总对话</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.deepPlays }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">深度游玩</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.avgCost }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">平均消耗</span>
        </div>
        <div class="flex flex-col items-center">
          <span class="text-[14px] font-bold text-[#F9C86D] font-mono leading-5">{{ character.metrics.totalTokens }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">累计 tokens</span>
        </div>
      </div>
    </div>

    <!-- 5. 核心资产卡片 (设定字数 15,003 + 世界书 5) -->
    <div class="relative z-10 flex items-center justify-center gap-6 mt-4 px-6 py-2 rounded-lg border border-[#F9C86D]/10 bg-[#F9C86D]/[0.05] backdrop-blur-sm">
      <!-- 设定字数 -->
      <div class="flex items-center gap-2">
        <FileText class="w-4 h-4 text-[#F9C86D]" />
        <div class="flex flex-col items-center">
          <span class="text-[16px] font-semibold text-[#F9C86D] font-mono leading-6">{{ character.settingsWordCount }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">设定字数</span>
        </div>
      </div>

      <!-- 分隔线 -->
      <div class="w-[1px] h-8 bg-[#F9C86D]/20" />

      <!-- 世界书 -->
      <div class="flex items-center gap-2">
        <BookOpen class="w-4 h-4 text-[#F9C86D]" />
        <div class="flex flex-col items-center">
          <span class="text-[16px] font-semibold text-[#F9C86D] font-mono leading-6">{{ character.worldBookCount }}</span>
          <span class="text-[10px] text-[#A8A29E] opacity-70">世界书</span>
        </div>
      </div>
    </div>

  </div>
</template>
