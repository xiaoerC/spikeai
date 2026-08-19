<script setup lang="ts">
/**
 * 官方活动卡片组件 (1:1 原型高保真)
 *
 * 包含活动标题、进行中状态胶囊、"新"角标、时间范围与手风琴折叠展开详情。
 *
 * @packageDocumentation
 */

import type { ActivityItem } from "@/views/activity/types";
import { ChevronDown } from "lucide-vue-next";

defineProps<{
  activity: ActivityItem;
  isExpanded: boolean;
}>();

const emit = defineEmits<(e: "toggle-expand", id: string) => void>();
</script>

<template>
  <div class="w-full rounded-xl border border-[rgba(168,162,158,0.30)] bg-gradient-to-br from-[#1C1917] via-[#221F1D] to-[#292524] p-4 shadow-lg flex flex-col gap-3 transition-all duration-200 hover:border-[#F9C86D]/40">
    
    <!-- 1. 卡片头部: 标题 + "新"角标 + 进行中 Badge -->
    <div class="flex items-center justify-between gap-2">
      <div class="flex items-center gap-2 flex-1">
        <!-- "新" 角标 (若有) -->
        <span
          v-if="activity.isNew"
          class="px-1.5 py-0.5 rounded bg-[#EF4444] text-white text-[10px] font-bold leading-tight shadow-sm"
        >
          新
        </span>

        <!-- 活动标题 -->
        <h3 class="text-sm font-bold text-[#F5F5F4] leading-snug">
          {{ activity.title }}
        </h3>
      </div>

      <!-- 进行中状态 Badge -->
      <div class="flex items-center gap-1 px-2 py-0.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-400 text-[11px] font-semibold flex-shrink-0">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        <span>{{ activity.statusText }}</span>
      </div>
    </div>

    <!-- 2. 活动简介摘要 / 富文本展开内容 -->
    <div class="text-xs text-[#A8A29E] leading-relaxed">
      <!-- 收起态: 显示简明摘要 -->
      <div v-if="!isExpanded" class="whitespace-pre-line line-clamp-3">
        {{ activity.summary }}
      </div>

      <!-- 展开态: 渲染富文本详情 -->
      <div
        v-else
        class="pt-2 border-t border-white/5 animate-in fade-in duration-200"
        v-html="activity.fullHtmlContent"
      />
    </div>

    <!-- 3. 底部信息行: 时间范围 + 展开/收起按钮 -->
    <div class="flex items-center justify-between pt-2 border-t border-white/5 text-[11px]">
      <!-- 日期范围 -->
      <span class="text-[#78716C] font-mono">
        {{ activity.dateRange }}
      </span>

      <!-- 展开/收起详情按钮 -->
      <button
        type="button"
        @click="emit('toggle-expand', activity.id)"
        class="flex items-center gap-1 text-[#F9C86D] hover:text-[#FFD475] font-medium transition-colors cursor-pointer select-none"
      >
        <span>{{ isExpanded ? "收起详情" : "展开详情" }}</span>
        <ChevronDown
          :class="[
            'w-3.5 h-3.5 transition-transform duration-200',
            isExpanded ? 'rotate-180' : ''
          ]"
        />
      </button>
    </div>

  </div>
</template>
