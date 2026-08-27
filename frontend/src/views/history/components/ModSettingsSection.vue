<script setup lang="ts">
/**
 * Mod 设置与优先级排序主面板 (Figma 111:13235 1:1 像素级高保真)
 *
 * 包含注入统计蓝色横幅、警告黄色横幅、优先级规则说明、已激活 Mod 优先级卡片矩阵 (抓手+最高优先级徽章+上移/下移+停用)。
 *
 * @packageDocumentation
 */

import type { PurchasedModItem } from "@/views/history/types";

defineProps<{
  activeModsList: PurchasedModItem[];
}>();

const emit = defineEmits<{
  (e: "move", index: number, direction: "up" | "down"): void;
  (e: "deactivate", id: string): void;
}>();
</script>

<template>
  <div class="w-full flex flex-col pt-5 pb-12">
    <!-- 1. 蓝色注入统计横幅 (Figma 111:13235) -->
    <div class="w-full p-3 rounded-[8px] bg-[rgba(59,130,246,0.10)] flex items-start gap-2">
      <span class="text-sm text-[#3B82F6] flex-shrink-0 pt-0.5">📊</span>
      <p class="text-[12px] leading-[16px] text-[#3B82F6]">
        已激活 <span class="font-bold">{{ activeModsList.length }}</span> 个 Mod，共注入：世界书 2 条（3,913字）、系统提示 2 条（1,252字）
      </p>
    </div>

    <!-- 2. 黄色警告横幅 (Figma 111:13235) -->
    <div class="w-full p-3 rounded-[8px] bg-[rgba(249,200,109,0.08)] flex items-start gap-2 mt-4">
      <span class="text-sm text-[#F9C86D] flex-shrink-0 pt-0.5">⚠️</span>
      <p class="text-[12px] leading-[16px] text-[#F9C86D]">
        建议开启少量使用的 mod，太多 mod 会导致输出变多，AI 变笨并且不回复的情况
      </p>
    </div>

    <!-- 3. 排序规则说明文案 (Figma 111:13235) -->
    <p class="text-[12px] leading-[16px] text-[#A8A29E] pt-4 pb-2">
      列表下方的 Mod 优先级更高，其内容会排在 Prompt 最前面。拖动调整顺序。
    </p>

    <!-- 4. 已激活 Mod 优先级排序矩阵 (Figma 111:13235) -->
    <div v-if="activeModsList.length > 0" class="w-full flex flex-col gap-3 pt-2">
      <div
        v-for="(mod, idx) in activeModsList"
        :key="mod.id"
        class="w-full p-3 rounded-[12px] flex items-center gap-3"
      >
        <!-- ① 左侧 6 点抓手图标 (Figma 111:13333) -->
        <div class="p-1 opacity-50 flex-shrink-0">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="6" cy="4" r="1.33" fill="#A8A29E" />
            <circle cx="10" cy="4" r="1.33" fill="#A8A29E" />
            <circle cx="6" cy="8" r="1.33" fill="#A8A29E" />
            <circle cx="10" cy="8" r="1.33" fill="#A8A29E" />
            <circle cx="6" cy="12" r="1.33" fill="#A8A29E" />
            <circle cx="10" cy="12" r="1.33" fill="#A8A29E" />
          </svg>
        </div>

        <!-- ② 中间 Mod 信息卡片 -->
        <div class="flex-1 min-w-0 p-3 rounded-[8px] border border-[#44403C] bg-[#292524] flex flex-col">
          <div class="flex items-center gap-2 flex-wrap">
            <h4
              class="truncate max-w-[170px]"
              :class="idx === activeModsList.length - 1 ? 'text-[14px] font-medium text-[#F5F5F4]' : 'text-[16px] font-normal text-[#C0A480]'"
            >
              {{ mod.title }}
            </h4>
            <!-- 最高优先级徽章 (最底部一项自动展示) (Figma 111:13414) -->
            <span
              v-if="idx === activeModsList.length - 1"
              class="px-1.5 py-0.5 rounded-full bg-[rgba(249,200,109,0.15)] text-[#F9C86D] text-[9px] leading-[15px] font-normal"
            >
              最高优先级
            </span>
          </div>

          <p class="text-[12px] leading-[16px] text-[#A8A29E] pt-1 truncate">
            {{ mod.description }}
          </p>
        </div>

        <!-- ③ 右侧 ↑ / ↓ 排序控制组 (Figma 111:13356) -->
        <div class="flex flex-col gap-1 flex-shrink-0">
          <!-- 上移 ↑ -->
          <button
            type="button"
            @click="emit('move', idx, 'up')"
            :disabled="idx === 0"
            class="w-7 h-7 rounded-[4px] border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#A8A29E] text-[16px] transition-all select-none"
            :class="idx === 0 ? 'opacity-30 cursor-not-allowed' : 'hover:text-[#F5F5F4] active:scale-95 cursor-pointer'"
            title="上移（降低优先级）"
          >
            ↑
          </button>

          <!-- 下移 ↓ -->
          <button
            type="button"
            @click="emit('move', idx, 'down')"
            :disabled="idx === activeModsList.length - 1"
            class="w-7 h-7 rounded-[4px] border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#A8A29E] text-[16px] transition-all select-none"
            :class="idx === activeModsList.length - 1 ? 'opacity-30 cursor-not-allowed' : 'hover:text-[#F5F5F4] active:scale-95 cursor-pointer'"
            title="下移（提高优先级）"
          >
            ↓
          </button>
        </div>

        <!-- ④ 红色停用 ✕ 按钮 (Figma 111:13356) -->
        <button
          type="button"
          @click="emit('deactivate', mod.id)"
          class="w-7 h-7 rounded-[4px] border border-[#44403C] bg-[#292524] flex items-center justify-center opacity-50 hover:opacity-100 hover:border-[#EF4444]/40 active:scale-95 transition-all cursor-pointer select-none flex-shrink-0"
          title="停用此 Mod"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M1 1L11 11M11 1L1 11" stroke="#EF4444" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </div>

    <!-- 5. 空状态 (未激活任何 Mod) -->
    <div
      v-else
      class="w-full py-16 rounded-[12px] border border-[#44403C] bg-[#292524] flex flex-col items-center justify-center text-center mt-3 px-4"
    >
      <div class="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-3">
        <span class="text-xl">⚙️</span>
      </div>
      <p class="text-[14px] leading-[20px] text-[#A8A29E]">当前未激活任何 Mod</p>
      <p class="text-[12px] text-[#78716C] mt-1">请前往「我购买的」或「广场」激活模组后在此配置优先级</p>
    </div>
  </div>
</template>
