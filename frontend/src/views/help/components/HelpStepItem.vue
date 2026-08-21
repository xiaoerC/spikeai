<script setup lang="ts">
/**
 * 帮助中心新手指南步骤项组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { HelpStep } from "@/views/help/types";
import { Check, Copy } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{
  step: HelpStep;
}>();

const emit = defineEmits<(e: "copy", text: string) => void>();

const isCopied = ref(false);

function handleCopy(text: string) {
  emit("copy", text);
  isCopied.value = true;
  setTimeout(() => {
    isCopied.value = false;
  }, 2000);
}
</script>

<template>
  <div class="w-full rounded-xl border border-[rgba(168,162,158,0.25)] bg-[rgba(26,21,16,0.90)] p-4 flex flex-col gap-3 shadow-md">
    <!-- 头部: 步骤编号 Badge + 标题 -->
    <div class="flex items-center gap-2.5">
      <span class="w-7 h-7 rounded-lg bg-[#F9C86D]/20 border border-[#F9C86D]/40 text-[#F9C86D] text-xs font-extrabold flex items-center justify-center font-mono">
        {{ step.stepNumber }}
      </span>
      <h3 class="text-sm font-bold text-[#F5F5F4]">
        {{ step.title }}
      </h3>
    </div>

    <!-- 描述正文 -->
    <p v-if="step.description" class="text-xs text-[#A8A29E] leading-relaxed whitespace-pre-line">
      {{ step.description }}
    </p>

    <!-- 推荐徽章 (如 Chrome / Edge) -->
    <div v-if="step.badges && step.badges.length > 0" class="flex flex-wrap gap-2 pt-1">
      <span
        v-for="badge in step.badges"
        :key="badge"
        class="px-2.5 py-1 rounded-md bg-[#292524] border border-white/10 text-[#D6D3D1] text-[11px] font-medium"
      >
        {{ badge }}
      </span>
    </div>

    <!-- 子章节与场景匹配 (如 2.1, 2.2, 2.3) -->
    <div v-if="step.subsections" class="flex flex-col gap-3 pt-1">
      <div
        v-for="(sub, idx) in step.subsections"
        :key="idx"
        class="p-3 rounded-lg bg-[#221F1D] border border-white/5 flex flex-col gap-2"
      >
        <h4 class="text-xs font-bold text-[#F9C86D]">
          {{ sub.subtitle }}
        </h4>
        <p class="text-xs text-[#A8A29E] leading-relaxed">
          {{ sub.detail }}
        </p>

        <!-- 场景列表 -->
        <div v-if="sub.scenarios" class="flex flex-col gap-2 mt-1">
          <div
            v-for="(sc, sIdx) in sub.scenarios"
            :key="sIdx"
            class="p-2.5 rounded bg-[#1C1917] border border-white/5 text-xs flex flex-col gap-1"
          >
            <div class="flex items-center gap-1.5 text-[#F5F5F4] font-semibold">
              <span class="px-1.5 py-0.5 rounded bg-[#383330] text-[10px] text-[#F9C86D]">{{ sc.name }}</span>
              <span>{{ sc.desc }}</span>
            </div>
            <div class="text-emerald-400 font-medium pl-1">
              👉 {{ sc.match }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 推荐指令卡片 (一键复制) -->
    <div v-if="step.promptCommand" class="p-3 rounded-lg bg-[#221F1D] border border-[#F9C86D]/30 flex flex-col gap-2 mt-1">
      <div class="flex items-center justify-between text-xs">
        <span class="text-[#F9C86D] font-bold">✨ 推荐指令</span>
        <button
          type="button"
          @click="handleCopy(step.promptCommand!)"
          class="flex items-center gap-1 px-2.5 py-1 rounded bg-[#F9C86D] text-[#0C0A09] text-xs font-bold hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none"
        >
          <Check v-if="isCopied" class="w-3.5 h-3.5" />
          <Copy v-else class="w-3.5 h-3.5" />
          <span>{{ isCopied ? "已复制" : "复制" }}</span>
        </button>
      </div>
      <div class="p-2 rounded bg-[#161412] font-mono text-xs text-[#E7E5E4] break-all select-all border border-white/5">
        {{ step.promptCommand }}
      </div>
    </div>

    <!-- 桌面添加步骤列表 (06) -->
    <div v-if="step.stepGuideList" class="flex flex-col gap-1.5 pt-1">
      <div
        v-for="(guide, gIdx) in step.stepGuideList"
        :key="gIdx"
        class="flex items-center gap-2 text-xs text-[#A8A29E]"
      >
        <span class="w-4 h-4 rounded-full bg-[#383330] text-[#F9C86D] text-[10px] font-bold flex items-center justify-center font-mono">
          {{ gIdx + 1 }}
        </span>
        <span>{{ guide }}</span>
      </div>
    </div>
  </div>
</template>
