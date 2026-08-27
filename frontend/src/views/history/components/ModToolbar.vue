<script setup lang="ts">
/**
 * Mod 模组中心搜索与筛选胶囊工具栏 (Figma 93:3270 1:1 像素级高保真)
 *
 * 包含 搜索输入框、第一层排序胶囊 (最新/热门/高评分/最多赞/最多评论)、第二层分类胶囊 (世界书/系统提示/历史指令/正则/作者助手)。
 *
 * @packageDocumentation
 */

import type { ModCategoryTag, ModSortType } from "@/views/history/types";
import { Search } from "lucide-vue-next";

defineProps<{
  searchQuery: string;
  activeSort: ModSortType;
  activeTag: ModCategoryTag;
}>();

const emit = defineEmits<{
  (e: "update:searchQuery", val: string): void;
  (e: "selectSort", sort: ModSortType): void;
  (e: "selectTag", tag: ModCategoryTag): void;
}>();

const SORT_OPTIONS: Array<{ id: ModSortType; label: string }> = [
  { id: "latest", label: "最新" },
  { id: "hot", label: "热门" },
  { id: "rating", label: "高评分" },
  { id: "likes", label: "最多赞" },
  { id: "comments", label: "最多评论" },
];

const TAG_OPTIONS: Array<{ id: ModCategoryTag; label: string }> = [
  { id: "worldbook", label: "世界书" },
  { id: "system", label: "系统提示" },
  { id: "command", label: "历史指令" },
  { id: "regex", label: "正则" },
  { id: "author", label: "作者助手" },
];
</script>

<template>
  <div class="w-full flex flex-col pt-5 gap-4">
    <!-- 1. 搜索输入框 (Figma 93:3270) -->
    <div class="relative w-full">
      <div class="absolute left-3 top-1/2 -translate-y-1/2 text-[#A8A29E] pointer-events-none">
        <Search class="w-4 h-4" />
      </div>
      <input
        :value="searchQuery"
        @input="emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
        type="text"
        placeholder="搜索 Mod..."
        class="w-full h-[37px] pl-9 pr-3 rounded-[6px] border border-[#44403C] bg-[#292524] text-[14px] text-[#F5F5F4] placeholder-[#F5F5F4]/50 focus:border-[#F9C86D] focus:outline-none transition-colors"
      />
    </div>

    <!-- 2. 双层筛选胶囊标签栏 (Figma 93:3270) -->
    <div class="w-full flex flex-col gap-2 overflow-x-auto no-scrollbar">
      <!-- 第一层: 排序胶囊 (最新 / 热门 / 高评分 / 最多赞 / 最多评论) -->
      <div class="flex items-center gap-1.5 flex-nowrap">
        <button
          v-for="sort in SORT_OPTIONS"
          :key="sort.id"
          type="button"
          @click="emit('selectSort', sort.id)"
          class="px-3 py-1.5 rounded-full text-[12px] leading-[16px] transition-all flex-shrink-0 cursor-pointer select-none"
          :class="
            activeSort === sort.id
              ? 'bg-[rgba(249,200,109,0.15)] text-[#F9C86D] font-medium'
              : 'border border-[#44403C] bg-[#292524] text-[#A8A29E] hover:text-[#F5F5F4]'
          "
        >
          {{ sort.label }}
        </button>
      </div>

      <!-- 第二层: 类型分类胶囊 (世界书 / 系统提示 / 历史指令 / 正则 / 作者助手) -->
      <div class="flex items-center gap-1.5 flex-nowrap">
        <button
          v-for="tag in TAG_OPTIONS"
          :key="tag.id"
          type="button"
          @click="emit('selectTag', tag.id)"
          class="px-2.5 py-1 rounded-full text-[12px] leading-[16px] transition-all flex-shrink-0 cursor-pointer select-none"
          :class="
            activeTag === tag.id
              ? 'border border-[#F9C86D] bg-[#F9C86D]/15 text-[#F9C86D] font-medium'
              : 'border border-[#44403C] bg-transparent text-[#A8A29E] hover:text-[#F5F5F4]'
          "
        >
          {{ tag.label }}
        </button>
      </div>
    </div>
  </div>
</template>
