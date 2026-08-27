<script setup lang="ts">
/**
 * AI 聊天界面 - 底部输入栏 (1:1 Figma 原型高保真)
 *
 * 支持折叠单行胶囊模式、展开大文本域模式 以及 底部「更多操作功能扩展面板」：
 * 1. 折叠模式 (Collapsed):
 *    - 胶囊药丸容器 (h-11, rounded-full, border-[#44403C]/80, bg-black/50, backdrop-blur-xl)
 *    - 左侧: ✦ AI 灵感按钮
 *    - 中间: 单行输入框 (带内框，右侧有 ⤢ 展开按钮)
 *    - 右侧: ✚ 加号 (无字时点击展开更多操作面板，有字时变为发送) / ✕ 旋转关闭
 * 2. 展开模式 (Expanded - 1:1 原型图):
 *    - 大圆角矩形容器 (h-64, rounded-2xl, border-[#44403C]/80, bg-black/60, backdrop-blur-xl)
 *    - 内部多行 textarea (支持滚动、长文编辑)
 *    - 底部横向操作栏:
 *      - 左下角: ✦ AI 灵感按钮
 *      - 右下角: ⤡ 收起按钮 + ✚ 加号/发送按钮
 * 3. 更多面板 (More Action Panel - Frame 99:7366):
 *    - 点击 ✚ 展开 / ✕ 收起，包含点数资产胶囊、对话增强、记忆增强、Mod管理、画师串
 *
 * @packageDocumentation
 */

import ChatMoreActionPanel from "@/views/chat/components/ChatMoreActionPanel.vue";
import { Square } from "lucide-vue-next";
import { nextTick, ref } from "vue";

const props = defineProps<{
  disabled?: boolean;
  isGenerating?: boolean;
}>();

const emit = defineEmits<{
  (e: "send", text: string): void;
  (e: "stop"): void;
  (e: "aiAssist"): void;
  (e: "moreAction", name: string): void;
}>();

const inputText = ref("");
const isExpanded = ref(false);
const isMorePanelOpen = ref(false);
const inputRef = ref<HTMLInputElement | null>(null);
const textareaRef = ref<HTMLTextAreaElement | null>(null);

function toggleExpand(): void {
  isExpanded.value = !isExpanded.value;
  if (isExpanded.value) {
    isMorePanelOpen.value = false;
  }
  nextTick(() => {
    if (isExpanded.value) {
      textareaRef.value?.focus();
    } else {
      inputRef.value?.focus();
    }
  });
}

function toggleMorePanel(): void {
  isMorePanelOpen.value = !isMorePanelOpen.value;
}

function handleMoreAction(name: string): void {
  emit("moreAction", name);
}

function handleSend(): void {
  if (!inputText.value.trim()) return;
  emit("send", inputText.value.trim());
  inputText.value = "";
  if (isExpanded.value) {
    isExpanded.value = false;
  }
}

function handleKeydown(e: KeyboardEvent): void {
  // 折叠模式下 Enter 直接发送
  if (!isExpanded.value) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  } else {
    // 展开模式下 Ctrl+Enter / Meta+Enter 发送，Enter 正常换行
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSend();
    }
  }
}

function appendPrompt(text: string): void {
  if (inputText.value) {
    inputText.value += ` ${text}`;
  } else {
    inputText.value = text;
  }
}

defineExpose({
  appendPrompt,
});
</script>

