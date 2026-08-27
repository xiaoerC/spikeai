<script setup lang="ts">
/**
 * 新建/编辑指令 1:1 模态弹框 (Figma 81:3138 像素级高保真)
 *
 * @packageDocumentation
 */

import { AppModal } from "@/components/common";
import type { CommandItem } from "@/views/history/types";
import { X } from "lucide-vue-next";
import { ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  command: CommandItem | null;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (
    e: "save",
    payload: {
      id?: string;
      label: string;
      content: string;
    },
  ): void;
}>();

const formLabel = ref("");
const formContent = ref("");

watch(
  () => props.command,
  (val) => {
    if (val) {
      formLabel.value = val.label || "";
      formContent.value = val.content || "";
    } else {
      formLabel.value = "";
      formContent.value = "";
    }
  },
  { immediate: true },
);

function handleSave() {
  emit("save", {
    id: props.command?.id,
    label: formLabel.value,
    content: formContent.value,
  });
}
</script>

<template>
  <AppModal
    :open="open"
    @update:open="emit('update:open', $event)"
    size="md"
  >
    <div class="w-full flex flex-col rounded-[8px] border-2 border-[#A8B968] bg-[#1C1917] shadow-[0_25px_50px_-12px_rgba(168,185,104,0.20)] overflow-hidden text-left">
      <!-- 1. Header 栏 -->
      <div class="w-full flex items-center justify-between px-4 py-3 border-b-2 border-[#A8B968]/30">
        <h2 class="text-[18px] font-semibold text-[#A8B968] leading-[21.6px] tracking-[-0.36px]">
          {{ command ? "编辑指令" : "新建指令" }}
        </h2>
        <button
          type="button"
          @click="emit('update:open', false)"
          class="w-8 h-8 rounded-full flex items-center justify-center text-[#C8D89F] hover:bg-white/5 active:scale-95 transition-all cursor-pointer"
        >
          <X class="w-5 h-5 stroke-[2]" />
        </button>
      </div>

      <!-- 2. Form 表单区 (Figma 81:3138) -->
      <div class="p-4 flex flex-col gap-3 max-h-[75vh] overflow-y-auto">
        <!-- ① 按钮标签 * -->
        <div class="flex flex-col">
          <label class="text-[14px] leading-[20px] text-[#C8D89F] pb-1.5 flex items-center gap-1">
            <span>按钮标签</span>
            <span class="text-[#FF6467] font-bold">*</span>
          </label>
          <input
            v-model="formLabel"
            type="text"
            placeholder="按钮显示文本"
            maxlength="20"
            class="w-full px-3 py-2.5 rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] text-[15px] text-[#F5F5F4] placeholder-[#6B6460] focus:border-[#A8B968] focus:outline-none transition-colors"
          />
          <div class="w-full text-right text-[12px] text-[#6B6460] pt-1">
            {{ formLabel.length }}/20
          </div>
        </div>

        <!-- ② 指令内容 * -->
        <div class="flex flex-col">
          <label class="text-[14px] leading-[20px] text-[#C8D89F] pb-1.5 flex items-center gap-1">
            <span>指令内容</span>
            <span class="text-[#FF6467] font-bold">*</span>
          </label>
          <textarea
            v-model="formContent"
            rows="5"
            placeholder="输入指令内容..."
            maxlength="2000"
            class="w-full px-3 py-2.5 rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] text-[14px] leading-[22px] text-[#F5F5F4] placeholder-[#6B6460] focus:border-[#A8B968] focus:outline-none resize-none transition-colors"
          ></textarea>
          <div class="w-full text-right text-[12px] text-[#6B6460] pt-1">
            {{ formContent.length }}/2000
          </div>
        </div>

        <!-- ③ 底部操作按钮 (取消 / 保存) -->
        <div class="w-full flex items-center justify-end gap-3 pt-4">
          <button
            type="button"
            @click="emit('update:open', false)"
            class="px-4 py-2 rounded-[4px] border border-[#44403C] text-[15px] text-[#C8D89F] hover:bg-white/5 active:scale-95 transition-all cursor-pointer select-none"
          >
            取消
          </button>
          <button
            type="button"
            @click="handleSave"
            class="px-5 py-2 rounded-[4px] bg-[#A8B968] text-[15px] font-bold text-[#1C1917] hover:bg-[#B8C978] active:scale-95 transition-all cursor-pointer select-none shadow-md"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </AppModal>
</template>
