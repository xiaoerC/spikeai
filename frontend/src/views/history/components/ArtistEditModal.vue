<script setup lang="ts">
/**
 * 新建/编辑画师串 1:1 模态弹框 (Figma 84:7007 像素级高保真)
 *
 * @packageDocumentation
 */

import { AppModal } from "@/components/common";
import type { ArtistPromptItem } from "@/views/history/types";
import { Check, X } from "lucide-vue-next";
import { ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  artist: ArtistPromptItem | null;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (
    e: "save",
    payload: {
      id?: string;
      name: string;
      prompt: string;
      description?: string;
      negativePrompt?: string;
      isActive: boolean;
    },
  ): void;
}>();

// 内置风格预设
const SYSTEM_PRESETS = [
  {
    id: "anime",
    name: "二次元",
    label: "二次元日系动漫风格",
    description: "日系动漫风格，鲜艳的色彩和动态构图",
    prompt:
      "0.55::meion::,0.55::aoisakura(seak5545)::,0.75::qiandaiyiyu::,0.75::akitahika::,0.75::dishwasher1910 ::,0.75::ke-ta::,0.95::wakaba(945599620)::,0.95::omone_hokoma_agm ::,1.25::mignon::,1.25::rebun::,1.45::cohi27151463 ::,1.55::myomomoo::,-1::ai-generated, ai-assisted, ::,-1::unfinished::, chiaroscuro",
    negativePrompt: "lowres, bad anatomy, bad hands, missing fingers",
  },
  {
    id: "oil-painting",
    name: "厚涂唯美油画",
    label: "写实厚涂唯美油画风",
    description: "古典大师油画质感，细腻笔触与深邃光影",
    prompt:
      "masterpiece, oil painting, highly detailed, dramatic lighting, rich texture, chiaroscuro, art by greg rutkowski, wlop, alphonse mucha",
    negativePrompt: "3d render, cartoon, flat color, blurry, low quality",
  },
  {
    id: "cyberpunk",
    name: "赛博朋克霓虹",
    label: "赛博朋克霓虹光影风",
    description: "未来科幻夜景，霓虹反光与雨夜机械都市",
    prompt:
      "cyberpunk city, neon lights, rainy street, cinematic lighting, ultra detailed, volumetric light, octane render, 8k resolution",
    negativePrompt: "daylight, nature, rustic, lowres, oversaturated",
  },
  {
    id: "chinese-ink",
    name: "国风仙侠水墨",
    label: "古风仙侠水墨国潮风",
    description: "飘逸古风水墨意境，东方仙侠唯美长衫",
    prompt:
      "traditional chinese painting, ink wash style, ethereal, flowing silk robes, misty mountains, dynamic brushwork, elegant atmosphere",
    negativePrompt: "modern clothing, western style, high contrast neon",
  },
];

const selectedPreset = ref("");
const formName = ref("");
const formPrompt = ref("");
const formDescription = ref("");
const formNegativePrompt = ref("");
const formIsActive = ref(false);

watch(
  () => props.artist,
  (val) => {
    if (val) {
      selectedPreset.value = "";
      formName.value = val.name || "";
      formPrompt.value = val.prompt || "";
      formDescription.value = val.description || "";
      formNegativePrompt.value = val.negativePrompt || "";
      formIsActive.value = !!val.isActive;
    } else {
      selectedPreset.value = "";
      formName.value = "";
      formPrompt.value = "";
      formDescription.value = "";
      formNegativePrompt.value = "";
      formIsActive.value = false;
    }
  },
  { immediate: true },
);

function handleSelectPreset(event: Event) {
  const target = event.target as HTMLSelectElement;
  const presetId = target.value;
  const preset = SYSTEM_PRESETS.find((p) => p.id === presetId);
  if (preset) {
    formName.value = preset.name;
    formPrompt.value = preset.prompt;
    formDescription.value = preset.description;
    formNegativePrompt.value = preset.negativePrompt;
  }
}

