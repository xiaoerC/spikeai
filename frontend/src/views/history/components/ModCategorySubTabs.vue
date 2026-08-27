<script setup lang="ts">
/**
 * Mod 模组中心二级分类导航栏 (Figma 93:3270 1:1 像素级高保真)
 *
 * 包含 🧩 广场 / 🎨 我创作的 / 🛍️ 我购买的 / 📦 合集 / ⚙️ Mod 设置 5 大分类，具备平滑滚动与绝对定位金色指示器。
 *
 * @packageDocumentation
 */

import type { ModSubCategory } from "@/views/history/types";

defineProps<{
  activeSubCategory: ModSubCategory;
}>();

const emit = defineEmits<(e: "selectSub", category: ModSubCategory) => void>();

const MOD_TABS = [
  { id: "square" as const, icon: "🧩", label: "广场" },
  { id: "created" as const, icon: "🎨", label: "我创作的" },
  { id: "purchased" as const, icon: "🛍️", label: "我购买的" },
  { id: "collection" as const, icon: "📦", label: "合集" },
  { id: "settings" as const, icon: "⚙️", label: "Mod 设置" },
];
</script>

<template>
  <div class="w-full relative pt-6">
    <div class="w-full flex items-center border-b border-[rgba(168,162,158,0.15)] overflow-x-auto no-scrollbar relative">
      <button
        v-for="tab in MOD_TABS"
        :key="tab.id"
        type="button"
        @click="emit('selectSub', tab.id)"
        class="flex items-center gap-1.5 px-3 py-2 text-[12px] leading-[16px] transition-colors relative flex-shrink-0 cursor-pointer select-none"
        :class="
          activeSubCategory === tab.id
            ? 'text-[#F9C86D] font-medium'
            : 'text-[#78716C] hover:text-[#A8A29E] font-normal'
        "
      >
        <span class="text-[11px]">{{ tab.icon }}</span>
        <span>{{ tab.label }}</span>
        <!-- 绝对定位底部金色指示条 (防 overflow 裁剪) -->
        <div
          v-if="activeSubCategory === tab.id"
          class="absolute bottom-0 left-0 right-0 h-[2px] bg-[#F9C86D] z-10"
        />
      </button>
    </div>
  </div>
</template>
