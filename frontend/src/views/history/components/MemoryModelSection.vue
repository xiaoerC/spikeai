<script setup lang="ts">
/**
 * AI 记忆增强模型主面板 (Figma 90:1083 1:1 像素级高保真)
 *
 * 包含 标题/描述、黄色注意告警框、「关于记忆增强模型」科普卡片、模型选择下拉框与操作按钮。
 *
 * @packageDocumentation
 */

import { ChevronDown, Info, TriangleAlert } from "lucide-vue-next";
import { ref, watch } from "vue";

const props = defineProps<{
  model: string;
}>();

const emit = defineEmits<{
  (e: "save", model: string): void;
  (e: "reset"): void;
}>();

const localModel = ref(props.model || "system");

watch(
  () => props.model,
  (val) => {
    localModel.value = val || "system";
  },
);

const MEMORY_MODELS = [
  {
    id: "system",
    label: "记忆增强 · 默认（system）",
  },
  {
    id: "system-1",
    label: "记忆增强 · 高可用（system-1）",
  },
  {
    id: "system-2",
    label: "记忆增强 · 极速（system-2）",
  },
  {
    id: "claude-3-5-sonnet",
    label: "claude-3-5-sonnet（高级增强）",
  },
  {
    id: "gpt-4o",
    label: "gpt-4o（深度语义归档）",
  },
];

function handleSave() {
  emit("save", localModel.value);
}

function handleReset() {
  localModel.value = "system";
  emit("reset");
}
</script>

<template>
  <div class="w-full px-4 pt-6 flex flex-col pb-12">
    <!-- 1. 标题与说明 (Figma 90:1083) -->
    <div class="w-full flex flex-col">
      <h3 class="text-[16px] font-semibold text-[#F5F5F4] leading-[19.2px] tracking-[-0.32px]">
        记忆增强模型
      </h3>
      <p class="text-[14px] leading-[20px] text-[#78716C] pt-1">
        选择副 AI 使用的模型。模型故障时自动回退到系统默认渠道，确保记忆不丢失。
      </p>
    </div>

    <!-- 2. 黄色注意告警框 (Figma 90:1083) -->
    <div class="w-full mt-4 p-3 rounded-[6px] border border-[#EAB308] bg-[#EAB308]/10 flex items-start gap-2">
      <div class="pt-0.5 flex-shrink-0 text-[#EAB308]">
        <TriangleAlert class="w-4 h-4" />
      </div>
      <p class="text-[12px] leading-[19.5px] text-[#A8A29E]">
        注意：仅 system 开头的渠道（system / system-1/2/3）会员免费且不限次；其余标注「会员免费」的模型包含在每天 30 次中。
      </p>
    </div>

    <!-- 3. 关于记忆增强模型科普卡片 (Figma 90:1083) -->
    <div class="w-full mt-4 p-3 rounded-[6px] border border-[#292524] bg-[#292524] flex flex-col">
      <!-- 卡片头部: 蓝色信息图标 + 标题 -->
      <div class="flex items-center gap-2 pb-2">
        <Info class="w-3.5 h-3.5 text-[#3B82F6] flex-shrink-0" />
        <span class="text-[14px] font-medium text-[#F5F5F4] leading-[20px]">
          关于记忆增强模型
        </span>
      </div>

      <!-- 段落 1 -->
      <p class="text-[12px] leading-[19.5px] text-[#A8A29E] pb-2">
        记忆增强（副 AI）在每条消息后默默整理角色卡的记忆表格——抽取关键信息、版本化归档，让主 AI 能稳定引用前文。故事的连贯性大半由它撑起。
      </p>

      <!-- 段落 2 -->
      <p class="text-[12px] leading-[19.5px] text-[#A8A29E] pb-2">
        默认的 <code class="px-1 py-0.5 rounded bg-[#44403C] text-[#A8A29E] font-mono text-[12px]">system</code> 渠道（含 <code class="px-1 py-0.5 rounded bg-[#44403C] text-[#A8A29E] font-mono text-[12px]">system-1/2/3</code>）由我们持续调优，对绝大多数场景已经够用，<span class="font-medium text-[#F5F5F4]">会员调用全部免费</span>。如果你正常体验中没觉得「角色突然忘事」或「记忆更新慢」，<span class="font-medium text-[#F5F5F4]">保持默认就是最佳选择。</span>
      </p>

      <!-- 段落 3 -->
      <p class="text-[12px] leading-[19.5px] text-[#A8A29E] pb-2">
        提供其他付费模型是为了应对少数情况：你觉得 <span class="font-medium text-[#F5F5F4]">默认渠道近期波动太大</span>（重试/失败次数明显增多）、或 <span class="font-medium text-[#F5F5F4]">记录下来的信息总不满意</span>（关键剧情漏掉、表格更新偏离原意），又或者你对某个特定模型的风格有偏好。这时切换到付费高级模型正常计费，来保证你的最佳体验。
      </p>

      <!-- 段落 4 -->
      <p class="text-[12px] leading-[19.5px] text-[#A8A29E]">
        无论你选哪个模型，失败时系统都会自动回退到 <code class="px-1 py-0.5 rounded bg-[#44403C] text-[#A8A29E] font-mono text-[12px]">system</code> 兜底，<span class="font-medium text-[#F5F5F4]">记忆表格不会丢。</span>
      </p>
    </div>

    <!-- 4. 模型选择下拉框 (Figma 90:1083) -->
    <div class="w-full mt-4">
      <div class="relative w-full">
        <select
          v-model="localModel"
          class="w-full appearance-none px-3 py-2 rounded-[6px] border border-[#44403C] bg-[#292524] text-[16px] leading-[27.2px] text-[#C0A480] focus:border-[#F9C86D] focus:outline-none transition-colors cursor-pointer select-none pr-9"
        >
          <option
            v-for="modelOpt in MEMORY_MODELS"
            :key="modelOpt.id"
            :value="modelOpt.id"
            class="bg-[#292524] text-[#F5F5F4]"
          >
            {{ modelOpt.label }}
          </option>
        </select>
        <div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none text-[#C0A480]">
          <ChevronDown class="w-4 h-4" />
        </div>
      </div>
    </div>

    <!-- 5. 底部操作按钮栏 (Figma 90:1083) -->
    <div class="w-full flex items-center gap-2 pt-4">
      <!-- 保存 -->
      <button
        type="button"
        @click="handleSave"
        class="px-4 py-2 rounded-[6px] bg-[#F9C86D] text-[16px] leading-[27.2px] font-normal text-[#0C0A09] hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none"
      >
        保存
      </button>

      <!-- 恢复默认 -->
      <button
        type="button"
        @click="handleReset"
        class="px-4 py-2 rounded-[6px] border border-[#44403C] text-[16px] leading-[27.2px] font-normal text-[#F5F5F4] hover:bg-white/5 active:scale-95 transition-all cursor-pointer select-none"
      >
        恢复默认
      </button>
    </div>
  </div>
</template>
