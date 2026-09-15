<script setup lang="ts">
/**
 * 剧情全景拓扑画布组件 (StoryBranchCanvasModal.vue)
 *
 * 基于 @vue-flow/core 实现的高奢黑金全景 DAG 剧情树可视化画布。
 * 流程方向：自顶向下 (Top-to-Bottom 垂直时序流)。
 * 支持多分支并列排版、平滑贝塞尔曲线、自适应居中、活跃节点呼吸光效与一键派生独立会话。
 *
 * @packageDocumentation
 */

import AppModal from "@/components/common/AppModal.vue";
import { type DAGGraph, type DAGNode, chatService } from "@/services/chat";
import { Background } from "@vue-flow/background";
import { Controls } from "@vue-flow/controls";
import { type Edge, Handle, type Node, Position, VueFlow, useVueFlow } from "@vue-flow/core";
import "@vue-flow/core/dist/style.css";
import "@vue-flow/core/dist/theme-default.css";
import "@vue-flow/controls/dist/style.css";
import { GitBranch, Maximize2, RefreshCw, RotateCcw, Sparkles, X } from "lucide-vue-next";
import { computed, nextTick, ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  sessionId: string;
  currentBranchId: string;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "switchBranch", branchId: string): void;
  (e: "forkBranch", fromMessageId: string, name?: string): void;
  (e: "rollback", messageId: string): void;
}>();

const loading = ref(false);
const graphData = ref<DAGGraph | null>(null);
const selectedNode = ref<DAGNode | null>(null);

const { fitView } = useVueFlow();

/**
 * 加载全景 DAG 拓扑图数据并转换为 Vue Flow 格式
 */
async function loadGraph(): Promise<void> {
  if (!props.sessionId) return;
  loading.value = true;
  try {
    const data = await chatService.getStoryTree(props.sessionId);
    graphData.value = data;
    await nextTick();
    setTimeout(() => {
      fitView({ padding: 0.18 });
    }, 120);
  } catch (err) {
    console.error("加载剧情树拓扑图失败:", err);
  } finally {
    loading.value = false;
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      loadGraph();
    }
  },
  { immediate: true },
);

// 转换 Vue Flow Nodes (自顶向下 Top-to-Bottom 垂直排版)
const flowNodes = computed<Node[]>(() => {
  if (!graphData.value) return [];

  const nodes = graphData.value.nodes;
  const branchIds = Array.from(new Set(nodes.map((n) => n.branch_id)));

  // 分支列索引映射 (主线居左列 0, 其余分支依次向右延展)
  const branchColMap = new Map<string, number>();
  let sideColIndex = 1;

  branchIds.forEach((bId) => {
    const isMain = nodes.find((n) => n.branch_id === bId)?.is_main;
    if (isMain) {
      branchColMap.set(bId, 0);
    } else {
      branchColMap.set(bId, sideColIndex);
      sideColIndex += 1;
    }
  });

  // 每个分支内部的消息按时序自上而下排列 (Y 坐标累加)
  const branchMsgCounts = new Map<string, number>();

  return nodes.map((node) => {
    const col = branchColMap.get(node.branch_id) || 0;
    const msgStep = branchMsgCounts.get(node.branch_id) || 0;
    branchMsgCounts.set(node.branch_id, msgStep + 1);

    // 垂直流向：X 对应分支列，Y 对应时序步长
    const x = 50 + col * 280;
    const y = 40 + msgStep * 150;

    return {
      id: node.id,
      type: "custom",
      position: { x, y },
      data: { ...node },
      class: "custom-story-node",
    };
  });
});

// 转换 Vue Flow Edges (上下自顶向下平滑曲线)
const flowEdges = computed<Edge[]>(() => {
  if (!graphData.value) return [];
  return graphData.value.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    type: "smoothstep",
    animated: e.is_main,
    style: {
      stroke: e.is_main ? "#F9C86D" : "#60A5FA",
      strokeWidth: e.is_main ? 2.5 : 1.8,
      strokeDasharray: e.is_main ? undefined : "5 5",
    },
  }));
});

function handleNodeClick(event: any): void {
  const n = event.node?.data as DAGNode | undefined;
  if (n) {
    selectedNode.value = n;
  }
}

function handleSwitchToSelected(): void {
  if (!selectedNode.value) return;
  emit("switchBranch", selectedNode.value.branch_id);
  emit("update:open", false);
}

function handleForkFromSelected(): void {
  if (!selectedNode.value) return;
  emit("forkBranch", selectedNode.value.message_id);
  emit("update:open", false);
}

function handleRollbackToSelected(): void {
  if (!selectedNode.value) return;
  emit("rollback", selectedNode.value.message_id);
  emit("update:open", false);
}
</script>

