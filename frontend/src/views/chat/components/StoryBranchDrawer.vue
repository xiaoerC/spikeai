<script setup lang="ts">
/**
 * AI 聊天界面 - 剧情分支与时间线抽屉 (方案 1: 移动端黑金折叠分支抽屉)
 *
 * 优化特性:
 * 1. 过滤冗余 thinking 代码杂音，仅展示纯净高价值的剧情转折点;
 * 2. 顶部支持横向平滑切换不同的平行分支路线 (主线 / 分支1 / 分支2);
 * 3. 垂直黑金发光时间轴，清晰标记当前所在节点 (金色脉冲光晕);
 * 4. 支持一键「回溯至此」、「从此开辟新分支」与「删除分支」;
 * 5. 底部高奢全宽主按钮，极度贴合移动端单手操作体验。
 *
 * @packageDocumentation
 */

import AppDrawer from "@/components/common/AppDrawer.vue";
import type { ChatMessage } from "@/views/chat/constants/mockChatData";
import { Clock, GitBranch, History, Plus, RotateCcw, Sparkles, Trash2, X } from "lucide-vue-next";
import { computed, ref, watch } from "vue";

export interface BranchRoute {
  id: string;
  name: string;
  isMain: boolean;
  createdAt: string;
  nodeCount: number;
}

export interface StoryTimelineNode {
  id: string;
  messageId: string;
  sender: "ai" | "user" | "system";
  characterName: string;
  avatarUrl?: string;
  summary: string;
  timestamp: string;
  isCurrent: boolean;
  isChoicePoint?: boolean; // 是否为关键抉择点
}

const props = defineProps<{
  open: boolean;
  currentMessageId?: string;
  messages: ChatMessage[];
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "jumpToNode", messageId: string): void;
  (e: "createBranch", fromMessageId: string, branchName: string): void;
  (e: "deleteBranch", branchId: string): void;
}>();

// 平行分支路线列表
const branchRoutes = ref<BranchRoute[]>([
  {
    id: "main",
    name: "🌿 主线剧情 (当前)",
    isMain: true,
    createdAt: "20:00",
    nodeCount: 3,
  },
  {
    id: "branch-1",
    name: "🔀 分支 1：独自探查破庙",
    isMain: false,
    createdAt: "20:05",
    nodeCount: 2,
  },
  {
    id: "branch-2",
    name: "🔀 分支 2：向炭治郎坦白身份",
    isMain: false,
    createdAt: "20:12",
    nodeCount: 4,
  },
]);

const activeBranchId = ref("main");

// 基于当前消息列表构建时间轴节点
const timelineNodes = computed<StoryTimelineNode[]>(() => {
  if (activeBranchId.value === "main") {
    return props.messages.map((m, idx) => {
      // 过滤掉思考标签与多余空格
      const cleanText = m.content
        .replace(/<thinking>[\s\S]*?<\/thinking>/gi, "")
        .replace(/<!--[\s\S]*?-->/gi, "")
        .trim();

      const isLast = idx === props.messages.length - 1;

      return {
        id: `node-${m.id}`,
        messageId: m.id,
        sender: m.sender,
        characterName: m.sender === "ai" ? m.characterName || "AI" : "我",
        avatarUrl: m.avatarUrl,
        summary: cleanText.length > 60 ? `${cleanText.slice(0, 60)}...` : cleanText,
        timestamp: m.timestamp || "20:00",
        isCurrent: props.currentMessageId ? m.id === props.currentMessageId : isLast,
        isChoicePoint: m.sender === "user",
      };
    });
  }

  // 模拟分支路线的节点数据
  if (activeBranchId.value === "branch-1") {
    return [
      {
        id: "node-b1-1",
        messageId: "msg-1",
        sender: "ai",
        characterName: "灶门炭治郎",
        summary: "夜色渐浓，深山中的寒风呼啸而过。我能闻到空气中那一丝极淡却危险的血腥味……",
        timestamp: "20:00",
        isCurrent: false,
      },
      {
        id: "node-b1-2",
        messageId: "b1-u1",
        sender: "user",
        characterName: "我",
        summary: "“炭治郎，你留在这里照顾伤员，我去前方的破庙探查情况！”",
        timestamp: "20:05",
        isCurrent: true,
        isChoicePoint: true,
      },
      {
        id: "node-b1-3",
        messageId: "b1-a1",
        sender: "ai",
        characterName: "灶门炭治郎",
        summary: "（炭治郎紧紧握住日轮刀，神色担忧）“不行，太危险了！破庙里很可能有十二鬼月！”",
        timestamp: "20:06",
        isCurrent: false,
      },
    ];
  }

  return [
    {
      id: "node-b2-1",
      messageId: "msg-1",
      sender: "ai",
      characterName: "灶门炭治郎",
      summary: "夜色渐浓，深山中的寒风呼啸而过。我能闻到空气中那一丝极淡却危险的血腥味……",
      timestamp: "20:00",
      isCurrent: false,
    },
    {
      id: "node-b2-2",
      messageId: "b2-u1",
      sender: "user",
      characterName: "我",
      summary: "“其实……我并不是鬼杀队的队员，我来自一个完全不同的世界。”",
      timestamp: "20:12",
      isCurrent: true,
      isChoicePoint: true,
    },
  ];
});

