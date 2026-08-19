<script setup lang="ts">
/**
 * 历史卡片项组件 (1:1 原图与 Figma 像素级高保真)
 *
 * @packageDocumentation
 */

import type { HistoryCardItem } from "@/views/history/types";

const props = defineProps<{
  /** 历史卡片数据 */
  card: HistoryCardItem;
  /** 是否处于批量管理模式 */
  isBatchMode?: boolean;
  /** 批量管理下是否被选中 */
  isSelected?: boolean;
}>();

const emit = defineEmits<{
  (e: "select", card: HistoryCardItem): void;
  (e: "toggle-check", card: HistoryCardItem): void;
  (e: "edit-note", card: HistoryCardItem): void;
  (e: "refresh", card: HistoryCardItem): void;
  (e: "toggle-pin", card: HistoryCardItem): void;
  (e: "clear-history", card: HistoryCardItem): void;
  (e: "delete-card", card: HistoryCardItem): void;
}>();

/**
 * 卡片主体点击事件
 */
function handleCardClick(): void {
  if (props.isBatchMode) {
    emit("toggle-check", props.card);
  } else {
    emit("select", props.card);
  }
}
</script>

<template>
  <div
    @click="handleCardClick"
    :class="[
      'group relative flex flex-col w-full rounded-2xl border overflow-hidden transition-all duration-200 cursor-pointer select-none bg-[rgba(26,25,21,0.70)] shadow-lg hover:border-[rgba(249,200,109,0.30)] active:scale-[0.98]',
      isSelected
        ? 'border-[#F9C86D] ring-2 ring-[#F9C86D]/40'
        : 'border-[rgba(83,71,65,0.25)]'
    ]"
  >
    <!-- 1. 封面图容器 (aspect-[4/5] 竖版大图) -->
    <div class="relative w-full aspect-[3/4] bg-[#161412] overflow-hidden">
      <img
        :src="card.avatarUrl"
        :alt="card.title"
        class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        loading="eager"
      />

      <!-- 2. 批量管理勾选框 (左上角) -->
      <div
        v-if="isBatchMode"
        class="absolute top-2 left-2 z-20 w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all bg-[rgba(26,23,20,0.95)]"
        :class="isSelected ? 'border-[#F9C86D] bg-[#F9C86D] text-black' : 'border-white/40'"
      >
        <svg v-if="isSelected" width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M2.5 6L5 8.5L9.5 3.5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- 3. 顶部 5 颗暗黑磨砂微操作按钮组 (清晰悬浮立绘上方) -->
      <div
        v-if="!isBatchMode"
        class="absolute top-2 right-2 z-10 flex items-center gap-1"
      >
        <!-- 按钮 1: 编辑备注 -->
        <button
          type="button"
          @click.stop="emit('edit-note', card)"
          class="w-7 h-7 rounded-full bg-[rgba(20,18,16,0.88)] border border-white/10 flex items-center justify-center backdrop-blur-md shadow-md text-[#E7E5E4] hover:text-[#F9C86D] hover:bg-black active:scale-90 transition-all cursor-pointer"
          title="编辑备注"
        >
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <path d="M9.33334 1.33334H4.00001C3.64638 1.33334 3.30724 1.47382 3.0572 1.72387C2.80715 1.97392 2.66667 2.31305 2.66667 2.66668V13.3333C2.66667 13.687 2.80715 14.0261 3.0572 14.2762C3.30724 14.5262 3.64638 14.6667 4.00001 14.6667H12C12.3536 14.6667 12.6928 14.5262 12.9428 14.2762C13.1929 14.0261 13.3333 13.687 13.3333 13.3333V5.33334L9.33334 1.33334Z" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 1.33334V5.33334H13.3333" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.6667 8.66666H5.33333" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.6667 11.3333H5.33333" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 按钮 2: 更新角色卡 -->
        <button
          type="button"
          @click.stop="emit('refresh', card)"
          class="w-7 h-7 rounded-full bg-[rgba(20,18,16,0.88)] border border-white/10 flex items-center justify-center backdrop-blur-md shadow-md text-[#E7E5E4] hover:text-[#F9C86D] hover:bg-black active:scale-90 transition-all cursor-pointer"
          title="更新角色卡"
        >
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <path d="M14.3333 1.33333V5.33333H10.3333M1.66666 14.6667V10.6667H5.66666M1.33333 7.66666C1.39647 6.20767 1.93693 4.80976 2.87168 3.68774C3.80642 2.56573 5.08372 1.78168 6.50732 1.45607C7.93092 1.13046 9.42206 1.2813 10.7516 1.88542C12.0812 2.48954 13.1756 3.51351 13.8667 4.8M14.6667 8.33333C14.5904 9.78698 14.0404 11.1757 13.1007 12.2874C12.161 13.3992 10.8833 14.1728 9.46269 14.4902C8.04206 14.8075 6.55659 14.6512 5.23314 14.0451C3.9097 13.4389 2.821 12.4163 2.13333 11.1333" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 按钮 3: 置顶 -->
        <button
          type="button"
          @click.stop="emit('toggle-pin', card)"
          :class="[
            'w-7 h-7 rounded-full flex items-center justify-center backdrop-blur-md shadow-md active:scale-90 transition-all cursor-pointer border border-white/10',
            card.isPinned
              ? 'bg-[#5B331A] text-[#F99B4B] border-[#F99B4B]/30'
              : 'bg-[rgba(20,18,16,0.88)] text-[#E7E5E4] hover:text-[#F9C86D] hover:bg-black'
          ]"
          :title="card.isPinned ? '取消置顶' : '置顶'"
        >
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <path d="M2 4H14" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 12V5.33334" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.33334 8.00001L8 5.33334L10.6667 8.00001" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 按钮 4: 清空历史 -->
        <button
          type="button"
          @click.stop="emit('clear-history', card)"
          class="w-7 h-7 rounded-full bg-[rgba(20,18,16,0.88)] border border-white/10 flex items-center justify-center backdrop-blur-md shadow-md text-[#E7E5E4] hover:text-amber-300 hover:bg-black active:scale-90 transition-all cursor-pointer"
          title="清空历史对话"
        >
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <path d="M2 4H14" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.6667 4V13.3333C12.6667 14 12 14.6667 11.3333 14.6667H4.66667C4 14.6667 3.33334 14 3.33334 13.3333V4" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.33334 4.00001V2.66668C5.33334 2.00001 6 1.33334 6.66667 1.33334H9.33334C10 1.33334 10.6667 2.00001 10.6667 2.66668V4.00001" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6.66667 7.33334V11.3333" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 7.33334V11.3333" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 按钮 5: 删除卡片 -->
        <button
          type="button"
          @click.stop="emit('delete-card', card)"
          class="w-7 h-7 rounded-full bg-[rgba(20,18,16,0.88)] border border-white/10 flex items-center justify-center backdrop-blur-md shadow-md text-[#E7E5E4] hover:text-red-400 hover:bg-black active:scale-90 transition-all cursor-pointer"
          title="删除卡片"
        >
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
            <path d="M2 4H3.33333H14" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.6667 4.00001V13.3333C12.6667 13.687 12.5262 14.0261 12.2761 14.2762C12.0261 14.5262 11.687 14.6667 11.3333 14.6667H4.66667C4.31304 14.6667 3.9739 14.5262 3.72386 14.2762C3.47381 14.0261 3.33333 13.687 3.33333 13.3333V4.00001M5.33333 4.00001V2.66668C5.33333 2.31305 5.47381 1.97392 5.72386 1.72387C5.97391 1.47382 6.31304 1.33334 6.66667 1.33334H9.33333C9.68695 1.33334 10.0261 1.47382 10.2761 1.72387C10.5262 1.97392 10.6667 2.31305 10.6667 2.66668V4.00001" stroke="currentColor" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 4. 底部角色信息区 (1:1 纯标题) -->
    <div class="px-3 py-2.5 flex items-center min-h-[42px] bg-[rgba(22,20,17,0.95)]">
      <h2 class="text-[14px] font-semibold text-[#F5F5F4] tracking-[0.5px] leading-tight truncate">
        {{ card.title }}
      </h2>
    </div>
  </div>
</template>
