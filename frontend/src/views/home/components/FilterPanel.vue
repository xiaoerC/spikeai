<script setup lang="ts">
/**
 * 复合筛选与搜索面板组件 (Home 页面私有)
 *
 * @packageDocumentation
 */

import { useMarketStore } from "@/stores/market";
import type { SortType, TimeSpan } from "@/types";
import { EXTRA_TAGS, HOT_TAGS } from "@/views/home/constants/marketConfig";
import { ref } from "vue";

const marketStore = useMarketStore();

/** 是否展开全部标签抽屉 */
const isTagsExpanded = ref(false);

/**
 * 切换排序
 * @param sort - 排序项
 */
function handleSortChange(sort: SortType): void {
  marketStore.setSortBy(sort);
}

/**
 * 切换趋势时间跨度
 * @param span - 日/周/月
 */
function handleTimeSpanChange(span: TimeSpan): void {
  marketStore.setTimeSpan(span);
}

/**
 * 点击标签过滤
 * @param tag - 标签名
 */
function handleTagClick(tag: string): void {
  marketStore.setSelectedTag(tag);
}
</script>

<template>
  <div class="flex flex-col items-start self-stretch w-full px-2">
    <!-- 面板内层容器: 深黑色微磨砂质感 -->
    <div class="flex flex-col items-start self-stretch w-full rounded-lg border border-[rgba(83,71,65,0.30)] bg-[rgba(26,23,20,0.95)] p-2 gap-2">
      
      <!-- 1. 顶部排序 Tab 栏 (纯深色透明底) -->
      <div class="flex items-center self-stretch h-10 border-b border-[#44403C] overflow-x-auto no-scrollbar w-full bg-transparent">
        <!-- 热度 -->
        <button
          type="button"
          @click="handleSortChange('heat')"
          :class="[
            'flex items-center h-10 px-3 gap-1.5 border-b-2 bg-transparent cursor-pointer select-none transition-colors flex-shrink-0',
            marketStore.sortBy === 'heat'
              ? 'border-[#F9C86D] text-[#F9C86D] font-semibold'
              : 'border-transparent text-[#78716C] font-normal hover:text-[#A8A29E]'
          ]"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.33333 3.5H11.6667M2.33333 5.83333H11.6667M2.33333 8.16667H11.6667M2.33333 10.5H11.6667" :stroke="marketStore.sortBy === 'heat' ? '#F9C86D' : '#78716C'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[12px] leading-4 tracking-tight">热度</span>
        </button>

        <!-- 荐 -->
        <button
          type="button"
          @click="handleSortChange('recommend')"
          :class="[
            'flex items-center h-10 px-3 gap-1.5 border-b-2 bg-transparent cursor-pointer select-none transition-colors flex-shrink-0',
            marketStore.sortBy === 'recommend'
              ? 'border-[#F9C86D] text-[#F9C86D] font-semibold'
              : 'border-transparent text-[#78716C] font-normal hover:text-[#A8A29E]'
          ]"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6.44524 1.70741C6.62024 1.17016 7.38033 1.17016 7.55474 1.70741L8.44083 4.43391C8.47896 4.55086 8.55309 4.65277 8.65262 4.72506C8.75215 4.79735 8.87198 4.83632 8.99499 4.83641H11.8621C12.4273 4.83641 12.6618 5.55974 12.2051 5.89224L9.88574 7.57691C9.78612 7.64934 9.71197 7.75145 9.67393 7.8686C9.63589 7.98575 9.63592 8.11194 9.67399 8.22908L10.5595 10.9556C10.7345 11.4934 10.1191 11.9402 9.66233 11.6077L7.34299 9.92308C7.24331 9.85061 7.12324 9.81158 6.99999 9.81158C6.87675 9.81158 6.75668 9.85061 6.65699 9.92308L4.33766 11.6077C3.88091 11.9402 3.26549 11.4928 3.44049 10.9556L4.32599 8.22908C4.36407 8.11194 4.3641 7.98575 4.32606 7.8686C4.28802 7.75145 4.21387 7.64934 4.11424 7.57691L1.79491 5.89224C1.33758 5.55974 1.57324 4.83641 2.13791 4.83641H5.00441C5.12752 4.83644 5.24749 4.79753 5.34713 4.72523C5.44678 4.65293 5.521 4.55096 5.55916 4.43391L6.44524 1.70741Z" :stroke="marketStore.sortBy === 'recommend' ? '#F9C86D' : '#78716C'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[12px] leading-4 tracking-tight">荐</span>
        </button>

        <!-- 趋 -->
        <button
          type="button"
          @click="handleSortChange('trend')"
          :class="[
            'flex items-center h-10 px-3 gap-1.5 border-b-2 bg-transparent cursor-pointer select-none transition-colors flex-shrink-0',
            marketStore.sortBy === 'trend'
              ? 'border-[#F9C86D] text-[#F9C86D] font-bold'
              : 'border-transparent text-[#78716C] font-normal hover:text-[#A8A29E]'
          ]"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M7.58333 1.16666L1.75 8.16666H7L6.41667 12.8333L12.25 5.83332H7L7.58333 1.16666Z" :fill="marketStore.sortBy === 'trend' ? '#F9C86D' : '#78716C'"/>
          </svg>
          <span class="text-[12px] leading-4 tracking-tight">趋</span>
        </button>

        <!-- 随 -->
        <button
          type="button"
          @click="handleSortChange('random')"
          :class="[
            'flex items-center h-10 px-3 gap-1.5 border-b-2 bg-transparent cursor-pointer select-none transition-colors flex-shrink-0',
            marketStore.sortBy === 'random'
              ? 'border-[#F9C86D] text-[#F9C86D] font-semibold'
              : 'border-transparent text-[#78716C] font-normal hover:text-[#A8A29E]'
          ]"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.33333 2.33334V5.25001H2.67283M2.67283 5.25001C3.06008 4.29225 3.75415 3.49004 4.64627 2.96909C5.53839 2.44815 6.57814 2.23792 7.60257 2.37134C8.627 2.50476 9.57821 2.97431 10.3071 3.70638C11.0361 4.43845 11.5015 5.39168 11.6305 6.41668M2.67283 5.25001H5.25M11.6667 11.6667V8.75001H11.3278M11.3278 8.75001C10.9399 9.7072 10.2457 10.5088 9.35365 11.0293C8.46162 11.5497 7.42218 11.7597 6.39806 11.6264C5.37394 11.493 4.42295 11.0238 3.69398 10.2922C2.96501 9.5606 2.49921 8.60794 2.3695 7.58334M11.3278 8.75001H8.75" :stroke="marketStore.sortBy === 'random' ? '#F9C86D' : '#78716C'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[12px] leading-4 tracking-tight">随</span>
        </button>

        <!-- 藏 -->
        <button
          type="button"
          @click="handleSortChange('favorite')"
          :class="[
            'flex items-center h-10 px-3 gap-1.5 border-b-2 bg-transparent cursor-pointer select-none transition-colors flex-shrink-0',
            marketStore.sortBy === 'favorite'
              ? 'border-[#F9C86D] text-[#F9C86D] font-semibold'
              : 'border-transparent text-[#78716C] font-normal hover:text-[#A8A29E]'
          ]"
        >
          <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M2.91667 2.91667C2.91667 2.60725 3.03958 2.3105 3.25838 2.09171C3.47717 1.87292 3.77392 1.75 4.08333 1.75H9.91667C10.2261 1.75 10.5228 1.87292 10.7416 2.09171C10.9604 2.3105 11.0833 2.60725 11.0833 2.91667V12.25L7 10.2083L2.91667 12.25V2.91667Z" :stroke="marketStore.sortBy === 'favorite' ? '#F9C86D' : '#78716C'" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[12px] leading-4 tracking-tight">藏</span>
        </button>
      </div>

      <!-- 2. 搜索输入条 -->
      <div class="flex items-center self-stretch w-full relative pt-1">
        <div class="relative w-full h-8 flex items-center">
          <svg class="absolute left-2.5 w-3.5 h-3.5 pointer-events-none z-10" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12.25 12.25L8.75 8.75M9.91667 5.83333C9.91667 6.36956 9.81105 6.90054 9.60584 7.39596C9.40063 7.89137 9.09986 8.34151 8.72069 8.72069C8.34151 9.09986 7.89137 9.40063 7.39596 9.60584C6.90054 9.81105 6.36956 9.91667 5.83333 9.91667C5.2971 9.91667 4.76612 9.81105 4.27071 9.60584C3.7753 9.40063 3.32515 9.09986 2.94598 8.72069C2.56681 8.34151 2.26603 7.89137 2.06083 7.39596C1.85562 6.90054 1.75 6.36956 1.75 5.83333C1.75 4.75037 2.18021 3.71175 2.94598 2.94598C3.71175 2.18021 4.75037 1.75 5.83333 1.75C6.9163 1.75 7.95491 2.18021 8.72069 2.94598C9.48646 3.71175 9.91667 4.75037 9.91667 5.83333Z" stroke="#78716C" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <input
            type="text"
            :value="marketStore.searchKeyword"
            @input="marketStore.setSearchKeyword(($event.target as HTMLInputElement).value)"
            placeholder="探寻角色..."
            class="w-full h-8 pl-8 pr-3 text-[12px] text-gray-200 placeholder-[#A18D6F] bg-[rgba(42,37,32,0.50)] border border-[rgba(83,71,65,0.60)] rounded-md outline-none focus:border-[#F9C86D]/60 focus:bg-[rgba(42,37,32,0.8)] transition-all font-sans"
          />
          <button
            v-if="marketStore.searchKeyword"
            @click="marketStore.setSearchKeyword('')"
            type="button"
            class="absolute right-2.5 text-xs text-[#78716C] hover:text-white cursor-pointer"
          >
            ✕
          </button>
        </div>
      </div>

      <!-- 3. 时间跨度三段式 + 热门标签胶囊 -->
      <div class="flex flex-col items-start gap-2 self-stretch w-full pt-1">
        <!-- 时间跨度三段式 -->
        <div class="flex items-center h-[29.33px] rounded-lg border border-[#44403C] overflow-hidden bg-transparent">
          <button
            type="button"
            @click="handleTimeSpanChange('day')"
            :class="[
              'h-7 px-2.5 flex items-center justify-center border-r border-[#44403C] text-[12px] cursor-pointer select-none transition-colors',
              marketStore.timeSpan === 'day'
                ? 'bg-[#F9C86D] text-[#0C0A09] font-bold'
                : 'bg-transparent text-[#A8A29E] font-normal hover:text-white'
            ]"
          >
            日趋势
          </button>

          <button
            type="button"
            @click="handleTimeSpanChange('week')"
            :class="[
              'h-7 px-2.5 flex items-center justify-center border-r border-[#44403C] text-[12px] cursor-pointer select-none transition-colors',
              marketStore.timeSpan === 'week'
                ? 'bg-[#F9C86D] text-[#0C0A09] font-bold'
                : 'bg-transparent text-[#A8A29E] font-normal hover:text-white'
            ]"
          >
            周趋势
          </button>

          <button
            type="button"
            @click="handleTimeSpanChange('month')"
            :class="[
              'h-7 px-2.5 flex items-center justify-center text-[12px] cursor-pointer select-none transition-colors',
              marketStore.timeSpan === 'month'
                ? 'bg-[#F9C86D] text-[#0C0A09] font-bold'
                : 'bg-transparent text-[#A8A29E] font-normal hover:text-white'
            ]"
          >
            月趋势
          </button>
        </div>

        <!-- 热门标签胶囊行 -->
        <div class="flex items-center gap-1.5 self-stretch overflow-x-auto no-scrollbar py-0.5">
          <button
            v-for="tag in HOT_TAGS"
            :key="tag"
            type="button"
            @click="handleTagClick(tag)"
            :class="[
              'h-6 px-2.5 py-1 flex items-center justify-center rounded-full border text-[12px] font-medium leading-none cursor-pointer whitespace-nowrap transition-all',
              marketStore.selectedTag === tag
                ? 'border-[#F9C86D] bg-[#F9C86D] text-[#0C0A09] font-bold'
                : 'border-[rgba(249,200,109,0.15)] bg-[rgba(249,200,109,0.08)] text-[#A8A29E] hover:text-white'
            ]"
          >
            {{ tag }}
          </button>

          <!-- 更多按钮 -->
          <button
            type="button"
            @click="isTagsExpanded = !isTagsExpanded"
            :class="[
              'h-6 px-2 py-1 flex items-center justify-center gap-0.5 rounded-full border text-[12px] font-medium leading-none cursor-pointer whitespace-nowrap transition-all',
              isTagsExpanded
                ? 'border-[#F9C86D] bg-[rgba(249,200,109,0.2)] text-[#F9C86D]'
                : 'border-[rgba(249,200,109,0.15)] bg-[rgba(249,200,109,0.08)] text-[#A8A29E]'
            ]"
          >
            <svg class="w-3 h-3 transition-transform duration-200" :class="{ 'rotate-180': isTagsExpanded }" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9.5 4.5L6 8L2.5 4.5" stroke="#A8A29E" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>更多</span>
          </button>
        </div>

        <!-- 展开的更多标签抽屉 -->
        <div
          v-if="isTagsExpanded"
          class="flex flex-wrap gap-1.5 pt-1 border-t border-[#44403C]/50 w-full animate-fade-in"
        >
          <button
            v-for="tag in EXTRA_TAGS"
            :key="tag"
            type="button"
            @click="handleTagClick(tag)"
            :class="[
              'h-6 px-2.5 py-1 flex items-center justify-center rounded-full border text-[12px] font-medium leading-none cursor-pointer whitespace-nowrap transition-all',
              marketStore.selectedTag === tag
                ? 'border-[#F9C86D] bg-[#F9C86D] text-[#0C0A09] font-bold'
                : 'border-[rgba(249,200,109,0.15)] bg-[rgba(249,200,109,0.08)] text-[#A8A29E] hover:text-white'
            ]"
          >
            {{ tag }}
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