function handleJump(messageId: string): void {
  emit("jumpToNode", messageId);
  emit("update:open", false);
}

function handleCreateNewBranch(fromMessageId?: string): void {
  const targetId =
    fromMessageId || props.currentMessageId || props.messages[props.messages.length - 1]?.id;
  const newBranchName = `🔀 分支 ${branchRoutes.value.length}：平行抉择线`;
  emit("createBranch", targetId, newBranchName);
  branchRoutes.value.push({
    id: `branch-${Date.now()}`,
    name: newBranchName,
    isMain: false,
    createdAt: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    nodeCount: 1,
  });
  activeBranchId.value = branchRoutes.value[branchRoutes.value.length - 1].id;
}

function handleClose(): void {
  emit("update:open", false);
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
            v-for="route in branchRoutes"
            :key="route.id"
            type="button"
            @click="activeBranchId = route.id"
            :class="[
              'px-3 py-1.5 rounded-full text-xs font-medium whitespace-nowrap transition-all flex items-center gap-1.5 cursor-pointer shrink-0 shadow-sm',
              activeBranchId === route.id
                ? 'bg-[#F9C86D] text-[#0C0A09] shadow-[0_0_12px_rgba(249,200,109,0.3)]'
                : 'border border-[#44403C] bg-[#2A261F] text-[#A8A29E] hover:text-white hover:border-[#F9C86D]/40'
            ]"
          >
            <span>{{ route.name }}</span>
            <span
              :class="[
                'text-[10px] px-1.5 py-0.2 rounded-full font-mono',
                activeBranchId === route.id ? 'bg-black/20 text-[#0C0A09]' : 'bg-black/40 text-[#A8A29E]'
              ]"
            >
              {{ route.nodeCount }} 节
            </span>
          </button>
        </div>

        <!-- + 新增分支快捷小按钮 -->
        <button
          type="button"
          @click="handleCreateNewBranch()"
          class="w-7 h-7 rounded-full border border-[#D1A35C]/60 bg-[#292524] flex items-center justify-center text-[#F9C86D] hover:scale-105 active:scale-95 transition-transform cursor-pointer shrink-0"
          title="开辟新分支"
        >
          <Plus class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- 2. 主体: 垂直发光时间轴列表 -->
      <div class="flex-1 overflow-y-auto px-4 py-4 [scrollbar-width:thin] space-y-4">
        
        <!-- 分支说明与状态条 -->
        <div class="p-2.5 rounded-lg border border-[#44403C]/40 bg-[#292524]/40 flex items-center justify-between text-xs text-[#A8A29E]">
          <div class="flex items-center gap-1.5">
            <GitBranch class="w-3.5 h-3.5 text-[#F9C86D]" />
            <span>当前路线：<strong class="text-white/90">{{ branchRoutes.find(r => r.id === activeBranchId)?.name }}</strong></span>
          </div>
          <span class="text-[11px] font-mono text-[#F9C86D]/80">点击节点可回溯或衍生</span>
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
                  ● 处于当前节点
                </span>
                <span v-else class="text-[11px] text-[#78716C]">
                  第 {{ index + 1 }} 幕
                </span>

                <div class="flex items-center gap-2">
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
          <span>基于当前对话开辟新分支</span>
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
