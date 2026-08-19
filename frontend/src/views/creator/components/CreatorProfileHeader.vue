<script setup lang="ts">
/**
 * 创作者头部信息栏组件 (1:1 原型高保真)
 *
 * 包含创作者昵称、Lv27 勋章、粉丝数、互动量、头像与关注切换按钮。
 *
 * @packageDocumentation
 */

import type { CreatorItem } from "@/views/creator/types";

defineProps<{
  creator: CreatorItem;
}>();

const emit = defineEmits<(e: "toggle-follow", id: string) => void>();
</script>

<template>
  <div class="flex items-center justify-between w-full">
    <!-- 左侧：昵称 + Lv 等级 + 统计数据 -->
    <div class="flex items-center gap-3">
      <!-- 创作者圆形头像 (40x40) -->
      <img
        :src="creator.avatarUrl"
        :alt="creator.username"
        class="w-10 h-10 rounded-full object-cover border border-[#A8A29E]/40 shadow-sm"
      />

      <div class="flex flex-col gap-0.5">
        <!-- 昵称与等级勋章行 -->
        <div class="flex items-center gap-2">
          <span class="text-base font-semibold text-[#F5F5F4] leading-tight">
            {{ creator.username }}
          </span>
          <span
            class="px-2 py-0.2 rounded-full text-[10px] font-bold text-[#F4E8C1] leading-normal"
            :style="{ backgroundColor: creator.levelBadgeColor || '#A78BFA' }"
          >
            Lv{{ creator.level }}
          </span>
        </div>

        <!-- 粉丝与互动统计行 -->
        <div class="flex items-center gap-3 text-xs text-[#A8A29E]/80">
          <span>粉丝 {{ creator.followersCount }}</span>
          <span>互动 {{ creator.interactionsCount }}</span>
        </div>
      </div>
    </div>

    <!-- 右侧：关注按钮 -->
    <button
      type="button"
      @click="emit('toggle-follow', creator.id)"
      :class="[
        'w-20 py-1.5 rounded-lg text-sm font-semibold transition-all duration-150 cursor-pointer select-none',
        creator.isFollowed
          ? 'border border-[rgba(168,162,158,0.30)] bg-[rgba(168,162,158,0.20)] text-[#A8A29E] hover:bg-[rgba(168,162,158,0.30)]'
          : 'bg-[#F9C86D] hover:bg-[#FFD475] text-[#0C0A09] shadow-md active:scale-95'
      ]"
    >
      {{ creator.isFollowed ? "已关注" : "+ 关注" }}
    </button>
  </div>
</template>
