<script setup lang="ts">
/**
 * 角色卡详情 - 标签列表卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

defineProps<{
  tags: readonly string[] | string[];
}>();
</script>

<template>
  <div class="w-full px-3 pt-3 select-none">
    <div class="w-full p-4 rounded-lg border border-[#292524] bg-[#1A1714]/95 flex flex-col gap-3">
      
      <!-- 标题: 标签 -->
      <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[-0.36px] leading-5">
        标签
      </h2>

      <!-- 标签药丸流 -->
      <div class="flex flex-wrap gap-2 pt-1">
        <span
          v-for="tag in tags"
          :key="tag"
          class="px-3 py-1 rounded-full border border-[#44403C]/60 bg-[#292524]/40 text-xs text-[#A8A29E] hover:text-[#F9C86D] hover:border-[#F9C86D]/40 transition-colors cursor-pointer"
        >
          {{ tag }}
        </span>
      </div>

    </div>
  </div>
</template>
