<script setup lang="ts">
/**
 * 模块 1: 作者的话组件 (1:1 原型高保真)
 *
 * 包含 Markdown 快捷工具栏、预览切换模式、字数统计与帮助链接。
 *
 * @packageDocumentation
 */

import { computed, ref } from "vue";

const props = defineProps<{
  /** 作者的话内容 (v-model) */
  modelValue: string;
}>();

const emit = defineEmits<(e: "update:modelValue", value: string) => void>();

// 是否处于预览模式
const isPreviewMode = ref<boolean>(false);

const charCount = computed<number>(() => props.modelValue.length);

/**
 * 插入 Markdown 格式标记
 */
function insertMarkdown(prefix: string, suffix = ""): void {
  const nextVal = `${props.modelValue}${prefix}${suffix}`;
  emit("update:modelValue", nextVal);
}
</script>

<template>
  <div class="w-full px-3 pb-3">
    <!-- 模块外层容器 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      
      <!-- 1. 模块主标题 (蓝色圆柱指示条 + 作者的话 + 蓝色气泡图标) -->
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-3">
          <!-- 蓝色指示条 -->
          <div class="w-1 h-6 rounded-full bg-[#3B82F6] shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
          <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[0.9px] leading-tight select-none">
            作者的话
          </h2>
        </div>

        <!-- 蓝色气泡图标 -->
        <svg class="w-5 h-5 text-[#3B82F6]" viewBox="0 0 22 22" fill="none">
          <path d="M7.1623 8.95287H7.17125M10.7434 8.95287H10.7524M14.3246 8.95287H14.3335M8.05758 14.3246H4.47643C4.00154 14.3246 3.5461 14.1359 3.21031 13.8001C2.87451 13.4644 2.68586 13.0089 2.68586 12.534V5.37172C2.68586 4.89683 2.87451 4.44139 3.21031 4.10559C3.5461 3.7698 4.00154 3.58115 4.47643 3.58115H17.0105C17.4853 3.58115 17.9408 3.7698 18.2766 4.10559C18.6124 4.44139 18.801 4.89683 18.801 5.37172V12.534C18.801 13.0089 18.6124 13.4644 18.2766 13.8001C17.9408 14.1359 17.4853 14.3246 17.0105 14.3246H12.534L8.05758 17.9057V14.3246Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- 2. 子标签与 Markdown 操作工具栏 -->
      <div class="flex flex-col gap-2 pt-1">
        <!-- 标签行 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2 text-[#F5F5F4] text-sm font-medium">
            <svg class="w-4 h-4 text-[#3B82F6]" viewBox="0 0 16 16" fill="none">
              <path d="M4.66667 5.33333H11.3333M4.66667 5.33333V4C4.66667 3.64638 4.80715 3.30724 5.0572 3.05719C5.30724 2.80714 5.64638 2.66666 6.00001 2.66666H10C10.3536 2.66666 10.6928 2.80714 10.9428 3.05719C11.1929 3.30724 11.3333 3.64638 11.3333 4V5.33333M4.66667 5.33333V12C4.66667 12.3536 4.80715 12.6928 5.0572 12.9428C5.30724 13.1929 5.64638 13.3333 6.00001 13.3333H10C10.3536 13.3333 10.6928 13.1929 10.9428 12.9428C11.1929 12.6928 11.3333 12.3536 11.3333 12V5.33333" stroke="currentColor" stroke-width="1.33" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>创作者留言</span>
          </div>

          <!-- 预览切换按钮 -->
          <button
            type="button"
            @click="isPreviewMode = !isPreviewMode"
            :class="[
              'flex items-center gap-1.5 px-2.5 py-1 rounded text-xs transition-colors cursor-pointer select-none',
              isPreviewMode
                ? 'bg-[#38BDF8]/20 text-[#38BDF8] border border-[#38BDF8]/40'
                : 'text-[#7BC7E2] hover:bg-white/5'
            ]"
          >
            <svg width="13" height="13" viewBox="0 0 14 14" fill="none">
              <path d="M1.2 7C1.67 8.35 2.48 9.33 3.51 10.02C4.54 10.71 5.75 11.08 7 11.08C8.24 11.08 9.45 10.71 10.48 10.02C11.51 9.33 12.32 8.35 12.8 7C12.32 5.65 11.51 4.67 10.48 3.98C9.45 3.29 8.24 2.92 7 2.92C5.75 2.92 4.54 3.29 3.51 3.98C2.48 4.67 1.67 5.65 1.2 7Z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 8.75C7.96 8.75 8.75 7.96 8.75 7C8.75 6.03 7.96 5.25 7 5.25C6.03 5.25 5.25 6.03 5.25 7C5.25 7.96 6.03 8.75 7 8.75Z" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ isPreviewMode ? "编辑" : "预览" }}</span>
          </button>
        </div>

        <!-- Markdown 快捷按钮行 -->
        <div class="flex items-center gap-1 p-1 rounded-md bg-[rgba(26,23,20,0.80)] border border-[#44403C]/50 overflow-x-auto text-[#A8A29E]">
          <!-- B -->
          <button type="button" @click="insertMarkdown('**', '**')" class="p-1.5 hover:text-white rounded hover:bg-white/10" title="加粗">
            <span class="font-bold text-xs">B</span>
          </button>
          <!-- I -->
          <button type="button" @click="insertMarkdown('*', '*')" class="p-1.5 hover:text-white rounded hover:bg-white/10" title="斜体">
            <span class="italic text-xs">I</span>
          </button>
          <!-- H2 -->
          <button type="button" @click="insertMarkdown('## ')" class="p-1.5 hover:text-white rounded hover:bg-white/10" title="二级标题">
            <span class="font-semibold text-[11px]">H2</span>
          </button>
          <!-- List -->
          <button type="button" @click="insertMarkdown('- ')" class="p-1.5 hover:text-white rounded hover:bg-white/10" title="无序列表">
            <span class="text-xs">• 列表</span>
          </button>
          <!-- Code -->
          <button type="button" @click="insertMarkdown('`', '`')" class="p-1.5 hover:text-white rounded hover:bg-white/10" title="行内代码">
            <span class="font-mono text-xs">&lt;/&gt;</span>
          </button>
        </div>

        <!-- 文本输入域 / 预览区 -->
        <div class="relative w-full min-h-[140px] rounded-lg border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] p-3 flex flex-col justify-between focus-within:border-[#3B82F6]/60 transition-colors">
          <textarea
            v-if="!isPreviewMode"
            :value="modelValue"
            @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
            class="w-full h-28 bg-transparent text-sm text-gray-200 placeholder-[#78716C] resize-none outline-none font-sans leading-relaxed"
            placeholder="任何你希望说的话，价值，世界以及♥️（会放在卡片的最开头）"
            maxlength="5000"
          />
          <div
            v-else
            class="w-full h-28 text-sm text-gray-300 overflow-y-auto leading-relaxed whitespace-pre-wrap font-sans"
          >
            {{ modelValue || "（暂无创作者留言预览内容）" }}
          </div>

          <!-- 底部：字数统计与帮助链接 -->
          <div class="flex items-center justify-between pt-2 border-t border-white/5 text-xs text-[#78716C]">
            <span>{{ charCount }} / 5000 字符</span>
            <a href="https://www.markdownguide.org" target="_blank" rel="noreferrer" class="text-[#F9C86D] hover:underline cursor-pointer">
              Markdown 帮助
            </a>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>
