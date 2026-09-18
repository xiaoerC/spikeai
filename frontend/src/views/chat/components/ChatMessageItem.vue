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

import { useUserStore } from "@/stores/user";
import ChatMessageMenu from "@/views/chat/components/ChatMessageMenu.vue";
import MessageHtmlSandbox from "@/views/chat/components/MessageHtmlSandbox.vue";
import { useAudioPlayer } from "@/views/chat/composables/useAudioPlayer";
import type { ChatMessage } from "@/views/chat/constants/mockChatData";
import DOMPurify from "dompurify";
import {
  AlertTriangle,
  ArrowUp,
  Brain,
  ChevronDown,
  Loader2,
  MoreHorizontal,
  RotateCcw,
  Volume2,
} from "lucide-vue-next";
import { computed, nextTick, ref } from "vue";

const {
  currentMessageId,
  isPlaying: isAudioPlaying,
  isLoading: isAudioLoading,
  togglePlay: toggleAudioPlay,
} = useAudioPlayer();

const props = withDefaults(
  defineProps<{
    message: ChatMessage;
    isFirstMessage?: boolean;
    alternateGreetings?: readonly string[];
    currentGreetingIndex?: number;
  }>(),
  {
    isFirstMessage: false,
    alternateGreetings: () => [],
    currentGreetingIndex: 0,
  },
);

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
  (e: "switchGreeting", index: number): void;
}>();

function handlePrevGreeting(): void {
  const total = props.alternateGreetings?.length || 1;
  const current = props.currentGreetingIndex || 0;
  const prev = (current - 1 + total) % total;
  emit("switchGreeting", prev);
}

function handleNextGreeting(): void {
  const total = props.alternateGreetings?.length || 1;
  const current = props.currentGreetingIndex || 0;
  const next = (current + 1) % total;
  emit("switchGreeting", next);
}

const isMenuOpen = ref(false);
const isEditing = ref(false);
const isThinkingExpanded = ref(false);
const editContent = ref("");
const editTextareaRef = ref<HTMLTextAreaElement | null>(null);

export interface MessageSegment {
  id: string;
  type: "text" | "html";
  content: string;
  title?: string;
}

const userStore = useUserStore();

/**
 * 消息内容分段解析：将包含的 ```html ... ``` 独立拆解为沙箱挂件段落与纯小说正文段落
 */
const messageSegments = computed<MessageSegment[]>(() => {
  if (!props.message.content) return [];

  const currentUserName = userStore.profile?.username || "你";

  // 1. 展开 {{user}} 宏，消除底层变量定义块、叙梦增量标签与泄漏的增量 JSON 字典 (彻底消除图 1 宏残留与图 2 裸 JSON 泄漏)
  const baseContent = props.message.content
    .replace(/{{user}}/g, currentUserName)
    .replace(/<narrative_delta>[\s\S]*?<\/narrative_delta>/gi, "")
    .replace(/<narrative_delta>[\s\S]*?$/gi, "")
    .replace(
      /```(?:json)?\s*\{[\s\S]*?"(?:new_event|history_events|player_states|variables|location|date_text|time_text|tasks|consumables|social_relations)"[\s\S]*?\}\s*```\s*$/gi,
      "",
    )
    .replace(
      /\{\s*"(?:new_event|history_events|player_states|variables|location|date_text|time_text|tasks|consumables|social_relations)"[\s\S]*?\}\s*$/gi,
      "",
    )
    .replace(/<initvar>[\s\S]*?<\/initvar>/gi, "")
    .replace(/<UpdateVariable>[\s\S]*?<\/UpdateVariable>/gi, "")
    .replace(/<(?:SceneHeaderPlaceHolder|StatusPlaceHolderImpl)\s*\/?>/gi, "")
    .trim();

  if (!baseContent) return [];

  // 2. 正则匹配 ```html ... ``` 代码块
  const htmlRegex = /```html\s*([\s\S]*?)```/gi;
  const segments: MessageSegment[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = htmlRegex.exec(baseContent)) !== null) {
    const textPart = baseContent.slice(lastIndex, match.index).trim();
    if (textPart) {
      segments.push({
        id: `text-${segments.length}`,
        type: "text",
        content: textPart,
      });
    }

    const htmlBody = match[1]?.trim() || match[0];
    let title = "剧情互动挂件";
    if (htmlBody.includes("昼夜") || htmlBody.includes("时间") || htmlBody.includes("地点")) {
      title = "昼夜时空状态";
    } else if (htmlBody.includes("MVU") || htmlBody.includes("状态") || htmlBody.includes("好感")) {
      title = "MVU 角色数值状态栏";
    }

    segments.push({
      id: `html-${segments.length}`,
      type: "html",
      content: htmlBody,
      title,
    });

    lastIndex = match.index + match[0].length;
  }

  const remainingText = baseContent.slice(lastIndex).trim();
  if (remainingText) {
    segments.push({
      id: `text-${segments.length}`,
      type: "text",
      content: remainingText,
    });
  }

  // 若无 html 代码块，整体作为单一文本段落
  if (segments.length === 0) {
    segments.push({
      id: "text-0",
      type: "text",
      content: baseContent,
    });
  }

  return segments;
});

