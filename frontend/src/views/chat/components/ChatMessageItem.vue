<script setup lang="ts">
/**
 * AI 聊天界面 - 消息气泡条目组件 (1:1 原型高保真)
 *
 * 严格按照 Figma 原型 (Frame 104:8282 & 用户消息双按钮媒体原型) 与设计规范：
 * - AI 消息: 头像 + 角色名 + 朗读按钮 + 正文气泡 + 底部统计与「···」操作菜单
 * - 消息菜单: 120px 宽悬浮菜单（重新生成、重跑记忆增强、续写500/500、编辑、分享、开新档、删除）
 * - 用户消息:
 *   1. 常态: 右下角 1:1 双黑金圆形按钮（修改 📝 + 剧情分支 📈）
 *   2. 编辑态 (方案 A): 内联多行深色编辑文本框 + 取消 / 仅保存 / 保存并重新生成
 *
 * @packageDocumentation
 */

import ChatMessageMenu from "@/views/chat/components/ChatMessageMenu.vue";
import type { ChatMessage } from "@/views/chat/constants/mockChatData";
import {
  AlertTriangle,
  ArrowUp,
  Brain,
  ChevronDown,
  MoreHorizontal,
  RotateCcw,
  Volume2,
} from "lucide-vue-next";
import { nextTick, ref } from "vue";

const props = defineProps<{
  message: ChatMessage;
}>();

const emit = defineEmits<{
  (e: "readAloud", msg: ChatMessage): void;
  (e: "regenerate", msg: ChatMessage): void;
  (e: "rerunMemory", msg: ChatMessage): void;
  (e: "continue", msg: ChatMessage): void;
  (e: "branch", msg: ChatMessage): void;
  (e: "edit", msg: ChatMessage): void;
  (e: "saveEdit", msg: ChatMessage, newContent: string, regenerate: boolean): void;
  (e: "share", msg: ChatMessage): void;
  (e: "delete", msg: ChatMessage): void;
}>();

const isMenuOpen = ref(false);
const isEditing = ref(false);
const isThinkingExpanded = ref(false);
const editContent = ref("");
const editTextareaRef = ref<HTMLTextAreaElement | null>(null);

function toggleMenu(): void {
  isMenuOpen.value = !isMenuOpen.value;
}

function handleMenuAction(action: string): void {
  switch (action) {
    case "regenerate":
      emit("regenerate", props.message);
      break;
    case "rerunMemory":
      emit("rerunMemory", props.message);
      break;
    case "continue":
      emit("continue", props.message);
      break;
    case "branch":
      emit("branch", props.message);
      break;
    case "edit":
      startEditing();
      break;
    case "share":
      emit("share", props.message);
      break;
    case "delete":
      emit("delete", props.message);
      break;
  }
}

function startEditing(): void {
  editContent.value = props.message.content;
  isEditing.value = true;
  nextTick(() => {
    if (editTextareaRef.value) {
      editTextareaRef.value.focus();
      editTextareaRef.value.select();
    }
  });
}

function cancelEditing(): void {
  isEditing.value = false;
  editContent.value = "";
}

function saveEdit(regenerate: boolean): void {
  if (!editContent.value.trim()) return;
  emit("saveEdit", props.message, editContent.value.trim(), regenerate);
  isEditing.value = false;
}

function handleEditKeydown(e: KeyboardEvent): void {
  if (e.key === "Escape") {
    e.preventDefault();
    cancelEditing();
  } else if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    saveEdit(true);
  }
}
</script>

