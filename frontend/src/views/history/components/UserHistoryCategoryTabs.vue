<script setup lang="ts">
/**
 * 个人历史记录 4 大分类切换栏 (1:1 原型像素级高保真)
 *
 * @packageDocumentation
 */

import type { UserHistoryCategory } from "@/views/history/types";

defineProps<{
  currentCategory: UserHistoryCategory;
  storyCount: number;
  tavernCount: number;
  customCount: number;
  moduleCount: number;
}>();

const emit = defineEmits<(e: "select-category", cat: UserHistoryCategory) => void>();
</script>

<template>
  <div class="px-4 pt-8">
    <div class="inline-flex items-center gap-[2px] p-[2px] rounded-[8px] border border-[#44403C] bg-[rgba(68,64,60,0.60)] backdrop-blur-[8px]">
      <!-- 1. 📖 剧情/全部卡片 -->
      <button
        type="button"
        @click="emit('select-category', 'story')"
        :class="[
          'flex items-center gap-1 px-2.5 py-1.5 rounded-[6px] text-[11px] font-semibold transition-all cursor-pointer select-none',
          currentCategory === 'story'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] text-[#0C0A09] shadow-[0_1px_8px_rgba(249,200,109,0.25)]'
            : 'text-[#A8A29E]/70 hover:text-white'
        ]"
      >
        <span>📖</span>
        <span
          v-if="storyCount > 0"
          :class="[
            'px-1 py-0.2 rounded-full text-[10px] font-bold leading-none min-w-[16px] text-center',
            currentCategory === 'story' ? 'bg-black/15 text-[#0C0A09]' : 'bg-white/10 text-[#A8A29E]'
          ]"
        >
          {{ storyCount }}
        </span>
      </button>

      <!-- 2. 🏪 酒馆/商城卡片 -->
      <button
        type="button"
        @click="emit('select-category', 'tavern')"
        :class="[
          'flex items-center gap-1 px-2.5 py-1.5 rounded-[6px] text-[11px] font-semibold transition-all cursor-pointer select-none',
          currentCategory === 'tavern'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] text-[#0C0A09] shadow-[0_1px_8px_rgba(249,200,109,0.25)]'
            : 'text-[#A8A29E]/70 hover:text-white'
        ]"
      >
        <span>🏪</span>
        <span
          v-if="tavernCount > 0"
          :class="[
            'px-1 py-0.2 rounded-full text-[10px] font-bold leading-none min-w-[16px] text-center',
            currentCategory === 'tavern' ? 'bg-black/15 text-[#0C0A09]' : 'bg-white/10 text-[#A8A29E]'
          ]"
        >
          {{ tavernCount }}
        </span>
      </button>

      <!-- 3. ⚙️ 自定义/自建卡片 -->
      <button
        type="button"
        @click="emit('select-category', 'custom')"
        :class="[
          'flex items-center gap-1 px-2.5 py-1.5 rounded-[6px] text-[11px] font-semibold transition-all cursor-pointer select-none',
          currentCategory === 'custom'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] text-[#0C0A09] shadow-[0_1px_8px_rgba(249,200,109,0.25)]'
            : 'text-[#A8A29E]/70 hover:text-white'
        ]"
      >
        <span>⚙️</span>
        <span
          v-if="customCount > 0"
          :class="[
            'px-1 py-0.2 rounded-full text-[10px] font-bold leading-none min-w-[16px] text-center',
            currentCategory === 'custom' ? 'bg-black/15 text-[#0C0A09]' : 'bg-white/10 text-[#A8A29E]'
          ]"
        >
          {{ customCount }}
        </span>
      </button>

      <!-- 4. 🧩 模组/插件卡片 -->
      <button
        type="button"
        @click="emit('select-category', 'module')"
        :class="[
          'flex items-center gap-1 px-2.5 py-1.5 rounded-[6px] text-[11px] font-semibold transition-all cursor-pointer select-none',
          currentCategory === 'module'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] text-[#0C0A09] shadow-[0_1px_8px_rgba(249,200,109,0.25)]'
            : 'text-[#A8A29E]/70 hover:text-white'
        ]"
      >
        <span>🧩</span>
        <span
          v-if="moduleCount > 0"
          :class="[
            'px-1 py-0.2 rounded-full text-[10px] font-bold leading-none min-w-[16px] text-center',
            currentCategory === 'module' ? 'bg-black/15 text-[#0C0A09]' : 'bg-white/10 text-[#A8A29E]'
          ]"
        >
          {{ moduleCount }}
        </span>
      </button>
    </div>
  </div>
</template>
