<script setup lang="ts">
/**
 * 桌面端角色社区顶部工具与复合筛选栏 (DesktopHomeToolbar.vue)
 *
 * 1:1 像素级还原参考截图 1 与截图 2 的顶部工具栏：
 * 包含第一行【剧情卡 / 绅士卡】模式切换、搜索框 (带 '/' 快捷键提示) 与【高级筛选】；
 * 第二行【精选 / 推荐 / 趋势 / 随机 / 收藏 / 最新】排序流与热门标签胶囊。
 *
 * @packageDocumentation
 */

import { useMarketStore } from "@/stores/market";
import type { CardMode, SortType } from "@/types";
import { HOT_TAGS } from "@/views/home/constants/marketConfig";
import {
  ChevronDown,
  Filter,
  Search,
  SlidersHorizontal,
  X,
} from "lucide-vue-next";
import { onMounted, onUnmounted, ref } from "vue";

const marketStore = useMarketStore();
const searchInputRef = ref<HTMLInputElement | null>(null);

/** 全局快捷键 '/' 唤起搜索 */
function handleKeyDown(e: KeyboardEvent): void {
  if (
    e.key === "/" &&
    document.activeElement?.tagName !== "INPUT" &&
    document.activeElement?.tagName !== "TEXTAREA"
  ) {
    e.preventDefault();
    searchInputRef.value?.focus();
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleKeyDown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeyDown);
});

/** 排序切换 */
function handleSortChange(sort: SortType): void {
  marketStore.setSortBy(sort);
}

/** 模式切换 */
function handleModeChange(mode: CardMode): void {
  marketStore.setMode(mode);
}

/** 标签选择 */
function handleTagClick(tag: string): void {
  marketStore.setSelectedTag(tag);
}
</script>

