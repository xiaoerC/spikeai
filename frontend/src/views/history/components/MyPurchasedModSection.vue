<script setup lang="ts">
/**
 * 我购买的 Mod 管理主面板 (Figma 106:8718 1:1 像素级高保真)
 *
 * 包含已购 Mod 卡片列表、已激活状态徽章、极简胶囊 Switch 开关以及 28x28 垃圾桶删除操作。
 *
 * @packageDocumentation
 */

import type { PurchasedModItem } from "@/views/history/types";
import { Trash2 } from "lucide-vue-next";

defineProps<{
  purchasedModList: PurchasedModItem[];
}>();

const emit = defineEmits<{
  (e: "toggle-active", id: string): void;
  (e: "delete", id: string): void;
}>();
</script>

<template>
  <div class="w-full flex flex-col pt-5 pb-12">
    <!-- 1. 已购 Mod 卡片流列表 (Figma 106:8718) -->
    <div v-if="purchasedModList.length > 0" class="w-full flex flex-col gap-3">
      <div
        v-for="mod in purchasedModList"
        :key="mod.id"
        class="w-full p-4 rounded-[12px] border border-[#44403C] bg-[#292524] flex items-start justify-between gap-3 transition-colors hover:border-[#F9C86D]/40"
      >
        <!-- 左侧信息区 (标题 + 激活徽章 + 简介) -->
        <div class="flex-1 min-w-0 flex flex-col">
          <div class="flex items-center gap-2 flex-wrap">
            <h4
              class="text-[14px] leading-[20px] font-medium truncate max-w-[200px]"
              :class="mod.isActive ? 'text-[#F5F5F4]' : 'text-[#C0A480]'"
            >
              {{ mod.title }}
            </h4>
            <span
              v-if="mod.isActive"
              class="px-2 py-0.5 rounded-full bg-[rgba(34,197,94,0.10)] text-[#22C55E] text-[10px] leading-[17px] font-normal"
            >
              已激活
            </span>
          </div>

          <p class="text-[12px] leading-[16px] text-[#A8A29E] pt-1 line-clamp-2">
            {{ mod.description }}
          </p>
        </div>

        <!-- 右侧操作区 (极简 Switch 开关 + 28x28 垃圾桶删除) -->
        <div class="flex-shrink-0 flex items-center gap-2 pt-0.5">
          <!-- Switch 激活/关闭开关 (Figma 106:8718) -->
          <button
            type="button"
            @click="emit('toggle-active', mod.id)"
            class="relative w-10 h-6 rounded-full transition-colors cursor-pointer select-none flex items-center p-0.5"
            :class="mod.isActive ? 'bg-[rgba(34,197,94,0.25)] justify-end' : 'border border-[#44403C] bg-[#292524] justify-start'"
            :title="mod.isActive ? '关闭 Mod' : '激活 Mod'"
          >
            <div
              class="w-4 h-4 rounded-full transition-transform"
              :class="mod.isActive ? 'bg-[#22C55E]' : 'bg-[#A8A29E]'"
            ></div>
          </button>

          <!-- 删除按钮 (Figma 106:8812) -->
          <button
            type="button"
            @click="emit('delete', mod.id)"
            class="w-7 h-7 rounded-[8px] border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#A8A29E] hover:text-[#EF4444] hover:border-[#EF4444]/40 active:scale-95 transition-all cursor-pointer select-none"
            title="删除"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>

    <!-- 2. 空状态 -->
    <div
      v-else
      class="flex flex-col items-center justify-center py-20 text-center px-4"
    >
      <div class="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center mb-3">
        <span class="text-2xl">🛍️</span>
      </div>
      <p class="text-sm text-[#A8A29E] font-medium">暂无购买的 Mod</p>
      <p class="text-xs text-[#78716C] mt-1">您可以前往“广场”浏览并选购心仪的扩展模组</p>
    </div>
  </div>
</template>
