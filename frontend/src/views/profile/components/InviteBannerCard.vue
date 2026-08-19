<script setup lang="ts">
/**
 * 个人中心 - 邀请活动卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { PROFILE_USER_DATA } from "@/views/profile/constants/profileMock";
import { Check, Copy, Gift } from "lucide-vue-next";
import { ref } from "vue";

const copied = ref(false);

function handleCopyInvite(): void {
  navigator.clipboard.writeText(PROFILE_USER_DATA.inviteCode);
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 1500);
}
</script>

<template>
  <div class="w-full p-4 rounded-lg border border-[#C0A480]/15 bg-gradient-to-br from-[#F4E8C1]/[0.04] to-[#F4E8C1]/[0.02] flex flex-col gap-3">
    <!-- 1. 标题行 -->
    <div class="flex items-center justify-between w-full">
      <div class="flex items-center gap-2">
        <Gift class="w-4 h-4 text-[#F9C86D]" />
        <h3 class="text-[16px] font-semibold text-[#F9C86D] tracking-[-0.32px] leading-5">
          邀请活动
        </h3>
      </div>
      <span class="text-xs text-[#78716C]">
        已邀请 <strong class="text-[#A8A29E] font-mono">0/∞</strong>
      </span>
    </div>

    <!-- 2. 邀请福利文案与 +100 徽章 -->
    <div class="flex items-center gap-3 pt-1">
      <!-- +100 炫彩微章 -->
      <div class="w-9 h-9 rounded-full p-[2px] bg-gradient-to-br from-[#A8A29E] via-[#FFD475] to-[#F9C86D] shrink-0">
        <div class="w-full h-full rounded-full bg-[#292524] flex items-center justify-center text-xs font-bold text-[#F9C86D] font-mono">
          +100
        </div>
      </div>

      <div class="flex flex-col">
        <p class="text-[13px] font-medium text-[#F5F5F4] leading-5">
          邀请你的朋友来叙梦naro！
        </p>
        <p class="text-xs text-[#78716C] mt-0.5">
          大家都可以获得额外的100星元！
        </p>
      </div>
    </div>

    <!-- 3. 邀请码与操作按钮 -->
    <div class="flex items-center justify-between pt-3 border-t border-[#44403C]/40">
      <div class="flex items-center gap-2">
        <div class="px-3 py-1 rounded-full bg-[#A8A29E]/20 text-xs font-mono font-medium text-[#F9C86D]">
          {{ PROFILE_USER_DATA.inviteCode }}
        </div>
        <button
          type="button"
          @click="handleCopyInvite"
          class="p-1 text-[#A8A29E] hover:text-[#F9C86D] transition-colors cursor-pointer"
        >
          <Check v-if="copied" class="w-3.5 h-3.5 text-[#22C55E]" />
          <Copy v-else class="w-3.5 h-3.5" />
        </button>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-3 py-1 rounded-full border border-[#A8A29E]/50 text-xs font-medium text-[#A8A29E] hover:text-white hover:border-[#F9C86D] transition-all cursor-pointer select-none"
        >
          生成链接
        </button>
        <button
          type="button"
          class="px-3 py-1 rounded-full border border-[#A8A29E]/50 text-xs font-medium text-[#A8A29E] hover:text-white hover:border-[#F9C86D] transition-all cursor-pointer select-none"
        >
          详情
        </button>
      </div>
    </div>

  </div>
</template>
