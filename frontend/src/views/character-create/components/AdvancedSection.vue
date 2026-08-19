<script setup lang="ts">
/**
 * 模块 6: 高级设置与世界书挂载组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { ChevronDown, ChevronUp, Settings } from "lucide-vue-next";
import { ref } from "vue";

defineProps<{
  /** 系统级前置 Prompt */
  systemPrompt: string;
  /** 对话后置指令 */
  postHistoryInstructions: string;
}>();

const emit = defineEmits<{
  (e: "update:systemPrompt", val: string): void;
  (e: "update:postHistoryInstructions", val: string): void;
}>();

const isExpanded = ref<boolean>(false);
</script>

<template>
  <div class="w-full px-3 pb-3">
    <!-- 模块外层容器 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      
      <!-- 1. 模块主标题 (折叠头部) -->
      <div
        @click="isExpanded = !isExpanded"
        class="flex items-center justify-between w-full cursor-pointer select-none"
      >
        <div class="flex items-center gap-3">
          <div class="w-1 h-6 rounded-full bg-[#10B981] shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
          <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[0.9px] leading-tight">
            高级设置
          </h2>
          <span class="text-xs text-[#78716C] font-normal">
            高级补充信息 (可不填)
          </span>
        </div>

        <button type="button" class="text-[#A8A29E] hover:text-white">
          <ChevronUp v-if="isExpanded" class="w-5 h-5" />
          <ChevronDown v-else class="w-5 h-5" />
        </button>
      </div>

      <!-- 2. 折叠表单内容 -->
      <div v-if="isExpanded" class="flex flex-col gap-4 pt-2 animate-fade-in">
        <!-- 系统前置 System Prompt -->
        <div class="flex flex-col gap-2">
          <label class="text-xs text-[#A8A29E]">前置 System Prompt (覆盖全局角色扮演系统提示)</label>
          <textarea
            :value="systemPrompt"
            @input="emit('update:systemPrompt', ($event.target as HTMLTextAreaElement).value)"
            rows="3"
            class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs font-mono text-gray-100 placeholder-[#78716C] focus:border-[#10B981] transition-colors resize-none leading-relaxed"
            placeholder="自定义全局 System Prompt 指令..."
          />
        </div>

        <!-- 对话后置指令 -->
        <div class="flex flex-col gap-2">
          <label class="text-xs text-[#A8A29E]">后置指导指令 Post History Instructions</label>
          <textarea
            :value="postHistoryInstructions"
            @input="emit('update:postHistoryInstructions', ($event.target as HTMLTextAreaElement).value)"
            rows="3"
            class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs font-mono text-gray-100 placeholder-[#78716C] focus:border-[#10B981] transition-colors resize-none leading-relaxed"
            placeholder="注入在历史记录最末尾的引导词..."
          />
        </div>
      </div>

    </div>
  </div>
</template>