<template>
  <div class="w-full flex flex-col gap-1 px-3 py-2">
    
    <!-- ==================== A. AI 角色消息 ==================== -->
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

      <!-- 2. AI 消息正文气泡 (支持思考流展开/收起) -->
      <div class="pl-10 pr-2">
        <!-- 思考流卡片 -->
        <div v-if="message.thinkingContent" class="mb-2">
          <button
            type="button"
            @click="isThinkingExpanded = !isThinkingExpanded"
            class="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#231F1C] border border-[#F9C86D]/20 text-xs text-[#F9C86D]/90 hover:bg-[#2A2420] transition-colors cursor-pointer"
          >
            <Brain class="w-3.5 h-3.5 text-[#F9C86D]" />
            <span>深度思考过程 ({{ message.thinkingContent.length }} 字)</span>
            <ChevronDown :class="['w-3.5 h-3.5 transition-transform duration-200', isThinkingExpanded ? 'rotate-180' : '']" />
          </button>
          <div
            v-if="isThinkingExpanded"
            class="mt-1.5 p-3 rounded-lg bg-[#1D1916]/80 border border-[#F9C86D]/15 text-xs text-gray-300 font-sans leading-relaxed whitespace-pre-wrap shadow-inner"
          >
            {{ message.thinkingContent }}
          </div>
        </div>

        <!-- 错误失败态气泡 -->
        <div
          v-if="message.status === 'error' || message.errorMessage"
          class="p-3.5 rounded-2xl rounded-tl-sm bg-[#2A1515]/90 border border-[#EF4444]/50 text-sm text-red-200 leading-relaxed font-sans shadow-lg flex flex-col gap-2.5"
        >
          <div class="flex items-center gap-2 text-red-400 font-medium">
            <AlertTriangle class="w-4 h-4 shrink-0 text-red-400" />
            <span class="text-xs">{{ message.errorMessage || "大模型请求失败或网络中断" }}</span>
          </div>

          <div v-if="message.content" class="text-xs text-gray-300 whitespace-pre-wrap border-t border-red-500/20 pt-2 opacity-80">
            {{ message.content }}
          </div>

          <div class="flex items-center gap-2 pt-1 border-t border-white/5">
            <button
              type="button"
              @click="emit('regenerate', message)"
              class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gradient-to-r from-[#F9C86D] to-[#E6B04D] text-[#0C0A09] text-xs font-bold hover:brightness-110 active:scale-95 transition-all shadow-md cursor-pointer"
            >
              <RotateCcw class="w-3.5 h-3.5" />
              <span>重新生成</span>
            </button>
          </div>
        </div>

        <!-- 正常正文气泡 -->
        <div
          v-else
          class="p-3.5 rounded-2xl rounded-tl-sm bg-[#292524]/60 border border-[#44403C]/50 text-sm text-white/90 leading-relaxed font-sans shadow-md whitespace-pre-wrap"
        >
          <template v-if="message.content">
            {{ message.content }}
          </template>
          <span v-else class="inline-flex items-center gap-1 text-[#F9C86D] animate-pulse">
            <span class="w-2 h-2 rounded-full bg-[#F9C86D]"></span>
            <span>正在沉浸式构思剧情……</span>
          </span>
        </div>

        <!-- 3. Token 消耗统计与指标 (输入: 72,502 | 输出: 65,536 | ✓) 及底部操作栏 -->
        <div class="flex items-center justify-between pt-2 px-1">
          
          <!-- 左下角: 「···」三点操作按钮 (点击展开 120px 菜单) -->
          <div class="relative z-30">
            <button
              type="button"
              @click.stop="toggleMenu"
              :class="[
                'w-7 h-7 rounded-md border flex items-center justify-center transition-all cursor-pointer shadow-sm',
                isMenuOpen
                  ? 'border-[#F9C86D] bg-[#292524] text-[#F9C86D] shadow-[0_0_8px_rgba(249,200,109,0.3)]'
                  : 'border-[#44403C] bg-[#292524]/80 text-[#A8A29E] hover:text-[#F5F5F4] hover:border-[#F9C86D]/40'
              ]"
              title="更多操作"
            >
              <MoreHorizontal class="w-4 h-4" />
            </button>

            <!-- 1:1 聊天信息操作菜单 (Frame 104:8282) -->
            <ChatMessageMenu
              v-model:open="isMenuOpen"
              @select="handleMenuAction"
            />
          </div>

          <!-- 中间: Token 消耗统计 (输入/输出/✓) -->
          <div
            v-if="message.metrics"
            class="flex items-center gap-2 text-[11px] font-mono text-[#A8A29E]"
          >
            <span>输入: <span class="text-[#22C55E]">{{ message.metrics.inputTokens.toLocaleString() }}</span></span>
            <span>输出: {{ message.metrics.outputTokens.toLocaleString() }}</span>
            <span class="text-[#22C55E] font-sans font-bold">✓</span>
          </div>

          <!-- 右下角: ↑ 快捷向上按钮 -->
          <button
            type="button"
            class="w-7 h-7 rounded-md border border-[#44403C] bg-[#292524]/80 flex items-center justify-center text-[#A8A29E] hover:text-[#F9C86D] transition-colors cursor-pointer shadow-sm"
            title="回到顶部"
          >
            <ArrowUp class="w-3.5 h-3.5" />
          </button>

        </div>
      </div>

    </div>

    <!-- ==================== B. 用户消息气泡 (1:1 双黑金圆形按钮与内联编辑模式) ==================== -->
    <div v-else class="w-full flex justify-end animate-fade-in pt-1 pb-1">
      
      <!-- 1. 编辑状态 (方案 A: 内联气泡编辑框) -->
      <div
        v-if="isEditing"
        class="w-full max-w-[90%] p-3 rounded-2xl rounded-tr-sm bg-[#1C1917]/95 border border-[#D1A35C]/60 backdrop-blur-xl shadow-2xl flex flex-col gap-2.5 animate-fade-in"
      >
        <textarea
          ref="editTextareaRef"
          v-model="editContent"
          rows="4"
          placeholder="编辑发送的内容..."
          @keydown="handleEditKeydown"
          class="w-full bg-transparent border-none outline-none resize-none text-[14px] text-white/95 placeholder-white/40 font-sans leading-relaxed tracking-tight [scrollbar-width:thin]"
        />

        <!-- 底部快捷控制栏 -->
        <div class="flex items-center justify-between pt-1 border-t border-white/10 text-xs">
          <span class="text-[10px] text-white/40 font-mono hidden sm:inline">
            Esc 取消 · Ctrl+Enter 保存
          </span>

          <div class="flex items-center gap-2 ml-auto">
            <!-- 取消 -->
            <button
              type="button"
              @click="cancelEditing"
              class="px-2.5 py-1 rounded-md border border-[#44403C] bg-white/5 text-[#A8A29E] hover:text-white transition-colors cursor-pointer"
            >
              取消
            </button>

            <!-- 仅保存 -->
            <button
              type="button"
              @click="saveEdit(false)"
              class="px-2.5 py-1 rounded-md border border-[#44403C] bg-[#292524] text-white/90 hover:border-[#F9C86D]/40 transition-colors cursor-pointer"
            >
              仅保存
            </button>

            <!-- 保存并重新生成 -->
            <button
              type="button"
              @click="saveEdit(true)"
              class="px-3 py-1 rounded-md bg-[#F9C86D] text-[#0C0A09] font-medium hover:scale-105 active:scale-95 transition-transform cursor-pointer shadow-sm"
            >
              保存并重新生成
            </button>
          </div>
        </div>
      </div>

      <!-- 2. 常态用户消息气泡 (1:1 media_1787487946692.png) -->
      <div v-else class="flex flex-col items-end gap-1.5 max-w-[85%]">
        <!-- 气泡主体 -->
        <div class="px-4 py-2.5 rounded-2xl rounded-tr-sm bg-gradient-to-br from-[#F9C86D]/20 to-[#F9C86D]/10 border border-[#F9C86D]/40 text-sm text-white/95 leading-relaxed font-sans shadow-md">
          {{ message.content }}
        </div>

        <!-- 1:1 双黑金圆形操作按钮组 (修改 📝 + 剧情分支 📈) -->
        <div class="flex items-center gap-1.5 pr-0.5">
          
          <!-- 按钮 1: 修改 (正方形框带斜笔 SVG) -->
          <button
            type="button"
            @click="startEditing"
            class="w-[26px] h-[26px] rounded-full border border-[#D1A35C]/80 bg-[#292524] flex items-center justify-center text-white/90 hover:scale-110 active:scale-95 hover:border-[#F9C86D] hover:text-[#F9C86D] transition-all cursor-pointer shadow-sm"
            title="修改本条消息"
          >
            <svg width="13" height="13" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M6.41667 2.33333H2.33333C1.78105 2.33333 1.33333 2.78105 1.33333 3.33333V11.6667C1.33333 12.2189 1.78105 12.6667 2.33333 12.6667H10.6667C11.2189 12.6667 11.6667 12.2189 11.6667 11.6667V7.58333" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10.7917 1.45833C11.1368 1.11316 11.6965 1.11316 12.0417 1.45833C12.3868 1.80351 12.3868 2.36316 12.0417 2.70833L6.125 8.625L4.08333 9.16667L4.625 7.125L10.7917 1.45833Z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <!-- 按钮 2: 剧情分支/折线树 (直角坐标折线图 SVG) -->
          <button
            type="button"
            @click="emit('branch', message)"
            class="w-[26px] h-[26px] rounded-full border border-[#D1A35C]/80 bg-[#292524] flex items-center justify-center text-white/90 hover:scale-110 active:scale-95 hover:border-[#F9C86D] hover:text-[#F9C86D] transition-all cursor-pointer shadow-sm"
            title="从此节点开新剧情分支"
          >
            <svg width="13" height="13" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.33333 2.33333V11.6667H11.6667" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4.66667 8.16667L7.58333 5.25L9.33333 7L11.6667 4.08333" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

        </div>
      </div>

    </div>

  </div>
</template>
