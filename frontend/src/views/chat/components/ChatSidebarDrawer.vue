<script setup lang="ts">
/**
 * AI 聊天界面 - 侧边抽屉菜单 (1:1 Figma 原型高保真)
 *
 * @packageDocumentation
 */

import {
  BookOpen,
  ChevronLeft,
  Cloud,
  Cpu,
  Download,
  ExternalLink,
  EyeOff,
  Feather,
  FileCode,
  GitFork,
  Settings,
  Sparkles,
  Upload,
  Zap,
} from "lucide-vue-next";

import { ref } from "vue";
import { useRouter } from "vue-router";

const props = defineProps<{
  open: boolean;
  characterId?: string;
  characterName?: string;
  avatarUrl?: string;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "openDagTree"): void;
  (e: "openSettings"): void;
}>();

const router = useRouter();

const tokenLength = ref(200);
const isAutoSummary = ref(true);
const isHidePrologue = ref(false);
const isCustomCss = ref(false);

function handleClose(): void {
  emit("update:open", false);
}

function handleGoDetail(): void {
  handleClose();
  router.push(`/character/${props.characterId || "c1"}`);
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

  <!-- 从左侧滑出的抽屉容器 -->
  <Transition name="slide-left">
    <aside
      v-if="open"
      class="fixed left-0 top-0 bottom-0 z-50 w-full max-w-[340px] bg-gradient-to-br from-[#12100F] via-[#1A1714] to-[#2A211B] border-r border-[#44403C] shadow-2xl flex flex-col overflow-y-auto select-none"
    >
      <!-- 1. 顶部收起侧边栏操作 -->
      <div class="p-4 pb-2 flex items-center justify-between border-b border-[#44403C]/40">
        <button
          type="button"
          @click="handleClose"
          class="flex items-center gap-2 text-xs text-[#C0A480] hover:text-[#F9C86D] transition-colors cursor-pointer py-1"
        >
          <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
            <ChevronLeft class="w-3.5 h-3.5" />
          </div>
          <span>收起侧边栏</span>
        </button>
      </div>

      <!-- 2. 当前角色资料胶囊 -->
      <div class="p-4 flex items-center gap-3 border-b border-[#44403C]/30 bg-black/20">
        <div class="w-10 h-10 rounded-lg border border-[#44403C] overflow-hidden bg-[#292524] shrink-0 shadow-md">
          <img
            :src="avatarUrl || 'https://images.unsplash.com/photo-1578632767115-351597cf2477?w=300&auto=format&fit=crop&q=80'"
            :alt="characterName"
            class="w-full h-full object-cover"
          />
        </div>

        <div class="flex flex-col flex-1 min-w-0">
          <h2 class="text-xs font-semibold text-[#F5F5F4] truncate">
            《{{ characterName || "鬼灭之刃" }}》
          </h2>
          <span class="text-[10px] text-[#A8A29E] mt-0.5">
            未定义性格
          </span>
        </div>
      </div>

      <!-- 3. 快捷导航菜单项 (角色详情页 / 剧情分支 / 云端同步 / 文学风格) -->
      <div class="p-3 flex flex-col gap-1 border-b border-[#44403C]/30">
        <!-- 角色详情页 (金色高光) -->
        <button
          type="button"
          @click="handleGoDetail"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#F9C86D] hover:bg-[#F9C86D]/10 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#F9C86D]/40 bg-[#F9C86D]/10 flex items-center justify-center text-[#F9C86D]">
              <ExternalLink class="w-3.5 h-3.5" />
            </div>
            <span class="font-medium">角色详情页</span>
          </div>
        </button>

        <!-- 剧情分支 -->
        <button
          type="button"
          @click="emit('openDagTree'); handleClose()"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
              <GitFork class="w-3.5 h-3.5" />
            </div>
            <span>剧情分支</span>
          </div>
        </button>

        <!-- 云端同步已开启 -->
        <div class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480]">
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#22C55E]">
              <Cloud class="w-3.5 h-3.5" />
            </div>
            <span>云端同步已开启</span>
          </div>
        </div>


        <!-- 文学风格 -->
        <button
          type="button"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
              <Feather class="w-3.5 h-3.5" />
            </div>
            <span>文学风格</span>
          </div>
        </button>
      </div>

      <!-- 4. 模型回复长度控制 -->
      <div class="p-4 border-b border-[#44403C]/30 flex flex-col gap-2">
        <div class="flex items-center justify-between text-[10px] text-[#78716C] font-semibold uppercase tracking-wider">
          <span>模型回复长度</span>
          <span class="text-xs font-mono text-[#FAFAF9]">{{ tokenLength }} tokens</span>
        </div>
        <input
          v-model.number="tokenLength"
          type="range"
          min="50"
          max="800"
          step="50"
          class="w-full accent-[#F9C86D] cursor-pointer"
        />
      </div>

      <!-- 5. 当前分支统计卡片 -->
      <div class="p-4 border-b border-[#44403C]/30">
        <div class="p-3.5 rounded-xl border border-[#44403C] bg-gradient-to-br from-[#1C1917] to-[#0C0A09] flex flex-col gap-2.5 shadow-inner">
          <span class="text-xs font-semibold text-[#78716C]">当前分支统计</span>
          
          <div class="flex items-center justify-between text-[11px]">
            <span class="text-[#78716C]">对话轮次</span>
            <span class="font-semibold text-white/90">2 轮</span>
          </div>

          <div class="flex items-center justify-between text-[11px]">
            <span class="text-[#78716C]">聊天记录长度</span>
            <span class="font-semibold font-mono text-white/90">12</span>
          </div>

          <div class="flex flex-col gap-1 pt-1">
            <div class="flex items-center justify-between text-[10px]">
              <span class="text-[#78716C]">下一次总结进度</span>
              <span class="text-[#22C55E] font-mono font-semibold">1%</span>
            </div>
            <div class="w-full h-1.5 rounded-full bg-[#1C1917] border border-[#44403C] overflow-hidden">
              <div class="w-[5%] h-full bg-[#22C55E] rounded-full" />
            </div>
          </div>
        </div>
      </div>

      <!-- 6. 高级操作列表 (自动总结 / 高级设置 / 隐藏序幕 / 启用自定义CSS / 导入导出) -->
      <div class="p-3 flex flex-col gap-1 pb-10">
        <!-- 自动总结 -->
        <button
          type="button"
          @click="isAutoSummary = !isAutoSummary"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center text-[#F9C86D]">
              <Zap class="w-3.5 h-3.5" />
            </div>
            <span>自动总结</span>
          </div>
          <span :class="isAutoSummary ? 'text-[#22C55E]' : 'text-[#78716C]'">{{ isAutoSummary ? '开启' : '关闭' }}</span>
        </button>

        <!-- 高级设置 -->
        <button
          type="button"
          @click="emit('openSettings'); handleClose()"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
              <Settings class="w-3.5 h-3.5" />
            </div>
            <span>高级设置</span>
          </div>
        </button>

        <!-- 隐藏序幕 -->
        <button
          type="button"
          @click="isHidePrologue = !isHidePrologue"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
              <EyeOff class="w-3.5 h-3.5" />
            </div>
            <span>隐藏序幕</span>
          </div>
          <span :class="isHidePrologue ? 'text-[#F9C86D]' : 'text-[#78716C]'">{{ isHidePrologue ? '已隐藏' : '显示' }}</span>
        </button>

        <!-- 启用自定义CSS -->
        <button
          type="button"
          @click="isCustomCss = !isCustomCss"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
              <FileCode class="w-3.5 h-3.5" />
            </div>
            <span>启用自定义CSS</span>
          </div>
          <span :class="isCustomCss ? 'text-[#22C55E]' : 'text-[#78716C]'">{{ isCustomCss ? '已开启' : '关闭' }}</span>
        </button>

        <!-- 导出对话到本地 -->
        <button
          type="button"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
              <Download class="w-3.5 h-3.5" />
            </div>
            <span>导出对话到本地</span>
          </div>
        </button>

        <!-- 从本地导入记录 -->
        <button
          type="button"
          class="w-full h-10 px-3 rounded-lg flex items-center justify-between text-xs text-[#C0A480] hover:text-white hover:bg-white/5 transition-colors cursor-pointer"
        >
          <div class="flex items-center gap-2">
            <div class="w-6 h-6 rounded-md border border-[#44403C] bg-[#292524] flex items-center justify-center">
              <Upload class="w-3.5 h-3.5" />
            </div>
            <span>从本地导入记录</span>
          </div>
        </button>
      </div>

    </aside>
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

.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(-100%);
}
</style>
