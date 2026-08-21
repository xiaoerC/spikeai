<script setup lang="ts">
/**
 * 帮助中心官方指令集列表组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import type { CommandItem } from "@/views/help/types";
import { Check, Copy, Terminal } from "lucide-vue-next";
import { ref } from "vue";

defineProps<{
  commands: CommandItem[];
}>();

const emit = defineEmits<(e: "copy", text: string) => void>();

const copiedId = ref<string | null>(null);

function handleCopy(cmd: CommandItem) {
  emit("copy", cmd.commandText);
  copiedId.value = cmd.id;
  setTimeout(() => {
    copiedId.value = null;
  }, 2000);
}
</script>

<template>
  <div class="flex flex-col gap-3">
    <div
      v-for="cmd in commands"
      :key="cmd.id"
      class="w-full rounded-xl border border-[rgba(168,162,158,0.25)] bg-[rgba(26,21,16,0.90)] p-4 flex flex-col gap-3 shadow-md"
    >
      <!-- 头部: 分类 + 指令名称 + 复制按钮 -->
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2">
          <Terminal class="w-4 h-4 text-[#F9C86D]" />
          <span class="px-2 py-0.5 rounded bg-[#383330] text-[10px] font-bold text-[#F9C86D]">
            {{ cmd.category }}
          </span>
          <h3 class="text-sm font-bold text-[#F5F5F4]">
            {{ cmd.name }}
          </h3>
        </div>

        <button
          type="button"
          @click="handleCopy(cmd)"
          class="flex items-center gap-1 px-2.5 py-1 rounded bg-[#F9C86D] text-[#0C0A09] text-xs font-bold hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer select-none"
        >
          <Check v-if="copiedId === cmd.id" class="w-3.5 h-3.5" />
          <Copy v-else class="w-3.5 h-3.5" />
          <span>{{ copiedId === cmd.id ? "已复制" : "复制" }}</span>
        </button>
      </div>

      <!-- 描述 -->
      <p class="text-xs text-[#A8A29E] leading-relaxed">
        {{ cmd.description }}
      </p>

      <!-- 指令文本代码块 -->
      <div class="p-2.5 rounded bg-[#161412] font-mono text-xs text-[#E7E5E4] break-all select-all border border-white/5">
        {{ cmd.commandText }}
      </div>
    </div>
  </div>
</template>
