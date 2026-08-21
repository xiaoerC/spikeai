<script setup lang="ts">
/**
 * 个人历史记录 2 列卡片流组件 (1:1 原型高保真)
 *
 * 包含卡片封面、标题、5 大圆形快捷悬浮操作按钮与批量选择多选框。
 *
 * @packageDocumentation
 */

import type { UserHistoryItem } from "@/views/history/types";
import { Check, Edit3, Pin, RefreshCw, RotateCcw, Trash2 } from "lucide-vue-next";

defineProps<{
  historyList: UserHistoryItem[];
  isBatchMode: boolean;
  selectedIds: Set<string>;
}>();

const emit = defineEmits<{
  (e: "select-card", item: UserHistoryItem): void;
  (e: "toggle-select", id: string): void;
  (e: "remark", item: UserHistoryItem): void;
  (e: "update-card", item: UserHistoryItem): void;
  (e: "pin", id: string): void;
  (e: "clear", id: string): void;
  (e: "delete", id: string): void;
}>();
</script>

<template>
  <div class="grid grid-cols-2 gap-3 w-full">
    <div
      v-for="item in historyList"
      :key="item.id"
      class="group relative flex flex-col rounded-xl border border-[rgba(83,71,65,0.30)] bg-[rgba(26,25,21,0.70)] backdrop-blur-xl overflow-hidden shadow-lg transition-all duration-200 hover:border-[#F9C86D]/40"
    >
      <!-- 1. 卡片主体 (点击进入对话) -->
      <div
        @click="isBatchMode ? emit('toggle-select', item.id) : emit('select-card', item)"
        class="flex flex-col cursor-pointer select-none"
      >
        <!-- 封面图容器 -->
        <div class="relative w-full aspect-[4/5] overflow-hidden bg-[#161412]">
          <img
            :src="item.avatar"
            :alt="item.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
          <!-- 渐变阴影底衬 -->
          <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/10 to-transparent" />
        </div>

        <!-- 底部标题栏 -->
        <div class="p-2.5 flex flex-col">
          <h3 class="text-xs font-bold text-[#F5F5F4] truncate leading-tight">
            {{ item.title }}
          </h3>
          <span v-if="item.remark" class="text-[10px] text-[#F9C86D] truncate mt-0.5">
            📝 {{ item.remark }}
          </span>
        </div>
      </div>

      <!-- 2. 卡片右上角 5 大圆形快捷悬浮操作按钮 -->
      <div
        v-if="!isBatchMode"
        class="absolute top-1.5 right-1.5 flex items-center gap-1 z-20"
      >
        <!-- ① 编辑备注 -->
        <button
          type="button"
          @click.stop="emit('remark', item)"
          title="编辑备注"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.92)] border border-white/10 text-[#A8A29E] hover:text-[#F9C86D] hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <Edit3 class="w-3.5 h-3.5" />
        </button>

        <!-- ② 更新角色卡 -->
        <button
          type="button"
          @click.stop="emit('update-card', item)"
          title="更新角色卡"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.92)] border border-white/10 text-[#A8A29E] hover:text-[#F9C86D] hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <RefreshCw class="w-3.5 h-3.5" />
        </button>

        <!-- ③ 置顶 -->
        <button
          type="button"
          @click.stop="emit('pin', item.id)"
          title="置顶角色"
          :class="[
            'w-7 h-7 rounded-full border transition-all cursor-pointer shadow-md flex items-center justify-center hover:scale-110 active:scale-95',
            item.isPinned
              ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09]'
              : 'bg-[rgba(26,23,20,0.92)] border-white/10 text-[#A8A29E] hover:text-[#F9C86D]'
          ]"
        >
          <Pin class="w-3.5 h-3.5" />
        </button>

        <!-- ④ 清空历史 -->
        <button
          type="button"
          @click.stop="emit('clear', item.id)"
          title="清空历史"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.92)] border border-white/10 text-[#A8A29E] hover:text-amber-400 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <RotateCcw class="w-3.5 h-3.5" />
        </button>

        <!-- ⑤ 删除 -->
        <button
          type="button"
          @click.stop="emit('delete', item.id)"
          title="删除"
          class="w-7 h-7 rounded-full bg-[rgba(26,23,20,0.92)] border border-white/10 text-[#A8A29E] hover:text-red-400 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <Trash2 class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- 3. 批量删除模式下的多选 Checkbox -->
      <div
        v-else
        @click.stop="emit('toggle-select', item.id)"
        class="absolute top-2 left-2 z-20"
      >
        <div
          :class="[
            'w-5 h-5 rounded-md border flex items-center justify-center transition-all cursor-pointer',
            selectedIds.has(item.id)
              ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09]'
              : 'bg-black/50 border-white/40 text-transparent'
          ]"
        >
          <Check class="w-3.5 h-3.5 stroke-[3]" />
        </div>
      </div>
    </div>
  </div>
</template>