<template>
  <div class="w-full z-30 select-none bg-transparent flex flex-col gap-2 relative">
    
    <!-- ==================== 1. 展开大输入框模式 (1:1 原型图 media_1787482360237.png) ==================== -->
    <div
      v-if="isExpanded"
      class="w-full h-64 p-3 rounded-2xl border border-[#44403C]/80 bg-black/60 backdrop-blur-2xl flex flex-col justify-between shadow-[0_8px_32px_rgba(0,0,0,0.6)] transition-all animate-fade-in"
    >
      <!-- 顶部多行文本编辑域 -->
      <div class="flex-1 w-full overflow-hidden flex flex-col">
        <textarea
          ref="textareaRef"
          v-model="inputText"
          :disabled="disabled"
          placeholder="发送消息..."
          @keydown="handleKeydown"
          class="w-full h-full bg-transparent border-none outline-none resize-none text-[14px] text-white/95 placeholder-white/40 font-sans leading-relaxed tracking-tight p-1 [scrollbar-width:thin] [-ms-overflow-style:none] overflow-y-auto"
        />
      </div>

      <!-- 底部操作栏: 左侧 AI 按钮，右侧 收起 + 发送 -->
      <div class="w-full flex items-center justify-between pt-2 border-t border-white/5">
        <!-- 左下角: ✦ AI 灵感按钮 -->
        <button
          type="button"
          @click="emit('aiAssist')"
          class="w-8 h-8 rounded-full flex items-center justify-center text-[#F9C86D] hover:scale-110 active:scale-95 transition-all cursor-pointer"
          title="AI 灵感辅助"
        >
          <svg width="18" height="18" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8 2L6.72533 5.87533C6.6601 6.07367 6.5492 6.25392 6.40156 6.40156C6.25392 6.5492 6.07367 6.6601 5.87533 6.72533L2 8L5.87533 9.27467C6.07367 9.3399 6.25392 9.4508 6.40156 9.59844C6.5492 9.74608 6.6601 9.92633 6.72533 10.1247L8 14L9.27467 10.1247C9.3399 9.92633 9.4508 9.74608 9.59844 9.59844C9.74608 9.4508 9.92633 9.3399 10.1247 9.27467L14 8L10.1247 6.72533C9.92633 6.6601 9.74608 6.5492 9.59844 6.40156C9.4508 6.25392 9.3399 6.07367 9.27467 5.87533L8 2Z" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3.33334 2V4.66667" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.6667 11.3333V14" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 3.33334H4.66667" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M11.3333 12.6667H14" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>

        <!-- 右下角: ⤡ 收起按钮 + ✚ 加号/发送按钮 -->
        <div class="flex items-center gap-2">
          <!-- ⤡ 收起按钮 (向内折叠箭头) -->
          <button
            type="button"
            @click="toggleExpand"
            class="w-7 h-7 rounded-full flex items-center justify-center text-white/70 hover:text-white hover:bg-white/10 active:scale-95 transition-all cursor-pointer"
            title="收起输入框"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M2.33333 5.83333H5.83333V2.33333" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M1.75 1.75L5.83333 5.83333" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M11.6667 8.16667H8.16667V11.6667" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M12.25 12.25L8.16667 8.16667" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>

          <!-- 停止生成按钮 (生成中) 或 ✚ 金色十字加号 / 发送按钮 -->
          <button
            v-if="isGenerating"
            type="button"
            @click="emit('stop')"
            class="w-7 h-7 rounded-full bg-red-500/20 border border-red-500/50 text-red-400 flex items-center justify-center hover:scale-105 active:scale-95 animate-pulse transition-all cursor-pointer"
            title="停止生成"
          >
            <Square class="w-3 h-3 fill-current" />
          </button>
          <button
            v-else
            type="button"
            @click="inputText.trim() ? handleSend() : toggleMorePanel()"
            :class="[
              'w-7 h-7 rounded-full flex items-center justify-center transition-all cursor-pointer',
              inputText.trim()
                ? 'bg-[#F9C86D] text-[#0C0A09] hover:scale-105 active:scale-95'
                : isMorePanelOpen
                  ? 'bg-[#D1A35C] text-[#2A261F] shadow-lg'
                  : 'text-[#D1A35C] hover:bg-white/10 active:scale-95'
            ]"
            :title="inputText.trim() ? '发送' : '更多功能'"
          >
            <!-- 若开启更多面板且无字，显示旋转叉号 ✕；否则显示 ✚ -->
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              :class="['transition-transform duration-200', isMorePanelOpen && !inputText.trim() ? 'rotate-45' : 'rotate-0']"
            >
              <path
                d="M3.33331 8H12.6666"
                :stroke="inputText.trim() ? '#0C0A09' : isMorePanelOpen ? '#2A261F' : '#D1A35C'"
                stroke-width="1.33333"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
              <path
                d="M8 3.33334V12.6667"
                :stroke="inputText.trim() ? '#0C0A09' : isMorePanelOpen ? '#2A261F' : '#D1A35C'"
                stroke-width="1.33333"
                stroke-linecap="round"
                stroke-linejoin="round"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- ==================== 2. 折叠单行胶囊模式 (1:1 原型图 Frame 99:7366) ==================== -->
    <div
      v-else
      class="w-full h-11 px-2 rounded-full border border-[#44403C]/80 bg-black/50 backdrop-blur-xl flex items-center justify-between gap-2 shadow-2xl transition-all"
    >
      <!-- 1. 左侧: ✦ AI 辅助/火花金色四角星图标 -->
      <button
        type="button"
        @click="emit('aiAssist')"
        class="w-7 h-7 rounded-full flex items-center justify-center text-[#F9C86D] hover:scale-110 active:scale-95 transition-all cursor-pointer shrink-0"
        title="AI 灵感辅助"
      >
        <svg width="18" height="18" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 2L6.72533 5.87533C6.6601 6.07367 6.5492 6.25392 6.40156 6.40156C6.25392 6.5492 6.07367 6.6601 5.87533 6.72533L2 8L5.87533 9.27467C6.07367 9.3399 6.25392 9.4508 6.40156 9.59844C6.5492 9.74608 6.6601 9.92633 6.72533 10.1247L8 14L9.27467 10.1247C9.3399 9.92633 9.4508 9.74608 9.59844 9.59844C9.74608 9.4508 9.92633 9.3399 10.1247 9.27467L14 8L10.1247 6.72533C9.92633 6.6601 9.74608 6.5492 9.59844 6.40156C9.4508 6.25392 9.3399 6.07367 9.27467 5.87533L8 2Z" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M3.33334 2V4.66667" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M12.6667 11.3333V14" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M2 3.33334H4.66667" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M11.3333 12.6667H14" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>

      <!-- 2. 中间输入区 (带微圆角内框: background: rgba(42, 37, 32, 0.50); border: 0.667px solid rgba(83, 71, 65, 0.30); border-radius: 6px) -->
      <div class="flex-1 h-8 px-2.5 rounded-md border border-[#534741]/30 bg-[#2A2520]/50 flex items-center justify-between gap-1 focus-within:border-[#F9C86D]/50 transition-colors">
        <input
          ref="inputRef"
          v-model="inputText"
          type="text"
          :disabled="disabled"
          placeholder="发送消息..."
          @keydown="handleKeydown"
          class="flex-1 bg-transparent border-none outline-none text-xs text-white/95 placeholder-white/40 font-sans tracking-tight"
        />

        <!-- ⤢ 展开输入框按钮 -->
        <button
          type="button"
          @click="toggleExpand"
          class="w-5 h-5 flex items-center justify-center text-white/70 hover:text-white transition-colors cursor-pointer shrink-0"
          title="展开输入框"
        >
          <svg width="12" height="12" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M8.75 1.75H12.25V5.25" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.25 1.75L8.16669 5.83333" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1.75 12.25L5.83333 8.16666" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.25 12.25H1.75V8.75" stroke="white" stroke-opacity="0.85" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>

      <!-- 3. 最右侧: 停止生成按钮 (生成中) 或 ✚ 金色十字加号 / ✕ 旋转关闭 / 发送按钮 -->
      <button
        v-if="isGenerating"
        type="button"
        @click="emit('stop')"
        class="w-7 h-7 rounded-full bg-red-500/20 border border-red-500/50 text-red-400 flex items-center justify-center hover:scale-105 active:scale-95 animate-pulse transition-all cursor-pointer shrink-0"
        title="停止生成"
      >
        <Square class="w-3 h-3 fill-current" />
      </button>
      <button
        v-else
        type="button"
        @click="inputText.trim() ? handleSend() : toggleMorePanel()"
        :class="[
          'w-7 h-7 rounded-full flex items-center justify-center transition-all cursor-pointer shrink-0',
          inputText.trim()
            ? 'bg-[#F9C86D] text-[#0C0A09] hover:scale-105 active:scale-95'
            : isMorePanelOpen
              ? 'bg-[#D1A35C] text-[#2A261F] shadow-lg'
              : 'text-[#D1A35C] hover:bg-white/5 active:scale-95'
        ]"
        :title="inputText.trim() ? '发送' : '更多功能'"
      >
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          :class="['transition-transform duration-200', isMorePanelOpen && !inputText.trim() ? 'rotate-45' : 'rotate-0']"
        >
          <path
            d="M3.33331 8H12.6666"
            :stroke="inputText.trim() ? '#0C0A09' : isMorePanelOpen ? '#2A261F' : '#D1A35C'"
            stroke-width="1.33333"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            d="M8 3.33334V12.6667"
            :stroke="inputText.trim() ? '#0C0A09' : isMorePanelOpen ? '#2A261F' : '#D1A35C'"
            stroke-width="1.33333"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>

    </div>

    <!-- ==================== 3. 1:1 更多操作功能扩展面板 (Frame 99:7366) ==================== -->
    <ChatMoreActionPanel
      v-model:open="isMorePanelOpen"
      @action="handleMoreAction"
    />

  </div>
</template>
