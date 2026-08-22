<script setup lang="ts">
/**
 * 个人历史记录单列列表排版组件 (1:1 原型高保真)
 *
 * 包含 40x40 封面头像、角色标题、✨ 翠绿色分支时间线、横排 5 大圆形快捷悬浮操作按钮与批量多选。
 *
 * @packageDocumentation
 */

import type { UserHistoryItem } from "@/views/history/types";
import { Check } from "lucide-vue-next";

defineProps<{
  historyList: UserHistoryItem[];
  isBatchMode: boolean;
  selectedIds: Set<string>;
}>();

const emit = defineEmits<{
  (e: "select-card", item: UserHistoryItem): void;
  (e: "toggle-select", id: string): void;
  (e: "remark", item: UserHistoryItem): void;
  (e: "update-card", item: UserHistoryItem): void;
  (e: "pin", id: string): void;
  (e: "clear", id: string): void;
  (e: "delete", id: string): void;
}>();
</script>

<template>
  <div class="flex flex-col gap-1.5 w-full px-4 pt-3">
    <div
      v-for="item in historyList"
      :key="item.id"
      class="group relative flex items-center justify-between p-[8px_12px] gap-3 rounded-[8px] border border-[#44403C]/60 bg-[rgba(26,21,16,0.60)] backdrop-blur-md transition-all duration-200 hover:border-[#F9C86D]/40"
    >
      <!-- 1. 批量多选 Checkbox -->
      <div
        v-if="isBatchMode"
        @click.stop="emit('toggle-select', item.id)"
        class="flex-shrink-0 cursor-pointer"
      >
        <div
          :class="[
            'w-4.5 h-4.5 rounded-[4px] border flex items-center justify-center transition-all',
            selectedIds.has(item.id)
              ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09]'
              : 'bg-black/50 border-white/40 text-transparent'
          ]"
        >
          <Check class="w-3 h-3 stroke-[3]" />
        </div>
      </div>

      <!-- 2. 左侧 40x40 封面头像与中间信息 (点击进入会话) -->
      <div
        @click="isBatchMode ? emit('toggle-select', item.id) : emit('select-card', item)"
        class="flex items-center gap-3 flex-1 min-w-0 cursor-pointer select-none"
      >
        <!-- 40x40 头像 -->
        <img
          :src="item.avatar"
          :alt="item.title"
          class="w-10 h-10 rounded-[4px] object-cover flex-shrink-0 bg-[#161412]"
          loading="lazy"
        />

        <!-- 中间文本区 -->
        <div class="flex flex-col min-w-0 flex-1 justify-center">
          <!-- 标题 -->
          <h3 class="text-[14px] font-semibold text-[#F5F5F4] leading-[16.8px] tracking-[0.7px] truncate">
            {{ item.title }}
          </h3>

          <!-- 次行: ✨ 翠绿色分支与时间戳 -->
          <div class="flex items-center gap-1 pt-1 overflow-hidden">
            <span class="text-[12px] text-[#22C55E] flex-shrink-0">✨</span>
            <span class="text-[12px] text-[#22C55E] truncate leading-[16px]">
              {{ item.branchName || item.title }} - {{ item.lastChatDate || '2026/08/19 13:28' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 3. 右侧横排 5 大圆形快捷操作按钮 (1:1 原型高保真) -->
      <div
        v-if="!isBatchMode"
        class="flex items-center gap-[2px] flex-shrink-0"
      >
        <!-- ① 编辑备注 (Figma 57:1234) -->
        <button
          type="button"
          @click.stop="emit('remark', item)"
          title="编辑备注"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.95)] border border-white/5 text-[#A8A29E] hover:text-[#F9C86D] hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-sm"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8.16667 1.16669H3.5C3.19058 1.16669 2.89383 1.2896 2.67504 1.5084C2.45625 1.72719 2.33333 2.02393 2.33333 2.33335V11.6667C2.33333 11.9761 2.45625 12.2729 2.67504 12.4916C2.89383 12.7104 3.19058 12.8334 3.5 12.8334H10.5C10.8094 12.8334 11.1062 12.7104 11.325 12.4916C11.5437 12.2729 11.6667 11.9761 11.6667 11.6667V4.66669L8.16667 1.16669Z" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8.16666 1.16669V4.66669H11.6667" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 7.58331H4.66667" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 9.91669H4.66667" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- ② 更新角色卡 (Figma 57:1240) -->
        <button
          type="button"
          @click.stop="emit('update-card', item)"
          title="更新角色卡"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.95)] border border-white/5 text-[#A8A29E] hover:text-[#F9C86D] hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-sm"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12.5417 1.16665V4.66665H9.04166M1.45833 12.8333V9.33332H4.95833M1.16666 6.70832C1.22191 5.4317 1.69482 4.20853 2.51272 3.22677C3.33062 2.245 4.44826 1.55896 5.69391 1.27405C6.93956 0.989139 8.2443 1.12113 9.40766 1.64973C10.571 2.17834 11.5286 3.07431 12.1333 4.19999M12.8333 7.29165C12.7666 8.5636 12.2853 9.77873 11.4631 10.7515C10.6409 11.7243 9.52291 12.4012 8.27986 12.6789C7.0368 12.9566 5.73702 12.8198 4.579 12.2894C3.42099 11.7591 2.46838 10.8643 1.86666 9.74165" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- ③ 置顶 (Figma 57:1243) -->
        <button
          type="button"
          @click.stop="emit('pin', item.id)"
          title="置顶"
          :class="[
            'w-7 h-7 rounded-full border transition-all cursor-pointer shadow-sm flex items-center justify-center hover:scale-110 active:scale-95',
            item.isPinned
              ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09]'
              : 'bg-[rgba(26,23,20,0.95)] border-white/5 text-[#A8A29E] hover:text-[#F9C86D]'
          ]"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1.75 3.5H12.25" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M7 10.5V4.66669" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.66666 7.00002L7 4.66669L9.33333 7.00002" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- ④ 清空历史 (Figma 57:1248) -->
        <button
          type="button"
          @click.stop="emit('clear', item.id)"
          title="清空历史"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.95)] border border-white/5 text-[#A8A29E] hover:text-amber-400 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-sm"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1.75 3.5H12.25" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M11.0833 3.5V11.6667C11.0833 12.25 10.5 12.8333 9.91667 12.8333H4.08334C3.50001 12.8333 2.91667 12.25 2.91667 11.6667V3.5" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.66667 3.50002V2.33335C4.66667 1.75002 5.25001 1.16669 5.83334 1.16669H8.16667C8.75 1.16669 9.33334 1.75002 9.33334 2.33335V3.50002" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.83333 6.41669V9.91669" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8.16667 6.41669V9.91669" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- ⑤ 删除 (Figma 57:1255) -->
        <button
          type="button"
          @click.stop="emit('delete', item.id)"
          title="删除"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.95)] border border-white/5 text-[#A8A29E] hover:text-red-400 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-sm"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1.75 3.5H2.91667H12.25" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M11.0833 3.50002V11.6667C11.0833 11.9761 10.9604 12.2729 10.7416 12.4916C10.5228 12.7104 10.2261 12.8334 9.91667 12.8334H4.08334C3.77392 12.8334 3.47717 12.7104 3.25838 12.4916C3.03959 12.2729 2.91667 11.9761 2.91667 11.6667V3.50002M4.66667 3.50002V2.33335C4.66667 2.02393 4.78959 1.72719 5.00838 1.5084C5.22717 1.2896 5.52392 1.16669 5.83334 1.16669H8.16667C8.47609 1.16669 8.77284 1.2896 8.99163 1.5084C9.21042 1.72719 9.33334 2.02393 9.33334 2.33335V3.50002" stroke="currentColor" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>
