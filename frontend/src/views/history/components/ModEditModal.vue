<script setup lang="ts">
/**
 * 新建/编辑 Mod 全屏/模态弹窗 (Figma 106:8552 1:1 像素级高保真)
 *
 * 包含 ← 返回、顶部保存、基本信息卡片 (名称 0/50 + 简介 0/500)、Mod 条目卡片 (类型选择 + 添加条目 + 虚线空状态) 及底部保存草稿。
 *
 * @packageDocumentation
 */

import type { CreatedModEntry, CreatedModItem, ModCategoryTag } from "@/views/history/types";
import { ChevronDown, Trash2 } from "lucide-vue-next";
import { computed, ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  mod: CreatedModItem | null;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (
    e: "save",
    payload: {
      id?: string;
      name: string;
      description: string;
      entries: CreatedModEntry[];
    },
  ): void;
}>();

const localName = ref("");
const localDescription = ref("");
const localEntries = ref<CreatedModEntry[]>([]);
const selectedEntryType = ref<ModCategoryTag>("worldbook");

const ENTRY_TYPE_OPTIONS: Array<{ id: ModCategoryTag; label: string }> = [
  { id: "worldbook", label: "世界书" },
  { id: "system", label: "系统提示" },
  { id: "command", label: "历史指令" },
  { id: "regex", label: "正则" },
  { id: "author", label: "作者助手" },
];

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      if (props.mod) {
        localName.value = props.mod.name || "";
        localDescription.value = props.mod.description || "";
        localEntries.value = props.mod.entries ? JSON.parse(JSON.stringify(props.mod.entries)) : [];
      } else {
        localName.value = "";
        localDescription.value = "";
        localEntries.value = [];
      }
      selectedEntryType.value = "worldbook";
    }
  },
  { immediate: true },
);

const isFormValid = computed(() => Boolean(localName.value.trim()));

function handleAddEntry() {
  const typeLabel =
    ENTRY_TYPE_OPTIONS.find((t) => t.id === selectedEntryType.value)?.label || "条目";
  const newEntry: CreatedModEntry = {
    id: `entry-${Date.now()}`,
    type: selectedEntryType.value,
    title: `${typeLabel} ${localEntries.value.length + 1}`,
    content: "",
  };
  localEntries.value.push(newEntry);
}

function handleRemoveEntry(index: number) {
  localEntries.value.splice(index, 1);
}

function handleSave() {
  if (!isFormValid.value) return;
  emit("save", {
    id: props.mod?.id,
    name: localName.value,
    description: localDescription.value,
    entries: localEntries.value,
  });
}

