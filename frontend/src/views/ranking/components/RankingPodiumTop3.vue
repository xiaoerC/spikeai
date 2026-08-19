<script setup lang="ts">
/**
 * 榜单前三名领奖台组件 (1:1 原型高保真)
 *
 * 采用 2 - 1 - 3 的经典领奖台布局，高光金冠/银冠/铜冠、光晕头像、称号与经验值。
 *
 * @packageDocumentation
 */

import type { RankingUserItem } from "@/views/ranking/types";

defineProps<{
  champion?: RankingUserItem;
  runnerUp?: RankingUserItem;
  thirdPlace?: RankingUserItem;
}>();
</script>

<template>
  <div class="w-full flex items-end justify-center gap-2 px-2 pt-8 pb-4">
    
    <!-- 2. 亚军 (No. 2 🥈 银冠) -->
    <div
      v-if="runnerUp"
      class="flex-1 flex flex-col items-center p-3 rounded-xl bg-gradient-to-b from-[#2A2420] to-[#1C1713] border border-[#A8A29E]/30 shadow-lg relative"
    >
      <!-- 银冠徽标 (2) -->
      <div class="absolute -top-3.5 w-7 h-7 rounded-full bg-[#E5E7EB] text-[#1F2937] flex items-center justify-center font-bold text-xs shadow-[0_0_10px_rgba(229,231,235,0.5)] border-2 border-white">
        2
      </div>

      <!-- 头像 -->
      <img
        :src="runnerUp.avatarUrl"
        :alt="runnerUp.username"
        class="w-13 h-13 rounded-full object-cover border-2 border-[#E5E7EB] mt-1 shadow-md"
      />

      <!-- 昵称 -->
      <span class="text-xs font-semibold text-[#F5F5F4] mt-2 line-clamp-1">
        {{ runnerUp.username }}
      </span>

      <!-- 称号与等级 -->
      <div class="flex items-center gap-1 text-[10px] text-[#A8A29E] mt-0.5">
        <span class="text-[#F9C86D]">⭐</span>
        <span>{{ runnerUp.title }}</span>
        <span>·</span>
        <span class="font-bold text-[#F4E8C1]">Lv.{{ runnerUp.level }}</span>
      </div>

      <!-- 经验值 -->
      <div class="flex items-center gap-1 text-[11px] font-bold text-[#F9C86D] mt-1.5 bg-[rgba(249,200,109,0.12)] px-2 py-0.5 rounded-full border border-[#F9C86D]/20">
        <span>✨</span>
        <span>{{ runnerUp.xp }}</span>
      </div>
    </div>

    <!-- 1. 冠军 (No. 1 👑 金冠，居中且最高) -->
    <div
      v-if="champion"
      class="flex-1 flex flex-col items-center p-3.5 -mt-4 rounded-xl bg-gradient-to-b from-[#382D20] via-[#241C15] to-[#1A140F] border-2 border-[#F9C86D]/60 shadow-[0_0_20px_rgba(249,200,109,0.25)] relative z-10"
    >
      <!-- 金冠徽标 (👑 1) -->
      <div class="absolute -top-4 w-8 h-8 rounded-full bg-gradient-to-tr from-[#D4AF37] via-[#F9C86D] to-[#FFF1C2] text-[#3D2900] flex items-center justify-center font-extrabold text-sm shadow-[0_0_15px_rgba(249,200,109,0.8)] border-2 border-white">
        1
      </div>

      <!-- 头像 -->
      <img
        :src="champion.avatarUrl"
        :alt="champion.username"
        class="w-16 h-16 rounded-full object-cover border-2 border-[#F9C86D] mt-1 shadow-[0_0_12px_rgba(249,200,109,0.40)]"
      />

      <!-- 昵称 -->
      <span class="text-sm font-bold text-[#F9C86D] mt-2 line-clamp-1">
        {{ champion.username }}
      </span>

      <!-- 称号与等级 -->
      <div class="flex items-center gap-1 text-[11px] text-[#F5F5F4] mt-0.5">
        <span class="text-[#F9C86D]">⭐</span>
        <span>{{ champion.title }}</span>
        <span>·</span>
        <span class="font-bold text-[#F9C86D]">Lv.{{ champion.level }}</span>
      </div>

      <!-- 经验值 -->
      <div class="flex items-center gap-1 text-xs font-extrabold text-[#F9C86D] mt-1.5 bg-gradient-to-r from-[#F9C86D]/25 to-[#F9C86D]/10 px-2.5 py-0.5 rounded-full border border-[#F9C86D]/40 shadow-sm">
        <span>✨</span>
        <span>{{ champion.xp }}</span>
      </div>
    </div>

    <!-- 3. 季军 (No. 3 🥉 铜冠) -->
    <div
      v-if="thirdPlace"
      class="flex-1 flex flex-col items-center p-3 rounded-xl bg-gradient-to-b from-[#2A221C] to-[#1C1511] border border-[#CD7F32]/40 shadow-lg relative"
    >
      <!-- 铜冠徽标 (3) -->
      <div class="absolute -top-3.5 w-7 h-7 rounded-full bg-[#CD7F32] text-white flex items-center justify-center font-bold text-xs shadow-[0_0_10px_rgba(205,127,50,0.5)] border-2 border-white">
        3
      </div>

      <!-- 头像 -->
      <img
        :src="thirdPlace.avatarUrl"
        :alt="thirdPlace.username"
        class="w-13 h-13 rounded-full object-cover border-2 border-[#CD7F32] mt-1 shadow-md"
      />

      <!-- 昵称 -->
      <span class="text-xs font-semibold text-[#F5F5F4] mt-2 line-clamp-1">
        {{ thirdPlace.username }}
      </span>

      <!-- 称号与等级 -->
      <div class="flex items-center gap-1 text-[10px] text-[#A8A29E] mt-0.5">
        <span class="text-[#F9C86D]">⭐</span>
        <span>{{ thirdPlace.title }}</span>
        <span>·</span>
        <span class="font-bold text-[#F4E8C1]">Lv.{{ thirdPlace.level }}</span>
      </div>

      <!-- 经验值 -->
      <div class="flex items-center gap-1 text-[11px] font-bold text-[#F9C86D] mt-1.5 bg-[rgba(249,200,109,0.12)] px-2 py-0.5 rounded-full border border-[#F9C86D]/20">
        <span>✨</span>
        <span>{{ thirdPlace.xp }}</span>
      </div>
    </div>

  </div>
</template>
