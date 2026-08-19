<script setup lang="ts">
/**
 * 角色卡详情 - 角色描述卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { ChevronDown, ChevronUp } from "lucide-vue-next";
import { ref } from "vue";

defineProps<{
  description: string;
}>();

const isExpanded = ref(false);
</script>

<template>
  <div class="w-full px-3 pt-3 select-none">
    <div class="w-full p-4 rounded-lg border border-[#292524] bg-[#1A1714]/95 flex flex-col gap-2.5">
      
      <!-- 标题: 角色描述 -->
      <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[-0.36px] leading-5">
        角色描述
      </h2>

      <!-- 描述文本与折叠 -->
      <div class="relative pt-1">
        <p
          :class="[
            'text-[15px] text-[#A8A29E] leading-relaxed transition-all font-sans',
            isExpanded ? '' : 'line-clamp-3'
          ]"
        >
          {{ description }}
        </p>

        <!-- 展开更多 按钮 -->
        <button
          type="button"
          @click="isExpanded = !isExpanded"
          class="mt-2.5 flex items-center gap-1 text-xs font-medium text-[#A8A29E] hover:text-[#F9C86D] transition-colors cursor-pointer"
        >
          <span>{{ isExpanded ? "收起" : "展开更多" }}</span>
          <ChevronUp v-if="isExpanded" class="w-3.5 h-3.5" />
          <ChevronDown v-else class="w-3.5 h-3.5" />
        </button>
      </div>

    </div>
  </div>
</template>
