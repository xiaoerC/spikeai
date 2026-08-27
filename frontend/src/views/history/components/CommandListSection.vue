<script setup lang="ts">
/**
 * 指令管理主面板组件 (Figma 81:2925 1:1 像素级高保真)
 *
 * 包含 共 X 个指令、(拖动条目可调整顺序)、+新建指令、卡片流、编辑/删除、保存排序。
 *
 * @packageDocumentation
 */

import type { CommandItem } from "@/views/history/types";
import { ChevronDown, ChevronUp, GripVertical } from "lucide-vue-next";

defineProps<{
  commandList: CommandItem[];
}>();

const emit = defineEmits<{
  (e: "create"): void;
  (e: "edit", item: CommandItem): void;
  (e: "delete", id: string): void;
  (e: "move", index: number, direction: "up" | "down"): void;
  (e: "save-order"): void;
}>();
</script>

<template>
  <div class="w-full px-4 pt-6 flex flex-col pb-6">
    <!-- 1. 顶部统计与新建按钮栏 (Figma 81:2925) -->
    <div class="w-full flex items-center justify-between pb-6">
      <!-- 左侧: 共 X 个指令 + (拖动条目可调整顺序) -->
      <div class="flex items-baseline gap-2">
        <div class="text-[14px] leading-[20px] text-[#F5F5F4]">
          共 <span class="font-bold text-[#F9C86D]">{{ commandList.length }}</span> 个指令
        </div>
        <span class="text-[12px] leading-[16px] text-[#78716C]">
          （拖动条目可调整顺序）
        </span>
      </div>

      <!-- 右侧: + 新建指令 -->
      <button
        type="button"
        @click="emit('create')"
        class="px-4 py-2 flex items-center justify-center rounded-[8px] bg-[#F9C86D] text-[16px] leading-[27.2px] font-normal text-[#0C0A09] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none shadow-md"
      >
        + 新建指令
      </button>
    </div>

    <!-- 2. 空状态 (暂无指令) -->
    <div
      v-if="commandList.length === 0"
      class="w-full flex flex-col items-center justify-center py-16 text-center"
    >
      <p class="text-[16px] text-[#78716C] leading-[27.2px] pb-6">
        暂无指令
      </p>
      <button
        type="button"
        @click="emit('create')"
        class="w-[159px] h-[51px] flex items-center justify-center rounded-[8px] bg-[#F9C86D] text-[16px] leading-[27.2px] font-normal text-[#0C0A09] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none shadow-lg"
      >
        创建第一个指令
      </button>
    </div>

    <!-- 3. 指令卡片列表 (Figma 81:2925) -->
    <div v-else class="w-full flex flex-col gap-3">
      <div
        v-for="(cmd, idx) in commandList"
        :key="cmd.id"
        class="w-full p-4 rounded-[8px] border border-[#44403C] bg-[#292524] flex flex-col shadow-sm"
      >
        <!-- 头部: 拖动图标 + 标题 + 创建时间 -->
        <div class="w-full flex items-start gap-2">
          <!-- 拖动图标 ☰ -->
          <div class="w-5 h-5 pt-0.5 flex items-center justify-center text-[#78716C] flex-shrink-0 cursor-grab">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M3.33334 5H16.6667M3.33334 10H16.6667M3.33334 15H16.6667" stroke="#78716C" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <!-- 标题与创建时间 -->
          <div class="flex flex-col flex-1">
            <h3 class="text-[16px] font-semibold text-[#F5F5F4] leading-[19.2px] tracking-[-0.32px]">
              {{ cmd.label }}
            </h3>
            <p v-if="cmd.createdAt" class="text-[12px] text-[#78716C] leading-[16px] pt-1">
              创建于 {{ cmd.createdAt }}
            </p>
          </div>

          <!-- 上下微调排序快捷钮 -->
          <div class="flex items-center gap-1">
            <button
              v-if="idx > 0"
              type="button"
              @click="emit('move', idx, 'up')"
              title="上移"
              class="p-1 rounded text-[#78716C] hover:text-[#F9C86D] hover:bg-white/5 transition-colors cursor-pointer"
            >
              <ChevronUp class="w-4 h-4" />
            </button>
            <button
              v-if="idx < commandList.length - 1"
              type="button"
              @click="emit('move', idx, 'down')"
              title="下移"
              class="p-1 rounded text-[#78716C] hover:text-[#F9C86D] hover:bg-white/5 transition-colors cursor-pointer"
            >
              <ChevronDown class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- 正文内容 (左缩进 28px) -->
        <div class="pl-7 pt-2">
          <p class="text-[14px] text-[#A8A29E] leading-[20px] line-clamp-2">
            {{ cmd.content }}
          </p>
        </div>

        <!-- 底部操作按钮: 编辑 / 删除 (左缩进 28px) -->
        <div class="pl-7 pt-3 flex items-center gap-2">
          <!-- 编辑 -->
          <button
            type="button"
            @click="emit('edit', cmd)"
            class="px-3 py-1.5 rounded-[4px] border border-[#44403C] text-[14px] text-[#F5F5F4] leading-[20px] hover:bg-white/5 active:scale-95 transition-all cursor-pointer select-none"
          >
            编辑
          </button>

          <!-- 删除 -->
          <button
            type="button"
            @click="emit('delete', cmd.id)"
            class="px-3 py-1.5 rounded-[4px] border border-[rgba(239,68,68,0.50)] text-[14px] text-[#EF4444] leading-[20px] hover:bg-[#EF4444]/10 active:scale-95 transition-all cursor-pointer select-none"
          >
            删除
          </button>
        </div>
      </div>

      <!-- 4. 底部 "保存排序" 按钮 (Figma 81:2925) -->
      <div class="w-full flex items-center justify-center pt-6">
        <button
          type="button"
          @click="emit('save-order')"
          class="px-6 py-2 rounded-[8px] border border-[#F9C86D] bg-[rgba(249,200,109,0.08)] text-[16px] leading-[27.2px] text-[#F9C86D] hover:bg-[#F9C86D]/15 active:scale-95 transition-all cursor-pointer select-none shadow-sm"
        >
          保存排序
        </button>
      </div>
    </div>
  </div>
</template>
