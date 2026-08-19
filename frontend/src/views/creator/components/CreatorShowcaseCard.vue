<script setup lang="ts">
/**
 * 创作者综合展示卡片组件 (1:1 原型高保真)
 *
 * 包装创作者个人资料栏与旗下 2x2 热门作品网格。
 *
 * @packageDocumentation
 */

import CreatorCharacterGrid from "@/views/creator/components/CreatorCharacterGrid.vue";
import CreatorProfileHeader from "@/views/creator/components/CreatorProfileHeader.vue";
import type { CreatorCharacterWork, CreatorItem } from "@/views/creator/types";

defineProps<{
  creator: CreatorItem;
}>();

const emit = defineEmits<{
  (e: "toggle-follow", id: string): void;
  (e: "select-work", work: CreatorCharacterWork): void;
}>();
</script>

<template>
  <div class="w-full rounded-xl border border-[rgba(168,162,158,0.40)] bg-gradient-to-br from-[#1C1917] via-[#221F1D] to-[#292524] p-4 shadow-xl flex flex-col transition-all duration-200">
    <!-- 1. 创作者个人资料头部 -->
    <CreatorProfileHeader
      :creator="creator"
      @toggle-follow="emit('toggle-follow', $event)"
    />

    <!-- 2. 代表作角色矩阵 -->
    <CreatorCharacterGrid
      :works="creator.featuredWorks"
      @select-work="emit('select-work', $event)"
    />
  </div>
</template>