<template>
  <div class="hidden md:flex flex-col w-full gap-3 pb-3 border-b border-[#251E17]">
    
    <!-- 第一行: 左侧模式切换 (剧情卡 / 绅士卡) + 右侧搜索框与高级筛选 (截图 1/2 顶部) -->
    <div class="flex items-center justify-between w-full">
      
      <!-- 剧情卡 / 绅士卡 模式切换 -->
      <div class="flex items-center gap-6">
        <button
          type="button"
          @click="handleModeChange('story')"
          :class="[
            'text-base font-bold transition-all cursor-pointer select-none pb-1 relative',
            marketStore.mode === 'story'
              ? 'text-[#F5F5F4]'
              : 'text-[#78716C] hover:text-[#D6D3D1]'
          ]"
        >
          剧情卡
          <!-- 激活指示微线 -->
          <div
            v-if="marketStore.mode === 'story'"
            class="absolute bottom-0 inset-x-0 h-0.5 bg-[#F9C86D] rounded-full shadow-[0_0_8px_#F9C86D]"
          />
        </button>

        <button
          type="button"
          @click="handleModeChange('nsfw')"
          :class="[
            'text-base font-bold transition-all cursor-pointer select-none pb-1 relative',
            marketStore.mode === 'nsfw'
              ? 'text-[#F5F5F4]'
              : 'text-[#78716C] hover:text-[#D6D3D1]'
          ]"
        >
          绅士卡
          <!-- 激活指示微线 -->
          <div
            v-if="marketStore.mode === 'nsfw'"
            class="absolute bottom-0 inset-x-0 h-0.5 bg-[#F9C86D] rounded-full shadow-[0_0_8px_#F9C86D]"
          />
        </button>
      </div>

      <!-- 右侧搜索输入框与高级筛选 -->
      <div class="flex items-center gap-3">
        <!-- 搜索输入框 (带 '/' 键盘快捷键提示) -->
        <div class="relative flex items-center w-64 lg:w-72">
          <Search class="absolute left-3 w-4 h-4 text-[#78716C] pointer-events-none" />
          <input
            ref="searchInputRef"
            type="text"
            :value="marketStore.searchKeyword"
            @input="marketStore.setSearchKeyword(($event.target as HTMLInputElement).value)"
            placeholder="探寻角色..."
            class="w-full h-9 pl-9 pr-14 text-xs text-[#F5F5F4] placeholder-[#78716C] bg-[#1F1914] border border-[#3A2E22] rounded-lg outline-none focus:border-[#F9C86D]/60 focus:bg-[#251E18] transition-all font-sans"
          />

          <!-- 快捷键提示 '/' 或 清除按钮 -->
          <div class="absolute right-2.5 flex items-center gap-1">
            <button
              v-if="marketStore.searchKeyword"
              @click="marketStore.setSearchKeyword('')"
              type="button"
              class="text-[#78716C] hover:text-white p-0.5 cursor-pointer"
            >
              <X class="w-3.5 h-3.5" />
            </button>
            <kbd
              v-else
              class="px-1.5 py-0.5 text-[10px] text-[#78716C] bg-[#2E241B] border border-[#443628] rounded font-mono select-none"
            >
              /
            </kbd>
          </div>
        </div>

        <!-- 设置/过滤图标 -->
        <button
          type="button"
          class="p-2 rounded-lg bg-[#1F1914] border border-[#3A2E22] text-[#A8A29E] hover:text-[#F9C86D] hover:border-[#F9C86D]/40 transition-colors cursor-pointer"
          title="筛选偏好"
        >
          <SlidersHorizontal class="w-4 h-4" />
        </button>

      </div>
    </div>

    <!-- 第二行: 次级排序控制栏与热门标签平铺条 (1:1 还原截图 1/2 黑金内嵌横条) -->
    <div class="flex items-center justify-between w-full px-3 py-1.5 rounded-lg bg-[#1B1611] border border-[#2D2319] overflow-x-auto no-scrollbar gap-4">
      
      <!-- 左侧排序 Tab 流与热门标签 -->
      <div class="flex items-center gap-3 shrink-0">
        
        <!-- 排序项: 精选 (heat) -->
        <button
          type="button"
          @click="handleSortChange('heat')"
          :class="[
            'text-xs px-2.5 py-1 rounded transition-colors cursor-pointer select-none',
            marketStore.sortBy === 'heat'
              ? 'text-[#F9C86D] font-bold bg-[#2A2016]'
              : 'text-[#A8A29E] hover:text-[#F5F5F4]'
          ]"
        >
          精选
        </button>

        <!-- 推荐 (recommend) -->
        <button
          type="button"
          @click="handleSortChange('recommend')"
          :class="[
            'text-xs px-2.5 py-1 rounded transition-colors cursor-pointer select-none',
            marketStore.sortBy === 'recommend'
              ? 'text-[#F9C86D] font-bold bg-[#2A2016]'
              : 'text-[#A8A29E] hover:text-[#F5F5F4]'
          ]"
        >
          推荐
        </button>

        <!-- 趋势 (trend) -->
        <button
          type="button"
          @click="handleSortChange('trend')"
          :class="[
            'text-xs px-2.5 py-1 rounded transition-colors cursor-pointer select-none',
            marketStore.sortBy === 'trend'
              ? 'text-[#F9C86D] font-bold bg-[#2A2016]'
              : 'text-[#A8A29E] hover:text-[#F5F5F4]'
          ]"
        >
          趋势
        </button>

        <!-- 随机 (random) -->
        <button
          type="button"
          @click="handleSortChange('random')"
          :class="[
            'text-xs px-2.5 py-1 rounded transition-colors cursor-pointer select-none',
            marketStore.sortBy === 'random'
              ? 'text-[#F9C86D] font-bold bg-[#2A2016]'
              : 'text-[#A8A29E] hover:text-[#F5F5F4]'
          ]"
        >
          随机
        </button>

        <!-- 收藏 (favorite) -->
        <button
          type="button"
          @click="handleSortChange('favorite')"
          :class="[
            'text-xs px-2.5 py-1 rounded transition-colors cursor-pointer select-none',
            marketStore.sortBy === 'favorite'
              ? 'text-[#F9C86D] font-bold bg-[#2A2016]'
              : 'text-[#A8A29E] hover:text-[#F5F5F4]'
          ]"
        >
          收藏
        </button>

        <!-- 最新 (下拉切换) -->
        <div class="relative flex items-center">
          <button
            type="button"
            class="flex items-center gap-1 text-xs px-2 py-1 rounded text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer select-none"
          >
            <span>最新</span>
            <ChevronDown class="w-3 h-3 text-[#78716C]" />
          </button>
        </div>

        <!-- 细竖分割线 -->
        <div class="w-[1px] h-3.5 bg-[#3A2E22] mx-1" />

        <!-- 标签胶囊列表 -->
        <div class="flex items-center gap-1.5">
          <!-- 全部 -->
          <button
            type="button"
            @click="handleTagClick('')"
            :class="[
              'text-[11px] px-2 py-0.5 rounded-full border transition-all cursor-pointer select-none',
              !marketStore.selectedTag
                ? 'bg-[#2E241B] border-[#F9C86D]/50 text-[#F9C86D] font-medium'
                : 'bg-transparent border-[#3A2E22] text-[#78716C] hover:text-[#A8A29E] hover:border-[#4A3B2C]'
            ]"
          >
            全部
          </button>

          <!-- 热门标签 -->
          <button
            v-for="tag in HOT_TAGS"
            :key="tag"
            type="button"
            @click="handleTagClick(marketStore.selectedTag === tag ? '' : tag)"
            :class="[
              'text-[11px] px-2 py-0.5 rounded-full border transition-all cursor-pointer select-none whitespace-nowrap',
              marketStore.selectedTag === tag
                ? 'bg-[#2E241B] border-[#F9C86D]/60 text-[#F9C86D] font-medium'
                : 'bg-transparent border-[#3A2E22] text-[#78716C] hover:text-[#A8A29E] hover:border-[#4A3B2C]'
            ]"
          >
            #{{ tag }}
          </button>
        </div>

      </div>

      <!-- 右侧高级筛选按钮 -->
      <button
        type="button"
        class="flex items-center gap-1 text-xs px-2.5 py-1 rounded bg-[#221A13] hover:bg-[#2D2319] text-[#A8A29E] hover:text-[#F9C86D] border border-[#3A2E22] transition-colors cursor-pointer shrink-0"
      >
        <Filter class="w-3.5 h-3.5" />
        <span>高级筛选</span>
      </button>

    </div>

  </div>
</template>
