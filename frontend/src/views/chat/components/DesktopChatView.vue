<script setup lang="ts">
/**
 * 叙梦 Naro - PC 桌面端沉浸剧场式 AI 对话组件 (DesktopChatView.vue)
 *
 * 1:1 像素级还原参考原型图 media_1789565500457.png：
 * 1. 顶部 Header：
 *    - 左侧: [< 离开对话] 胶囊按钮 + 角色圆形头像 + 角色全名/标题
 *    - 右侧: [⚡ Naro助手] (金) + [🔀 节点伪造] (蓝) + [🌲 主线剧情] (绿) + [➡️ 隐藏剧情] (灰) + [⚙️ 设置]
 * 2. 中部舞台：
 *    - 右侧: 1:1 站姿角色超清全身立绘与氛围景深（自然融入场景）
 *    - 左侧: 视觉小说 / Galgame 式故事叙事流 (消除圆角气泡框，沉浸排版，支持变量监控与可选行动快捷填充)
 *    - 底部: Token 消耗实时指示器 (输入: 83,965 输出: 1,258 ✓) 与浮动滚动置顶/底按钮
 * 3. 底部操作区：
 *    - 宽屏大输入框: 提示 "输入消息...(shift enter)" + 右下角 ⤢ 展开与「发送」按钮
 *    - 底部状态胶囊条: [∧ 展开控制] + [✦ 快速双子星3 | ⚡ 18 金币免费(0/30) ∨] + [⭐ 466  🍇 1,522] + [📜 插件]
 *
 * @packageDocumentation
 */

import { useUserStore } from "@/stores/user";
import ChatNoticeBanner from "@/views/chat/components/ChatNoticeBanner.vue";
import ChatSettingsMenu from "@/views/chat/components/ChatSettingsMenu.vue";
import { useAudioPlayer } from "@/views/chat/composables/useAudioPlayer";
import type { AiModelItem, ChatMessage } from "@/views/chat/constants/mockChatData";
import DOMPurify from "dompurify";
import {
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  Brain,
  ChevronDown,
  ChevronUp,
  GitBranch,
  GitFork,
  Maximize2,
  Minimize2,
  RotateCcw,
  Scroll,
  Settings,
  Sparkles,
  Square,
  Trash2,
  Volume2,
} from "lucide-vue-next";
import { computed, nextTick, ref, watch } from "vue";

export interface DesktopChatProps {
  character: {
    id: string;
    name: string;
    avatarUrl?: string;
    backgroundUrl?: string;
    backgroundImageUrl?: string;
    authorNote?: string;
    prologueTitle?: string;
    prologueContent?: string;
    tags?: readonly string[];
  };
  messages: ChatMessage[];
  currentModel: AiModelItem;
  currentMode: "story" | "room";
  isGenerating?: boolean;
  alternateGreetings?: readonly string[];
  currentGreetingIndex?: number;
}

const props = withDefaults(defineProps<DesktopChatProps>(), {
  isGenerating: false,
  alternateGreetings: () => [],
  currentGreetingIndex: 0,
});

const emit = defineEmits<{
  (e: "back"): void;
  (e: "send", text: string): void;
  (e: "stop"): void;
  (e: "regenerate", msg: ChatMessage): void;
  (e: "rerunMemory", msg: ChatMessage): void;
  (e: "continue", msg: ChatMessage): void;
  (e: "branch", msg: ChatMessage): void;
  (e: "edit", msg: ChatMessage): void;
  (e: "saveEdit", msg: ChatMessage, text: string, regen: boolean): void;
  (e: "delete", msg: ChatMessage): void;
  (e: "readAloud", msg: ChatMessage): void;
  (e: "switchGreeting", index: number): void;
  (e: "openAssistant"): void;
  (e: "openBranchCanvas"): void;
  (e: "openBranchDrawer"): void;
  (e: "openNarrativePanel"): void;
  (e: "openControlPanel"): void;
  (e: "openModelSelector"): void;
  (e: "openModManager"): void;
  (e: "settingsAction", action: string): void;
}>();

const userStore = useUserStore();
const {
  currentMessageId,
  isPlaying: isAudioPlaying,
  togglePlay: toggleAudioPlay,
} = useAudioPlayer();

