<script setup lang="ts">
/**
 * 个人中心 - 玩家等级卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { PLAYER_LEVEL_DATA } from "@/views/profile/constants/profileMock";
import { ChevronRight, Gem, Moon, Sparkles, Star } from "lucide-vue-next";
</script>

<template>
  <div class="w-full p-4 rounded-lg border border-[#C0A480]/15 bg-gradient-to-br from-[#F4E8C1]/[0.04] to-[#F4E8C1]/[0.02] flex flex-col gap-3">
    <!-- 1. 标题行 -->
    <div class="flex items-center justify-between w-full">
      <div class="flex items-center gap-2">
        <Sparkles class="w-4 h-4 text-[#F9C86D]" />
        <h3 class="text-[16px] font-semibold text-[#F9C86D] tracking-[-0.32px] leading-5">
          玩家等级
        </h3>
      </div>
    </div>

    <!-- 2. 等级头衔与经验进度 -->
    <div class="w-full flex flex-col pt-1">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="text-[14px] font-semibold text-[#A8A29E] leading-5">
            {{ PLAYER_LEVEL_DATA.title }}
          </span>
          <span class="text-xs text-[#78716C] font-medium">
            等级 {{ PLAYER_LEVEL_DATA.level }}
          </span>
        </div>
        <button
          type="button"
          class="w-6 h-6 rounded-full border border-[#A8A29E]/30 flex items-center justify-center text-[#A8A29E] hover:text-white transition-colors cursor-pointer"
        >
          <ChevronRight class="w-3 h-3" />
        </button>
      </div>

      <!-- XP 进度条 -->
      <div class="flex flex-col gap-1 mt-3">
        <div class="flex items-center justify-between text-xs">
          <span class="text-[#78716C]">经验值</span>
          <span class="text-[#A8A29E] font-mono font-medium">
            {{ PLAYER_LEVEL_DATA.currentXp }} / {{ PLAYER_LEVEL_DATA.nextLevelXp }} XP
          </span>
        </div>
        <div class="w-full h-2 rounded-full bg-[#292524] overflow-hidden relative">
          <div
            class="h-full rounded-full bg-[#F9C86D] opacity-80 shadow-[0_0_8px_rgba(249,200,109,0.15)] transition-all duration-300"
            :style="{ width: `${PLAYER_LEVEL_DATA.progressPercentage}%` }"
          />
        </div>
        <p class="text-[11px] text-[#78716C] text-right mt-0.5">
          {{ PLAYER_LEVEL_DATA.progressPercentage }}% 至下一等级
        </p>
      </div>
    </div>

    <!-- 3. 5 项指标阵列 (总经验、月华使用、星元使用、会员使用量、累计充值) -->
    <div class="w-full grid grid-cols-5 gap-1 pt-3 mt-1 border-t border-[#44403C]/60 text-center">
      <!-- (1) 总经验 -->
      <div class="flex flex-col items-center">
        <span class="text-[13px] font-bold text-[#F5F5F4] font-mono tracking-tight">{{ PLAYER_LEVEL_DATA.totalXp }}</span>
        <span class="text-[10px] text-[#78716C] mt-0.5">总经验</span>
      </div>

      <!-- (2) 月华使用 -->
      <div class="flex flex-col items-center">
        <div class="flex items-center gap-0.5">
          <Moon class="w-2.5 h-2.5 text-[#FF9F43]" />
          <span class="text-[13px] font-bold text-[#F5F5F4] font-mono tracking-tight">{{ PLAYER_LEVEL_DATA.moonGemsUsed }}</span>
        </div>
        <span class="text-[10px] text-[#78716C] mt-0.5">月华使用</span>
      </div>

      <!-- (3) 星元使用 -->
      <div class="flex flex-col items-center">
        <div class="flex items-center gap-0.5">
          <Star class="w-2.5 h-2.5 text-[#F9C86D] fill-[#F9C86D]" />
          <span class="text-[13px] font-bold text-[#F5F5F4] font-mono tracking-tight">{{ PLAYER_LEVEL_DATA.starCoinsUsed }}</span>
        </div>
        <span class="text-[10px] text-[#78716C] mt-0.5">星元使用</span>
      </div>

      <!-- (4) 会员使用量 -->
      <div class="flex flex-col items-center">
        <div class="flex items-center gap-0.5">
          <Gem class="w-2.5 h-2.5 text-[#60A5FA]" />
          <span class="text-[13px] font-bold text-[#F5F5F4] font-mono tracking-tight">{{ PLAYER_LEVEL_DATA.vipUsage }}</span>
        </div>
        <span class="text-[10px] text-[#78716C] mt-0.5">会员使用量</span>
      </div>

      <!-- (5) 累计充值 -->
      <div class="flex flex-col items-center">
        <span class="text-[13px] font-bold text-[#F5F5F4] font-mono tracking-tight">{{ PLAYER_LEVEL_DATA.totalRecharged }}</span>
        <span class="text-[10px] text-[#78716C] mt-0.5">累计充值</span>
      </div>
    </div>

  </div>
</template>
