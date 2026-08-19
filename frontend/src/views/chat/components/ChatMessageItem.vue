<script setup lang="ts">
/**
 * AI 聊天界面 - 消息气泡条目组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { ChatMessage } from "@/views/chat/constants/mockChatData";
import { Check, Copy, GitFork, Pencil, RefreshCw, Trash2, Volume2 } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{
  message: ChatMessage;
}>();

const emit = defineEmits<{
  (e: "readAloud", msg: ChatMessage): void;
  (e: "regenerate", msg: ChatMessage): void;
  (e: "branch", msg: ChatMessage): void;
  (e: "edit", msg: ChatMessage): void;
  (e: "delete", msg: ChatMessage): void;
}>();

const copied = ref(false);

function handleCopy(): void {
  navigator.clipboard.writeText(props.message.content);
  copied.value = true;
  setTimeout(() => {
    copied.value = false;
  }, 1500);
}
</script>

<template>
  <div class="w-full flex flex-col gap-1 px-3 py-2">
    
    <!-- A. AI 角色消息 -->
    <div v-if="message.sender === 'ai'" class="w-full flex flex-col gap-1.5 animate-fade-in">
      
      <!-- 1. 角色头像 + 昵称 + 朗读按钮 -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <div class="w-8 h-8 rounded border border-[#44403C] overflow-hidden bg-[#292524] flex items-center justify-center shrink-0">
            <img
              v-if="message.avatarUrl"
              :src="message.avatarUrl"
              :alt="message.characterName"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-xs">🤖</span>
          </div>

          <span class="text-sm font-medium text-white/95 leading-5">
            {{ message.characterName || "AI 角色" }}
          </span>
        </div>

        <!-- 开始朗读语音按钮 -->
        <button
          type="button"
          @click="emit('readAloud', message)"
          class="w-7 h-7 rounded-full flex items-center justify-center text-white/60 hover:text-[#F9C86D] hover:bg-white/5 transition-all cursor-pointer"
          title="开始朗读"
        >
          <Volume2 class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- 2. AI 消息正文气泡 -->
      <div class="pl-10 pr-2">
        <div class="p-3.5 rounded-2xl rounded-tl-sm bg-[#292524]/60 border border-[#44403C]/50 text-sm text-white/90 leading-relaxed font-sans shadow-md">
          {{ message.content }}
        </div>

        <!-- 3. Token 消耗统计与指标 (输入: 9,217 | 输出: 5,976 | ✓) -->
        <div
          v-if="message.metrics"
          class="flex items-center justify-between pt-1.5 px-1 text-[11px] text-[#A18D6F] font-mono"
        >
          <div class="flex items-center gap-3">
            <span>输入: {{ message.metrics.inputTokens.toLocaleString() }}</span>
            <span>输出: {{ message.metrics.outputTokens.toLocaleString() }}</span>
            <span class="text-[#C0A480] font-sans">✓</span>
          </div>

          <!-- 4. 底部快捷操作微图标 (重生成、分支、复制、编辑、删除) -->
          <div class="flex items-center gap-1">
            <button
              type="button"
              @click="emit('regenerate', message)"
              title="重新生成"
              class="w-6 h-6 rounded border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#A8A29E] hover:text-[#F9C86D] transition-colors cursor-pointer"
            >
              <RefreshCw class="w-3 h-3" />
            </button>

            <button
              type="button"
              @click="emit('branch', message)"
              title="分叉剧情"
              class="w-6 h-6 rounded border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#A8A29E] hover:text-[#3B82F6] transition-colors cursor-pointer"
            >
              <GitFork class="w-3 h-3" />
            </button>

            <button
              type="button"
              @click="handleCopy"
              title="复制正文"
              class="w-6 h-6 rounded border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#A8A29E] hover:text-white transition-colors cursor-pointer"
            >
              <Check v-if="copied" class="w-3 h-3 text-[#22C55E]" />
              <Copy v-else class="w-3 h-3" />
            </button>
          </div>
        </div>
      </div>

    </div>

    <!-- B. 用户消息气泡 -->
    <div v-else class="w-full flex justify-end animate-fade-in pt-1 pb-1">
      <div class="flex flex-col items-end gap-1 max-w-[80%]">
        <!-- 气泡主体 -->
        <div class="px-4 py-2.5 rounded-2xl rounded-tr-sm bg-gradient-to-br from-[#F9C86D]/20 to-[#F9C86D]/10 border border-[#F9C86D]/40 text-sm text-white/95 leading-relaxed font-sans shadow-md">
          {{ message.content }}
        </div>

        <!-- 悬浮快捷微操作按钮 -->
        <div class="flex items-center gap-1.5 pr-1 opacity-0 hover:opacity-100 transition-opacity">
          <button
            type="button"
            @click="emit('edit', message)"
            class="w-5 h-5 rounded-full border border-[#F9C86D] bg-[#44403C] flex items-center justify-center text-[#F9C86D] hover:scale-105 transition-transform cursor-pointer"
            title="编辑"
          >
            <Pencil class="w-2.5 h-2.5" />
          </button>
          <button
            type="button"
            @click="emit('delete', message)"
            class="w-5 h-5 rounded-full border border-[#F9C86D] bg-[#44403C] flex items-center justify-center text-[#F9C86D] hover:scale-105 transition-transform cursor-pointer"
            title="删除"
          >
            <Trash2 class="w-2.5 h-2.5" />
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
