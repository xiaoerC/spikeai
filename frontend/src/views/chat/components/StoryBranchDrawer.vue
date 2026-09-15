<script setup lang="ts">
/**
 * AI 聊天界面 - 剧情分支与时间线抽屉 (StoryBranchDrawer.vue)
 *
 * 优化特性:
 * 1. 过滤冗余 thinking 代码杂音，仅展示纯净高价值的剧情转折点;
 * 2. 顶部支持横向平滑切换真实的平行分支路线 (主线 / 分支1 / 分支2);
 * 3. 垂直黑金发光时间轴，清晰标记当前所在节点 (金色脉冲光晕);
 * 4. 支持一键「回溯至此」、「从此开辟新分支」、「删除分支」与「唤起全景拓扑图」;
 * 5. 底部高奢全宽主按钮，极度贴合移动端单手操作体验。
 *
 * @packageDocumentation
 */

import AppDrawer from "@/components/common/AppDrawer.vue";
import type { StoryBranchDetail } from "@/services/chat";
import type { ChatMessage } from "@/views/chat/constants/mockChatData";
import {
  Clock,
  GitBranch,
  History,
  LayoutGrid,
  Plus,
  RotateCcw,
  Sparkles,
  Trash2,
  X,
} from "lucide-vue-next";
import { computed, ref, watch } from "vue";

export interface StoryTimelineNode {
  id: string;
  messageId: string;
  sender: "ai" | "user" | "system";
  characterName: string;
  avatarUrl?: string;
  summary: string;
  timestamp: string;
  isCurrent: boolean;
  isChoicePoint?: boolean;
  actIndex: number;
}

const props = defineProps<{
  open: boolean;
  currentBranchId?: string;
  branches: StoryBranchDetail[];
  currentMessageId?: string;
  messages: ChatMessage[];
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "switchBranch", branchId: string): void;
  (e: "createBranch", fromMessageId?: string, branchName?: string): void;
  (e: "deleteBranch", branchId: string): void;
  (e: "jumpToNode", messageId: string): void;
  (e: "rollback", messageId: string, mode: "fork" | "truncate"): void;
  (e: "openCanvas"): void;
}>();

// 当前选中的分支 ID
const activeBranchId = ref<string>("");

watch(
  () => props.currentBranchId,
  (newId) => {
    if (newId) {
      activeBranchId.value = newId;
    }
  },
  { immediate: true },
);

// 备用兜底分支列表
const displayBranches = computed<StoryBranchDetail[]>(() => {
  if (props.branches && props.branches.length > 0) {
    return props.branches;
  }
  return [
    {
      id: "main",
      session_id: "",
      name: "🌿 主线剧情",
      is_main: true,
      node_count: props.messages.length,
      total_path_count: props.messages.length,
      created_at: new Date().toISOString(),
    },
  ];
});

// 基于当前消息列表构建时间轴节点 (倒序: 越新的越在顶部展示)
const timelineNodes = computed<StoryTimelineNode[]>(() => {
  const total = props.messages.length;
  const reversed = [...props.messages].reverse();

  return reversed.map((m, revIdx) => {
    // 过滤掉思考标签与多余空格
    const cleanText = m.content
      .replace(/<thinking>[\s\S]*?<\/thinking>/gi, "")
      .replace(/<!--[\s\S]*?-->/gi, "")
      .trim();

    const originalIdx = total - 1 - revIdx;
    const isNewest = revIdx === 0;

    return {
      id: `node-${m.id}`,
      messageId: m.id,
      sender: m.sender,
      characterName: m.sender === "ai" ? m.characterName || "AI" : "我",
      avatarUrl: m.avatarUrl,
      summary: cleanText.length > 60 ? `${cleanText.slice(0, 60)}...` : cleanText,
      timestamp: m.timestamp || "20:00",
      isCurrent: props.currentMessageId ? m.id === props.currentMessageId : isNewest,
      isChoicePoint: m.sender === "user",
      actIndex: originalIdx + 1,
    };
  });
});

function handleSelectBranch(branchId: string): void {
  activeBranchId.value = branchId;
  emit("switchBranch", branchId);
}

function handleJump(messageId: string): void {
  emit("jumpToNode", messageId);
  emit("update:open", false);
}

function handleCreateNewBranch(fromMessageId?: string): void {
  emit("createBranch", fromMessageId);
  emit("update:open", false);
}

function handleDeleteCurrentBranch(branchId: string): void {
  emit("deleteBranch", branchId);
}

function handleOpenCanvas(): void {
  emit("update:open", false);
  emit("openCanvas");
}
</script>

