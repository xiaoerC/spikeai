<script setup lang="ts">
/**
 * 分节 3: 【舞台】组件 (玩家在对话中看到的内容)
 *
 * 涵盖首次问候、备选开场白、开场快捷引导回复、AI 一键生成序幕与沉浸扩展挂件 (侧边栏/助手/CSS/BGM)。
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { characterService } from "@/services/character";
import {
  Code,
  Eye,
  Music,
  Palette,
  PanelRight,
  Plus,
  Sparkles,
  Trash2,
  UserCheck,
} from "lucide-vue-next";
import { ref } from "vue";
import type { AlternateGreetingItem, DisplayMode, StageExtensions } from "../types";

const props = defineProps<{
  /** 角色名称 (用于 AI 生成序幕) */
  name: string;
  /** 描述 (用于 AI 生成序幕) */
  description: string;
  /** 性格 (用于 AI 生成序幕) */
  personality: string;
  /** 场景背景 (用于 AI 生成序幕) */
  scenario: string;
  /** 首次问候 (必填) */
  firstMes: string;
  /** 备选开场白列表 */
  alternateGreetings: AlternateGreetingItem[];
  /** 开场引导快捷回复列表 */
  openingReplies: string[];
  /** 序幕 HTML 代码 */
  prologueHtml: string;
  /** 沉浸式扩展挂件 */
  stageExtensions: StageExtensions;
  /** 显示模式 */
  displayMode: DisplayMode;
}>();

const emit = defineEmits<{
  (e: "update:firstMes", val: string): void;
  (e: "update:alternateGreetings", val: AlternateGreetingItem[]): void;
  (e: "update:openingReplies", val: string[]): void;
  (e: "update:prologueHtml", val: string): void;
  (e: "update:stageExtensions", val: StageExtensions): void;
}>();

const toast = useToast();
const activeGreetingIndex = ref<number>(0);
const isPreviewMode = ref<boolean>(false);
const isGeneratingPrologue = ref<boolean>(false);
const newReplyInput = ref<string>("");

// 挂件激活展示开关
const activeWidget = ref<"sidebar" | "assistant" | "css" | "bgm" | null>(null);

function toggleWidget(widget: "sidebar" | "assistant" | "css" | "bgm"): void {
  activeWidget.value = activeWidget.value === widget ? null : widget;
}

function handleAddAlternateGreeting(): void {
  const nextList = [...props.alternateGreetings];
  const newIdx = nextList.length + 1;
  nextList.push({
    id: `alt-${Date.now()}`,
    title: `备选开场白 ${newIdx}`,
    greetingText: "",
    responsePreview: "",
  });
  emit("update:alternateGreetings", nextList);
  activeGreetingIndex.value = nextList.length - 1;
}

function handleRemoveAlternateGreeting(index: number): void {
  const nextList = props.alternateGreetings.filter((_, i) => i !== index);
  emit("update:alternateGreetings", nextList);
  if (activeGreetingIndex.value >= nextList.length) {
    activeGreetingIndex.value = Math.max(0, nextList.length - 1);
  }
}

function handleUpdateGreetingText(text: string): void {
  const nextList = [...props.alternateGreetings];
  if (nextList[activeGreetingIndex.value]) {
    nextList[activeGreetingIndex.value] = {
      ...nextList[activeGreetingIndex.value],
      greetingText: text,
    };
    emit("update:alternateGreetings", nextList);
  }
}

function handleAddOpeningReply(): void {
  const reply = newReplyInput.value.trim();
  if (!reply) return;
  emit("update:openingReplies", [...props.openingReplies, reply]);
  newReplyInput.value = "";
}

function handleRemoveOpeningReply(idx: number): void {
  emit(
    "update:openingReplies",
    props.openingReplies.filter((_, i) => i !== idx),
  );
}

/**
 * AI 智能生成序幕 HTML
 */
async function handleAIGeneratePrologue(): Promise<void> {
  if (!props.name.trim()) {
    toast.error("请先输入角色名称");
    return;
  }

  isGeneratingPrologue.value = true;
  try {
    const generatedHtml = await characterService.generatePrologue({
      name: props.name,
      description: props.description,
      personality: props.personality,
      scenario: props.scenario,
      first_mes: props.firstMes,
    });
    emit("update:prologueHtml", generatedHtml);
    isPreviewMode.value = true;
    toast.success("AI 故事序幕已生成并自动切换至预览模式！");
  } catch (err) {
    console.error("生成序幕失败:", err);
    toast.error("生成序幕失败，请检查网络或后端服务");
  } finally {
    isGeneratingPrologue.value = false;
  }
}

