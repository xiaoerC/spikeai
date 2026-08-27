<script setup lang="ts">
/**
 * 我创作的 Mod 管理主面板 (Figma 106:8347 1:1 像素级高保真)
 *
 * 包含 "+ 新建 Mod" 按钮、我创作的 Mod 卡片列表、私密草稿/已发布状态徽章、编辑/发布/删除操作栏。
 *
 * @packageDocumentation
 */

import type { CreatedModItem } from "@/views/history/types";

defineProps<{
  createdModList: CreatedModItem[];
}>();

const emit = defineEmits<{
  (e: "create"): void;
  (e: "edit", mod: CreatedModItem): void;
  (e: "publish", id: string): void;
  (e: "delete", id: string): void;
}>();
</script>

<template>
  <div class="w-full flex flex-col pt-5 pb-12">
    <!-- 1. 顶部操作栏: 右侧 "+ 新建 Mod" 按钮 (Figma 106:8347) -->
    <div class="w-full flex justify-end items-center pb-4">
      <button
        type="button"
        @click="emit('create')"
        class="px-4 py-2 rounded-[8px] bg-[rgba(249,200,109,0.15)] text-[#F9C86D] text-[14px] leading-[20px] font-medium hover:bg-[rgba(249,200,109,0.25)] active:scale-95 transition-all cursor-pointer select-none"
      >
        + 新建 Mod
      </button>
    </div>

    <!-- 2. 创作 Mod 卡片列表 (Figma 106:8347) -->
    <div v-if="createdModList.length > 0" class="w-full flex flex-col gap-4">
      <div
        v-for="mod in createdModList"
        :key="mod.id"
        class="w-full p-4 rounded-[12px] border border-[#44403C] bg-[#292524] flex items-start justify-between gap-3 transition-colors hover:border-[#F9C86D]/40"
      >
        <!-- 左侧信息区 (标题 + 状态徽章 + 简介) -->
        <div class="flex-1 min-w-0 flex flex-col">
          <div class="flex items-center gap-2 flex-wrap">
            <h4 class="text-[14px] leading-[20px] font-medium text-[#F5F5F4] truncate max-w-[180px]">
              {{ mod.name }}
            </h4>
            <span
              v-if="mod.status === 'draft'"
              class="px-2 py-0.5 rounded-full bg-white/5 text-[#78716C] text-[10px] leading-[17px] font-normal"
            >
              私密草稿
            </span>
            <span
              v-else
              class="px-2 py-0.5 rounded-full bg-[rgba(34,197,94,0.10)] text-[#22C55E] text-[10px] leading-[17px] font-normal"
            >
              已发布
            </span>
          </div>

          <p class="text-[12px] leading-[16px] text-[#A8A29E] pt-1 truncate">
            {{ mod.description || '暂无简介' }}
          </p>
        </div>

        <!-- 右侧操作栏 (编辑 / 发布 / 删除) -->
        <div class="flex-shrink-0 flex items-center gap-2">
          <!-- 编辑 -->
          <button
            type="button"
            @click="emit('edit', mod)"
            class="px-3 py-1.5 rounded-[8px] border border-[#44403C] bg-[#292524] text-[12px] leading-[16px] text-[#A8A29E] hover:text-[#F5F5F4] active:scale-95 transition-all cursor-pointer select-none"
          >
            编辑
          </button>

          <!-- 发布 / 下架 -->
          <button
            type="button"
            @click="emit('publish', mod.id)"
            class="px-3 py-1.5 rounded-[8px] bg-[rgba(34,197,94,0.10)] text-[12px] leading-[16px] text-[#22C55E] hover:bg-[rgba(34,197,94,0.20)] active:scale-95 transition-all cursor-pointer select-none"
          >
            {{ mod.status === 'published' ? '下架' : '发布' }}
          </button>

          <!-- 删除 -->
          <button
            type="button"
            @click="emit('delete', mod.id)"
            class="px-3 py-1.5 rounded-[8px] bg-[rgba(239,68,68,0.10)] text-[12px] leading-[16px] text-[#EF4444] hover:bg-[rgba(239,68,68,0.20)] active:scale-95 transition-all cursor-pointer select-none"
          >
            删除
          </button>
        </div>
      </div>
    </div>

    <!-- 3. 空状态 -->
    <div
      v-else
      class="flex flex-col items-center justify-center py-20 text-center px-4"
    >
      <div class="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center mb-3">
        <span class="text-2xl">🎨</span>
      </div>
      <p class="text-sm text-[#A8A29E] font-medium">还没有创建任何 Mod</p>
      <p class="text-xs text-[#78716C] mt-1">点击右上角「+ 新建 Mod」开始创作属于你的专属模组吧</p>
    </div>
  </div>
</template>
