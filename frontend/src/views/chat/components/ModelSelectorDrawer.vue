<script setup lang="ts">
/**
 * AI 聊天界面 - 模型选择抽屉 (基于 AppDrawer)
 *
 * @packageDocumentation
 */

import { AppDrawer } from "@/components/common";
import { type AiModelItem, MOCK_AI_MODELS } from "@/views/chat/constants/mockChatData";
import { Check, Cpu, Moon, Zap } from "lucide-vue-next";

defineProps<{
  open: boolean;
  currentModelId: string;
}>();

const emit = defineEmits<{
  (e: "update:open", value: boolean): void;
  (e: "selectModel", model: AiModelItem): void;
}>();

function handleSelect(model: AiModelItem): void {
  emit("selectModel", model);
  emit("update:open", false);
}
</script>

<template>
  <AppDrawer
    :open="open"
    @update:open="(val) => emit('update:open', val)"
    title="选择对话大模型"
    description="选择适合当前剧情深度与响应速度的 AI 语言模型"
  >
    <div class="flex flex-col gap-2.5 p-1">
      <div
        v-for="model in MOCK_AI_MODELS"
        :key="model.id"
        @click="handleSelect(model)"
        :class="[
          'p-3 rounded-xl border flex items-center justify-between transition-all cursor-pointer select-none',
          model.id === currentModelId
            ? 'bg-[#F9C86D]/10 border-[#F9C86D] shadow-gold'
            : 'bg-[#292524]/60 border-[#44403C]/60 hover:border-[#F9C86D]/40'
        ]"
      >
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-lg bg-[#1A1714] border border-[#44403C] flex items-center justify-center text-[#F9C86D]">
            <Cpu class="w-5 h-5" />
          </div>

          <div class="flex flex-col">
            <div class="flex items-center gap-2">
              <span class="text-sm font-semibold text-[#F5F5F4]">
                {{ model.name }}
              </span>
              <span
                v-if="model.isStreaming"
                class="px-1.5 py-0.5 rounded text-[10px] bg-[#22C55E]/10 text-[#22C55E] flex items-center gap-0.5"
              >
                <Zap class="w-2.5 h-2.5" />
                流式
              </span>
            </div>
            <span class="text-xs text-[#FF9F43] mt-0.5">
              {{ model.freeCountText }}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1 text-xs font-mono text-[#F9C86D]">
            <Moon class="w-3.5 h-3.5 text-[#FF9F43]" />
            <span>{{ model.cost }} / 次</span>
          </div>

          <div
            class="w-5 h-5 rounded-full border flex items-center justify-center"
            :class="model.id === currentModelId ? 'border-[#F9C86D] bg-[#F9C86D] text-[#0C0A09]' : 'border-[#44403C] text-transparent'"
          >
            <Check class="w-3 h-3" />
          </div>
        </div>
      </div>
    </div>
  </AppDrawer>
</template>
