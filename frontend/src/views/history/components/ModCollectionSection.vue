<script setup lang="ts">
/**
 * Mod 合集管理主面板 (Figma 109:12064 1:1 像素级高保真)
 *
 * 包含我的合集/公开合集切换、+ 新建合集按钮、合集卡片列表 (标题/描述/统计明细/预览/编辑/分享/删除)、空状态。
 *
 * @packageDocumentation
 */

import type { CollectionSubTab, ModCollectionItem } from "@/views/history/types";

defineProps<{
  activeSubTab: CollectionSubTab;
  myCollectionList: ModCollectionItem[];
  publicCollectionList: ModCollectionItem[];
}>();

const emit = defineEmits<{
  (e: "select-sub-tab", tab: CollectionSubTab): void;
  (e: "create"): void;
  (e: "preview", coll: ModCollectionItem): void;
  (e: "edit", coll: ModCollectionItem): void;
  (e: "share", id: string): void;
  (e: "delete", id: string): void;
}>();
</script>

<template>
  <div class="w-full flex flex-col pt-5 pb-12">
    <!-- 1. 顶部子栏切换 (我的合集 / 公开合集) (Figma 109:12064) -->
    <div class="w-full flex items-center justify-between pb-4">
      <div class="flex items-center gap-2">
        <!-- 我的合集 -->
        <button
          type="button"
          @click="emit('select-sub-tab', 'mine')"
          class="px-3 py-1.5 rounded-[8px] text-[12px] leading-[16px] transition-all cursor-pointer select-none"
          :class="activeSubTab === 'mine' ? 'bg-[rgba(249,200,109,0.15)] text-[#F9C86D] font-normal' : 'border border-[#44403C] bg-[#292524] text-[#A8A29E]'"
        >
          我的合集
        </button>

        <!-- 公开合集 -->
        <button
          type="button"
          @click="emit('select-sub-tab', 'public')"
          class="px-3 py-1.5 rounded-[8px] text-[12px] leading-[16px] transition-all cursor-pointer select-none"
          :class="activeSubTab === 'public' ? 'bg-[rgba(249,200,109,0.15)] text-[#F9C86D] font-normal' : 'border border-[#44403C] bg-[#292524] text-[#A8A29E]'"
        >
          公开合集
        </button>
      </div>

      <!-- 右侧 "+ 新建合集" 按钮 (仅在我的合集下展示) -->
      <button
        v-if="activeSubTab === 'mine'"
        type="button"
        @click="emit('create')"
        class="px-4 py-2 rounded-[8px] bg-[rgba(249,200,109,0.15)] text-[#F9C86D] text-[14px] leading-[20px] font-medium hover:bg-[rgba(249,200,109,0.25)] active:scale-95 transition-all cursor-pointer select-none"
      >
        + 新建合集
      </button>
    </div>

    <!-- 2. 我的合集列表卡片流 (Figma 109:12064) -->
    <template v-if="activeSubTab === 'mine'">
      <div v-if="myCollectionList.length > 0" class="w-full flex flex-col gap-4">
        <div
          v-for="coll in myCollectionList"
          :key="coll.id"
          class="w-full p-4 rounded-[12px] border border-[#44403C] bg-[#292524] flex flex-col gap-1.5 transition-colors hover:border-[#F9C86D]/40"
        >
          <!-- 标题 -->
          <h4 class="text-[16px] leading-[27px] font-normal text-[#C0A480]">
            {{ coll.title }}
          </h4>

          <!-- 描述 -->
          <p class="text-[12px] leading-[16px] text-[#A8A29E] line-clamp-2">
            {{ coll.description || '暂无描述' }}
          </p>

          <!-- 详细统计明细 -->
          <p class="text-[10px] leading-[17px] text-[#78716C] pt-1">
            {{ coll.statsText }}
          </p>

          <!-- 底部操作栏 (预览 / 编辑 / 分享 / 删除) (Figma 109:12064) -->
          <div class="flex items-center gap-2 pt-3">
            <!-- 预览 -->
            <button
              type="button"
              @click="emit('preview', coll)"
              class="px-3 py-1.5 rounded-[8px] bg-[rgba(249,200,109,0.15)] text-[12px] leading-[16px] text-[#F9C86D] hover:bg-[rgba(249,200,109,0.25)] active:scale-95 transition-all cursor-pointer select-none"
            >
              预览
            </button>

            <!-- 编辑 -->
            <button
              type="button"
              @click="emit('edit', coll)"
              class="px-3 py-1.5 rounded-[8px] border border-[#44403C] bg-[#292524] text-[12px] leading-[16px] text-[#A8A29E] hover:text-[#F5F5F4] active:scale-95 transition-all cursor-pointer select-none"
            >
              编辑
            </button>

            <!-- 分享 -->
            <button
              type="button"
              @click="emit('share', coll.id)"
              class="px-3 py-1.5 rounded-[8px] text-[12px] leading-[16px] text-[#22C55E] hover:bg-[rgba(34,197,94,0.10)] active:scale-95 transition-all cursor-pointer select-none"
            >
              分享
            </button>

            <!-- 删除 -->
            <button
              type="button"
              @click="emit('delete', coll.id)"
              class="px-3 py-1.5 rounded-[8px] text-[12px] leading-[16px] text-[#EF4444] hover:bg-[rgba(239,68,68,0.10)] active:scale-95 transition-all cursor-pointer select-none"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态卡片 (Figma 109:12064) -->
      <div
        v-else
        class="w-full py-12 rounded-[12px] border border-[#44403C] bg-[#292524] flex flex-col items-center justify-center text-center"
      >
        <p class="text-[14px] leading-[20px] text-[#A8A29E]">
          还没有任何合集
        </p>
      </div>
    </template>

    <!-- 3. 公开合集广场列表 -->
    <template v-else>
      <div v-if="publicCollectionList.length > 0" class="w-full flex flex-col gap-4">
        <div
          v-for="coll in publicCollectionList"
          :key="coll.id"
          class="w-full p-4 rounded-[12px] border border-[#44403C] bg-[#292524] flex flex-col gap-1.5 transition-colors hover:border-[#F9C86D]/40"
        >
          <div class="flex items-center justify-between">
            <h4 class="text-[16px] leading-[27px] font-normal text-[#C0A480]">
              {{ coll.title }}
            </h4>
            <span class="text-[11px] text-[#A8A29E]">{{ coll.author }}</span>
          </div>

          <p class="text-[12px] leading-[16px] text-[#A8A29E] line-clamp-2">
            {{ coll.description }}
          </p>

          <p class="text-[10px] leading-[17px] text-[#78716C] pt-1">
            {{ coll.statsText }}
          </p>

          <div class="flex items-center gap-2 pt-3">
            <button
              type="button"
              @click="emit('preview', coll)"
              class="px-3 py-1.5 rounded-[8px] bg-[rgba(249,200,109,0.15)] text-[12px] leading-[16px] text-[#F9C86D] hover:bg-[rgba(249,200,109,0.25)] active:scale-95 transition-all cursor-pointer select-none"
            >
              预览合集
            </button>
          </div>
        </div>
      </div>

      <div
        v-else
        class="w-full py-12 rounded-[12px] border border-[#44403C] bg-[#292524] flex flex-col items-center justify-center text-center"
      >
        <p class="text-[14px] leading-[20px] text-[#A8A29E]">
          暂无公开合集
        </p>
      </div>
    </template>
  </div>
</template>