function handleClose() {
  emit("update:open", false);
}
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 bg-[#0F0D0B] overflow-y-auto flex flex-col justify-start items-center"
  >
    <div class="w-full max-w-[440px] px-4 py-6 flex flex-col pb-24">
      <!-- 1. 顶部导航与 Header (Figma 106:8552) -->
      <div class="w-full flex justify-between items-center pb-6">
        <!-- 左侧: ← 返回 + 大标题 -->
        <div class="flex flex-col items-start">
          <button
            type="button"
            @click="handleClose"
            class="text-[14px] leading-[20px] text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer select-none pb-1"
          >
            ← 返回
          </button>
          <h1 class="text-[20px] leading-[24px] font-semibold text-[#F5F5F4] tracking-[-0.4px]">
            {{ mod ? "编辑 Mod" : "新建 Mod" }}
          </h1>
        </div>

        <!-- 右侧: 保存按钮 -->
        <button
          type="button"
          @click="handleSave"
          :disabled="!isFormValid"
          class="px-4 py-2 rounded-[8px] border border-[rgba(249,200,109,0.30)] bg-[rgba(249,200,109,0.15)] text-[#F9C86D] text-[14px] leading-[20px] font-medium transition-all select-none"
          :class="isFormValid ? 'hover:bg-[rgba(249,200,109,0.25)] active:scale-95 cursor-pointer opacity-100' : 'opacity-50 cursor-not-allowed'"
        >
          保存
        </button>
      </div>

      <!-- 2. 基本信息卡片 (Figma 106:8552) -->
      <div class="w-full p-5 rounded-[12px] border border-[#292524] bg-[#1A1714] flex flex-col gap-4">
        <h2 class="text-[14px] leading-[16.8px] font-semibold text-[#F5F5F4] tracking-[-0.28px]">
          基本信息
        </h2>

        <!-- Mod 名称 * -->
        <div class="w-full flex flex-col">
          <label class="text-[14px] leading-[20px] font-medium text-[#F5F5F4] pb-1.5">
            Mod 名称 <span class="text-[#EF4444]">*</span>
          </label>
          <div class="relative w-full">
            <input
              v-model="localName"
              type="text"
              maxlength="50"
              placeholder="给你的 Mod 起一个名字"
              class="w-full h-[37px] px-3 rounded-[6px] border border-[#292524] bg-[#292524] text-[14px] text-[#F5F5F4] placeholder-[#F5F5F4]/50 focus:border-[#F9C86D] focus:outline-none transition-colors"
            />
          </div>
          <div class="w-full text-right text-[12px] leading-[16px] text-[#A8A29E] pt-1">
            {{ localName.length }}/50
          </div>
        </div>

        <!-- 简介 -->
        <div class="w-full flex flex-col">
          <label class="text-[14px] leading-[20px] font-medium text-[#F5F5F4] pb-1.5">
            简介
          </label>
          <div class="relative w-full">
            <textarea
              v-model="localDescription"
              rows="3"
              maxlength="500"
              placeholder="描述你的 Mod 能做什么..."
              class="w-full p-3 rounded-[6px] border border-[#292524] bg-[#292524] text-[14px] leading-[20px] text-[#F5F5F4] placeholder-[#F5F5F4]/50 focus:border-[#F9C86D] focus:outline-none resize-none transition-colors"
            ></textarea>
          </div>
          <div class="w-full text-right text-[12px] leading-[16px] text-[#A8A29E] pt-1">
            {{ localDescription.length }}/500
          </div>
        </div>
      </div>

      <!-- 3. Mod 条目卡片 (Figma 106:8552) -->
      <div class="w-full p-5 rounded-[12px] border border-[#292524] bg-[#1A1714] flex flex-col mt-6">
        <!-- 头部: 标题 + 下拉选择 + 添加条目按钮 -->
        <div class="w-full flex items-center justify-between pb-3 flex-wrap gap-2">
          <h3 class="text-[14px] leading-[16.8px] font-semibold text-[#F5F5F4] tracking-[-0.28px]">
            Mod 条目
          </h3>

          <div class="flex items-center gap-2">
            <!-- 类型选择下拉框 -->
            <div class="relative">
              <select
                v-model="selectedEntryType"
                class="appearance-none h-[32px] pl-3 pr-7 rounded-[6px] border border-[#292524] bg-[#292524] text-[12px] text-[#F5F5F4] focus:border-[#F9C86D] focus:outline-none cursor-pointer"
              >
                <option
                  v-for="opt in ENTRY_TYPE_OPTIONS"
                  :key="opt.id"
                  :value="opt.id"
                  class="bg-[#292524] text-[#F5F5F4]"
                >
                  {{ opt.label }}
                </option>
              </select>
              <div class="absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none text-[#A8A29E]">
                <ChevronDown class="w-3.5 h-3.5" />
              </div>
            </div>

            <!-- + 添加条目 -->
            <button
              type="button"
              @click="handleAddEntry"
              class="px-3 py-1.5 rounded-[8px] border border-[rgba(249,200,109,0.25)] bg-[rgba(249,200,109,0.12)] text-[#F9C86D] text-[12px] leading-[16px] font-normal hover:bg-[rgba(249,200,109,0.20)] active:scale-95 transition-all cursor-pointer select-none"
            >
              + 添加条目
            </button>
          </div>
        </div>

        <!-- 空状态 / 条目列表 (Figma 106:8552) -->
        <div
          v-if="localEntries.length === 0"
          class="w-full py-8 px-4 rounded-[12px] border border-dashed border-[#292524] bg-[#1A1714] flex flex-col items-center justify-center text-center mt-1"
        >
          <p class="text-[14px] leading-[20px] text-[#A8A29E]">
            还没有条目，选择类型后点击「添加条目」
          </p>
        </div>

        <!-- 已经添加的条目矩阵 -->
        <div v-else class="w-full flex flex-col gap-3 mt-2">
          <div
            v-for="(entry, idx) in localEntries"
            :key="entry.id"
            class="w-full p-3 rounded-[8px] border border-[#292524] bg-[#292524] flex flex-col gap-2"
          >
            <div class="flex items-center justify-between">
              <span class="text-[12px] font-medium text-[#F9C86D]">
                #{{ idx + 1 }} {{ ENTRY_TYPE_OPTIONS.find((t) => t.id === entry.type)?.label }}
              </span>
              <button
                type="button"
                @click="handleRemoveEntry(idx)"
                class="text-[#EF4444] hover:text-[#FF6B6B] p-1 cursor-pointer"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
            <input
              v-model="entry.title"
              type="text"
              placeholder="条目标题"
              class="w-full h-[30px] px-2 rounded-[4px] border border-[#44403C] bg-[#1A1714] text-[12px] text-[#F5F5F4] focus:outline-none"
            />
            <textarea
              v-model="entry.content"
              rows="2"
              placeholder="条目内容或具体提示词规则..."
              class="w-full p-2 rounded-[4px] border border-[#44403C] bg-[#1A1714] text-[12px] text-[#F5F5F4] focus:outline-none resize-none"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- 4. 底部保存草稿大按钮 (Figma 106:8552) -->
      <div class="w-full pt-6">
        <button
          type="button"
          @click="handleSave"
          :disabled="!isFormValid"
          class="w-full h-[45px] rounded-[12px] border border-[rgba(249,200,109,0.30)] bg-[rgba(249,200,109,0.15)] text-[#F9C86D] text-[14px] leading-[20px] font-semibold transition-all select-none"
          :class="isFormValid ? 'hover:bg-[rgba(249,200,109,0.25)] active:scale-95 cursor-pointer opacity-100' : 'opacity-50 cursor-not-allowed'"
        >
          保存草稿
        </button>
      </div>
    </div>
  </div>
</template>
