<script setup lang="ts">
/**
 * 公告详情弹窗组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { AppModal } from "@/components/common";
import type { NoticeItem } from "@/views/notice/types";
import { Megaphone, X } from "lucide-vue-next";

defineProps<{
  open: boolean;
  notice: NoticeItem | null;
}>();

const emit = defineEmits<(e: "update:open", val: boolean) => void>();
</script>

<template>
  <AppModal
    :open="open"
    @update:open="emit('update:open', $event)"
    size="md"
  >
    <div v-if="notice" class="p-5 flex flex-col gap-4 text-left">
      <!-- 头部: 类型 + 标题 + 关闭 -->
      <div class="flex items-start justify-between gap-3 border-b border-white/10 pb-3">
        <div class="flex flex-col gap-1.5 flex-1">
          <div class="flex items-center gap-2">
            <span
              :class="[
                'px-2 py-0.5 rounded text-[10px] font-bold',
                notice.type === 'update'
                  ? 'bg-blue-500/15 text-blue-400 border border-blue-500/30'
                  : notice.type === 'activity'
                    ? 'bg-amber-500/15 text-[#F9C86D] border border-amber-500/30'
                    : 'bg-purple-500/15 text-purple-400 border border-purple-500/30'
              ]"
            >
              {{ notice.typeText }}
            </span>
            <span class="text-xs text-[#78716C] font-mono">
              {{ notice.publishedAt }}
            </span>
          </div>

          <h3 class="text-base font-bold text-[#F5F5F4] leading-snug">
            {{ notice.title }}
          </h3>
        </div>

        <button
          type="button"
          @click="emit('update:open', false)"
          class="p-1 rounded-lg text-[#78716C] hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
        >
          <X class="w-5 h-5" />
        </button>
      </div>

      <!-- 公告正文 -->
      <div class="text-xs text-[#D6D3D1] leading-relaxed whitespace-pre-line max-h-96 overflow-y-auto pr-1">
        {{ notice.content.trim() }}
      </div>

      <!-- 底部官方落款 -->
      <div class="pt-3 border-t border-white/5 flex items-center justify-between text-[11px] text-[#78716C]">
        <div class="flex items-center gap-1 text-[#F9C86D]">
          <Megaphone class="w-3.5 h-3.5" />
          <span>Naro · 叙梦官方运营组</span>
        </div>
        <button
          type="button"
          @click="emit('update:open', false)"
          class="px-4 py-1.5 rounded-lg bg-[#292524] text-white hover:bg-[#383330] font-medium transition-colors cursor-pointer"
        >
          我知道了
        </button>
      </div>
    </div>
  </AppModal>
</template>