// 输入状态
const inputText = ref("");
const isExpandedInput = ref(false);
const isSettingsOpen = ref(false);
const scrollContainerRef = ref<HTMLElement | null>(null);
const textareaRef = ref<HTMLTextAreaElement | null>(null);

// 编辑状态
const editingMessageId = ref<string | null>(null);
const editContent = ref("");

// 深度思考折叠映射
const expandedThinkingIds = ref<Record<string, boolean>>({});

function toggleThinking(msgId: string): void {
  expandedThinkingIds.value[msgId] = !expandedThinkingIds.value[msgId];
}

/** 触发发送 */
function handleSend(): void {
  const text = inputText.value.trim();
  if (!text || props.isGenerating) return;
  emit("send", text);
  inputText.value = "";
  if (isExpandedInput.value) {
    isExpandedInput.value = false;
  }
}

/** 键盘回车发送（Shift+Enter 换行） */
function handleKeydown(e: KeyboardEvent): void {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSend();
  }
}

/** 切换输入框全屏/常规高度 */
function toggleExpandInput(): void {
  isExpandedInput.value = !isExpandedInput.value;
  nextTick(() => {
    textareaRef.value?.focus();
  });
}

/** 供外部注入文本（例如助手指令或行动候选项） */
function appendPrompt(text: string): void {
  if (inputText.value) {
    inputText.value += ` ${text}`;
  } else {
    inputText.value = text;
  }
  nextTick(() => {
    textareaRef.value?.focus();
  });
}

/** 滚动置顶/置底 */
function handleScrollToggle(): void {
  if (!scrollContainerRef.value) return;
  const { scrollTop, scrollHeight } = scrollContainerRef.value;
  if (scrollTop < 100) {
    scrollContainerRef.value.scrollTo({ top: scrollHeight, behavior: "smooth" });
  } else {
    scrollContainerRef.value.scrollTo({ top: 0, behavior: "smooth" });
  }
}

// 自动滚动到底部
watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      if (scrollContainerRef.value) {
        scrollContainerRef.value.scrollTop = scrollContainerRef.value.scrollHeight;
      }
    });
  },
);

// 提取最新一条 AI 消息的 Token 监控统计
const latestAiMetrics = computed(() => {
  for (let i = props.messages.length - 1; i >= 0; i--) {
    const m = props.messages[i];
    if (m.sender === "ai" && m.metrics) {
      return m.metrics;
    }
  }
  return {
    inputTokens: 83965,
    outputTokens: 1258,
    isSuccess: true,
  };
});

/** 净化 HTML 富文本 */
function sanitizeHtml(raw: string): string {
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
      "p",
      "div",
      "br",
      "hr",
      "ruby",
      "rt",
      "rp",
      "details",
      "summary",
      "mark",
      "small",
    ],
    ALLOWED_ATTR: ["style", "color", "class", "align"],
  });
}

defineExpose({
  appendPrompt,
});
</script>