<template>
  <AppDrawer
    :open="open"
    title="剧情分支与时间线"
    height="h-[80vh]"
    @update:open="emit('update:open', $event)"
  >
    <div class="flex flex-col h-full bg-[#1C1917] text-white select-none">
      
      <!-- 1. 顶部分支切换药丸栏 (水平平滑滚动) -->
      <div class="px-4 py-2.5 border-b border-[#44403C]/60 bg-[#292524]/60 flex items-center justify-between gap-2">
        <div class="flex items-center gap-2 overflow-x-auto no-scrollbar py-0.5 flex-1">
          <button
            v-for="b in displayBranches"
            :key="b.id"
            type="button"
            @click="handleSelectBranch(b.id)"
            :class="[
              'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 cursor-pointer shrink-0 shadow-sm group',
              activeBranchId === b.id
                ? 'bg-[#F9C86D] text-[#0C0A09] shadow-[0_0_12px_rgba(249,200,109,0.3)]'
                : 'border border-[#44403C] bg-[#2A261F] text-[#A8A29E] hover:text-white hover:border-[#F9C86D]/40'
            ]"
          >
            <span>{{ b.name }}</span>
            <span
              :class="[
                'text-[10px] px-1.5 py-0.2 rounded-full font-mono',
                activeBranchId === b.id ? 'bg-black/20 text-[#0C0A09]' : 'bg-black/40 text-[#A8A29E]'
              ]"
            >
              {{ b.total_path_count || b.node_count || 1 }} 节
            </span>

            <!-- 删除非主线分支 -->
            <span
              v-if="!b.is_main"
              @click.stop="handleDeleteCurrentBranch(b.id)"
              class="w-3.5 h-3.5 rounded-full flex items-center justify-center opacity-60 hover:opacity-100 hover:text-red-500 transition-opacity ml-0.5"
              title="删除此分支"
            >
              <Trash2 class="w-3 h-3" />
            </span>
          </button>
        </div>

        <div class="flex items-center gap-1.5 shrink-0">
          <!-- 全景拓扑图按钮 -->
          <button
            type="button"
            @click="handleOpenCanvas"
            class="px-2 py-1 rounded-lg border border-[#D1A35C]/50 bg-[#292524] flex items-center gap-1 text-[#F9C86D] text-xs hover:bg-[#D1A35C]/20 transition-all cursor-pointer"
            title="全景剧情树画布"
          >
            <LayoutGrid class="w-3.5 h-3.5" />
            <span class="hidden sm:inline">全景图</span>
          </button>

          <!-- + 新增分支快捷小按钮 -->
          <button
            type="button"
            @click="handleCreateNewBranch()"
            class="w-7 h-7 rounded-full border border-[#D1A35C]/60 bg-[#292524] flex items-center justify-center text-[#F9C86D] hover:scale-105 active:scale-95 transition-transform cursor-pointer"
            title="开辟新分支"
          >
            <Plus class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <!-- 2. 主体: 垂直发光时间轴列表 -->
      <div class="flex-1 overflow-y-auto px-4 py-4 [scrollbar-width:thin] space-y-4">
        
        <!-- 分支说明与状态条 -->
        <div class="p-2.5 rounded-lg border border-[#44403C]/40 bg-[#292524]/40 flex items-center justify-between text-xs text-[#A8A29E]">
          <div class="flex items-center gap-1.5">
            <GitBranch class="w-3.5 h-3.5 text-[#F9C86D]" />
            <span>当前路线：<strong class="text-white/90">{{ displayBranches.find(r => r.id === activeBranchId)?.name || '主线剧情' }}</strong></span>
          </div>
          <span class="text-[11px] font-mono text-[#F9C86D]/80">点击节点可回溯或分叉</span>
        </div>

        <!-- 节点时间轴树 -->
        <div class="relative pl-6 space-y-4 before:content-[''] before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[2px] before:bg-gradient-to-b before:from-[#F9C86D] before:via-[#44403C] before:to-[#44403C]/20">
          
          <div
            v-for="(node, index) in timelineNodes"
            :key="node.id"
            class="relative group animate-fade-in"
          >
            <!-- 时间轴圆点指示器 -->
            <div
              :class="[
                'absolute -left-[24px] top-3 w-4 h-4 rounded-full flex items-center justify-center transition-all z-10',
                node.isCurrent
                  ? 'bg-[#F9C86D] ring-4 ring-[#F9C86D]/20 shadow-[0_0_8px_#F9C86D]'
                  : 'border-2 border-[#44403C] bg-[#1C1917] group-hover:border-[#F9C86D]'
              ]"
            >
              <div
                v-if="node.isCurrent"
                class="w-1.5 h-1.5 rounded-full bg-[#0C0A09]"
              />
            </div>

            <!-- 节点卡片主体 -->
            <div
              :class="[
                'p-3.5 rounded-xl border transition-all',
                node.isCurrent
                  ? 'border-[#F9C86D]/80 bg-gradient-to-br from-[#292524] to-[#1C1917] shadow-[0_4px_16px_rgba(249,200,109,0.15)]'
                  : 'border-[#44403C]/60 bg-[#292524]/60 hover:border-[#F9C86D]/40 hover:bg-[#292524]/90'
              ]"
            >
              <!-- 顶部信息: 角色/我 + 时间 + 关键抉择徽标 -->
              <div class="flex items-center justify-between pb-1.5 border-b border-white/5 text-xs">
                <div class="flex items-center gap-1.5">
                  <!-- 发言人徽标 -->
                  <span
                    :class="[
                      'px-1.5 py-0.5 rounded text-[10px] font-medium leading-none',
                      node.sender === 'user'
                        ? 'bg-[#3B82F6]/20 text-[#60A5FA] border border-[#3B82F6]/30'
                        : 'bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/30'
                    ]"
                  >
                    {{ node.characterName }}
                  </span>

                  <span v-if="node.isChoicePoint" class="px-1.5 py-0.5 rounded text-[10px] bg-purple-500/20 text-purple-300 border border-purple-500/30 flex items-center gap-0.5">
                    <Sparkles class="w-2.5 h-2.5" />
                    剧情抉择
                  </span>
                </div>

                <div class="flex items-center gap-2 text-[11px] text-[#A8A29E] font-mono">
                  <Clock class="w-3 h-3 text-[#78716C]" />
                  <span>{{ node.timestamp }}</span>
                </div>
              </div>

              <!-- 节点纯净内容摘要 (无 thinking 杂音) -->
              <p class="pt-2 text-xs text-white/90 leading-relaxed font-sans">
                {{ node.summary }}
              </p>

              <!-- 底部操作按钮栏 -->
              <div class="pt-2.5 mt-1 flex items-center justify-between text-xs">
                <span v-if="node.isCurrent" class="text-[11px] text-[#F9C86D] font-medium flex items-center gap-1">
                  ● 当前最新进度 (第 {{ node.actIndex }} 幕)
                </span>
                <span v-else class="text-[11px] text-[#78716C]">
                  第 {{ node.actIndex }} 幕
                </span>

                <!-- 仅对 AI 角色发言节点显示分叉与回溯操作 (避免用户发言节点回溯后产生连续两句用户输入) -->
                <div v-if="node.sender === 'ai'" class="flex items-center gap-2">
                  <!-- 1. 回溯至此 -->
                  <button
                    type="button"
                    @click="handleJump(node.messageId)"
                    class="px-2.5 py-1 rounded-md border border-[#44403C] bg-black/30 hover:border-[#F9C86D] hover:text-[#F9C86D] text-white/80 transition-all flex items-center gap-1 cursor-pointer"
                  >
                    <RotateCcw class="w-3 h-3" />
                    <span>回溯至此</span>
                  </button>

                  <!-- 2. 从此开辟新分支 -->
                  <button
                    type="button"
                    @click="handleCreateNewBranch(node.messageId)"
                    class="px-2.5 py-1 rounded-md border border-[#D1A35C]/60 bg-[#D1A35C]/10 text-[#F9C86D] hover:bg-[#D1A35C] hover:text-[#0C0A09] transition-all flex items-center gap-1 cursor-pointer font-medium"
                  >
                    <GitBranch class="w-3 h-3" />
                    <span>从此分叉</span>
                  </button>
                </div>
                <div v-else class="text-[10.5px] text-[#78716C] italic font-mono">
                  用户发言节点
                </div>
              </div>

            </div>
          </div>

        </div>

      </div>

      <!-- 3. 底部全宽主按钮 -->
      <div class="p-4 border-t border-[#44403C]/60 bg-[#292524] flex items-center justify-between gap-3">
        <button
          type="button"
          @click="handleCreateNewBranch()"
          class="flex-1 h-10 rounded-xl bg-[#F9C86D] text-[#0C0A09] font-medium text-sm flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-[0.98] transition-all shadow-[0_4px_16px_rgba(249,200,109,0.3)] cursor-pointer"
        >
          <GitBranch class="w-4 h-4" />
          <span>从当前对话派生全新独立记录</span>
        </button>
      </div>

    </div>
  </AppDrawer>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
