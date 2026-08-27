<script setup lang="ts">
/**
 * AI 聊天界面 - Naro助手浮层弹窗 (1:1 Figma 原型高保真)
 *
 * 严格按照 Figma FrameId 61:784 与原型截图进行 1:1 像素级复刻：
 * 包含双层金边磨砂卡片、作者助手/系统助手/我的指令 3 大 Tab、提示文案与快捷指令注入。
 *
 * @packageDocumentation
 */

import { X } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "insertPrompt", text: string): void;
}>();

// 当前选中的 Tab ("author" | "system" | "my")
const activeTab = ref<"author" | "system" | "my">("author");

// 指令预设库
const authorCommands = [
  { id: "c1", title: "哈基米指令", prompt: "【系统提示：切换为哈基米萌态互动模式】" },
];

const systemCommands = [
  { id: "s1", title: "继续推进剧情", prompt: "请根据当前氛围与角色性格，自然推进下一步剧情发展。" },
  {
    id: "s2",
    title: "环境与心理描写",
    prompt: "请详细描写当前场景的光影细节、周围声响以及角色内心的细微波澜。",
  },
  {
    id: "s3",
    title: "重写并增加对话深度",
    prompt: "请润色上一段回复，增加角色言语间的宿命感与情绪张力。",
  },
];

const myCommands = [
  { id: "m1", title: "展开长文对话", prompt: "请使用丰富细腻的文学笔触，分多段深入展开本次对话。" },
];

function handleClose(): void {
  emit("update:open", false);
}

function handleSelectCommand(promptText: string): void {
  emit("insertPrompt", promptText);
  handleClose();
}
</script>

<template>
  <!-- 遮罩蒙层 -->
  <Transition name="fade">
    <div
      v-if="open"
      @click="handleClose"
      class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm transition-opacity"
    />
  </Transition>

  <!-- 居中浮层弹窗 (1:1 Figma 规格: width: 396px, height: 430px, border: 0.667px solid #F9C86D, background: #292524) -->
  <Transition name="scale">
    <div
      v-if="open"
      class="fixed top-16 left-1/2 -translate-x-1/2 z-50 w-[396px] max-w-[calc(100vw-24px)] h-[430px] rounded-lg border border-[#F9C86D] bg-[#292524] shadow-[-4px_0_20px_rgba(0,0,0,0.30)] backdrop-blur-md flex flex-col overflow-hidden select-none"
    >
      <!-- 1. 顶栏: 标题 + 关闭按钮 -->
      <div class="px-3 py-2 flex items-center justify-between border-b border-[#44403C] shrink-0">
        <h2 class="text-sm font-semibold text-[#F5F5F4] tracking-tight">
          Naro助手
        </h2>

        <button
          type="button"
          @click="handleClose"
          class="w-8 h-8 rounded-full flex items-center justify-center text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-white/5 active:scale-95 transition-all cursor-pointer"
          title="关闭"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- 2. 三大分类 Tab 切换栏 -->
      <div class="grid grid-cols-3 border-b border-[#44403C] shrink-0">
        <!-- Tab 1: 作者助手 -->
        <button
          type="button"
          @click="activeTab = 'author'"
          :class="[
            'h-10 text-xs font-medium flex items-center justify-center transition-all cursor-pointer border-b-2',
            activeTab === 'author'
              ? 'border-[#F9C86D] bg-[#44403C] text-[#F5F5F4]'
              : 'border-transparent text-[#78716C] hover:text-[#A8A29E]'
          ]"
        >
          作者助手
        </button>

        <!-- Tab 2: 系统助手 -->
        <button
          type="button"
          @click="activeTab = 'system'"
          :class="[
            'h-10 text-xs font-medium flex items-center justify-center transition-all cursor-pointer border-b-2',
            activeTab === 'system'
              ? 'border-[#F9C86D] bg-[#44403C] text-[#F5F5F4]'
              : 'border-transparent text-[#78716C] hover:text-[#A8A29E]'
          ]"
        >
          系统助手
        </button>

        <!-- Tab 3: 我的指令 -->
        <button
          type="button"
          @click="activeTab = 'my'"
          :class="[
            'h-10 text-xs font-medium flex items-center justify-center transition-all cursor-pointer border-b-2',
            activeTab === 'my'
              ? 'border-[#F9C86D] bg-[#44403C] text-[#F5F5F4]'
              : 'border-transparent text-[#78716C] hover:text-[#A8A29E]'
          ]"
        >
          我的指令
        </button>
      </div>

      <!-- 3. 指令内容卡片展示区 -->
      <div class="flex-1 p-2 flex flex-col gap-2 overflow-y-auto">
        <!-- 提示文案 -->
        <div class="text-[10px] text-[#78716C] px-1 pt-1 leading-tight">
          点击按钮将内容追加到输入框
        </div>

        <!-- Tab 1: 作者助手指令列表 -->
        <div v-if="activeTab === 'author'" class="flex flex-col gap-1.5 w-full">
          <button
            v-for="cmd in authorCommands"
            :key="cmd.id"
            type="button"
            @click="handleSelectCommand(cmd.prompt)"
            class="w-full px-3 py-2 rounded border border-[#44403C] bg-[#292524] hover:border-[#F9C86D]/60 hover:bg-[#332D28] active:scale-[0.99] transition-all flex items-center text-left cursor-pointer group"
          >
            <span class="text-[11px] text-[#A8A29E] group-hover:text-[#F5F5F4] transition-colors">
              {{ cmd.title }}
            </span>
          </button>
        </div>

        <!-- Tab 2: 系统助手指令列表 -->
        <div v-else-if="activeTab === 'system'" class="flex flex-col gap-1.5 w-full">
          <button
            v-for="cmd in systemCommands"
            :key="cmd.id"
            type="button"
            @click="handleSelectCommand(cmd.prompt)"
            class="w-full px-3 py-2 rounded border border-[#44403C] bg-[#292524] hover:border-[#F9C86D]/60 hover:bg-[#332D28] active:scale-[0.99] transition-all flex items-center text-left cursor-pointer group"
          >
            <span class="text-[11px] text-[#A8A29E] group-hover:text-[#F5F5F4] transition-colors">
              {{ cmd.title }}
            </span>
          </button>
        </div>

        <!-- Tab 3: 我的指令列表 -->
        <div v-else class="flex flex-col gap-1.5 w-full">
          <button
            v-for="cmd in myCommands"
            :key="cmd.id"
            type="button"
            @click="handleSelectCommand(cmd.prompt)"
            class="w-full px-3 py-2 rounded border border-[#44403C] bg-[#292524] hover:border-[#F9C86D]/60 hover:bg-[#332D28] active:scale-[0.99] transition-all flex items-center text-left cursor-pointer group"
          >
            <span class="text-[11px] text-[#A8A29E] group-hover:text-[#F5F5F4] transition-colors">
              {{ cmd.title }}
            </span>
          </button>
        </div>
      </div>

    </div>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-enter-active,
.scale-leave-active {
  transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.scale-enter-from,
.scale-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px) scale(0.96);
}
</style>
