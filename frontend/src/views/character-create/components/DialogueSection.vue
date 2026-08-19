<script setup lang="ts">
/**
 * 模块 5: 对话设置组件 (1:1 原型高保真)
 *
 * 包含首次问候语必填项、多版本备选开场白 Tab 切换与增删管理。
 *
 * @packageDocumentation
 */

import type { AlternateGreetingItem } from "@/views/character-create/types";
import { Plus, Trash2 } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{
  /** 首次问候语 (必填) */
  firstMes: string;
  /** 备选开场白列表 */
  alternateGreetings: AlternateGreetingItem[];
}>();

const emit = defineEmits<{
  (e: "update:firstMes", val: string): void;
  (e: "update:alternateGreetings", val: AlternateGreetingItem[]): void;
}>();

// 当前激活选中的备选开场白索引
const activeGreetingIndex = ref<number>(0);

/**
 * 添加一条新的备选开场白
 */
function handleAddAlternateGreeting(): void {
  const nextList = [...props.alternateGreetings];
  const newIndex = nextList.length + 1;
  nextList.push({
    id: `alt-${Date.now()}`,
    title: `备选开场白 ${newIndex}`,
    greetingText: "",
    responsePreview: "",
  });
  emit("update:alternateGreetings", nextList);
  activeGreetingIndex.value = nextList.length - 1;
}

/**
 * 移除指定备选开场白
 */
function handleRemoveAlternateGreeting(index: number): void {
  const nextList = props.alternateGreetings.filter((_, i) => i !== index);
  emit("update:alternateGreetings", nextList);
  if (activeGreetingIndex.value >= nextList.length) {
    activeGreetingIndex.value = Math.max(0, nextList.length - 1);
  }
}

/**
 * 更新当前备选开场白文本
 */
function handleUpdateCurrentGreetingText(text: string): void {
  const nextList = [...props.alternateGreetings];
  if (nextList[activeGreetingIndex.value]) {
    nextList[activeGreetingIndex.value] = {
      ...nextList[activeGreetingIndex.value],
      greetingText: text,
    };
    emit("update:alternateGreetings", nextList);
  }
}
</script>

<template>
  <div class="w-full px-3 pb-3">
    <!-- 模块外层容器 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-5 shadow-xl">
      
      <!-- 1. 模块主标题 (蓝色圆柱指示条 + 对话设置) -->
      <div class="flex items-center gap-3">
        <div class="w-1 h-6 rounded-full bg-[#3B82F6] shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
        <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[0.9px] leading-tight select-none">
          对话设置
        </h2>
      </div>

      <!-- 2. ① 首次问候 * -->
      <div class="flex flex-col gap-2">
        <label class="flex items-center gap-1.5 text-sm font-medium text-[#F5F5F4]">
          <span class="text-[#F9C86D]">✨</span>
          <span>首次问候 *</span>
        </label>
        <textarea
          :value="firstMes"
          @input="emit('update:firstMes', ($event.target as HTMLTextAreaElement).value)"
          rows="4"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-sm text-gray-100 placeholder-[#78716C] focus:border-[#3B82F6] transition-colors resize-none leading-relaxed"
          placeholder="角色与用户初次见面时的开场白...（第一句话哦，太过暴露过不了审核哦）"
        />
      </div>

      <!-- 3. ② 备选开场白 -->
      <div class="flex flex-col gap-3 pt-2">
        <div class="flex items-center justify-between">
          <label class="text-sm font-medium text-[#F5F5F4]">
            备选开场白
          </label>
          <button
            type="button"
            @click="handleAddAlternateGreeting"
            class="flex items-center gap-1 text-xs text-[#F9C86D] hover:underline cursor-pointer select-none"
          >
            <Plus class="w-3.5 h-3.5" />
            <span>添加备选开场白</span>
          </button>
        </div>

        <!-- 备选开场白 Tab 标签栏 -->
        <div v-if="alternateGreetings.length > 0" class="flex items-center gap-2 overflow-x-auto pb-1">
          <button
            v-for="(item, idx) in alternateGreetings"
            :key="item.id"
            type="button"
            @click="activeGreetingIndex = idx"
            :class="[
              'px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-150 cursor-pointer select-none border shrink-0 flex items-center gap-1.5',
              activeGreetingIndex === idx
                ? 'bg-[#F9C86D] text-black border-[#F9C86D] shadow-sm'
                : 'bg-[rgba(42,37,32,0.60)] text-[#A8A29E] border-[#44403C]/60 hover:text-white'
            ]"
          >
            <span>开场白 {{ idx + 1 }}</span>
            <button
              v-if="alternateGreetings.length > 1"
              type="button"
              @click.stop="handleRemoveAlternateGreeting(idx)"
              class="hover:opacity-70"
            >
              <Trash2 class="w-3 h-3" />
            </button>
          </button>
        </div>

        <!-- 当前激活开场白内容输入框 -->
        <div v-if="alternateGreetings[activeGreetingIndex]" class="flex flex-col gap-2">
          <textarea
            :value="alternateGreetings[activeGreetingIndex].greetingText"
            @input="handleUpdateCurrentGreetingText(($event.target as HTMLTextAreaElement).value)"
            rows="3"
            class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-sm text-gray-100 placeholder-[#78716C] focus:border-[#3B82F6] transition-colors resize-none leading-relaxed"
            :placeholder="`输入备选开场白 ${activeGreetingIndex + 1} 的具体内容...`"
          />
        </div>
      </div>

    </div>
  </div>
</template>
