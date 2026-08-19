<script setup lang="ts">
/**
 * 公告列表单项组件 (1:1 原型高保真)
 *
 * 包含更新/活动/系统类型 Badge、公告标题、发布时间与点击查看交互。
 *
 * @packageDocumentation
 */

import type { NoticeItem } from "@/views/notice/types";
import { ChevronRight } from "lucide-vue-next";

defineProps<{
  notice: NoticeItem;
}>();

const emit = defineEmits<(e: "select", notice: NoticeItem) => void>();
</script>

<template>
  <div
    @click="emit('select', notice)"
    class="w-full flex items-center justify-between px-3.5 py-3 rounded-xl bg-[rgba(26,21,16,0.85)] border border-white/5 hover:border-[#F9C86D]/30 transition-all cursor-pointer group shadow-sm active:scale-[0.99]"
  >
    <!-- 左侧: 类型 Badge + 标题 -->
    <div class="flex items-center gap-2.5 flex-1 min-w-0 pr-2">
      <!-- 类型 Badge -->
      <span
        :class="[
          'px-2 py-0.5 rounded text-[11px] font-bold flex-shrink-0 leading-normal',
          notice.type === 'update'
            ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30'
            : notice.type === 'activity'
              ? 'bg-amber-500/15 text-[#F9C86D] border border-amber-500/30'
              : 'bg-purple-500/15 text-purple-400 border border-purple-500/30'
        ]"
      >
        {{ notice.typeText }}
      </span>

      <!-- 标题 -->
      <span class="text-xs font-semibold text-[#F5F5F4] group-hover:text-[#F9C86D] transition-colors truncate">
        {{ notice.title }}
      </span>
    </div>

    <!-- 右侧: 发布时间 + 右箭头 -->
    <div class="flex items-center gap-1.5 flex-shrink-0 text-[11px] text-[#78716C] font-mono">
      <span>{{ notice.publishedAt }}</span>
      <ChevronRight class="w-3.5 h-3.5 text-[#57534E] group-hover:text-[#F9C86D] transition-colors" />
    </div>
  </div>
</template>
