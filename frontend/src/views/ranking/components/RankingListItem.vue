<script setup lang="ts">
/**
 * 榜单第 4~N 名单项组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { RankingUserItem } from "@/views/ranking/types";

defineProps<{
  user: RankingUserItem;
}>();
</script>

<template>
  <div class="flex items-center justify-between px-3.5 py-3 rounded-xl bg-[rgba(26,21,16,0.60)] border border-white/5 hover:border-white/10 transition-colors">
    <!-- 左侧：排名 + 头像 + 昵称与称号 -->
    <div class="flex items-center gap-3">
      <!-- 排名序号 -->
      <span class="w-6 text-center text-sm font-bold text-[#A8A29E]">
        {{ user.rank }}
      </span>

      <!-- 头像 -->
      <img
        :src="user.avatarUrl"
        :alt="user.username"
        class="w-10 h-10 rounded-full object-cover border border-white/10"
      />

      <!-- 昵称与称号等级 -->
      <div class="flex flex-col gap-0.5">
        <span class="text-sm font-semibold text-[#F5F5F4]">
          {{ user.username }}
        </span>
        <div class="flex items-center gap-1 text-[10px] text-[#A8A29E]">
          <span class="text-[#F9C86D]">⭐</span>
          <span>{{ user.title }}</span>
          <span>·</span>
          <span class="font-medium text-[#F4E8C1]">Lv.{{ user.level }}</span>
        </div>
      </div>
    </div>

    <!-- 右侧：经验值 -->
    <div class="flex items-center gap-1 text-xs font-bold text-[#F9C86D]">
      <span>✨</span>
      <span>{{ user.xp }}</span>
    </div>
  </div>
</template>
