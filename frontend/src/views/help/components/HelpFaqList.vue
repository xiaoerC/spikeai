<script setup lang="ts">
/**
 * 帮助中心 FAQ 列表组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { FaqItem } from "@/views/help/types";
import { ChevronDown, HelpCircle } from "lucide-vue-next";

defineProps<{
  faqs: FaqItem[];
  expandedFaqIds: Set<string>;
}>();

const emit = defineEmits<(e: "toggle-faq", id: string) => void>();
</script>

<template>
  <div class="flex flex-col gap-3">
    <div
      v-for="faq in faqs"
      :key="faq.id"
      class="w-full rounded-xl border border-[rgba(168,162,158,0.25)] bg-[rgba(26,21,16,0.90)] p-4 flex flex-col gap-2.5 shadow-md transition-all hover:border-[#F9C86D]/40"
    >
      <!-- 问题头部行 -->
      <button
        type="button"
        @click="emit('toggle-faq', faq.id)"
        class="w-full flex items-center justify-between gap-2 text-left cursor-pointer select-none"
      >
        <div class="flex items-center gap-2 flex-1">
          <HelpCircle class="w-4 h-4 text-[#F9C86D] flex-shrink-0" />
          <h3 class="text-sm font-bold text-[#F5F5F4]">
            {{ faq.question }}
          </h3>
        </div>
        <ChevronDown
          :class="[
            'w-4 h-4 text-[#78716C] transition-transform duration-200 flex-shrink-0',
            expandedFaqIds.has(faq.id) ? 'rotate-180 text-[#F9C86D]' : ''
          ]"
        />
      </button>

      <!-- 回答展开层 -->
      <div
        v-if="expandedFaqIds.has(faq.id)"
        class="pt-2 border-t border-white/5 text-xs text-[#A8A29E] leading-relaxed animate-in fade-in duration-200"
      >
        {{ faq.answer }}
      </div>
    </div>
  </div>
</template>
