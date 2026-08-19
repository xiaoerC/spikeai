<script setup lang="ts">
/**
 * 历史分类 Tab 药丸栏组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { HistoryTabType } from "@/views/history/types";

defineProps<{
  /** 当前激活的分类 Tab */
  modelValue: HistoryTabType;
  /** 剧情卡记录总数 */
  storyCount?: number;
}>();

const emit = defineEmits<(e: "update:modelValue", val: HistoryTabType) => void>();

/**
 * 切换分类 Tab
 */
function handleSelect(tab: HistoryTabType): void {
  emit("update:modelValue", tab);
}
</script>

<template>
  <div class="w-full px-4 pt-6">
    <!-- 药丸容器: border: 0.667px solid #44403C; bg: rgba(68, 64, 60, 0.60) -->
    <div class="inline-flex items-center p-[2px] gap-[2px] rounded-lg border border-[#44403C] bg-[rgba(68,64,60,0.60)] backdrop-blur-md">
      
      <!-- 1. 📖 剧情卡 Tab (激活态: 金黄渐变高光 + 数量徽标) -->
      <button
        type="button"
        @click="handleSelect('story')"
        :class="[
          'flex items-center gap-1.5 px-2.5 py-1.5 rounded-md transition-all duration-150 cursor-pointer select-none',
          modelValue === 'story'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] shadow-[0_1px_8px_0_rgba(249,200,109,0.25)] text-[#0C0A09]'
            : 'text-[rgba(168,162,158,0.70)] hover:text-white'
        ]"
      >
        <span class="text-[11px] leading-none font-semibold">📖</span>
        <!-- 数量徽标 -->
        <div
          v-if="(storyCount ?? 0) > 0"
          :class="[
            'w-4 h-4 min-w-4 rounded-full flex items-center justify-center text-[10px] font-semibold leading-none',
            modelValue === 'story'
              ? 'bg-black/15 text-[#0C0A09]'
              : 'bg-white/10 text-gray-300'
          ]"
        >
          {{ storyCount }}
        </div>
      </button>

      <!-- 2. 🏪 市场/收藏 Tab -->
      <button
        type="button"
        @click="handleSelect('market')"
        :class="[
          'flex items-center justify-center px-2.5 py-1.5 rounded-md transition-all duration-150 cursor-pointer select-none',
          modelValue === 'market'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] shadow-[0_1px_8px_0_rgba(249,200,109,0.25)] text-[#0C0A09]'
            : 'text-[rgba(168,162,158,0.70)] hover:text-white'
        ]"
      >
        <span class="text-[11px] leading-none">🏪</span>
      </button>

      <!-- 3. ⚙️ 设置 Tab -->
      <button
        type="button"
        @click="handleSelect('settings')"
        :class="[
          'flex items-center justify-center px-2.5 py-1.5 rounded-md transition-all duration-150 cursor-pointer select-none',
          modelValue === 'settings'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] shadow-[0_1px_8px_0_rgba(249,200,109,0.25)] text-[#0C0A09]'
            : 'text-[rgba(168,162,158,0.70)] hover:text-white'
        ]"
      >
        <span class="text-[11px] leading-none">⚙️</span>
      </button>

      <!-- 4. 🧩 插件 Tab -->
      <button
        type="button"
        @click="handleSelect('plugins')"
        :class="[
          'flex items-center justify-center px-2.5 py-1.5 rounded-md transition-all duration-150 cursor-pointer select-none',
          modelValue === 'plugins'
            ? 'bg-gradient-to-br from-[#FFD475] via-[#F9C86D] to-[#D1A35C] shadow-[0_1px_8px_0_rgba(249,200,109,0.25)] text-[#0C0A09]'
            : 'text-[rgba(168,162,158,0.70)] hover:text-white'
        ]"
      >
        <span class="text-[11px] leading-none">🧩</span>
      </button>

    </div>
  </div>
</template>
