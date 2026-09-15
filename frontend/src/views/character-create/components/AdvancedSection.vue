<script setup lang="ts">
/**
 * 模块 6: 高级设置与世界书挂载组件 (1:1 原型高保真，支持世界书条目动态增删改)。
 *
 * @packageDocumentation
 */

import type { WorldbookEntryItem } from "@/views/character-create/types";
import { BookOpen, Check, ChevronDown, ChevronUp, Plus, Trash2 } from "lucide-vue-next";
import { ref } from "vue";

const props = withDefaults(
  defineProps<{
    /** 系统级前置 Prompt */
    systemPrompt: string;
    /** 对话后置指令 */
    postHistoryInstructions: string;
    /** 世界书条目列表 */
    worldbookEntries?: WorldbookEntryItem[];
  }>(),
  {
    worldbookEntries: () => [],
  },
);

const emit = defineEmits<{
  (e: "update:systemPrompt", val: string): void;
  (e: "update:postHistoryInstructions", val: string): void;
  (e: "update:worldbookEntries", val: WorldbookEntryItem[]): void;
}>();

const isExpanded = ref<boolean>(false);

function handleAddWorldbookEntry(): void {
  const nextList = [...props.worldbookEntries];
  nextList.push({
    id: `wb-${Date.now()}`,
    name: `世界书设定 ${nextList.length + 1}`,
    keys: [],
    content: "",
    isEnabled: true,
  });
  emit("update:worldbookEntries", nextList);
}

function handleRemoveWorldbookEntry(idx: number): void {
  const nextList = props.worldbookEntries.filter((_, i) => i !== idx);
  emit("update:worldbookEntries", nextList);
}

function handleUpdateEntryKeys(idx: number, keysStr: string): void {
  const nextList = [...props.worldbookEntries];
  if (nextList[idx]) {
    const keys = keysStr
      .split(/[,，\s]+/)
      .map((k) => k.trim())
      .filter(Boolean);
    nextList[idx] = { ...nextList[idx], keys };
    emit("update:worldbookEntries", nextList);
  }
}

function handleUpdateEntryContent(idx: number, content: string): void {
  const nextList = [...props.worldbookEntries];
  if (nextList[idx]) {
    nextList[idx] = { ...nextList[idx], content };
    emit("update:worldbookEntries", nextList);
  }
}

function handleToggleConstant(idx: number): void {
  const nextList = [...props.worldbookEntries];
  if (nextList[idx]) {
    nextList[idx] = { ...nextList[idx], isEnabled: !nextList[idx].isEnabled };
    emit("update:worldbookEntries", nextList);
  }
}
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
            高级设置 & 世界书
          </h2>
          <span class="text-xs text-[#78716C] font-normal">
            (System Prompt / 世界书设定)
          </span>
        </div>

        <button type="button" class="text-[#A8A29E] hover:text-white">
          <ChevronUp v-if="isExpanded" class="w-5 h-5" />
          <ChevronDown v-else class="w-5 h-5" />
        </button>
      </div>

      <!-- 2. 折叠表单内容 -->
      <div v-if="isExpanded" class="flex flex-col gap-5 pt-2 animate-fade-in">
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

        <!-- 3. 世界书条目挂载管理 -->
        <div class="flex flex-col gap-3 pt-2 border-t border-[#44403C]/40">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <BookOpen class="w-4 h-4 text-[#F9C86D]" />
              <label class="text-sm font-semibold text-[#F5F5F4]">
                世界书条目 (WorldBook RAG)
              </label>
            </div>
            <button
              type="button"
              @click="handleAddWorldbookEntry"
              class="flex items-center gap-1 text-xs text-[#F9C86D] hover:underline cursor-pointer select-none"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>添加世界书设定</span>
            </button>
          </div>

          <!-- 世界书条目列表 -->
          <div v-if="worldbookEntries.length > 0" class="flex flex-col gap-3">
            <div
              v-for="(wb, idx) in worldbookEntries"
              :key="wb.id"
              class="p-3.5 rounded-lg border border-[#44403C]/80 bg-[#1F1C18]/90 flex flex-col gap-2.5 animate-fade-in"
            >
              <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-[#F9C86D]">条目 {{ idx + 1 }}</span>
                <div class="flex items-center gap-2">
                  <label class="flex items-center gap-1 text-[11px] text-[#A8A29E] cursor-pointer">
                    <input
                      type="checkbox"
                      :checked="wb.isEnabled"
                      @change="handleToggleConstant(idx)"
                      class="rounded border-gray-600 accent-[#F9C86D]"
                    />
                    <span>常驻注入</span>
                  </label>
                  <button
                    type="button"
                    @click="handleRemoveWorldbookEntry(idx)"
                    class="text-red-400 hover:text-red-300 p-1 cursor-pointer"
                  >
                    <Trash2 class="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              <!-- 关键词输入 -->
              <input
                :value="wb.keys.join(', ')"
                @input="handleUpdateEntryKeys(idx, ($event.target as HTMLInputElement).value)"
                type="text"
                placeholder="触发关键词 (多个用逗号隔开，如: 霜华剑, 灵根)"
                class="w-full px-3 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D]"
              />

              <!-- 正文设定 -->
              <textarea
                :value="wb.content"
                @input="handleUpdateEntryContent(idx, ($event.target as HTMLTextAreaElement).value)"
                rows="2"
                placeholder="设定正文内容（当对话命中关键词或常驻时注入大模型提示词）"
                class="w-full p-2.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D] resize-none leading-relaxed"
              />
            </div>
          </div>

          <div v-else class="text-center py-3 text-xs text-[#78716C]">
            暂未添加世界书条目，点击上方“+ 添加世界书设定”可增加专属名词设定。
          </div>
        </div>

      </div>

    </div>
  </div>
</template>
