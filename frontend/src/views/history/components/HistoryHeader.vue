<script setup lang="ts">
/**
 * 历史记录页面顶部 Header 导航与周次筛选胶囊 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { WeekOption } from "@/views/history/types";
import { ArrowLeft, Calendar, ChevronDown, Trash2 } from "lucide-vue-next";
import { useRouter } from "vue-router";

defineProps<{
  currentWeekLabel: string;
  selectedWeek: string;
  weekOptions: WeekOption[];
  isWeekSelectorOpen: boolean;
}>();

const emit = defineEmits<{
  (e: "toggle-week"): void;
  (e: "select-week", id: string): void;
  (e: "clear-history"): void;
}>();

const router = useRouter();

function handleBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
}
</script>

<template>
  <header class="sticky top-0 z-40 w-full max-w-[440px] mx-auto px-4 py-3 flex items-center justify-between bg-[rgba(26,21,16,0.92)] backdrop-blur-md border-b border-white/5 shadow-md relative">
    <!-- 左侧返回按钮 -->
    <button
      type="button"
      @click="handleBack"
      class="p-1 rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/10 active:scale-95 transition-all cursor-pointer"
    >
      <ArrowLeft class="w-5 h-5" />
    </button>

    <!-- 中间：“选择周次”黑金下拉胶囊 -->
    <div class="relative">
      <button
        type="button"
        @click="emit('toggle-week')"
        class="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[rgba(249,200,109,0.35)] bg-gradient-to-r from-[rgba(249,200,109,0.15)] to-[rgba(249,200,109,0.05)] text-[#F9C86D] hover:border-[#F9C86D]/60 active:scale-95 transition-all cursor-pointer shadow-sm select-none"
      >
        <Calendar class="w-3.5 h-3.5 text-[#F9C86D]" />
        <span class="text-xs font-semibold tracking-wide">
          {{ currentWeekLabel }}
        </span>
        <ChevronDown
          :class="[
            'w-3.5 h-3.5 text-[#F9C86D] transition-transform duration-200',
            isWeekSelectorOpen ? 'rotate-180' : ''
          ]"
        />
      </button>

      <!-- 周次下拉浮层 -->
      <div
        v-if="isWeekSelectorOpen"
        class="absolute left-1/2 -translate-x-1/2 top-full mt-2 w-48 rounded-xl border border-[rgba(83,71,65,0.60)] bg-[#1F1B17] shadow-2xl p-1.5 flex flex-col gap-1 z-50 animate-in fade-in zoom-in-95 duration-150"
      >
        <button
          v-for="opt in weekOptions"
          :key="opt.id || opt.value"
          type="button"
          @click="emit('select-week', opt.id || opt.value || '')"
          :class="[
            'w-full text-left px-3 py-2 rounded-lg text-xs font-medium transition-colors cursor-pointer',
            selectedWeek === (opt.id || opt.value)
              ? 'bg-[#F9C86D]/20 text-[#F9C86D] font-bold'
              : 'text-[#A8A29E] hover:bg-white/5 hover:text-white'
          ]"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- 右侧清空/操作按钮 -->
    <button
      type="button"
      @click="emit('clear-history')"
      class="p-1 rounded-lg text-[#78716C] hover:text-[#EF4444] hover:bg-white/5 transition-colors cursor-pointer"
      title="清空历史记录"
    >
      <Trash2 class="w-4 h-4" />
    </button>
  </header>
</template>
