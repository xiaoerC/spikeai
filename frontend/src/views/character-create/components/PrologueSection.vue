<script setup lang="ts">
/**
 * 模块 4: 序幕组件 (1:1 原型高保真)
 *
 * 包含 HTML/Markdown 炫酷卡面代码编辑器、AI 生成模拟与实时沙箱预览。
 *
 * @packageDocumentation
 */

import { Sparkles } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{
  /** 序幕 HTML 代码 (v-model) */
  modelValue: string;
}>();

const emit = defineEmits<(e: "update:modelValue", val: string) => void>();

const isPreviewMode = ref<boolean>(false);
const isGenerating = ref<boolean>(false);

/**
 * 模拟 AI 一键生成序幕卡面模板
 */
function handleAIGenerate(): void {
  isGenerating.value = true;
  setTimeout(() => {
    isGenerating.value = false;
    const template = `<div class="p-4 bg-gradient-to-br from-amber-950/40 to-black/80 rounded-xl border border-amber-500/30 text-amber-100 font-serif shadow-2xl">
  <h3 class="text-lg font-bold text-[#F9C86D] tracking-wider mb-2">✦ 命运交汇之夜 ✦</h3>
  <p class="text-xs leading-relaxed text-gray-300">
    风雪吹过破碎的鸟居，夜幕低垂。你握紧了腰间的配刀，等待着属于你的破晓之战……
  </p>
</div>`;
    emit("update:modelValue", template);
  }, 600);
}
</script>

<template>
  <div class="w-full px-3 pb-3">
    <!-- 模块外层容器 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      
      <!-- 1. 模块主标题 (金黄圆柱指示条 + 序幕 + 可选 Badge) -->
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-3">
          <!-- 金黄指示条 -->
          <div class="w-1 h-6 rounded-full bg-[#F9C86D] shadow-[0_0_10px_rgba(249,200,109,0.5)]" />
          <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[0.9px] leading-tight select-none">
            序幕
          </h2>
          <!-- 可选胶囊 Badge -->
          <span class="px-2 py-0.5 rounded-full bg-[#F9C86D]/15 text-[#F9C86D] border border-[#F9C86D]/30 text-[10px] font-medium select-none">
            可选
          </span>
        </div>

        <!-- AI 生成与预览按钮 -->
        <div class="flex items-center gap-2">
          <!-- AI 生成按钮 -->
          <button
            type="button"
            @click="handleAIGenerate"
            :disabled="isGenerating"
            class="flex items-center gap-1 px-2.5 py-1 rounded bg-[#F9C86D]/15 text-[#F9C86D] border border-[#F9C86D]/30 hover:bg-[#F9C86D]/25 text-xs font-medium transition-colors cursor-pointer select-none"
          >
            <Sparkles class="w-3.5 h-3.5" :class="{ 'animate-spin': isGenerating }" />
            <span>AI生成</span>
          </button>

          <!-- 预览切换 -->
          <button
            type="button"
            @click="isPreviewMode = !isPreviewMode"
            :class="[
              'px-2.5 py-1 rounded text-xs transition-colors cursor-pointer select-none',
              isPreviewMode
                ? 'bg-[#38BDF8]/20 text-[#38BDF8] border border-[#38BDF8]/40'
                : 'text-[#7BC7E2] hover:bg-white/5'
            ]"
          >
            {{ isPreviewMode ? "代码" : "预览" }}
          </button>
        </div>
      </div>

      <!-- 2. 编辑区与实时预览 -->
      <div class="flex flex-col gap-2">
        <label class="text-xs text-[#A8A29E]">序幕内容 (支持 HTML 与 CSS 样式美化)</label>
        
        <!-- 代码输入框 -->
        <textarea
          v-if="!isPreviewMode"
          :value="modelValue"
          @input="emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
          rows="5"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs font-mono text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D] transition-colors resize-none leading-relaxed"
          placeholder="关于角色最炫酷的展示&#10;&#10;请把代码放在这里~格式建议如下，这样更好效果：&#10;&#10;html代码请使用：&#10;```html&#10;代码内容&#10;```"
        />

        <!-- 沙箱实时预览渲染区 -->
        <div
          v-else
          class="w-full min-h-[120px] p-3 rounded-lg border border-dashed border-[#F9C86D]/40 bg-black/40 flex flex-col justify-center overflow-x-hidden"
        >
          <div v-if="modelValue" v-html="modelValue" class="prologue-preview" />
          <div v-else class="text-center text-xs text-[#78716C] py-4">
            输入 HTML 代码后将在此处显示预览效果
          </div>
        </div>

        <span class="text-[11px] text-[#78716C]">
          预览效果与实际显示一致，可在故事卡开局前呈现华丽特效。
        </span>
      </div>

    </div>
  </div>
</template>
