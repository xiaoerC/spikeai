<script setup lang="ts">
/**
 * Mod 合集全览与预览模态弹窗
 *
 * 包含合集标题、作者/创建时间、描述、包含的全部 Mod 列表及一键启用/应用合集功能。
 *
 * @packageDocumentation
 */

import type { ModCollectionItem } from "@/views/history/types";
import { Check, X } from "lucide-vue-next";

defineProps<{
  open: boolean;
  collection: ModCollectionItem | null;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "apply", coll: ModCollectionItem): void;
}>();

function handleClose() {
  emit("update:open", false);
}
</script>

<template>
  <div
    v-if="open && collection"
    class="fixed inset-0 z-50 bg-black/75 flex items-center justify-center p-4 overflow-y-auto"
  >
    <div class="w-full max-w-[420px] max-h-[85vh] rounded-[12px] border border-[#44403C] bg-[#292524] flex flex-col overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
      <!-- 头部 -->
      <div class="flex items-start justify-between p-5 border-b border-[#44403C]">
        <div class="flex flex-col">
          <h3 class="text-[16px] leading-[20px] font-semibold text-[#F5F5F4]">
            合集预览 · {{ collection.title }}
          </h3>
          <p class="text-[12px] leading-[16px] text-[#A8A29E] pt-1">
            {{ collection.author ? `${collection.author} · ` : '' }}共包含 {{ collection.mods?.length || 0 }} 个模组
          </p>
        </div>

        <button
          type="button"
          @click="handleClose"
          class="p-1 rounded-[4px] text-[#78716C] hover:text-[#F5F5F4] transition-colors cursor-pointer select-none"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- 内容区 -->
      <div class="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
        <!-- 简介 -->
        <div v-if="collection.description" class="p-3 rounded-[8px] bg-[#1A1714] border border-[#44403C]">
          <p class="text-[13px] leading-[18px] text-[#A8A29E]">
            {{ collection.description }}
          </p>
        </div>

        <!-- 统计明细 -->
        <div class="text-[11px] text-[#F9C86D]/80 bg-[rgba(249,200,109,0.08)] p-2.5 rounded-[6px]">
          {{ collection.statsText }}
        </div>

        <!-- Mod 明细列表 -->
        <div class="flex flex-col gap-2">
          <div class="text-[12px] text-[#A8A29E] font-medium">包含 Mod 明细：</div>
          <div
            v-for="(mod, idx) in collection.mods"
            :key="mod.id"
            class="p-3 rounded-[8px] border border-[#44403C] bg-[#1A1714] flex flex-col gap-1"
          >
            <div class="flex items-center gap-2">
              <span class="text-[11px] text-[#F9C86D]">#{{ idx + 1 }}</span>
              <span class="text-[13px] font-medium text-[#F5F5F4]">{{ mod.title }}</span>
            </div>
            <p class="text-[11px] text-[#78716C] leading-[15px]">
              {{ mod.description }}
            </p>
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="flex items-center justify-end gap-2 p-4 border-t border-[#44403C] bg-[#1A1714]">
        <button
          type="button"
          @click="handleClose"
          class="px-4 py-2 rounded-[8px] border border-[#44403C] bg-[#292524] text-[13px] text-[#A8A29E] hover:text-[#F5F5F4] cursor-pointer select-none"
        >
          关闭
        </button>

        <button
          type="button"
          @click="emit('apply', collection); handleClose()"
          class="px-4 py-2 rounded-[8px] bg-[rgba(249,200,109,0.15)] border border-[rgba(249,200,109,0.30)] text-[#F9C86D] text-[13px] font-medium hover:bg-[rgba(249,200,109,0.25)] active:scale-95 transition-all cursor-pointer select-none flex items-center gap-1.5"
        >
          <Check class="w-3.5 h-3.5" />
          <span>应用此合集全部 Mod</span>
        </button>
      </div>
    </div>
  </div>
</template>