function updateExtensionField(field: keyof StageExtensions, val: string): void {
  emit("update:stageExtensions", {
    ...props.stageExtensions,
    [field]: val,
  });
}
</script>

<template>
  <section id="section-stage" class="w-full px-3 pb-4 flex flex-col gap-4">
    <!-- 分节大标题: 舞台 (玩家在对话中看到的内容) -->
    <div class="flex items-center justify-between pt-1">
      <div class="flex items-center gap-2.5">
        <div class="w-1 h-5 rounded-full bg-[#A855F7] shadow-[0_0_10px_rgba(168,85,247,0.5)]" />
        <h2 class="text-base font-bold text-gray-100 tracking-wide select-none">
          舞台
        </h2>
        <span class="text-xs text-[#78716C] font-normal">
          玩家在对话中看到的内容
        </span>
      </div>
    </div>

    <!-- 1. 对话设置卡片 -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      <h3 class="text-xs font-semibold text-gray-200">
        对话设置
      </h3>

      <!-- 首次问候 * -->
      <div class="flex flex-col gap-1.5">
        <label class="flex items-center gap-1.5 text-xs font-semibold text-gray-200">
          <span class="text-[#F9C86D]">✨</span>
          <span>首次问候 *</span>
        </label>
        <textarea
          :value="firstMes"
          @input="emit('update:firstMes', ($event.target as HTMLTextAreaElement).value)"
          rows="4"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#A855F7] transition-colors resize-none leading-relaxed"
          placeholder="角色与玩家初次见面时的开场白台词（第一句话）..."
        />
      </div>

      <!-- 备选开场白 -->
      <div class="flex flex-col gap-2 pt-1 border-t border-[#44403C]/40">
        <div class="flex items-center justify-between">
          <label class="text-xs text-[#A8A29E]">
            备选开场白 (支持不同故事线切入)
          </label>
          <button
            type="button"
            @click="handleAddAlternateGreeting"
            class="flex items-center gap-1 text-xs text-[#F9C86D] hover:underline cursor-pointer select-none font-medium"
          >
            <Plus class="w-3.5 h-3.5" />
            <span>+ 添加备选开场白</span>
          </button>
        </div>

        <!-- 备选开场白 Tabs -->
        <div v-if="alternateGreetings.length > 0" class="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
          <button
            v-for="(item, idx) in alternateGreetings"
            :key="item.id"
            type="button"
            @click="activeGreetingIndex = idx"
            :class="[
              'px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer select-none border shrink-0 flex items-center gap-1.5',
              activeGreetingIndex === idx
                ? 'bg-[#F9C86D] text-black border-[#F9C86D] font-semibold shadow-sm'
                : 'bg-[rgba(42,37,32,0.60)] text-[#A8A29E] border-[#44403C]/60 hover:text-white'
            ]"
          >
            <span>开场白 {{ idx + 1 }}</span>
            <button
              v-if="alternateGreetings.length > 1"
              type="button"
              @click.stop="handleRemoveAlternateGreeting(idx)"
              class="hover:opacity-70 text-red-700"
            >
              <Trash2 class="w-3 h-3" />
            </button>
          </button>
        </div>

        <div v-if="alternateGreetings[activeGreetingIndex]" class="flex flex-col gap-1">
          <textarea
            :value="alternateGreetings[activeGreetingIndex].greetingText"
            @input="handleUpdateGreetingText(($event.target as HTMLTextAreaElement).value)"
            rows="3"
            class="w-full p-2.5 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#A855F7] transition-colors resize-none leading-relaxed"
            :placeholder="`输入备选开场白 ${activeGreetingIndex + 1} 的具体台词...`"
          />
        </div>
      </div>

      <!-- 开场引导快捷回复 (Opening Replies) -->
      <div class="flex flex-col gap-2 pt-1 border-t border-[#44403C]/40">
        <div class="flex items-center justify-between">
          <label class="text-xs text-[#A8A29E]">
            开场快捷回复 (提供玩家首轮快速回应按钮)
          </label>
        </div>

        <div class="flex items-center gap-2">
          <input
            v-model="newReplyInput"
            type="text"
            placeholder="例如: [拔刀相助] / [默默旁观] / [主动搭话]"
            class="flex-1 px-3 py-1.5 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#A855F7]"
            @keyup.enter="handleAddOpeningReply"
          />
          <button
            type="button"
            @click="handleAddOpeningReply"
            :disabled="!newReplyInput.trim()"
            class="h-8 px-3 rounded-lg border border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10 disabled:opacity-40 transition-colors flex items-center justify-center cursor-pointer text-xs"
          >
            添加
          </button>
        </div>

        <div v-if="openingReplies.length > 0" class="flex flex-wrap gap-1.5 pt-1">
          <span
            v-for="(reply, idx) in openingReplies"
            :key="idx"
            class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-[#A855F7]/15 text-[#D8B4FE] border border-[#A855F7]/30 text-xs"
          >
            <span>{{ reply }}</span>
            <button type="button" @click="handleRemoveOpeningReply(idx)" class="hover:text-white">
              <Trash2 class="w-3 h-3" />
            </button>
          </span>
        </div>
      </div>
    </div>

    <!-- 2. 序幕卡片 (HTML / 故事卡呈现) -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <h3 class="text-xs font-semibold text-gray-200">
            序幕 (Prologue)
          </h3>
          <span class="px-1.5 py-0.5 rounded-full bg-[#F9C86D]/15 text-[#F9C86D] border border-[#F9C86D]/30 text-[10px]">
            可选
          </span>
        </div>

        <div class="flex items-center gap-2">
          <!-- AI 生成按钮 -->
          <button
            type="button"
            @click="handleAIGeneratePrologue"
            :disabled="isGeneratingPrologue"
            class="flex items-center gap-1 px-2.5 py-1 rounded bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/40 hover:bg-[#F9C86D]/30 text-xs font-medium transition-colors cursor-pointer select-none"
          >
            <Sparkles class="w-3.5 h-3.5" :class="{ 'animate-spin': isGeneratingPrologue }" />
            <span>{{ isGeneratingPrologue ? "生成中..." : "AI生成" }}</span>
          </button>

          <!-- 预览模式切换 -->
          <button
            type="button"
            @click="isPreviewMode = !isPreviewMode"
            :class="[
              'flex items-center gap-1 px-2 py-1 rounded text-xs transition-colors cursor-pointer select-none border',
              isPreviewMode
                ? 'bg-[#38BDF8]/20 text-[#38BDF8] border-[#38BDF8]/40 font-medium'
                : 'bg-stone-800 text-stone-300 border-stone-700 hover:text-white'
            ]"
          >
            <component :is="isPreviewMode ? Code : Eye" class="w-3 h-3" />
            <span>{{ isPreviewMode ? "代码" : "预览" }}</span>
          </button>
        </div>
      </div>

      <!-- 序幕提示说明 -->
      <p class="text-[11px] text-[#78716C] leading-relaxed">
        序幕将作为"screen"字段保存在角色卡中，在首次开局对话前呈现，请确保 HTML 格式正确。
      </p>

      <!-- 代码编辑框 -->
      <textarea
        v-if="!isPreviewMode"
        :value="prologueHtml"
        @input="emit('update:prologueHtml', ($event.target as HTMLTextAreaElement).value)"
        rows="4"
        class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs font-mono text-gray-100 placeholder-[#78716C] focus:border-[#A855F7] transition-colors resize-none leading-relaxed"
        placeholder="关于角色最炫酷的故事排版展示，支持嵌入 HTML/CSS 代码..."
      />

      <!-- 沙箱实时预览渲染区 -->
      <div
        v-else
        class="w-full min-h-[100px] p-3 rounded-lg border border-dashed border-[#F9C86D]/40 bg-black/50 overflow-hidden"
      >
        <div v-if="prologueHtml" v-html="prologueHtml" class="prologue-preview" />
        <div v-else class="text-center text-xs text-[#78716C] py-4">
          暂无序幕内容，点击上方“AI生成”或输入 HTML 即可预览。
        </div>
      </div>
    </div>

    <!-- 3. 沉浸式扩展挂件入口 (仅在完整模式下呈现) -->
    <div v-if="displayMode === 'full'" class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <h3 class="text-xs font-semibold text-gray-200">
        沉浸式扩展挂件
      </h3>

      <div class="grid grid-cols-2 gap-2">
        <button
          type="button"
          @click="toggleWidget('sidebar')"
          :class="[
            'h-9 px-2.5 rounded-lg border text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer',
            activeWidget === 'sidebar' || stageExtensions.sidebarPanelHtml
              ? 'bg-[#F9C86D]/20 text-[#F9C86D] border-[#F9C86D]/60 font-semibold'
              : 'bg-black/40 text-stone-300 border-stone-700 hover:text-white'
          ]"
        >
          <PanelRight class="w-3.5 h-3.5" />
          <span>侧边栏面板</span>
        </button>

        <button
          type="button"
          @click="toggleWidget('assistant')"
          :class="[
            'h-9 px-2.5 rounded-lg border text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer',
            activeWidget === 'assistant' || stageExtensions.assistantNote
              ? 'bg-[#F9C86D]/20 text-[#F9C86D] border-[#F9C86D]/60 font-semibold'
              : 'bg-black/40 text-stone-300 border-stone-700 hover:text-white'
          ]"
        >
          <UserCheck class="w-3.5 h-3.5" />
          <span>作者助手</span>
        </button>

        <button
          type="button"
          @click="toggleWidget('css')"
          :class="[
            'h-9 px-2.5 rounded-lg border text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer',
            activeWidget === 'css' || stageExtensions.customCss
              ? 'bg-[#F9C86D]/20 text-[#F9C86D] border-[#F9C86D]/60 font-semibold'
              : 'bg-black/40 text-stone-300 border-stone-700 hover:text-white'
          ]"
        >
          <Palette class="w-3.5 h-3.5" />
          <span>全局美化 CSS</span>
        </button>

        <button
          type="button"
          @click="toggleWidget('bgm')"
          :class="[
            'h-9 px-2.5 rounded-lg border text-xs flex items-center justify-center gap-1.5 transition-all cursor-pointer',
            activeWidget === 'bgm' || stageExtensions.bgmUrl
              ? 'bg-[#F9C86D]/20 text-[#F9C86D] border-[#F9C86D]/60 font-semibold'
              : 'bg-black/40 text-stone-300 border-stone-700 hover:text-white'
          ]"
        >
          <Music class="w-3.5 h-3.5" />
          <span>背景音乐 BGM</span>
        </button>
      </div>

      <!-- 激活挂件的输入卡片 -->
      <div v-if="activeWidget === 'sidebar'" class="flex flex-col gap-1 pt-2 border-t border-stone-800">
        <label class="text-[11px] text-stone-400">侧边栏自定义面板 HTML</label>
        <textarea
          :value="stageExtensions.sidebarPanelHtml || ''"
          @input="updateExtensionField('sidebarPanelHtml', ($event.target as HTMLTextAreaElement).value)"
          rows="3"
          placeholder="挂载在聊天侧边栏的状态面板 HTML 代码..."
          class="w-full p-2.5 rounded bg-black/40 border border-[#44403C] text-xs font-mono text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D] resize-none"
        />
      </div>

      <div v-if="activeWidget === 'assistant'" class="flex flex-col gap-1 pt-2 border-t border-stone-800">
        <label class="text-[11px] text-stone-400">作者助手设定说明</label>
        <textarea
          :value="stageExtensions.assistantNote || ''"
          @input="updateExtensionField('assistantNote', ($event.target as HTMLTextAreaElement).value)"
          rows="2"
          placeholder="作者助手挂件提示说明..."
          class="w-full p-2.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D] resize-none"
        />
      </div>

      <div v-if="activeWidget === 'css'" class="flex flex-col gap-1 pt-2 border-t border-stone-800">
        <label class="text-[11px] text-stone-400">全局个性化主题 CSS</label>
        <textarea
          :value="stageExtensions.customCss || ''"
          @input="updateExtensionField('customCss', ($event.target as HTMLTextAreaElement).value)"
          rows="3"
          placeholder="针对当前角色对话界面的注入 CSS 样式..."
          class="w-full p-2.5 rounded bg-black/40 border border-[#44403C] text-xs font-mono text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D] resize-none"
        />
      </div>

      <div v-if="activeWidget === 'bgm'" class="flex flex-col gap-1 pt-2 border-t border-stone-800">
        <label class="text-[11px] text-stone-400">背景音乐 (BGM) 音频外链 URL</label>
        <input
          :value="stageExtensions.bgmUrl || ''"
          @input="updateExtensionField('bgmUrl', ($event.target as HTMLInputElement).value)"
          type="text"
          placeholder="https://example.com/soundtrack.mp3"
          class="w-full px-2.5 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D]"
        />
      </div>
    </div>
  </section>
</template>
