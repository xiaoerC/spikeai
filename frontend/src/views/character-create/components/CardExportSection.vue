<script setup lang="ts">
/**
 * 模块 8: 实时卡片预览、表单校验与角色卡导出下载 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { AppButton } from "@/components/common";
import { useCardExporter } from "@/views/character-create/composables/useCardExporter";
import type { CharacterFormData, FormValidationError } from "@/views/character-create/types";
import { AlertCircle, Check, Code, Copy, Download, Eye } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{
  /** 角色全量表单数据 */
  formData: CharacterFormData;
  /** 校验错误列表 */
  validationErrors: FormValidationError[];
  /** 是否通过全部校验 */
  isValid: boolean;
}>();

const { jsonPreviewString, downloadJsonFile, copyJsonToClipboard } = useCardExporter({
  value: props.formData,
});

const isJsonExpanded = ref<boolean>(false);
const isCopied = ref<boolean>(false);

async function handleCopyJson(): Promise<void> {
  const ok = await copyJsonToClipboard();
  if (ok) {
    isCopied.value = true;
    setTimeout(() => {
      isCopied.value = false;
    }, 2000);
  }
}
</script>

<template>
  <div class="w-full px-3 pb-24 flex flex-col gap-4">
    
    <!-- 1. 实时卡片预览微缩模型 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <div class="flex items-center gap-2 text-sm font-semibold text-[#F5F5F4]">
        <Eye class="w-4 h-4 text-[#F9C86D]" />
        <span>实时预览</span>
      </div>

      <!-- 微缩卡片容器 -->
      <div class="w-full h-44 rounded-xl overflow-hidden border border-[rgba(83,71,65,0.30)] bg-gradient-to-t from-black via-[#161412] to-[#2A231C] relative flex flex-col justify-end p-4 shadow-lg">
        <img
          v-if="formData.avatarUrl"
          :src="formData.avatarUrl"
          alt="Avatar Preview"
          class="absolute inset-0 w-full h-full object-cover opacity-60"
        />
        <div class="absolute inset-0 bg-gradient-to-t from-[#0C0A09] via-transparent to-transparent" />

        <div class="relative z-10 flex flex-col gap-1.5">
          <h3 class="text-base font-bold text-white tracking-wide">
            {{ formData.name || "角色名称" }}
          </h3>
          <div v-if="formData.tags.length > 0" class="flex flex-wrap gap-1">
            <span
              v-for="t in formData.tags"
              :key="t"
              class="px-2 py-0.5 rounded bg-black/40 text-[10px] text-[#F9C86D] border border-[#F9C86D]/30"
            >
              #{{ t }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 校验与下载操作卡片 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      
      <!-- 未完善提示 -->
      <div v-if="!isValid" class="flex flex-col gap-2 p-3 rounded-lg bg-amber-950/20 border border-amber-500/20 text-xs text-amber-300">
        <div class="flex items-center gap-1.5 font-semibold text-amber-200">
          <AlertCircle class="w-4 h-4" />
          <span>内容尚不完善</span>
        </div>
        <ul class="flex flex-col gap-1 pl-4 list-disc list-inside text-amber-300/80">
          <li v-for="err in validationErrors" :key="err.field">
            {{ err.message }}
          </li>
        </ul>
      </div>

      <!-- 下载大按钮 (金黄渐变实心大按钮) -->
      <button
        type="button"
        :disabled="!isValid"
        @click="downloadJsonFile"
        :class="[
          'w-full h-11 rounded-xl font-semibold text-sm flex items-center justify-center gap-2 transition-all shadow-xl select-none',
          isValid
            ? 'bg-gradient-to-r from-[#FFD475] via-[#F9C86D] to-[#D1A35C] text-[#0C0A09] hover:opacity-90 active:scale-[0.98] cursor-pointer'
            : 'bg-neutral-800 text-neutral-500 cursor-not-allowed opacity-50'
        ]"
      >
        <Download class="w-4 h-4" />
        <span>下载角色卡</span>
      </button>

      <!-- 社区上传收益引导说明 -->
      <p class="text-center text-[11px] text-[#78716C] leading-normal">
        从历史记录-我的上传-上传到社区，即可上传（原创卡片享受星元/月华回报）
      </p>
    </div>

    <!-- 3. JSON 格式代码预览折叠卡片 -->
    <div class="w-full p-4 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2 text-xs font-medium text-[#F5F5F4]">
          <Code class="w-4 h-4 text-[#38BDF8]" />
          <span>JSON 规范预览 (SillyTavern V2 标准)</span>
        </div>
        <button
          type="button"
          @click="isJsonExpanded = !isJsonExpanded"
          class="text-xs text-[#F9C86D] hover:underline cursor-pointer select-none"
        >
          {{ isJsonExpanded ? "收起代码" : "展开代码" }}
        </button>
      </div>

      <div v-if="isJsonExpanded" class="flex flex-col gap-2 pt-2 animate-fade-in">
        <div class="relative">
          <pre class="w-full max-h-60 p-3 rounded-lg bg-black/80 text-[11px] font-mono text-emerald-400 overflow-x-auto overflow-y-auto leading-relaxed border border-white/5">{{ jsonPreviewString }}</pre>
          <!-- 一键复制按钮 -->
          <button
            type="button"
            @click="handleCopyJson"
            class="absolute top-2 right-2 p-1.5 rounded-md bg-white/10 hover:bg-white/20 text-gray-200 text-xs flex items-center gap-1 backdrop-blur cursor-pointer"
          >
            <Check v-if="isCopied" class="w-3.5 h-3.5 text-green-400" />
            <Copy v-else class="w-3.5 h-3.5" />
            <span>{{ isCopied ? "已复制" : "复制" }}</span>
          </button>
        </div>
      </div>
    </div>

  </div>
</template>
