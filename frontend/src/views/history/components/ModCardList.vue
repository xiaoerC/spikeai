<script setup lang="ts">
/**
 * Mod 模组卡片列表矩阵 (Figma 93:3270 1:1 像素级高保真)
 *
 * 包含 🧩 模组图标底座、标题与绿色已购徽章、描述正文、作者/评分/点赞元数据栏、🌙 月亮价格与购买按钮状态机。
 *
 * @packageDocumentation
 */

import type { ModItem } from "@/views/history/types";

defineProps<{
  modList: ModItem[];
}>();

const emit = defineEmits<(e: "buy", id: string) => void>();
</script>

<template>
  <div class="w-full pt-4 pb-12 flex flex-col">
    <!-- Mod 卡片流容器 (Figma 93:3270) -->
    <div
      v-if="modList.length > 0"
      class="w-full rounded-[12px] border border-[#44403C] bg-[#292524] overflow-hidden flex flex-col"
    >
      <div
        v-for="item in modList"
        :key="item.id"
        class="w-full p-3 sm:px-4 flex items-start gap-3 border-b border-[#44403C] last:border-b-0 transition-colors hover:bg-white/[0.02]"
      >
        <!-- 1. 左侧 🧩 模组图标底座 (Figma 93:3270) -->
        <div class="pt-0.5 flex-shrink-0">
          <div class="w-9 h-9 rounded-[8px] border border-[rgba(249,200,109,0.15)] bg-[rgba(249,200,109,0.08)] flex items-center justify-center">
            <span class="text-[18px] text-[#C0A480]">🧩</span>
          </div>
        </div>

        <!-- 2. 中间内容区 (标题 + 已购徽章 + 描述 + 作者/评分/点赞) -->
        <div class="flex-1 min-w-0 flex flex-col">
          <!-- 标题与状态标签 -->
          <div class="flex items-center gap-1.5 flex-wrap">
            <h4 class="text-[14px] leading-[20px] font-medium text-[#F5F5F4] truncate max-w-[200px]">
              {{ item.title }}
            </h4>
            <span
              v-if="item.isPurchased"
              class="px-1.5 py-0.5 rounded-full bg-[rgba(34,197,94,0.10)] text-[#22C55E] text-[9px] leading-[15.3px] font-normal"
            >
              已购
            </span>
          </div>

          <!-- 描述正文 (单行截断) -->
          <p class="text-[12px] leading-[16px] text-[#A8A29E] pt-0.5 truncate">
            {{ item.description }}
          </p>

          <!-- 作者、评分与点赞元数据 -->
          <div class="flex items-center gap-2 pt-1 text-[9px] text-[#78716C] leading-[15.3px]">
            <span>{{ item.author }}</span>
            <span class="flex items-center gap-0.5">
              <span>⭐</span>
              <span>{{ item.rating }}</span>
            </span>
            <span class="flex items-center gap-0.5">
              <span>👍</span>
              <span>{{ item.likes }}</span>
            </span>
          </div>
        </div>

        <!-- 3. 右侧价格与购买按钮 (Figma 93:3270) -->
        <div class="flex-shrink-0 flex flex-col items-end gap-1.5 pl-1">
          <!-- 价格 -->
          <div
            class="text-[12px] leading-[16px] tracking-[-0.176px]"
            :class="item.isPurchased ? 'text-[#C0A480] text-[14px]' : 'text-[#F9C86D] font-bold'"
          >
            🌙 {{ item.price }}
          </div>

          <!-- 购买按钮 -->
          <button
            v-if="!item.isPurchased"
            type="button"
            @click="emit('buy', item.id)"
            class="px-2.5 py-1 rounded-[8px] bg-[rgba(249,200,109,0.08)] text-[#F9C86D] text-[10px] leading-[14px] hover:bg-[rgba(249,200,109,0.18)] active:scale-95 transition-all cursor-pointer select-none"
          >
            购买
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div
      v-else
      class="flex flex-col items-center justify-center py-16 text-center px-4"
    >
      <div class="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3">
        <span class="text-2xl">🧩</span>
      </div>
      <p class="text-sm text-[#A8A29E] font-medium">暂无匹配的 Mod 模组</p>
      <p class="text-xs text-[#78716C] mt-1">尝试切换分类或搜索其他关键词</p>
    </div>
  </div>
</template>
