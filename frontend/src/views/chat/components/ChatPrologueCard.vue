<script setup lang="ts">
/**
 * AI 聊天界面 - 「序幕」引导卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import MessageHtmlSandbox from "@/views/chat/components/MessageHtmlSandbox.vue";
import DOMPurify from "dompurify";
import { computed } from "vue";

const props = defineProps<{
  title?: string;
  content: string;
}>();

/**
 * 检测是否为包含自定义样式或脚本的复杂 HTML 挂件（如酒馆序幕手风琴卡片）
 * 此类富文本必须通过沙箱 iframe 强隔离渲染，彻底杜绝全局 <style> 对宿主 body/html 造成样式污染与视口偏移
 */
const isRichHtmlWidget = computed<boolean>(() => {
  if (!props.content) return false;
  const lower = props.content.toLowerCase();
  return (
    lower.includes("<style") ||
    lower.includes("<script") ||
    lower.includes('class="prologue-container"') ||
    lower.includes("class='prologue-container'") ||
    lower.includes("<!doctype") ||
    lower.includes("<html")
  );
});

/**
 * 局部纯文本或轻量富文本的净化内容（严格剔除 <style> 与 <script> 标签）
 */
const safeInlineContent = computed<string>(() => {
  if (!props.content) return "";
  return DOMPurify.sanitize(props.content, {
    ALLOWED_TAGS: [
      "span",
      "font",
      "b",
      "strong",
      "i",
      "em",
      "u",
      "s",
      "del",
      "p",
      "div",
      "br",
      "hr",
      "blockquote",
      "code",
      "pre",
      "ruby",
      "rt",
      "rp",
      "details",
      "summary",
      "mark",
      "small",
      "sub",
      "sup",
      "table",
      "thead",
      "tbody",
      "tr",
      "th",
      "td",
      "ul",
      "ol",
      "li",
    ],
    ALLOWED_ATTR: ["style", "class", "color"],
  });
});
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
    <!-- 情况 A: 包含 <style>/<script> 的复杂酒馆挂件，采用沙箱 iframe 绝对隔离渲染 -->
    <div v-if="isRichHtmlWidget" class="w-full pt-1">
      <MessageHtmlSandbox
        :html="content"
        :title="title || '序幕剧情'"
        :default-expanded="true"
      />
    </div>

    <!-- 情况 B: 基础富文本或纯文本卡片 -->
    <div v-else class="w-full rounded-lg border border-[#44403C]/40 bg-[#292524]/40 p-4 shadow-sm backdrop-blur-sm">
      <div
        v-if="content.includes('<') && content.includes('>')"
        class="text-xs text-[#A8A29E] leading-relaxed font-sans space-y-1.5"
        v-html="safeInlineContent"
      />
      <p v-else class="text-xs text-[#A8A29E] leading-relaxed font-sans whitespace-pre-line italic">
        {{ content }}
      </p>
    </div>

  </div>
</template>
