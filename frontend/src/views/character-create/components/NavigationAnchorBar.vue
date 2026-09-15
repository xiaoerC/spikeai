<script setup lang="ts">
/**
 * 角色卡创建器吸顶锚点导航栏与模式切换器
 *
 * 遵循 4 大分节体系 (卡面/角色/舞台/机制/预览) 与 简洁/完整 模式切换。
 *
 * @packageDocumentation
 */

import type { CreateSectionTab, DisplayMode } from "../types";

const props = defineProps<{
  /** 当前激活分节 Tab */
  activeTab: CreateSectionTab;
  /** 当前显示模式 (简洁 vs 完整) */
  displayMode: DisplayMode;
}>();

const emit = defineEmits<{
  (e: "update:activeTab", tab: CreateSectionTab): void;
  (e: "update:displayMode", mode: DisplayMode): void;
  (e: "open-preview"): void;
}>();

const tabs: { key: CreateSectionTab; label: string }[] = [
  { key: "cover", label: "卡面" },
  { key: "character", label: "角色" },
  { key: "stage", label: "舞台" },
  { key: "mechanics", label: "机制" },
  { key: "preview", label: "预览" },
];

function handleTabClick(key: CreateSectionTab): void {
  emit("update:activeTab", key);
  if (key === "preview") {
    emit("open-preview");
    return;
  }
  const el = document.getElementById(`section-${key}`);
  if (el) {
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}
</script>

<template>
  <div class="sticky top-0 z-30 w-full px-3 py-2.5 bg-[rgba(20,18,15,0.92)] backdrop-blur-md border-b border-[rgba(83,71,65,0.30)] flex items-center justify-between shadow-lg">
    <!-- 1. 左侧 5 大分节锚点 Tab 标签组 -->
    <nav class="flex items-center gap-1.5 overflow-x-auto no-scrollbar">
      <button
        v-for="t in tabs"
        :key="t.key"
        type="button"
        @click="handleTabClick(t.key)"
        :class="[
          'px-3 py-1 rounded-lg text-xs font-medium transition-all duration-150 cursor-pointer select-none shrink-0 border',
          activeTab === t.key
            ? 'bg-[#F9C86D] text-black border-[#F9C86D] shadow-[0_0_12px_rgba(249,200,109,0.3)] font-semibold'
            : 'bg-[rgba(35,30,25,0.5)] text-[#A8A29E] border-[#44403C]/40 hover:text-white hover:border-[#666]'
        ]"
      >
        {{ t.label }}
      </button>
    </nav>

    <!-- 2. 右侧 简洁 / 完整 双模式胶囊切换器 -->
    <div class="flex items-center p-0.5 rounded-full bg-[rgba(35,30,25,0.8)] border border-[rgba(83,71,65,0.40)] text-[11px] shrink-0 ml-2">
      <button
        type="button"
        @click="emit('update:displayMode', 'simple')"
        :class="[
          'px-2.5 py-0.5 rounded-full transition-all duration-150 cursor-pointer select-none',
          displayMode === 'simple'
            ? 'bg-[#F9C86D] text-black font-semibold shadow'
            : 'text-[#A8A29E] hover:text-white'
        ]"
      >
        简洁
      </button>
      <button
        type="button"
        @click="emit('update:displayMode', 'full')"
        :class="[
          'px-2.5 py-0.5 rounded-full transition-all duration-150 cursor-pointer select-none',
          displayMode === 'full'
            ? 'bg-[#F9C86D] text-black font-semibold shadow'
            : 'text-[#A8A29E] hover:text-white'
        ]"
      >
        完整
      </button>
    </div>
  </div>
</template>
