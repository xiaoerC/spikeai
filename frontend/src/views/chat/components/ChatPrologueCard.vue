<script setup lang="ts">
/**
 * AI 聊天界面 - 「序幕」引导卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

defineProps<{
  title?: string;
  content: string;
}>();
</script>

<template>
  <div class="w-full flex flex-col items-center px-4 py-2 select-none relative">
    
    <!-- 1. 居中药丸徽标: 序幕 (#F9C86D) -->
    <div class="px-3.5 py-0.5 rounded-full border border-[#F9C86D]/15 bg-gradient-to-r from-[#F9C86D]/[0.08] to-[#F9C86D]/[0.08] flex items-center justify-center z-10 -mb-2.5 shadow-sm">
      <span class="text-xs text-[#F9C86D]">
        {{ title || "序幕" }}
      </span>
    </div>

    <!-- 2. 剧情卡片主体 -->
    <div class="w-full rounded-lg border border-[#44403C]/40 bg-[#292524]/40 p-4 shadow-sm backdrop-blur-sm">
      <div
        v-if="content.includes('<') && content.includes('>')"
        class="text-xs text-[#A8A29E] leading-relaxed font-sans space-y-1.5"
        v-html="content"
      />
      <p v-else class="text-xs text-[#A8A29E] leading-relaxed font-sans whitespace-pre-line italic">
        {{ content }}
      </p>
    </div>

  </div>
</template>
