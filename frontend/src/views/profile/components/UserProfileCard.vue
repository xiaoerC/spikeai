<script setup lang="ts">
/**
 * 个人中心 - 用户核心信息大卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { PROFILE_USER_DATA } from "@/views/profile/constants/profileMock";
import { Check, Copy, Moon, Sparkles, Star } from "lucide-vue-next";
import { ref } from "vue";

const emit = defineEmits<{
  (e: "recharge"): void;
  (e: "dailyReward"): void;
  (e: "navigate", route: string): void;
  (e: "logout"): void;
}>();

const copied = ref(false);

function handleCopyId(): void {
  navigator.clipboard.writeText(PROFILE_USER_DATA.id);
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 1500);
}
</script>

<template>
  <div class="w-full p-4 rounded-lg border border-[#C0A480]/15 bg-gradient-to-br from-[#F4E8C1]/[0.04] to-[#F4E8C1]/[0.02] relative flex flex-col items-center">
    
    <!-- 1. 头像与状态指示 -->
    <div class="relative flex flex-col items-center">
      <!-- 皇冠/VIP微章 (顶部小徽标) -->
      <div class="w-6 h-6 rounded-full bg-[#F9C86D] shadow-glass flex items-center justify-center -mb-2 z-10">
        <Sparkles class="w-3.5 h-3.5 text-[#0C0A09]" />
      </div>

      <!-- 大圆形头像 -->
      <div class="w-20 h-20 rounded-full border-2 border-[#F9C86D]/40 bg-[#292524] overflow-hidden flex items-center justify-center shadow-lg">
        <img
          :src="PROFILE_USER_DATA.avatarUrl"
          alt="Avatar"
          class="w-full h-full object-cover"
        />
      </div>

      <!-- 在线状态绿点 -->
      <div class="w-4 h-4 rounded-full border-2 border-[#1C1917] bg-[#22C55E] absolute right-1 bottom-1" />
    </div>

    <!-- 2. 用户名、邮箱与 ID -->
    <div class="flex flex-col items-center mt-3 gap-0.5">
      <h2 class="text-[20px] font-semibold text-[#F5F5F4] tracking-[-0.4px] leading-6 font-sans">
        {{ PROFILE_USER_DATA.username }}
      </h2>
      <p class="text-xs text-[#78716C] tracking-[-0.176px]">
        {{ PROFILE_USER_DATA.email }}
      </p>

      <!-- ID 与复制按钮 -->
      <div class="flex items-center gap-1 mt-1 text-[10px] text-[#78716C] font-mono">
        <span>{{ PROFILE_USER_DATA.shortId }}</span>
        <button
          type="button"
          @click="handleCopyId"
          title="复制完整 ID"
          class="p-1 hover:text-[#F9C86D] transition-colors cursor-pointer"
        >
          <Check v-if="copied" class="w-3 h-3 text-[#22C55E]" />
          <Copy v-else class="w-3 h-3 text-[#78716C]" />
        </button>
      </div>
    </div>

    <!-- 3. 资产核心指标徽标行 (星元、月华、等级) -->
    <div class="flex items-center justify-center gap-2 mt-3 flex-wrap">
      <!-- 星元胶囊 -->
      <div class="flex items-center gap-1 px-2.5 py-1 rounded-full border border-[#F9C86D]/30 bg-[#292524]">
        <Star class="w-3 h-3 text-[#F9C86D] fill-[#F9C86D]" />
        <span class="text-xs font-bold text-[#F9C86D]">{{ PROFILE_USER_DATA.starCoins }}</span>
      </div>

      <!-- 月华胶囊 -->
      <div class="flex items-center gap-1 px-2.5 py-1 rounded-full border border-[#FF9F43]/30 bg-[#292524]">
        <Moon class="w-3 h-3 text-[#FF9F43] fill-[#FF9F43]" />
        <span class="text-xs font-bold text-[#FF9F43]">{{ PROFILE_USER_DATA.moonGems }}</span>
      </div>

      <!-- 会员等级胶囊 -->
      <div class="flex items-center gap-1 px-2.5 py-1 rounded-full border border-[#6A7282]/30 bg-[#6A7282]/20">
        <span class="text-xs font-medium text-[#99A1AF]">{{ PROFILE_USER_DATA.vipLevel }}</span>
      </div>
    </div>

    <!-- 4. 快捷主操作按钮行 (充值 / 每日奖励日常) -->
    <div class="w-full grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-[#44403C]/30">
      <button
        type="button"
        @click="emit('recharge')"
        class="h-8 rounded-full border border-[#F9C86D]/60 flex items-center justify-center gap-1.5 text-xs font-semibold text-[#F9C86D] hover:bg-[#F9C86D]/10 active:scale-95 transition-all cursor-pointer select-none"
      >
        <span>充值</span>
      </button>

      <button
        type="button"
        @click="emit('dailyReward')"
        class="h-8 rounded-full border border-[#F9C86D]/60 bg-gradient-to-r from-[#F9C86D]/20 to-[#F9C86D]/20 flex items-center justify-center gap-1.5 text-xs font-medium text-[#F9C86D] hover:from-[#F9C86D]/30 hover:to-[#F9C86D]/30 active:scale-95 transition-all cursor-pointer select-none"
      >
        <span>每日奖励日常</span>
      </button>
    </div>

    <!-- 5. 辅助功能导航微胶囊 -->
    <div class="w-full flex items-center gap-2 overflow-x-auto no-scrollbar mt-3 pt-3 pb-2 border-t border-[#44403C]/30">
      <button
        type="button"
        @click="emit('navigate', 'home')"
        class="px-3 py-1 rounded-full border border-[#A8A29E]/50 text-xs text-[#A8A29E] hover:text-white hover:border-[#F9C86D] whitespace-nowrap transition-colors cursor-pointer shrink-0"
      >
        个人首页
      </button>
      <button
        type="button"
        @click="emit('navigate', 'community')"
        class="px-3 py-1 rounded-full border border-[#A8A29E]/50 text-xs text-[#A8A29E] hover:text-white hover:border-[#F9C86D] whitespace-nowrap transition-colors cursor-pointer shrink-0"
      >
        社区
      </button>
      <button
        type="button"
        @click="emit('navigate', 'search-pref')"
        class="px-3 py-1 rounded-full border border-[#A8A29E]/50 text-xs text-[#A8A29E] hover:text-white hover:border-[#F9C86D] whitespace-nowrap transition-colors cursor-pointer shrink-0"
      >
        搜索偏好
      </button>
      <button
        type="button"
        @click="emit('navigate', 'advanced')"
        class="px-3 py-1 rounded-full border border-[#A8A29E]/50 text-xs text-[#A8A29E] hover:text-white hover:border-[#F9C86D] whitespace-nowrap transition-colors cursor-pointer shrink-0"
      >
        高级设置
      </button>
      <button
        type="button"
        @click="emit('navigate', 'guide')"
        class="px-3 py-1 rounded-full border border-[#A8A29E]/50 text-xs text-[#A8A29E] hover:text-white hover:border-[#F9C86D] whitespace-nowrap transition-colors cursor-pointer shrink-0"
      >
        新手攻略
      </button>
    </div>

    <!-- 6. 退出登录全宽红边按钮 -->
    <div class="w-full mt-2">
      <button
        type="button"
        @click="emit('logout')"
        class="w-full h-8 rounded-full border border-[#EF4444]/30 flex items-center justify-center text-xs font-medium text-[#EF4444] hover:bg-[#EF4444]/10 active:scale-98 transition-all cursor-pointer select-none"
      >
        退出登录
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