<template>
  <div class="flex flex-col h-full w-full relative overflow-hidden bg-[#100D0B] text-[#F5F5F4] select-none font-sans">
    
    <!-- 0. 全屏景深暗色背景 -->
    <div
      v-if="character.backgroundUrl || character.backgroundImageUrl"
      class="absolute inset-0 z-0 bg-cover bg-center pointer-events-none opacity-20 filter blur-[2px]"
      :style="{ backgroundImage: `url('${character.backgroundUrl || character.backgroundImageUrl}')` }"
    />
    <div class="absolute inset-0 z-0 bg-gradient-to-b from-[#16120E] via-[#100D0B]/95 to-[#0C0A09] pointer-events-none" />

    <!-- ==================== 1. 顶部 1:1 Desktop Header ==================== -->
    <header class="h-14 w-full px-6 flex items-center justify-between border-b border-white/5 bg-[#16120E]/85 backdrop-blur-md z-30 shrink-0">
      
      <!-- 1.1 左侧: [< 离开对话] 胶囊按钮 + 角色头像 + 角色名 -->
      <div class="flex items-center gap-3 min-w-0">
        <!-- 离开对话药丸按钮 -->
        <button
          type="button"
          @click="emit('back')"
          class="h-8 px-3 rounded-full bg-[#201A14]/90 border border-white/10 hover:border-[#F9C86D]/40 text-[#D6D3D1] hover:text-white flex items-center gap-1.5 text-xs font-medium cursor-pointer transition-colors shadow-sm active:scale-95 shrink-0"
        >
          <ArrowLeft class="w-3.5 h-3.5" />
          <span>离开对话</span>
        </button>

        <!-- 角色圆形头像 -->
        <div class="w-8 h-8 rounded-full border border-[#F9C86D]/40 overflow-hidden bg-[#2D2318] shrink-0 shadow-sm">
          <img
            v-if="character.avatarUrl"
            :src="character.avatarUrl"
            :alt="character.name"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-xs text-[#F9C86D]">
            ✦
          </div>
        </div>

        <!-- 角色全名 / 标题 -->
        <div class="flex items-center gap-1.5 min-w-0">
          <span class="text-sm font-bold text-[#F5F5F4] tracking-wide truncate max-w-[220px]" :title="character.name">
            {{ character.name || "当前对话角色" }}
          </span>
          <span class="text-xs text-[#F9C86D]">···</span>
        </div>
      </div>

      <!-- 1.2 右侧: 4 个功能胶囊按钮 + 设置齿轮 (1:1 还原 media_1789565500457.png) -->
      <div class="flex items-center gap-2.5">
        
        <!-- (1) ⚡ Naro助手 (金边金色高光) -->
        <button
          type="button"
          @click="emit('openAssistant')"
          class="h-8 px-3.5 rounded-full bg-[#2A2117] border border-[#F9C86D]/40 hover:border-[#F9C86D] text-[#F9C86D] text-xs font-medium flex items-center gap-1.5 hover:bg-[#382D1E] cursor-pointer transition-all shadow-sm active:scale-95"
        >
          <Sparkles class="w-3.5 h-3.5 text-[#F9C86D]" />
          <span>Naro助手</span>
        </button>

        <!-- (2) 🔀 节点伪造 (天蓝高光) -->
        <button
          type="button"
          @click="emit('openBranchCanvas')"
          class="h-8 px-3.5 rounded-full bg-[#132233] border border-[#3B82F6]/40 hover:border-[#3B82F6] text-[#60A5FA] text-xs font-medium flex items-center gap-1.5 hover:bg-[#1A2E46] cursor-pointer transition-all shadow-sm active:scale-95"
        >
          <GitFork class="w-3.5 h-3.5 text-[#60A5FA]" />
          <span>节点伪造</span>
        </button>

        <!-- (3) 🌲 主线剧情 (葱绿高光) -->
        <button
          type="button"
          @click="emit('openBranchDrawer')"
          class="h-8 px-3.5 rounded-full bg-[#15281C] border border-[#22C55E]/40 hover:border-[#22C55E] text-[#4ADE80] text-xs font-medium flex items-center gap-1.5 hover:bg-[#1E3827] cursor-pointer transition-all shadow-sm active:scale-95"
        >
          <GitBranch class="w-3.5 h-3.5 text-[#4ADE80]" />
          <span>主线剧情</span>
        </button>

        <!-- (4) ➡️ 隐藏剧情 (暗灰高光) -->
        <button
          type="button"
          @click="emit('openNarrativePanel')"
          class="h-8 px-3.5 rounded-full bg-[#201A14] border border-white/15 hover:border-white/30 text-[#A8A29E] hover:text-white text-xs font-medium flex items-center gap-1.5 hover:bg-[#2A231C] cursor-pointer transition-all shadow-sm active:scale-95"
        >
          <ArrowRight class="w-3.5 h-3.5 text-[#A8A29E]" />
          <span>隐藏剧情</span>
        </button>

        <!-- (5) ⚙️ 设置下拉菜单 -->
        <div class="relative">
          <button
            type="button"
            @click="isSettingsOpen = !isSettingsOpen"
            class="w-8 h-8 rounded-lg bg-[#201A14] border border-white/15 hover:border-[#F9C86D]/40 text-[#A8A29E] hover:text-[#F9C86D] flex items-center justify-center cursor-pointer transition-colors shadow-sm"
            title="设置"
          >
            <Settings class="w-4 h-4" />
          </button>
          <ChatSettingsMenu
            v-model:open="isSettingsOpen"
            @select="(act) => emit('settingsAction', act)"
          />
        </div>

      </div>

    </header>

    <!-- ==================== 2. 主舞台区 (右侧立绘 + 左侧故事流) ==================== -->
    <div class="flex-1 relative flex overflow-hidden min-h-0">
      
      <!-- 2.1 右侧: 1:1 站姿角色超清全身立绘 -->
      <div class="absolute right-0 top-0 bottom-0 w-[46%] lg:w-[48%] xl:w-[50%] flex items-end justify-end pointer-events-none select-none z-0 overflow-hidden pr-6 pb-2">
        <img
          v-if="character.backgroundUrl || character.avatarUrl"
          :src="character.backgroundUrl || character.avatarUrl"
          :alt="character.name"
          class="h-[96%] max-h-[calc(100vh-160px)] object-contain object-bottom drop-shadow-[0_0_50px_rgba(0,0,0,0.92)] filter contrast-105 transition-opacity duration-500"
        />
      </div>

      <!-- 左向右暗黑蒙层：保障左侧叙述文本高保真可读性 -->
      <div class="absolute inset-0 pointer-events-none z-0 bg-gradient-to-r from-[#100D0B] via-[#100D0B]/90 via-55% to-transparent w-[65%]" />

      <!-- 2.2 左侧: 叙事小说流与输入交互区 (占比 ~60%) -->
      <div class="w-full max-w-[58%] xl:max-w-[62%] h-full flex flex-col z-10 pl-8 pr-6 min-w-0">
        
        <!-- 消息滚动列表 -->
        <div
          ref="scrollContainerRef"
          class="flex-1 overflow-y-auto overflow-x-hidden flex flex-col gap-5 pt-4 pb-2 pr-2 scroll-smooth select-text [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden"
        >
          <!-- 合规提示条 -->
          <ChatNoticeBanner />

          <!-- 序幕背景卡片 -->
          <div
            v-if="character.prologueContent && messages.length <= 1"
            class="p-4 rounded-xl bg-[#1A140E]/60 border border-[#3A2D20]/50 text-xs text-[#A8A29E] leading-relaxed backdrop-blur-sm"
          >
            <div class="text-[#F9C86D] font-bold mb-1">✦ {{ character.prologueTitle || "序幕" }}</div>
            <p class="whitespace-pre-wrap">{{ character.prologueContent }}</p>
          </div>

          <!-- 循环渲染故事段落 (Visual Novel 格式) -->
          <template v-for="msg in messages" :key="msg.id">
            
            <!-- AI 角色叙事段落 (消除臃肿气泡框，文本行距与小说对齐) -->
            <div
              v-if="msg.sender === 'ai'"
              class="flex flex-col gap-2 group relative py-1"
            >
              <!-- 深度思考内容折叠 -->
              <div v-if="msg.thinkingContent" class="mb-1">
                <button
                  type="button"
                  @click="toggleThinking(msg.id)"
                  class="flex items-center gap-1.5 px-2.5 py-1 rounded bg-[#1C1712] border border-[#F9C86D]/20 text-[11px] text-[#F9C86D]/80 hover:bg-[#2A231A] transition-colors cursor-pointer"
                >
                  <Brain class="w-3.5 h-3.5 text-[#F9C86D]" />
                  <span>深度思考过程 ({{ msg.thinkingContent.length }} 字)</span>
                  <ChevronDown :class="['w-3 h-3 transition-transform', expandedThinkingIds[msg.id] ? 'rotate-180' : '']" />
                </button>
                <div
                  v-if="expandedThinkingIds[msg.id]"
                  class="mt-1.5 p-3 rounded-lg bg-[#14100C] border border-[#F9C86D]/15 text-xs text-[#A8A29E] whitespace-pre-wrap leading-relaxed"
                >
                  {{ msg.thinkingContent }}
                </div>
              </div>

              <!-- 正文文本：大行高、文字柔和、支持段落解析 -->
              <div class="text-[14.5px] text-[#E7E5E4] leading-[1.85] font-sans tracking-wide space-y-2.5">
                <div
                  v-html="sanitizeHtml(msg.content)"
                  class="whitespace-pre-wrap break-words"
                />
                
                <!-- 流式输出光标 -->
                <span
                  v-if="msg.status === 'streaming'"
                  class="inline-block w-1.5 h-4 ml-0.5 align-middle bg-[#F9C86D] animate-pulse"
                />
              </div>

              <!-- 浮动悬停操作栏 (hover 时浮现: 重新生成/朗读/分支/删除) -->
              <div class="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 pt-1">
                <button
                  type="button"
                  @click="emit('regenerate', msg)"
                  class="p-1 rounded hover:bg-white/10 text-[#A8A29E] hover:text-[#F9C86D] transition-colors cursor-pointer"
                  title="重新生成"
                >
                  <RotateCcw class="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  @click="toggleAudioPlay(msg.id, msg.content); emit('readAloud', msg)"
                  :class="[
                    'p-1 rounded hover:bg-white/10 transition-colors cursor-pointer',
                    currentMessageId === msg.id && isAudioPlaying ? 'text-[#F9C86D]' : 'text-[#A8A29E] hover:text-[#F9C86D]'
                  ]"
                  title="朗读"
                >
                  <Volume2 class="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  @click="emit('branch', msg)"
                  class="p-1 rounded hover:bg-white/10 text-[#A8A29E] hover:text-[#F9C86D] transition-colors cursor-pointer"
                  title="以此创建分支"
                >
                  <GitBranch class="w-3.5 h-3.5" />
                </button>
                <button
                  type="button"
                  @click="emit('delete', msg)"
                  class="p-1 rounded hover:bg-white/10 text-[#A8A29E] hover:text-red-400 transition-colors cursor-pointer"
                  title="删除"
                >
                  <Trash2 class="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <!-- 用户输入段落 (金边左引线、区分明显) -->
            <div
              v-else
              class="flex flex-col gap-1 py-1 pl-3 border-l-2 border-[#F9C86D]/50 text-[14px] text-[#F9C86D]/95 bg-white/[0.02] rounded-r-lg p-2"
            >
              <div class="text-[11px] text-[#A8A29E] flex items-center justify-between">
                <span>{{ userStore.profile?.username || "你" }}</span>
                <span class="text-[10px] text-[#78716C]">{{ msg.timestamp }}</span>
              </div>
              <p class="whitespace-pre-wrap leading-relaxed font-sans">{{ msg.content }}</p>
            </div>

          </template>

          <!-- 正在构思中动画 -->
          <div v-if="isGenerating" class="flex items-center gap-2 text-xs text-[#F9C86D] animate-pulse py-2">
            <span class="w-2 h-2 rounded-full bg-[#F9C86D]" />
            <span>正在沉浸式推进剧情……</span>
          </div>

        </div>

        <!-- 2.3 消息流底部统计指示条 (1:1 还原 media_1789565500457.png) -->
        <div class="flex items-center justify-between pt-2 pb-1 border-t border-white/5 select-none shrink-0">
          <!-- 左侧 Token 指标 -->
          <div class="flex items-center gap-2 text-[11px] text-[#78716C]">
            <span>输入: <strong class="text-emerald-400 font-mono font-medium">{{ latestAiMetrics.inputTokens.toLocaleString() }}</strong></span>
            <span>输出: <strong class="text-emerald-400 font-mono font-medium">{{ latestAiMetrics.outputTokens.toLocaleString() }}</strong></span>
            <span class="text-emerald-400 font-bold">✓</span>
          </div>

          <!-- 右侧浮动置顶/底按钮 -->
          <button
            type="button"
            @click="handleScrollToggle"
            class="w-6 h-6 rounded bg-[#201A14]/80 border border-white/10 hover:border-[#F9C86D]/40 text-[#A8A29E] hover:text-white flex items-center justify-center cursor-pointer transition-colors shadow-sm"
            title="滚动到顶部/底部"
          >
            <ArrowUp class="w-3.5 h-3.5" />
          </button>
        </div>

        <!-- ==================== 3. 底部输入框与模型状态控制栏 ==================== -->
        <div class="pt-1 pb-3 flex flex-col gap-2 shrink-0">
          
          <!-- 3.1 宽屏大输入框 -->
          <div
            :class="[
              'w-full rounded-2xl bg-[#1C1712]/90 border border-[#3A2D20] p-3 flex flex-col justify-between shadow-2xl backdrop-blur-md transition-all',
              isExpandedInput ? 'h-48' : 'min-h-[64px]'
            ]"
          >
            <textarea
              ref="textareaRef"
              v-model="inputText"
              :disabled="isGenerating"
              placeholder="输入消息...(shift enter)"
              @keydown="handleKeydown"
              class="w-full h-full bg-transparent border-none outline-none resize-none text-[13.5px] text-white/95 placeholder-[#78716C] font-sans leading-relaxed select-text"
            />

            <!-- 输入框右下角操作：⤢ 展开按钮 + 发送按钮 -->
            <div class="flex items-center justify-end gap-2 pt-1">
              <button
                type="button"
                @click="toggleExpandInput"
                class="p-1 text-[#78716C] hover:text-white transition-colors cursor-pointer"
                title="展开/收起输入框"
              >
                <Minimize2 v-if="isExpandedInput" class="w-3.5 h-3.5" />
                <Maximize2 v-else class="w-3.5 h-3.5" />
              </button>

              <button
                v-if="isGenerating"
                type="button"
                @click="emit('stop')"
                class="px-3 py-1 rounded bg-red-500/20 text-red-400 hover:bg-red-500/30 text-xs font-medium cursor-pointer flex items-center gap-1"
              >
                <Square class="w-3 h-3 fill-current" />
                <span>停止</span>
              </button>

              <button
                v-else
                type="button"
                @click="handleSend"
                :class="[
                  'px-3 py-1 rounded text-xs font-medium transition-colors cursor-pointer',
                  inputText.trim()
                    ? 'bg-[#F9C86D] text-[#0C0A09] font-bold shadow-md hover:bg-[#F9C86D]/90'
                    : 'text-[#78716C] hover:text-[#A8A29E]'
                ]"
              >
                发送
              </button>
            </div>
          </div>

          <!-- 3.2 底部控制栏药丸组 (1:1 还原 media_1789565500457.png) -->
          <div class="flex items-center gap-2 text-xs text-[#A8A29E] flex-wrap">
            
            <!-- 1. [∧ 展开控制] -->
            <button
              type="button"
              @click="emit('openControlPanel')"
              class="h-7 px-3 rounded-full bg-[#1C1712] border border-white/10 hover:border-[#F9C86D]/40 text-[#A8A29E] hover:text-white flex items-center gap-1 cursor-pointer transition-all shadow-sm"
            >
              <ChevronUp class="w-3.5 h-3.5" />
              <span>展开控制</span>
            </button>

            <!-- 2. [✦ 快速双子星3 | ⚡ 18 金币免费(0/30) ∨] -->
            <button
              type="button"
              @click="emit('openModelSelector')"
              class="h-7 px-3 rounded-full bg-[#1C1712] border border-white/10 hover:border-[#F9C86D]/40 text-[#D6D3D1] hover:text-white flex items-center gap-1.5 cursor-pointer transition-all shadow-sm"
            >
              <span class="text-[#3B82F6] font-bold">✦</span>
              <span class="truncate max-w-[100px]">{{ currentModel.name }}</span>
              <span class="text-[#F9C86D] text-[11px]">⚡ {{ currentModel.cost }} 金币{{ currentModel.freeCountText }}</span>
              <ChevronDown class="w-3 h-3 text-[#78716C]" />
            </button>

            <!-- 3. 资产星元与代币 [⭐ 466  🍇 1,522] -->
            <div class="h-7 px-3 rounded-full bg-[#1C1712] border border-white/10 flex items-center gap-2.5 text-[11px]">
              <span class="text-[#F9C86D] font-mono flex items-center gap-1">
                <span>⭐</span>
                <span>{{ userStore.starCoins || 466 }}</span>
              </span>
              <span class="text-[#C084FC] font-mono flex items-center gap-1">
                <span>🍇</span>
                <span>1,522</span>
              </span>
            </div>

            <!-- 4. [📜 插件] -->
            <button
              type="button"
              @click="emit('openModManager')"
              class="h-7 px-3 rounded-full bg-[#1C1712] border border-white/10 hover:border-[#F9C86D]/40 text-[#A8A29E] hover:text-white flex items-center gap-1 cursor-pointer transition-all shadow-sm"
            >
              <Scroll class="w-3.5 h-3.5 text-[#F9C86D]" />
              <span>插件</span>
            </button>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>
