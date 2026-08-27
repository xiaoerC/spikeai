<script setup lang="ts">
/**
 * 画师串管理主面板组件 (Figma 84:6799 1:1 像素级高保真)
 *
 * 包含 已使用 X/50、+新建画师串、画师串卡片流 (已激活徽章/描述/创建时间/提示词预览)、编辑/删除/激活。
 *
 * @packageDocumentation
 */

import type { ArtistPromptItem } from "@/views/history/types";

defineProps<{
  artistList: ArtistPromptItem[];
}>();

const emit = defineEmits<{
  (e: "create"): void;
  (e: "edit", item: ArtistPromptItem): void;
  (e: "delete", id: string): void;
  (e: "set-active", id: string): void;
}>();
</script>

<template>
  <div class="w-full px-4 pt-6 flex flex-col pb-6">
    <!-- 1. 顶部统计与新建按钮栏 (Figma 84:6799) -->
    <div class="w-full flex items-center justify-between pb-6">
      <!-- 左侧: 已使用 X/50 -->
      <div class="text-[14px] leading-[20px] text-[#F5F5F4]">
        已使用 <span class="font-bold text-[#F9C86D]">{{ artistList.length }}</span>/50
      </div>

      <!-- 右侧: + 新建画师串 -->
      <button
        type="button"
        @click="emit('create')"
        class="px-4 py-2 flex items-center justify-center rounded-[8px] bg-[#F9C86D] text-[16px] leading-[27.2px] font-normal text-[#0C0A09] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none shadow-md"
      >
        + 新建画师串
      </button>
    </div>

    <!-- 2. 空状态 (暂无画师串) -->
    <div
      v-if="artistList.length === 0"
      class="w-full flex flex-col items-center justify-center py-16 text-center"
    >
      <p class="text-[16px] text-[#78716C] leading-[27.2px] pb-6">
        暂无画师串
      </p>
      <button
        type="button"
        @click="emit('create')"
        class="w-[159px] h-[51px] flex items-center justify-center rounded-[8px] bg-[#F9C86D] text-[16px] leading-[27.2px] font-normal text-[#0C0A09] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none shadow-lg"
      >
        创建第一个画师串
      </button>
    </div>

    <!-- 3. 画师串卡片列表 (Figma 84:6799) -->
    <div v-else class="w-full flex flex-col gap-3">
      <div
        v-for="artist in artistList"
        :key="artist.id"
        class="w-full p-4 rounded-[8px] border border-[#44403C] bg-[#292524] flex flex-col shadow-sm"
      >
        <!-- 头部: 名称 + 状态徽章 + 描述 + 创建时间 -->
        <div class="w-full flex flex-col">
          <div class="flex items-center gap-2">
            <h3 class="text-[16px] font-semibold text-[#F5F5F4] leading-[19.2px] tracking-[-0.32px]">
              {{ artist.name }}
            </h3>
            <span
              v-if="artist.isActive"
              class="px-2 py-0.5 rounded-[4px] bg-[rgba(249,200,109,0.08)] text-[#F9C86D] text-[12px] leading-[16px]"
            >
              已激活
            </span>
          </div>

          <!-- 风格描述 -->
          <p v-if="artist.description" class="text-[12px] text-[#F9C86D] leading-[16px] pt-1">
            {{ artist.description }}
          </p>

          <!-- 创建时间 -->
          <p v-if="artist.createdAt" class="text-[12px] text-[#78716C] leading-[16px] pt-1">
            创建于 {{ artist.createdAt }}
          </p>
        </div>

        <!-- 提示词文本正文预览 -->
        <div class="pt-2">
          <p class="text-[14px] text-[#A8A29E] leading-[20px] line-clamp-2 break-all font-sans">
            {{ artist.prompt }}
          </p>
        </div>

        <!-- 底部操作栏: 激活 / 编辑 / 删除 -->
        <div class="pt-3 flex items-center gap-2">
          <!-- 设为激活 -->
          <button
            v-if="!artist.isActive"
            type="button"
            @click="emit('set-active', artist.id)"
            class="px-3 py-1.5 rounded-[4px] border border-[#F9C86D] text-[14px] text-[#F9C86D] leading-[20px] hover:bg-[#F9C86D]/10 active:scale-95 transition-all cursor-pointer select-none"
          >
            设为激活
          </button>

          <!-- 编辑 -->
          <button
            type="button"
            @click="emit('edit', artist)"
            class="px-3 py-1.5 rounded-[4px] border border-[#44403C] text-[14px] text-[#F5F5F4] leading-[20px] hover:bg-white/5 active:scale-95 transition-all cursor-pointer select-none"
          >
            编辑
          </button>

          <!-- 删除 -->
          <button
            type="button"
            @click="emit('delete', artist.id)"
            class="px-3 py-1.5 rounded-[4px] border border-[rgba(239,68,68,0.50)] text-[14px] text-[#EF4444] leading-[20px] hover:bg-[#EF4444]/10 active:scale-95 transition-all cursor-pointer select-none"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
