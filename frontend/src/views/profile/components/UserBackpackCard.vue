<script setup lang="ts">
/**
 * 个人中心 - 我的背包卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { Briefcase } from "lucide-vue-next";
import { ref } from "vue";

const activeCategory = ref("avatar-frame");
</script>

<template>
  <div class="w-full p-4 rounded-lg border border-[#C0A480]/15 bg-gradient-to-br from-[#F4E8C1]/[0.04] to-[#F4E8C1]/[0.02] flex flex-col gap-3">
    <!-- 1. 标题行 -->
    <div class="flex items-center justify-between w-full">
      <div class="flex items-center gap-2">
        <Briefcase class="w-4 h-4 text-[#F9C86D]" />
        <h3 class="text-[16px] font-semibold text-[#F9C86D] tracking-[-0.32px] leading-5">
          我的背包
        </h3>
      </div>
    </div>

    <!-- 2. 分类 Tab 栏 (带橙色高亮下划线) -->
    <div class="flex items-center gap-4 border-b border-[#44403C]/50 pt-1">
      <button
        type="button"
        @click="activeCategory = 'avatar-frame'"
        class="pb-2 flex items-center gap-1 text-sm font-medium border-b-2 transition-all cursor-pointer"
        :class="activeCategory === 'avatar-frame' ? 'text-[#FF9F43] border-[#FF9F43]' : 'text-[#78716C] border-transparent'"
      >
        <span>头像框</span>
        <span class="text-xs text-[#78716C] font-mono">(1)</span>
      </button>

      <button
        type="button"
        @click="activeCategory = 'title'"
        class="pb-2 flex items-center gap-1 text-sm font-medium border-b-2 transition-all cursor-pointer"
        :class="activeCategory === 'title' ? 'text-[#FF9F43] border-[#FF9F43]' : 'text-[#78716C] border-transparent'"
      >
        <span>称号</span>
        <span class="text-xs text-[#78716C] font-mono">(0)</span>
      </button>

      <button
        type="button"
        @click="activeCategory = 'items'"
        class="pb-2 flex items-center gap-1 text-sm font-medium border-b-2 transition-all cursor-pointer"
        :class="activeCategory === 'items' ? 'text-[#FF9F43] border-[#FF9F43]' : 'text-[#78716C] border-transparent'"
      >
        <span>消耗道具</span>
        <span class="text-xs text-[#78716C] font-mono">(0)</span>
      </button>
    </div>

    <!-- 3. 道具网格 -->
    <div class="grid grid-cols-3 gap-3 pt-2">
      <!-- 道具 1: 月卡头像框 -->
      <div class="flex flex-col items-center p-2.5 rounded-xl border-2 border-[#44403C] bg-[#292524]/30 hover:border-[#F9C86D]/50 transition-all cursor-pointer group">
        <!-- 道具图标/预览 -->
        <div class="w-14 h-14 rounded-full border border-[#F9C86D]/40 bg-[#1A1714] flex items-center justify-center relative overflow-hidden group-hover:scale-105 transition-transform">
          <span class="text-xl">🌙</span>
        </div>

        <span class="text-xs text-[#F5F5F4] font-medium mt-1.5">月卡</span>
        <span class="text-[11px] text-[#A8A29E]">普通</span>
        <span class="text-[10px] text-[#78716C]">勋章奖励</span>
      </div>
    </div>

  </div>
</template>