/**
 * 安全渲染局部 HTML 标签：
 * 放行 span, font, b, i, ruby, details 等富文本标签与 style, color 等安全样式属性，
 * 严格过滤 script, iframe, onerror 等高危标签与脚本注入，防止 XSS 攻击。
 */
function sanitizeInlineHtml(raw: string): string {
  if (!raw) return "";
  return DOMPurify.sanitize(raw, {
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
    ALLOWED_ATTR: ["style", "color", "size", "face", "class", "title", "open", "align", "dir"],
  });
}

/**
 * 纯剧情正文（供 TTS 语音合成朗读，剔除所有前端挂件代码与局部 HTML 标签）
 */
const speechCleanText = computed(() => {
  return messageSegments.value
    .filter((s) => s.type === "text")
    .map((s) => s.content.replace(/<[^>]+>/g, "").trim())
    .filter(Boolean)
    .join("\n\n");
});

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
        <div class="flex items-center gap-2 min-w-0">
          <div class="w-8 h-8 rounded border border-[#44403C] overflow-hidden bg-[#292524] flex items-center justify-center shrink-0">
            <img
              v-if="message.avatarUrl"
              :src="message.avatarUrl"
              :alt="message.characterName"
              class="w-full h-full object-cover"
            />
            <span v-else class="text-xs">🤖</span>
          </div>

          <span class="text-sm font-medium text-white/95 leading-5 truncate max-w-[170px]" :title="message.characterName || ''">
            {{ message.characterName || "AI 角色" }}
          </span>

          <!-- 备选开场白切换器 (第一条消息且存在多条开场白时显示) -->
          <div
            v-if="isFirstMessage && alternateGreetings && alternateGreetings.length > 1"
            class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[#1C1917]/90 border border-[#F9C86D]/40 text-xs text-[#F9C86D] shadow-sm select-none shrink-0"
          >
            <button
              type="button"
              @click="handlePrevGreeting"
              class="hover:text-white transition-colors cursor-pointer px-0.5 font-bold"
              title="上一条开场白"
            >
              ‹
            </button>
            <span class="font-mono text-[11px]">{{ (currentGreetingIndex || 0) + 1 }}/{{ alternateGreetings.length }}</span>
            <button
              type="button"
              @click="handleNextGreeting"
              class="hover:text-white transition-colors cursor-pointer px-0.5 font-bold"
              title="下一条开场白"
            >
              ›
            </button>
          </div>
        </div>

        <!-- 开始朗读语音按钮 (集成 Edge-TTS 与声波跳动) -->
        <button
          type="button"
          @click="toggleAudioPlay(message.id, speechCleanText || message.content); emit('readAloud', message)"
          :class="[
            'w-7 h-7 rounded-full flex items-center justify-center transition-all cursor-pointer',
            currentMessageId === message.id && isAudioPlaying
              ? 'text-[#F9C86D] bg-[#F9C86D]/15 shadow-[0_0_10px_rgba(249,200,109,0.3)]'
              : 'text-white/60 hover:text-[#F9C86D] hover:bg-white/5'
          ]"
          :title="currentMessageId === message.id && isAudioPlaying ? '暂停朗读' : '朗读对白'"
        >
          <!-- 加载转圈 -->
          <Loader2
            v-if="currentMessageId === message.id && isAudioLoading"
            class="w-3.5 h-3.5 animate-spin text-[#F9C86D]"
          />
          <!-- 律动声波 -->
          <div
            v-else-if="currentMessageId === message.id && isAudioPlaying"
            class="flex items-end gap-0.5 h-3"
          >
            <span class="w-0.5 h-1.5 bg-[#F9C86D] animate-bounce" style="animation-delay: 0ms;" />
            <span class="w-0.5 h-3 bg-[#F9C86D] animate-bounce" style="animation-delay: 150ms;" />
            <span class="w-0.5 h-2 bg-[#F9C86D] animate-bounce" style="animation-delay: 300ms;" />
          </div>
          <!-- 常态喇叭 -->
          <Volume2 v-else class="w-3.5 h-3.5" />
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

        <!-- 正常正文气泡 (支持 60fps 平滑打字机、黑金呼吸光标与 HTML 沙箱挂件) -->
        <div
          v-else
          class="p-3.5 rounded-2xl rounded-tl-sm bg-[#292524]/60 border border-[#44403C]/50 text-sm text-white/90 leading-relaxed font-sans shadow-md flex flex-col gap-2.5"
        >
          <template v-if="messageSegments.length > 0">
            <template v-for="segment in messageSegments" :key="segment.id">
              <!-- A. 纯文本与局部 HTML 正文 (支持 <span style="...">, <font>, <ruby>, <details> 等) -->
              <div v-if="segment.type === 'text'" class="whitespace-pre-wrap leading-relaxed inline-rich-text">
                <span v-html="sanitizeInlineHtml(segment.content)" />
                <span
                  v-if="message.status === 'streaming'"
                  class="inline-block w-1.5 h-3.5 ml-0.5 align-middle bg-[#F9C86D] animate-pulse shadow-[0_0_8px_rgba(249,200,109,0.8)]"
                />
              </div>

              <!-- B. 交互式 HTML/JS 挂件 (沙箱隔离容器) -->
              <MessageHtmlSandbox
                v-else-if="segment.type === 'html'"
                :html="segment.content"
                :title="segment.title"
              />
            </template>
          </template>
          <span v-else class="inline-flex items-center gap-1.5 text-[#F9C86D] animate-pulse">
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

          <!-- 中间: Token 消耗统计 (输入/输出/✓) - 开场白严格不显示 -->
          <div
            v-if="message.metrics && !isFirstMessage && (message.metrics.inputTokens > 0 || message.metrics.outputTokens > 0)"
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

        <!-- 用户消息气泡操作按钮 (仅保留【修改】📝) -->
        <div class="flex items-center gap-1.5 pr-0.5">
          
          <!-- 按钮: 修改 (正方形框带斜笔 SVG) -->
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

        </div>
      </div>

    </div>

  </div>
</template>

<style scoped>
:deep(.inline-rich-text) {
  word-break: break-word;
}
:deep(.inline-rich-text ruby) {
  ruby-position: over;
}
:deep(.inline-rich-text rt) {
  font-size: 0.65em;
  opacity: 0.85;
}
:deep(.inline-rich-text details) {
  margin: 0.35rem 0;
  padding: 0.4rem 0.6rem;
  border-radius: 0.5rem;
  background: rgba(35, 31, 28, 0.7);
  border: 1px solid rgba(249, 200, 109, 0.2);
}
:deep(.inline-rich-text summary) {
  cursor: pointer;
  color: #f9c86d;
  font-weight: 500;
  user-select: none;
}
</style>
