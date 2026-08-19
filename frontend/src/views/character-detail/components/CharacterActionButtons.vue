<script setup lang="ts">
/**
 * 角色卡详情 - 核心操作按钮组 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { Coins, Flag, Heart, MessageCircle, Share2, Star } from "lucide-vue-next";

defineProps<{
  isLiked?: boolean;
  isFavorited?: boolean;
}>();

const emit = defineEmits<{
  (e: "startChat"): void;
  (e: "toggleLike"): void;
  (e: "toggleFavorite"): void;
  (e: "openRating"): void;
  (e: "share"): void;
  (e: "report"): void;
  (e: "reward"): void;
}>();
</script>

<template>
  <div class="w-full flex flex-col gap-2.5 px-3 pt-2 select-none">
    
    <!-- 1. 第一行操作组 (开始聊天 + 点赞 + 收藏 + 评分 + 分享) -->
    <div class="flex items-center gap-2 overflow-x-auto no-scrollbar">
      <!-- (1) 开始聊天 (主高亮按钮) -->
      <button
        type="button"
        @click="emit('startChat')"
        class="h-9 px-4 rounded-full bg-[#F9C86D] text-[#0C0A09] font-medium text-xs flex items-center gap-1.5 shadow-gold hover:brightness-105 active:scale-95 transition-all cursor-pointer shrink-0"
      >
        <MessageCircle class="w-3.5 h-3.5 fill-[#0C0A09]" />
        <span>开始聊天</span>
      </button>

      <!-- (2) 点赞 -->
      <button
        type="button"
        @click="emit('toggleLike')"
        :class="[
          'h-9 px-3 rounded-full border flex items-center gap-1.5 text-xs transition-all active:scale-95 cursor-pointer shrink-0',
          isLiked
            ? 'bg-[#F9C86D]/20 border-[#F9C86D] text-[#F9C86D]'
            : 'border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10'
        ]"
      >
        <Heart class="w-3.5 h-3.5" :class="{ 'fill-[#F9C86D]': isLiked }" />
        <span>点赞</span>
      </button>

      <!-- (3) 收藏 -->
      <button
        type="button"
        @click="emit('toggleFavorite')"
        :class="[
          'h-9 px-3 rounded-full border flex items-center gap-1.5 text-xs transition-all active:scale-95 cursor-pointer shrink-0',
          isFavorited
            ? 'bg-[#F9C86D]/20 border-[#F9C86D] text-[#F9C86D]'
            : 'border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10'
        ]"
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M19 21L12 16L5 21V5C5 4.46957 5.21071 3.96086 5.58579 3.58579C5.96086 3.21071 6.46957 3 7 3H17C17.5304 3 18.0391 3.21071 18.4142 3.58579C18.7893 3.96086 19 4.46957 19 5V21Z" :stroke="isFavorited ? '#F9C86D' : 'currentColor'" :fill="isFavorited ? '#F9C86D' : 'none'" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span>收藏</span>
      </button>

      <!-- (4) 评分 -->
      <button
        type="button"
        @click="emit('openRating')"
        class="h-9 px-3 rounded-full border border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10 flex items-center gap-1.5 text-xs transition-all active:scale-95 cursor-pointer shrink-0"
      >
        <Star class="w-3.5 h-3.5" />
        <span>评分</span>
      </button>

      <!-- (5) 分享 -->
      <button
        type="button"
        @click="emit('share')"
        class="h-9 px-3 rounded-full border border-[#44403C] text-[#A8A29E] hover:text-white hover:border-[#A8A29E] flex items-center gap-1.5 text-xs transition-all active:scale-95 cursor-pointer shrink-0"
      >
        <Share2 class="w-3.5 h-3.5" />
        <span>分享</span>
      </button>
    </div>

    <!-- 2. 第二行操作组 (举报 + 打赏) -->
    <div class="flex items-center gap-2">
      <!-- 举报 -->
      <button
        type="button"
        @click="emit('report')"
        class="h-9 px-3 rounded-full border border-transparent text-[#A8A29E] hover:text-[#EF4444] flex items-center gap-1.5 text-xs transition-all active:scale-95 cursor-pointer"
      >
        <Flag class="w-3.5 h-3.5" />
        <span>举报</span>
      </button>

      <!-- 打赏 -->
      <button
        type="button"
        @click="emit('reward')"
        class="h-9 px-3 rounded-full border border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10 flex items-center gap-1.5 text-xs transition-all active:scale-95 cursor-pointer"
      >
        <Coins class="w-3.5 h-3.5" />
        <span>打赏</span>
      </button>
    </div>

  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