<template>
  <AppModal
    :open="open"
    title="🕸️ 剧情全景拓扑图 (Top-to-Bottom Flow)"
    max-width="max-w-5xl"
    @update:open="emit('update:open', $event)"
  >
    <div class="flex flex-col h-[75vh] bg-[#12100E] rounded-2xl overflow-hidden relative border border-[#3A332B]/60 shadow-2xl">
      
      <!-- 顶部控制与图例状态栏 (响应式防折叠) -->
      <div class="px-4 py-3 bg-[#1A1613]/95 border-b border-[#3A332B] flex flex-wrap items-center justify-between gap-3 z-10 select-none">
        
        <!-- 图例标识 -->
        <div class="flex items-center gap-3 text-xs">
          <div class="flex items-center gap-1.5 px-2 py-1 rounded-md bg-[#241F1A] border border-[#F9C86D]/30">
            <span class="w-2.5 h-2.5 rounded-full bg-[#F9C86D] shadow-[0_0_8px_#F9C86D]"></span>
            <span class="text-[#F9C86D] font-medium">🌿 主线</span>
          </div>

          <div class="flex items-center gap-1.5 px-2 py-1 rounded-md bg-[#162033] border border-[#3B82F6]/30">
            <span class="w-2.5 h-2.5 rounded-full bg-[#60A5FA]"></span>
            <span class="text-[#93C5FD]">🔀 分支</span>
          </div>

          <div class="flex items-center gap-1.5 px-2 py-1 rounded-md bg-[#241F1A] border border-white/10">
            <span class="w-2 h-2 rounded-full ring-2 ring-[#F9C86D] bg-[#0C0A09]"></span>
            <span class="text-[#D6D3D1]">📍 当前进度</span>
          </div>
        </div>

        <!-- 快捷操作按钮 -->
        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="loadGraph"
            class="px-3 py-1.5 rounded-lg border border-[#44403C] bg-[#241F1A] text-xs text-[#D6D3D1] hover:text-[#F9C86D] hover:border-[#F9C86D]/50 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm active:scale-95"
          >
            <RefreshCw class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" />
            <span>刷新</span>
          </button>
          <button
            type="button"
            @click="() => fitView({ padding: 0.18 })"
            class="px-3 py-1.5 rounded-lg border border-[#44403C] bg-[#241F1A] text-xs text-[#D6D3D1] hover:text-[#F9C86D] hover:border-[#F9C86D]/50 transition-all flex items-center gap-1.5 cursor-pointer shadow-sm active:scale-95"
          >
            <Maximize2 class="w-3.5 h-3.5" />
            <span>自适应居中</span>
          </button>
        </div>
      </div>

      <!-- Vue Flow 自顶向下主画布 -->
      <div class="flex-1 w-full h-full relative bg-[#0D0B0A]">
        <VueFlow
          :nodes="flowNodes"
          :edges="flowEdges"
          :min-zoom="0.2"
          :max-zoom="2"
          :fit-view-on-init="true"
          class="bg-[#0D0B0A]"
          @node-click="handleNodeClick"
        >
          <!-- 自定义节点渲染模板 (上下连接 Handle) -->
          <template #node-custom="{ data }">
            <div
              :class="[
                'p-3.5 rounded-2xl border backdrop-blur-xl transition-all shadow-xl select-none text-left w-[240px] cursor-pointer relative group',
                data.is_current
                  ? 'border-[#F9C86D] bg-gradient-to-b from-[#2C241E] to-[#1A1613] shadow-[0_0_24px_rgba(249,200,109,0.35)] ring-2 ring-[#F9C86D]/60'
                  : data.is_main
                  ? 'border-[#D1A35C]/50 bg-[#1A1613]/95 hover:border-[#F9C86D] hover:shadow-[0_4px_20px_rgba(249,200,109,0.2)]'
                  : 'border-[#3B82F6]/50 bg-[#121929]/95 hover:border-[#60A5FA] hover:shadow-[0_4px_20px_rgba(96,165,250,0.2)]'
              ]"
            >
              <!-- 顶部接收父节点连线 Handle -->
              <Handle
                type="target"
                :position="Position.Top"
                class="!bg-[#F9C86D] !w-2.5 !h-2.5 !-top-1.5 !border-2 !border-[#0C0A09]"
              />

              <!-- 节点顶部徽标行 -->
              <div class="flex items-center justify-between pb-2 border-b border-white/10 text-[11px]">
                <div class="flex items-center gap-1.5">
                  <span
                    :class="[
                      'px-1.5 py-0.5 rounded font-mono text-[10px] leading-tight font-medium',
                      data.sender === 'user'
                        ? 'bg-[#3B82F6]/20 text-[#93C5FD] border border-[#3B82F6]/30'
                        : 'bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/30'
                    ]"
                  >
                    {{ data.sender === "user" ? "我" : (data.character_name || "AI") }}
                  </span>
                </div>
                <span class="text-[#78716C] font-mono text-[10px]">{{ data.timestamp }}</span>
              </div>

              <!-- 节点正文摘要 -->
              <p class="pt-2 text-xs text-[#E7E5E4] leading-relaxed line-clamp-2 font-sans">
                {{ data.summary }}
              </p>

              <!-- 节点底部信息行 -->
              <div class="pt-2 mt-1 flex items-center justify-between text-[10px] text-[#A8A29E] border-t border-white/5">
                <span class="truncate max-w-[130px] font-mono text-[#D6D3D1]">{{ data.branch_name }}</span>
                <span v-if="data.is_current" class="text-[#F9C86D] font-medium flex items-center gap-1 shrink-0 animate-pulse">
                  ● 活跃进度
                </span>
              </div>

              <!-- 底部发射给子节点连线 Handle -->
              <Handle
                type="source"
                :position="Position.Bottom"
                class="!bg-[#F9C86D] !w-2.5 !h-2.5 !-bottom-1.5 !border-2 !border-[#0C0A09]"
              />
            </div>
          </template>

          <Background pattern-color="#2E2822" :gap="24" />
          <Controls />
        </VueFlow>

        <!-- 悬浮节点操作侧边/底部卡片 (点击节点时唤出) -->
        <transition name="fade">
          <div
            v-if="selectedNode"
            class="absolute left-4 right-4 sm:left-auto sm:right-6 bottom-6 sm:w-88 p-4 rounded-2xl border border-[#F9C86D]/50 bg-[#1A1613]/95 backdrop-blur-2xl shadow-[0_12px_40px_rgba(0,0,0,0.8)] z-20 flex flex-col gap-3 animate-fade-in"
          >
            <div class="flex items-center justify-between border-b border-white/10 pb-2">
              <div class="flex items-center gap-2 text-xs font-medium text-[#F9C86D]">
                <GitBranch class="w-3.5 h-3.5" />
                <span>{{ selectedNode.branch_name }}</span>
              </div>
              <button
                type="button"
                @click="selectedNode = null"
                class="w-6 h-6 rounded-full flex items-center justify-center text-[#78716C] hover:text-white hover:bg-white/10 transition-colors cursor-pointer"
              >
                <X class="w-4 h-4" />
              </button>
            </div>

            <!-- 节点发言者与时间 -->
            <div class="flex items-center justify-between text-xs text-[#A8A29E]">
              <span
                :class="[
                  'px-2 py-0.5 rounded font-mono text-[10px]',
                  selectedNode.sender === 'user' ? 'bg-[#3B82F6]/20 text-[#93C5FD]' : 'bg-[#F9C86D]/20 text-[#F9C86D]'
                ]"
              >
                {{ selectedNode.sender === "user" ? "我" : (selectedNode.character_name || "AI 角色") }}
              </span>
              <span class="font-mono">{{ selectedNode.timestamp }}</span>
            </div>

            <!-- 详细内容正文 -->
            <div class="p-2.5 rounded-xl bg-black/40 border border-white/5 max-h-32 overflow-y-auto text-xs text-[#E7E5E4] leading-relaxed font-sans [scrollbar-width:thin]">
              {{ selectedNode.content }}
            </div>

            <!-- 操作按钮组 (仅对 AI 角色节点开放分叉与回溯，保障对话轮次节奏) -->
            <div v-if="selectedNode.sender === 'ai'" class="flex items-center gap-2.5 pt-1">
              <button
                type="button"
                @click="handleRollbackToSelected"
                class="flex-1 h-9 rounded-xl border border-[#44403C] bg-[#241F1A] text-xs text-white/90 hover:border-[#F9C86D] hover:text-[#F9C86D] transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-sm active:scale-95"
              >
                <RotateCcw class="w-3.5 h-3.5" />
                <span>回溯至此</span>
              </button>
              <button
                type="button"
                @click="handleForkFromSelected"
                class="flex-1 h-9 rounded-xl bg-[#F9C86D] text-[#0C0A09] text-xs font-semibold hover:scale-102 active:scale-98 transition-all flex items-center justify-center gap-1.5 cursor-pointer shadow-[0_4px_16px_rgba(249,200,109,0.3)]"
              >
                <Sparkles class="w-3.5 h-3.5" />
                <span>从此派生新对话</span>
              </button>
            </div>
            <div v-else class="text-center py-1 text-[11px] text-[#78716C] font-mono italic">
              用户输入节点 · 请选择 AI 剧情节点进行回溯或分叉
            </div>
          </div>
        </transition>

      </div>

    </div>
  </AppModal>
</template>

<style>
/* Vue Flow 节点暗黑金奢华定制样式 */
.vue-flow__handle {
  background: #F9C86D !important;
  width: 8px !important;
  height: 8px !important;
  border-radius: 50% !important;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