function handleSave() {
  emit("save", {
    id: props.artist?.id,
    name: formName.value,
    prompt: formPrompt.value,
    description: formDescription.value,
    negativePrompt: formNegativePrompt.value,
    isActive: formIsActive.value,
  });
}
</script>

<template>
  <AppModal
    :open="open"
    @update:open="emit('update:open', $event)"
    size="md"
  >
    <div class="w-full flex flex-col rounded-[8px] border-2 border-[#EC4899] bg-[#1C1917] shadow-[0_25px_50px_-12px_rgba(236,72,153,0.20)] overflow-hidden text-left">
      <!-- 1. Header 栏 -->
      <div class="w-full flex items-center justify-between px-4 py-3 border-b-2 border-[#EC4899]/30">
        <h2 class="text-[18px] font-semibold text-[#EC4899] leading-[21.6px] tracking-[-0.36px]">
          {{ artist ? "编辑画师串" : "新建画师串" }}
        </h2>
        <button
          type="button"
          @click="emit('update:open', false)"
          class="w-8 h-8 rounded-full flex items-center justify-center text-[#F9A8D4] hover:bg-white/5 active:scale-95 transition-all cursor-pointer"
        >
          <X class="w-5 h-5 stroke-[2]" />
        </button>
      </div>

      <!-- 2. Form 表单区 (Figma 84:7007) -->
      <div class="p-4 flex flex-col gap-3 max-h-[75vh] overflow-y-auto">
        <!-- ① 使用系统预设（可选） -->
        <div class="flex flex-col">
          <label class="text-[14px] leading-[20px] text-[#F9A8D4] pb-0.5">
            使用系统预设（可选）
          </label>
          <p class="text-[12px] text-[#9CA3AF] leading-[16px] pb-1.5">
            选择一个预设风格快速开始，或留空自定义
          </p>
          <select
            v-model="selectedPreset"
            @change="handleSelectPreset"
            class="w-full px-3 py-2.5 rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] text-[15px] text-[#F5F5F4] focus:border-[#EC4899] focus:outline-none transition-colors"
          >
            <option value="" class="bg-[#1C1917] text-[#9CA3AF]">-- 选择预设风格 --</option>
            <option
              v-for="preset in SYSTEM_PRESETS"
              :key="preset.id"
              :value="preset.id"
              class="bg-[#1C1917] text-[#F5F5F4]"
            >
              {{ preset.label }}
            </option>
          </select>
        </div>

        <!-- ② 画师串名称 * -->
        <div class="flex flex-col">
          <label class="text-[14px] leading-[20px] text-[#F9A8D4] pb-1.5 flex items-center gap-1">
            <span>画师串名称</span>
            <span class="text-[#FF6467] font-bold">*</span>
          </label>
          <input
            v-model="formName"
            type="text"
            placeholder="给这个画师串起个名字"
            maxlength="100"
            class="w-full px-3 py-2.5 rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] text-[15px] text-[#F5F5F4] placeholder-[#6B6460] focus:border-[#EC4899] focus:outline-none transition-colors"
          />
          <div class="w-full text-right text-[12px] text-[#6B6460] pt-1">
            {{ formName.length }}/100
          </div>
        </div>

        <!-- ③ 提示词文本 * -->
        <div class="flex flex-col">
          <label class="text-[14px] leading-[20px] text-[#F9A8D4] pb-0.5 flex items-center gap-1">
            <span>提示词文本</span>
            <span class="text-[#FF6467] font-bold">*</span>
          </label>
          <p class="text-[12px] text-[#9CA3AF] leading-[16px] pb-1.5">
            使用英文标签，逗号分隔。这些提示词会与AI生成的场景标签组合
          </p>
          <textarea
            v-model="formPrompt"
            rows="4"
            placeholder="例如: anime style, vibrant colors, detailed background..."
            maxlength="2000"
            class="w-full px-3 py-2.5 rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] text-[14px] leading-[22px] text-[#F5F5F4] placeholder-[#6B6460] focus:border-[#EC4899] focus:outline-none resize-none transition-colors"
          ></textarea>
          <div class="w-full text-right text-[12px] text-[#6B6460] pt-1">
            {{ formPrompt.length }}/2000
          </div>
        </div>

        <!-- ④ 描述（可选） -->
        <div class="flex flex-col">
          <label class="text-[14px] leading-[20px] text-[#F9A8D4] pb-0.5">
            描述（可选）
          </label>
          <p class="text-[12px] text-[#9CA3AF] leading-[16px] pb-1.5">
            为这个画师串添加一些说明，帮助你记住它的用途
          </p>
          <textarea
            v-model="formDescription"
            rows="2"
            placeholder="例如: 适合绘制温馨的日常场景..."
            maxlength="500"
            class="w-full px-3 py-2.5 rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] text-[14px] leading-[22px] text-[#F5F5F4] placeholder-[#6B6460] focus:border-[#EC4899] focus:outline-none resize-none transition-colors"
          ></textarea>
          <div class="w-full text-right text-[12px] text-[#6B6460] pt-1">
            {{ formDescription.length }}/500
          </div>
        </div>

        <!-- ⑤ 负面提示词（可选） -->
        <div class="flex flex-col">
          <label class="text-[14px] leading-[20px] text-[#F9A8D4] pb-0.5">
            负面提示词（可选）
          </label>
          <p class="text-[12px] text-[#9CA3AF] leading-[16px] pb-1.5">
            用于排除不想要的元素，例如低质量、解剖错误等
          </p>
          <textarea
            v-model="formNegativePrompt"
            rows="2"
            placeholder="例如: lowres, bad anatomy, bad hands..."
            maxlength="2000"
            class="w-full px-3 py-2.5 rounded-[6px] border border-[rgba(83,71,65,0.30)] bg-[rgba(42,37,32,0.50)] text-[14px] leading-[22px] text-[#F5F5F4] placeholder-[#6B6460] focus:border-[#EC4899] focus:outline-none resize-none transition-colors"
          ></textarea>
          <div class="w-full text-right text-[12px] text-[#6B6460] pt-1">
            {{ formNegativePrompt.length }}/2000
          </div>
        </div>

        <!-- ⑥ 激活此画师串 Checkbox -->
        <div
          @click="formIsActive = !formIsActive"
          class="flex items-center gap-2 pt-1 cursor-pointer select-none"
        >
          <div
            :class="[
              'w-4 h-4 rounded-[4px] border flex items-center justify-center transition-all',
              formIsActive
                ? 'bg-[#EC4899] border-[#EC4899] text-[#1C1917]'
                : 'bg-[rgba(42,37,32,0.50)] border-[#6B6460] text-transparent'
            ]"
          >
            <Check class="w-3 h-3 stroke-[3]" />
          </div>
          <span class="text-[14px] text-[#F9A8D4]">
            激活此画师串（同一时间只能激活一个）
          </span>
        </div>

        <!-- ⑦ 底部操作按钮 (取消 / 保存) -->
        <div class="w-full flex items-center justify-end gap-3 pt-4">
          <button
            type="button"
            @click="emit('update:open', false)"
            class="px-4 py-2 rounded-[4px] border border-[#44403C] text-[15px] text-[#F9A8D4] hover:bg-white/5 active:scale-95 transition-all cursor-pointer select-none"
          >
            取消
          </button>
          <button
            type="button"
            @click="handleSave"
            class="px-5 py-2 rounded-[4px] bg-[#EC4899] text-[15px] font-bold text-[#F4E8C1] hover:bg-[#F472B6] active:scale-95 transition-all cursor-pointer select-none shadow-md"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  </AppModal>
</template>
