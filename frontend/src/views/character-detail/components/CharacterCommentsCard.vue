<script setup lang="ts">
/**
 * 角色卡详情 - 评论区模块 (1:1 原型高保真，支持真实评论渲染与发表)。
 *
 * @packageDocumentation
 */

import type { CharacterComment } from "@/services/character";
import { MessageSquare, ThumbsUp } from "lucide-vue-next";
import { ref } from "vue";

const props = withDefaults(
  defineProps<{
    comments?: CharacterComment[];
  }>(),
  {
    comments: () => [],
  }
);

const commentText = ref("");
const maxChars = 1000;

const emit = defineEmits<(e: "submitComment", text: string) => void>();

function handleSubmit(): void {
  if (!commentText.value.trim()) return;
  emit("submitComment", commentText.value.trim());
  commentText.value = "";
}

function formatCommentDate(dateStr: string): string {
  if (!dateStr) return "刚刚";
  try {
    const d = new Date(dateStr);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  } catch {
    return "刚刚";
  }
}
</script>

<template>
  <div class="w-full px-3 pt-3 select-none">
    <div class="w-full rounded-lg border border-[#292524] bg-[#1A1714]/95 flex flex-col overflow-hidden">
      
      <!-- 1. 评论区标题 -->
      <div class="p-4 border-b border-[#292524] flex items-center justify-between">
        <div class="flex items-center gap-2">
          <MessageSquare class="w-4 h-4 text-[#F9C86D]" />
          <h3 class="text-[16px] font-semibold text-[#F5F5F4] tracking-[-0.32px] leading-5">
            评论区
          </h3>
        </div>
        <span class="text-xs text-[#78716C]">
          共 {{ comments.length }} 条评价
        </span>
      </div>

      <!-- 2. 评论输入表单 -->
      <div class="p-4 flex flex-col gap-2 border-b border-[#292524]/60">
        <div class="w-full rounded-lg border border-[#44403C]/80 bg-[#292524]/40 p-3 flex flex-col focus-within:border-[#F9C86D]/60 transition-colors">
          <textarea
            v-model="commentText"
            :maxlength="maxChars"
            placeholder="分享你的想法和感受...（优质评论标准：1. 言之有物 2. 尊重他人 3. 真实体验）"
            class="w-full h-20 bg-transparent border-none outline-none text-xs text-[#F5F5F4] placeholder-[#78716C]/60 resize-none font-sans leading-relaxed"
          />

          <div class="flex items-center justify-between pt-2 text-[11px] text-[#78716C]">
            <span>{{ maxChars - commentText.length }} 字符剩余</span>
            
            <button
              type="button"
              @click="handleSubmit"
              :disabled="!commentText.trim()"
              class="px-4 py-1 rounded-full border-[1px] border-solid border-[#F9C86D]/40 bg-gradient-to-r from-[#A18D6F]/30 to-[#A18D6F]/20 text-xs font-medium text-[#F9C86D] disabled:opacity-40 disabled:cursor-not-allowed hover:brightness-110 active:scale-95 transition-all cursor-pointer"
            >
              发表评论
            </button>
          </div>
        </div>
      </div>

      <!-- 3. 评论列表 -->
      <div v-if="comments.length > 0" class="flex flex-col divide-y divide-[#292524]/50">
        <div
          v-for="item in comments"
          :key="item.id"
          class="p-4 flex gap-3 animate-fade-in"
        >
          <img
            :src="item.avatar_url"
            :alt="item.username"
            class="w-8 h-8 rounded-full border border-[#44403C] object-cover shrink-0"
          />
          <div class="flex-1 flex flex-col gap-1">
            <div class="flex items-center justify-between">
              <span class="text-xs font-medium text-[#E7E5E4]">{{ item.username }}</span>
              <span class="text-[10px] text-[#78716C]">{{ formatCommentDate(item.created_at) }}</span>
            </div>
            <p class="text-xs text-[#D6D3D1] leading-relaxed break-words whitespace-pre-wrap">
              {{ item.content }}
            </p>
          </div>
        </div>
      </div>

      <!-- 4. 空状态展示 -->
      <div v-else class="py-12 flex flex-col items-center justify-center gap-2 text-center">
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
