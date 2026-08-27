<script setup lang="ts">
/**
 * 自定义/设置二级功能横向导航栏 (1:1 原型像素级高保真)
 *
 * 包含 👤人设 / ⌨️指令 / 🎨画师串 / 📝总结提示词 / 🤖记忆增强模型 5 大分类。
 *
 * @packageDocumentation
 */

import type { CustomSubCategory } from "@/views/history/types";

defineProps<{
  activeSubCategory: CustomSubCategory;
}>();

const emit = defineEmits<(e: "select-sub", cat: CustomSubCategory) => void>();

const TABS: Array<{
  id: CustomSubCategory;
  icon: string;
  label: string;
}> = [
  { id: "persona", icon: "👤", label: "人设" },
  { id: "command", icon: "⌨️", label: "指令" },
  { id: "artist", icon: "🎨", label: "画师串" },
  { id: "summary", icon: "📝", label: "总结提示词" },
  { id: "memory", icon: "AI", label: "记忆增强模型" },
];
</script>

<template>
  <div class="w-full px-4 pt-6">
    <div class="w-full flex items-center border-b border-[#44403C] overflow-x-auto [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden relative">
      <button
        v-for="tab in TABS"
        :key="tab.id"
        type="button"
        @click="emit('select-sub', tab.id)"
        :class="[
          'flex items-center gap-1.5 px-3 h-[48px] transition-all cursor-pointer select-none flex-shrink-0 relative',
          activeSubCategory === tab.id
            ? 'text-[#F9C86D] font-medium'
            : 'text-[#78716C] hover:text-[#A8A29E]'
        ]"
      >
        <span :class="['text-[11px]', tab.id === 'memory' ? 'font-bold' : '']">
          {{ tab.icon }}
        </span>
        <span class="text-[12px] leading-[16px]">
          {{ tab.label }}
        </span>

        <!-- 选中的金色高光指示条 (1:1 覆盖底边) -->
        <div
          v-if="activeSubCategory === tab.id"
          class="absolute bottom-0 left-0 right-0 h-[2px] bg-[#F9C86D] z-10"
        />
      </button>
    </div>
  </div>
</template>
