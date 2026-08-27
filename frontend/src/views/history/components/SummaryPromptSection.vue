<script setup lang="ts">
/**
 * 总结提示词管理主面板 (Figma 86:8397 1:1 像素级高保真)
 *
 * 包含 说明文案、自动总结模型选择、5000 字自定义提示词多行文本域、保存设置与恢复默认按钮。
 *
 * @packageDocumentation
 */

import { ChevronDown } from "lucide-vue-next";
import { ref, watch } from "vue";

const props = defineProps<{
  model: string;
  prompt: string;
}>();

const emit = defineEmits<{
  (
    e: "save",
    payload: {
      model: string;
      prompt: string;
    },
  ): void;
  (e: "reset"): void;
}>();

const localModel = ref(props.model || "claude-sonnet-4.5");
const localPrompt = ref(props.prompt || "");

watch(
  () => props.model,
  (val) => {
    localModel.value = val || "claude-sonnet-4.5";
  },
);

watch(
  () => props.prompt,
  (val) => {
    localPrompt.value = val || "";
  },
);

const MODEL_OPTIONS = [
  {
    id: "claude-sonnet-4.5",
    label: "系统默认（claude-sonnet-4.5）— 会员免费",
  },
  {
    id: "claude-3-haiku",
    label: "claude-3-haiku — 极速响应",
  },
  {
    id: "gemini-2.5-flash",
    label: "gemini-2.5-flash — 智能精炼",
  },
  {
    id: "gpt-4o-mini",
    label: "gpt-4o-mini — 均衡稳定",
  },
];

const DEFAULT_PLACEHOLDER = `留空则使用系统默认提示词。

示例：
请从以下对话中提取关键信息，生成一份简洁的总结。总结应包含：
1. 主要情节发展
2. 重要角色互动
3. 关键道具或线索

请用中文输出，保持简洁清晰。`;

function handleSave() {
  emit("save", {
    model: localModel.value,
    prompt: localPrompt.value,
  });
}

function handleReset() {
  localModel.value = "claude-sonnet-4.5";
  localPrompt.value = "";
  emit("reset");
}
</script>

<template>
  <div class="w-full px-4 pt-6 flex flex-col pb-12">
    <!-- 1. 顶部说明文案 (Figma 86:8397) -->
    <div class="w-full pb-4">
      <p class="text-[14px] leading-[22.75px] text-[#A8A29E]/70">
        自定义自动总结提示词后，系统将完全使用你的提示词替代默认提示词来生成对话总结。清空并保存可恢复系统默认。
      </p>
    </div>

    <!-- 2. 自动总结模型选择栏 (Figma 86:8397) -->
    <div class="w-full flex flex-col pb-4">
      <label class="text-[12px] leading-[16px] text-[#A8A29E]/70 pb-2">
        自动总结模型
      </label>
      <div class="relative w-full">
        <select
          v-model="localModel"
          class="w-full appearance-none px-3 py-2 rounded-[6px] border border-[#44403C] bg-[#292524] text-[16px] leading-[27.2px] text-[#C0A480] focus:border-[#F9C86D] focus:outline-none transition-colors cursor-pointer select-none pr-9"
        >
          <option
            v-for="opt in MODEL_OPTIONS"
            :key="opt.id"
            :value="opt.id"
            class="bg-[#292524] text-[#F5F5F4]"
          >
            {{ opt.label }}
          </option>
        </select>
        <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#C0A480]">
          <ChevronDown class="w-4 h-4" />
        </div>
      </div>
    </div>

    <!-- 3. 自定义提示词多行文本域 (Figma 86:8397) -->
    <div class="w-full flex flex-col pb-4">
      <div class="relative w-full rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] p-3 min-h-[192px] flex flex-col justify-between">
        <textarea
          v-model="localPrompt"
          rows="7"
          maxlength="5000"
          :placeholder="DEFAULT_PLACEHOLDER"
          class="w-full bg-transparent text-[14px] leading-[20px] text-[#F5F5F4] placeholder-[#78716C] focus:outline-none resize-none"
        ></textarea>
        <div class="w-full text-right text-[12px] leading-[16px] text-[#78716C] pt-1">
          {{ localPrompt.length }} / 5000
        </div>
      </div>
    </div>

    <!-- 4. 底部操作按钮栏 (Figma 86:8397) -->
    <div class="w-full flex items-center gap-3 pt-2">
      <!-- 保存设置 -->
      <button
        type="button"
        @click="handleSave"
        class="px-6 py-2 rounded-[8px] bg-[#F9C86D] text-[14px] leading-[20px] font-medium text-[#0C0A09] shadow-[0_0_15px_rgba(249,200,109,0.15)] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none"
      >
        保存设置
      </button>

      <!-- 恢复默认 -->
      <button
        type="button"
        @click="handleReset"
        class="px-4 py-2 rounded-[8px] text-[14px] leading-[20px] font-normal text-[#A8A29E]/60 hover:text-[#F5F5F4] active:scale-95 transition-all cursor-pointer select-none"
      >
        恢复默认
      </button>
    </div>
  </div>
</template>
