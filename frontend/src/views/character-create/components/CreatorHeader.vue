<script setup lang="ts">
/**
 * 角色创建器顶部标题栏与快捷操作工具箱 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { type CardParseResult, parseCharacterCardFile } from "@/utils/cardParser";
import { ref } from "vue";

const emit = defineEmits<{
  (e: "import-card", result: CardParseResult): void;
  (e: "import-file", jsonStr: string): void;
  (e: "save-form"): void;
  (e: "clear-form"): void;
  (e: "open-tutorial"): void;
  (e: "open-assets"): void;
}>();

const fileInputRef = ref<HTMLInputElement | null>(null);

function triggerFileInput(): void {
  fileInputRef.value?.click();
}

async function handleFileChange(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const result = await parseCharacterCardFile(file);
  emit("import-card", result);

  if (result.success && result.jsonData) {
    emit("import-file", JSON.stringify(result.jsonData));
  }

  // 清空 input 避免重复选择同一文件不触发 change
  target.value = "";
}
</script>

<template>
  <div class="w-full p-3 flex flex-col gap-4">
    <!-- 隐藏的文件上传 input (支持 .json, .png 及常规图片辅助识别) -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".json,.png,.jpg,.jpeg,.webp"
      class="hidden"
      @change="handleFileChange"
    />

    <!-- 顶部卡片主体: border-radius: 12px; border: 0.667px solid rgba(83, 71, 65, 0.20); bg: rgba(26, 25, 21, 0.60) -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      
      <!-- 1. 标题区 (魔法棒 + 原创角色卡 + 英文副标) -->
      <div class="flex items-center gap-3">
        <!-- 发光魔法棒图标 (带光晕滤镜) -->
        <div class="relative flex items-center justify-center">
          <svg class="w-8 h-8 filter drop-shadow-[0_0_16px_rgba(249,200,109,0.25)]" viewBox="0 0 32 32" fill="none">
            <path d="M27.1467 3.14668L28.8533 4.85334C29.0065 5.00244 29.1283 5.18072 29.2115 5.37767C29.2946 5.57462 29.3375 5.78623 29.3375 6.00001C29.3375 6.21379 29.2946 6.4254 29.2115 6.62235C29.1283 6.8193 29.0065 6.99758 28.8533 7.14668L7.14666 28.8533C6.99757 29.0066 6.81928 29.1283 6.62233 29.2115C6.42539 29.2946 6.21377 29.3375 5.99999 29.3375C5.78621 29.3375 5.5746 29.2946 5.37765 29.2115C5.18071 29.1283 5.00242 29.0066 4.85333 28.8533L3.14666 27.1467C2.99508 26.9967 2.87475 26.8181 2.79263 26.6212C2.71051 26.4244 2.66823 26.2133 2.66823 26C2.66823 25.7867 2.71051 25.5756 2.79263 25.3788C2.87475 25.182 2.99508 25.0034 3.14666 24.8533L24.8533 3.14668C25.0034 2.9951 25.1819 2.87477 25.3788 2.79265C25.5756 2.71053 25.7867 2.66824 26 2.66824C26.2133 2.66824 26.4244 2.71053 26.6212 2.79265C26.8181 2.87477 26.9966 2.9951 27.1467 3.14668Z" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M18.6667 9.33334L22.6667 13.3333" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6.66667 8V13.3333" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M25.3333 18.6667V24" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13.3333 2.66666V5.33332" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 10.6667H4" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M28 21.3333H22.6667" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14.6667 4H12" stroke="#F9C86D" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <!-- 背景微金圆晕 -->
          <div class="absolute inset-0 rounded-full bg-[#F9C86D]/15 blur-sm" />
        </div>

        <!-- 文本标题 -->
        <div class="flex flex-col">
          <h1 class="text-[24px] font-semibold text-[#F5F5F4] tracking-[1.2px] leading-tight select-none">
            原创角色卡
          </h1>
          <span class="text-sm text-[#78716C] font-mono tracking-tight select-none mt-0.5">
            Create Your Character Card
          </span>
        </div>
      </div>

      <!-- 2. 操作按钮组 (2 列 Grid 布局) -->
      <div class="grid grid-cols-2 gap-2 w-full pt-1">
        <!-- 按钮 1: 文件导入 (高亮实心金黄) -->
        <button
          type="button"
          @click="triggerFileInput"
          class="h-9 px-3 rounded-lg bg-[#F9C86D] hover:bg-[#FFD475] active:scale-95 text-[#0C0A09] font-medium text-xs flex items-center justify-center gap-1.5 transition-all shadow-md cursor-pointer select-none"
        >
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M8 2V10" stroke="#0C0A09" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M11.3333 5.33333L8 2L4.66666 5.33333" stroke="#0C0A09" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 10V12.6667C14 13.0203 13.8595 13.3594 13.6095 13.6095C13.3594 13.8595 13.0203 14 12.6667 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V10" stroke="#0C0A09" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>文件导入</span>
        </button>

        <!-- 按钮 2: 保存表格 (香槟金细边框) -->
        <button
          type="button"
          @click="emit('save-form')"
          class="h-9 px-3 rounded-lg border border-[#F9C86D] hover:bg-[#F9C86D]/10 active:scale-95 text-[#F9C86D] font-medium text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer select-none"
        >
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M8 10V2" stroke="#F9C86D" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14 10V12.6667C14 13.0203 13.8595 13.3594 13.6095 13.6095C13.3594 13.8595 13.0203 14 12.6667 14H3.33333C2.97971 14 2.64057 13.8595 2.39052 13.6095C2.14048 13.3594 2 13.0203 2 12.6667V10" stroke="#F9C86D" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.66666 6.66666L8 9.99999L11.3333 6.66666" stroke="#F9C86D" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>保存表格</span>
        </button>

        <!-- 按钮 3: 清空表格 (红色警示按钮) -->
        <button
          type="button"
          @click="emit('clear-form')"
          class="h-9 px-3 rounded-lg bg-[#EF4444] hover:bg-red-600 active:scale-95 text-[#F4E8C1] font-medium text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer select-none shadow"
        >
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M12 4L4 12" stroke="#F4E8C1" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 4L12 12" stroke="#F4E8C1" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>清空表格</span>
        </button>

        <!-- 按钮 4: 高级教程 -->
        <button
          type="button"
          @click="emit('open-tutorial')"
          class="h-9 px-3 rounded-lg border border-[#44403C] hover:text-white hover:border-[#666] active:scale-95 text-[#A8A29E] font-medium text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer select-none"
        >
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M8 4.66667V14" stroke="#A8A29E" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2 12C1.82319 12 1.65362 11.9298 1.5286 11.8047C1.40357 11.6797 1.33334 11.5101 1.33334 11.3333V2.66667C1.33334 2.48986 1.40357 2.32029 1.5286 2.19526C1.65362 2.07024 1.82319 2 2 2H5.33334C6.04058 2 6.71886 2.28095 7.21895 2.78105C7.71905 3.28115 8 3.95942 8 4.66667C8 3.95942 8.28095 3.28115 8.78105 2.78105C9.28115 2.28095 9.95943 2 10.6667 2H14C14.1768 2 14.3464 2.07024 14.4714 2.19526C14.5964 2.32029 14.6667 2.48986 14.6667 2.66667V11.3333C14.6667 11.5101 14.5964 11.6797 14.4714 11.8047C14.3464 11.9298 14.1768 12 14 12H10C9.46957 12 8.96086 12.2107 8.58579 12.5858C8.21072 12.9609 8 13.4696 8 14C8 13.4696 7.78929 12.9609 7.41422 12.5858C7.03914 12.2107 6.53044 12 6 12H2Z" stroke="#A8A29E" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>高级教程</span>
        </button>

        <!-- 按钮 5: 我的素材库 (单占一整行或左列) -->
        <button
          type="button"
          @click="emit('open-assets')"
          class="h-9 px-3 rounded-lg border border-[#44403C] hover:text-white hover:border-[#666] active:scale-95 text-[#A8A29E] font-medium text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer select-none"
        >
          <svg width="15" height="15" viewBox="0 0 16 16" fill="none">
            <path d="M4 9.33334L5 7.4C5.10872 7.1841 5.27408 7.00181 5.47841 6.87264C5.68274 6.74346 5.91833 6.67227 6.16 6.66667H13.3333M13.3333 6.66667C13.537 6.66631 13.7381 6.71263 13.9211 6.80206C14.1041 6.89149 14.2642 7.02166 14.3891 7.18258C14.5139 7.3435 14.6003 7.53089 14.6415 7.73037C14.6827 7.92985 14.6776 8.13612 14.6267 8.33334L13.6 12.3333C13.5257 12.621 13.3575 12.8757 13.1219 13.0569C12.8864 13.238 12.5971 13.3353 12.3 13.3333H2.66667C2.31305 13.3333 1.97391 13.1929 1.72386 12.9428C1.47381 12.6928 1.33334 12.3536 1.33334 12V3.33334C1.33334 2.97971 1.47381 2.64058 1.72386 2.39053C1.97391 2.14048 2.31305 2 2.66667 2H5.26667C5.48966 1.99782 5.70964 2.0516 5.90647 2.15642C6.1033 2.26124 6.2707 2.41375 6.39334 2.6L6.93334 3.4C7.05474 3.58436 7.22002 3.73568 7.41434 3.84041C7.60865 3.94513 7.82593 3.99997 8.04667 4H12C12.3536 4 12.6928 4.14048 12.9428 4.39053C13.1929 4.64058 13.3333 4.97971 13.3333 5.33334V6.66667Z" stroke="#A8A29E" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>我的素材库</span>
        </button>
      </div>

    </div>
  </div>
</template>
