<script setup lang="ts">
/**
 * 角色卡详情 - 评论区模块 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { MessageSquare } from "lucide-vue-next";
import { ref } from "vue";

const commentText = ref("");
const maxChars = 1000;

const emit = defineEmits<(e: "submitComment", text: string) => void>();

function handleSubmit(): void {
  if (!commentText.value.trim()) return;
  emit("submitComment", commentText.value.trim());
  commentText.value = "";
}
</script>

<template>
  <div class="w-full px-3 pt-3 select-none">
    <div class="w-full rounded-lg border border-[#292524] bg-[#1A1714]/95 flex flex-col overflow-hidden">
      
      <!-- 1. 评论区标题 -->
      <div class="p-4 border-b border-[#292524] flex items-center gap-2">
        <MessageSquare class="w-4 h-4 text-[#F9C86D]" />
        <h3 class="text-[16px] font-semibold text-[#F5F5F4] tracking-[-0.32px] leading-5">
          评论区
        </h3>
      </div>

      <!-- 2. 评论输入表单 -->
      <div class="p-4 flex flex-col gap-2 border-b border-[#292524]/60">
        <div class="w-full rounded-lg border border-[#44403C]/80 bg-[#292524]/40 p-3 flex flex-col focus-within:border-[#F9C86D]/60 transition-colors">
          <textarea
            v-model="commentText"
            :maxlength="maxChars"
            placeholder="分享你的想法和感受...（优质评论标准：1. 言之有物 2. 尊重他人 3. 至少有一定量有效聊天条数）"
            class="w-full h-20 bg-transparent border-none outline-none text-xs text-[#F5F5F4] placeholder-[#78716C]/60 resize-none font-sans leading-relaxed"
          />

          <div class="flex items-center justify-between pt-2 text-[11px] text-[#78716C]">
            <span>{{ maxChars - commentText.length }} 字符剩余</span>
            
            <button
              type="button"
              @click="handleSubmit"
              :disabled="!commentText.trim()"
              class="px-4 py-1 rounded-full border border-[#F9C86D]/40 bg-gradient-to-r from-[#A18D6F]/30 to-[#A18D6F]/20 text-xs font-medium text-[#F9C86D] disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 active:scale-95 transition-all cursor-pointer"
            >
              发表评论
            </button>
          </div>
        </div>
      </div>

      <!-- 3. 空状态展示 (插画 + 还没有评论 + 来发表第一条评论吧！) -->
      <div class="py-12 flex flex-col items-center justify-center gap-2 text-center">
        <div class="w-12 h-12 rounded-full bg-[#292524] border border-[#44403C] flex items-center justify-center text-[#78716C]">
          <MessageSquare class="w-6 h-6" />
        </div>
        <p class="text-[16px] font-medium text-[#A8A29E] mt-1">
          还没有评论
        </p>
        <p class="text-xs text-[#78716C]">
          来发表第一条评论吧！
        </p>
      </div>

    </div>
  </div>
</template>
