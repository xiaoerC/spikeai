<script setup lang="ts">
/**
 * 个人历史记录 2 列网格卡片流组件 (1:1 Figma 原型高保真)
 *
 * 严格按照 Figma 原型 media_1787833396896.png 像素级还原：
 * - 2 列网格瀑布流 (grid grid-cols-2 gap-3)
 * - 高比例沉浸式卡片 (h-[270px], rounded-2xl, border-[#44403C]/40, overflow-hidden)
 * - 顶部 5 大圆形微光悬浮操作按钮 (编辑备注 / 更新角色 / 置顶 / 清空 / 删除)
 * - 底部渐变半透明黑金遮罩 + 角色卡标题与备注
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
      class="group relative flex flex-col h-[270px] rounded-2xl border border-[rgba(83,71,65,0.40)] bg-[#1A1511] overflow-hidden shadow-xl transition-all duration-300 hover:border-[#F9C86D]/50 hover:shadow-[0_8px_24px_rgba(0,0,0,0.6)] select-none"
    >
      <!-- 1. 卡片背景大封面 (点击进入对话) -->
      <div
        @click="isBatchMode ? emit('toggle-select', item.id) : emit('select-card', item)"
        class="absolute inset-0 w-full h-full cursor-pointer"
      >
        <img
          :src="item.avatar"
          :alt="item.title"
          class="w-full h-full object-cover object-top group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />

        <!-- 顶部微暗遮罩 (让顶部操作按钮更清晰) -->
        <div class="absolute inset-x-0 top-0 h-16 bg-gradient-to-b from-black/60 to-transparent pointer-events-none" />

        <!-- 底部渐变暗黑遮罩 + 标题栏 -->
        <div class="absolute inset-x-0 bottom-0 pt-10 pb-3 px-3 bg-gradient-to-t from-black/95 via-black/60 to-transparent flex flex-col justify-end">
          <h3 class="text-[13px] font-bold text-white truncate leading-snug drop-shadow-md">
            {{ item.title }}
          </h3>
          <span v-if="item.remark" class="text-[10.5px] text-[#F9C86D] truncate mt-0.5 font-medium drop-shadow">
            📝 {{ item.remark }}
          </span>
        </div>
      </div>

      <!-- 2. 卡片顶部 5 大圆形快捷悬浮操作按钮 -->
      <div
        v-if="!isBatchMode"
        class="absolute top-2 inset-x-2 flex items-center justify-between z-20 pointer-events-auto"
      >
        <!-- ① 编辑备注 -->
        <button
          type="button"
          @click.stop="emit('remark', item)"
          title="编辑备注"
          class="w-6.5 h-6.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-white/70 hover:text-[#F9C86D] hover:bg-black/80 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <Edit3 class="w-3 h-3" />
        </button>

        <!-- ② 更新角色卡 -->
        <button
          type="button"
          @click.stop="emit('update-card', item)"
          title="更新角色卡"
          class="w-6.5 h-6.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-white/70 hover:text-[#F9C86D] hover:bg-black/80 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <RefreshCw class="w-3 h-3" />
        </button>

        <!-- ③ 置顶 -->
        <button
          type="button"
          @click.stop="emit('pin', item.id)"
          title="置顶角色"
          :class="[
            'w-6.5 h-6.5 rounded-full border transition-all cursor-pointer shadow-md flex items-center justify-center hover:scale-110 active:scale-95 backdrop-blur-md',
            item.isPinned
              ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09]'
              : 'bg-black/60 border-white/10 text-white/70 hover:text-[#F9C86D] hover:bg-black/80'
          ]"
        >
          <Pin class="w-3 h-3" />
        </button>

        <!-- ④ 清空历史 -->
        <button
          type="button"
          @click.stop="emit('clear', item.id)"
          title="清空历史"
          class="w-6.5 h-6.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-white/70 hover:text-amber-400 hover:bg-black/80 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <RotateCcw class="w-3 h-3" />
        </button>

        <!-- ⑤ 删除 -->
        <button
          type="button"
          @click.stop="emit('delete', item.id)"
          title="删除"
          class="w-6.5 h-6.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-white/70 hover:text-red-400 hover:bg-black/80 hover:scale-110 active:scale-95 flex items-center justify-center transition-all cursor-pointer shadow-md"
        >
          <Trash2 class="w-3 h-3" />
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
            'w-6 h-6 rounded-md border flex items-center justify-center transition-all cursor-pointer shadow-lg backdrop-blur-md',
            selectedIds.has(item.id)
              ? 'bg-[#F9C86D] border-[#F9C86D] text-[#0C0A09]'
              : 'bg-black/60 border-white/40 text-transparent'
          ]"
        >
          <Check class="w-4 h-4 stroke-[3]" />
        </div>
      </div>
    </div>
  </div>
</template>
