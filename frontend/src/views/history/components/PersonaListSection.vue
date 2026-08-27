<script setup lang="ts">
/**
 * 人设管理主面板组件 (1:1 原型像素级高保真)
 *
 * 包含 已使用 X/10 统计、+新建人设、暂无人设空状态与人设列表卡片。
 *
 * @packageDocumentation
 */

import type { PersonaItem } from "@/views/history/types";
import { Edit2, Star, Trash2 } from "lucide-vue-next";

defineProps<{
  personaList: PersonaItem[];
}>();

const emit = defineEmits<{
  (e: "create"): void;
  (e: "edit", item: PersonaItem): void;
  (e: "delete", id: string): void;
  (e: "set-default", id: string): void;
}>();
</script>

<template>
  <div class="w-full px-4 pt-6 flex flex-col">
    <!-- 1. 顶部统计与新建按钮栏 -->
    <div class="w-full flex items-center justify-between pb-4">
      <!-- 左侧: 已使用 X/10 -->
      <div class="text-[14px] leading-[20px] text-[#F5F5F4]">
        已使用 <span class="font-bold text-[#F9C86D]">{{ personaList.length }}</span>/10
      </div>

      <!-- 右侧: + 新建人设 (Figma 原型高保真) -->
      <button
        type="button"
        @click="emit('create')"
        class="px-4 py-2 flex items-center justify-center rounded-[8px] bg-[#F9C86D] text-[16px] leading-[27.2px] font-normal text-[#0C0A09] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none shadow-md"
      >
        + 新建人设
      </button>
    </div>

    <!-- 2. 空状态 (暂无人设) -->
    <div
      v-if="personaList.length === 0"
      class="w-full flex flex-col items-center justify-center py-16 text-center"
    >
      <p class="text-[16px] text-[#78716C] leading-[27.2px] pb-6">
        暂无人设
      </p>

      <button
        type="button"
        @click="emit('create')"
        class="w-[159px] h-[51px] flex items-center justify-center rounded-[8px] bg-[#F9C86D] text-[16px] leading-[27.2px] font-normal text-[#0C0A09] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none shadow-lg"
      >
        创建第一个人设
      </button>
    </div>

    <!-- 3. 已有人设列表矩阵 -->
    <div v-else class="w-full flex flex-col gap-3 pt-2">
      <div
        v-for="persona in personaList"
        :key="persona.id"
        class="p-4 rounded-[10px] border border-[#44403C] bg-[rgba(26,21,16,0.60)] backdrop-blur-md flex flex-col gap-2 relative group hover:border-[#F9C86D]/40 transition-colors"
      >
        <!-- 头部: 名称 + 默认标记 + 操作按钮 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <h4 class="text-[15px] font-bold text-[#F5F5F4]">
              {{ persona.name }}
            </h4>
            <span
              v-if="persona.displayName"
              class="text-[12px] text-[#A8A29E] bg-white/5 px-2 py-0.5 rounded"
            >
              显示为: {{ persona.displayName }}
            </span>
            <span
              v-if="persona.isDefault"
              class="text-[11px] font-medium text-[#F9C86D] bg-[#F9C86D]/15 border border-[#F9C86D]/40 px-1.5 py-0.2 rounded"
            >
              ★ 默认
            </span>
          </div>

          <div class="flex items-center gap-1.5">
            <!-- 设为默认 -->
            <button
              v-if="!persona.isDefault"
              type="button"
              @click="emit('set-default', persona.id)"
              title="设为默认人设"
              class="p-1.5 rounded-md text-[#78716C] hover:text-[#F9C86D] hover:bg-white/5 transition-colors cursor-pointer"
            >
              <Star class="w-4 h-4" />
            </button>

            <!-- 编辑 -->
            <button
              type="button"
              @click="emit('edit', persona)"
              title="编辑人设"
              class="p-1.5 rounded-md text-[#78716C] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
            >
              <Edit2 class="w-4 h-4" />
            </button>

            <!-- 删除 -->
            <button
              type="button"
              @click="emit('delete', persona.id)"
              title="删除人设"
              class="p-1.5 rounded-md text-[#78716C] hover:text-[#EF4444] hover:bg-white/5 transition-colors cursor-pointer"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- 正文简介 -->
        <p class="text-[13px] text-[#A8A29E] leading-[18px] line-clamp-3 bg-black/20 p-2.5 rounded-[6px] border border-white/5">
          {{ persona.content }}
        </p>
      </div>
    </div>
  </div>
</template>
