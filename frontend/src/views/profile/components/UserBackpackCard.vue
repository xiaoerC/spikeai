<script setup lang="ts">
/**
 * 个人中心 - 我的背包卡片 (真实空状态与分类展示)
 *
 * @packageDocumentation
 */

import { Briefcase, PackageOpen } from "lucide-vue-next";
import { ref } from "vue";

const activeCategory = ref<"avatar-frame" | "title" | "items">("avatar-frame");
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

    <!-- 2. 分类 Tab 栏 -->
    <div class="flex items-center gap-4 border-b border-[#44403C]/50 pt-1">
      <button
        type="button"
        @click="activeCategory = 'avatar-frame'"
        class="pb-2 flex items-center gap-1 text-sm font-medium border-b-2 transition-all cursor-pointer"
        :class="activeCategory === 'avatar-frame' ? 'text-[#FF9F43] border-[#FF9F43]' : 'text-[#78716C] border-transparent'"
      >
        <span>头像框</span>
        <span class="text-xs text-[#78716C] font-mono">(0)</span>
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

    <!-- 3. 背包空状态 -->
    <div class="py-8 flex flex-col items-center justify-center gap-2 text-center text-[#78716C]">
      <PackageOpen class="w-8 h-8 opacity-40 text-[#A8A29E]" />
      <p class="text-xs">
        {{ activeCategory === 'avatar-frame' ? '暂无可用头像框' : activeCategory === 'title' ? '暂无专属称号' : '背包中暂无消耗道具' }}
      </p>
    </div>
  </div>
</template>
