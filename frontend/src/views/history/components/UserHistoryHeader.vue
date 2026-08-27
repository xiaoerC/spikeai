<script setup lang="ts">
/**
 * 个人历史记录顶部 Header (1:1 原型像素级高保真)
 *
 * 支持主线态（云端备份）、我的上传记录态（🎁收获奖励 / 上传到社区 / 创建角色）与自定义/模组态（纯标题）动态呈现。
 *
 * @packageDocumentation
 */

import type { UserHistoryCategory } from "@/views/history/types";

defineProps<{
  currentCategory: UserHistoryCategory;
}>();

const emit = defineEmits<{
  (e: "backup"): void;
  (e: "claim-rewards"): void;
  (e: "upload-community"): void;
  (e: "create-character"): void;
}>();
</script>

<template>
  <header class="w-full flex items-center justify-between pt-8 px-4 pb-0">
    <!-- 左侧大标题 -->
    <h1 class="text-[20px] font-semibold text-[#F5F5F4] leading-[24px] tracking-[1px] flex-shrink-0">
      历史记录
    </h1>

    <!-- 1. 主线历史态: 右侧单个云端备份金边按钮 (72.6px * 36px) -->
    <button
      v-if="currentCategory === 'story'"
      type="button"
      @click="emit('backup')"
      class="w-[72.6px] h-[36px] px-3 flex items-center justify-center rounded-[8px] border border-[#F9C86D] bg-transparent text-[12px] font-medium text-[#A8A29E] hover:text-[#F9C86D] hover:bg-[#F9C86D]/10 active:scale-95 transition-all shadow-[0_0_15px_rgba(249,200,109,0.08)] cursor-pointer select-none"
    >
      云端备份
    </button>

    <!-- 2. 我的上传记录态: 右侧 3 大高保真彩色操作胶囊 (1:1 原型高光色彩) -->
    <div
      v-else-if="currentCategory === 'tavern'"
      class="flex items-center gap-2 flex-shrink-0"
    >
      <!-- ① 🎁 收获奖励 (91.5px * 36px) -->
      <button
        type="button"
        @click="emit('claim-rewards')"
        style="background: linear-gradient(180deg, #FF9F43 0%, #FFB76B 100%);"
        class="w-[91.5px] h-[36px] px-2 flex items-center justify-center gap-1 rounded-[8px] border border-[#44403C] text-[12px] font-bold text-[#0C0A09] hover:brightness-105 active:scale-95 transition-all cursor-pointer select-none shadow-md"
      >
        <span class="text-[13px]">🎁</span>
        <span>收获奖励</span>
      </button>

      <!-- ② 上传到社区 (83.1px * 36px) -->
      <button
        type="button"
        @click="emit('upload-community')"
        style="background: linear-gradient(180deg, #F9C86D 0%, #D1A35C 100%); box-shadow: 0 0 20px 0 rgba(249, 200, 109, 0.25);"
        class="w-[83.1px] h-[36px] px-2.5 flex items-center justify-center rounded-[8px] text-[12px] font-bold text-[#0C0A09] hover:brightness-105 active:scale-95 transition-all cursor-pointer select-none"
      >
        上传到社区
      </button>

      <!-- ③ 创建角色 (71.3px * 36px) -->
      <button
        type="button"
        @click="emit('create-character')"
        class="w-[71.3px] h-[36px] px-2.5 flex items-center justify-center rounded-[8px] bg-[#22C55E] text-[12px] font-bold text-[#0C0A09] hover:bg-[#16A34A] active:scale-95 transition-all cursor-pointer select-none shadow-md"
      >
        创建角色
      </button>
    </div>
  </header>
</template>
