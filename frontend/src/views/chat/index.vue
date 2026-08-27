<script setup lang="ts">
/**
 * 叙梦 Naro - AI 对话交互界面主页面 (Smart Container 主入口)
 *
 * 1:1 严格还原 Figma 原型《Naro叙梦 - AI聊天》全部交互与高奢黑金视觉。
 *
 * @packageDocumentation
 */

import ChatHeader from "@/views/chat/components/ChatHeader.vue";
import ChatInputBar from "@/views/chat/components/ChatInputBar.vue";
import ChatChatMessageList from "@/views/chat/components/ChatMessageList.vue";
import ChatSidebarDrawer from "@/views/chat/components/ChatSidebarDrawer.vue";
import ChatToolbar from "@/views/chat/components/ChatToolbar.vue";
import ControlPanelDrawer from "@/views/chat/components/ControlPanelDrawer.vue";
import FloatingMascotBadge from "@/views/chat/components/FloatingMascotBadge.vue";
import ModelSelectorDrawer from "@/views/chat/components/ModelSelectorDrawer.vue";
import NaroAssistantModal from "@/views/chat/components/NaroAssistantModal.vue";
import NarrativePanelDrawer from "@/views/chat/components/NarrativePanelDrawer.vue";
import StoryBranchDrawer from "@/views/chat/components/StoryBranchDrawer.vue";
import { useChatSession } from "@/views/chat/composables/useChatSession";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const characterId = computed(() => (route.params.id as string) || "c1");

const isSidebarOpen = ref(false);
const isAssistantOpen = ref(false);
const isControlPanelOpen = ref(false);
const isNarrativePanelOpen = ref(false);
const isBranchDrawerOpen = ref(false);
const activeBranchTargetId = ref<string | undefined>(undefined);
const inputBarRef = ref<{ appendPrompt: (text: string) => void } | null>(null);

const {
  character,
  messages,
  currentModel,
  currentMode,
  isGenerating,
  isModelDrawerOpen,
  toastMessage,
  showToast,
  handleBack,
  handleSendMessage,
  handleStopGeneration,
  handleRegenerate,
  handleBranch,
  handleEditMessage,
  handleSaveEditMessage,
  handleDeleteMessage,
  handleReadAloud,
  handleSelectModel,
  handleSwitchMode,
} = useChatSession(characterId);

/**
 * 响应 Naro 助手指令注入
 */
function handleInsertPrompt(text: string): void {
  inputBarRef.value?.appendPrompt(text);
}

/**
 * 响应设置菜单点击
 */
function handleSettingsAction(action: string): void {
  const map: Record<string, string> = {
    language: "已切换至简体中文",
    toggleSound: "声音设置已更新",
    theme: "已切换至黑金奢华主题",
    advanced: "已打开高级设置",
    guide: "已打开新手攻略指南",
  };
  if (action === "advanced") {
    isControlPanelOpen.value = true;
  }
  showToast(map[action] || "已触发设置");
}

/**
 * 响应底部更多扩展功能面板点击
 */
function handleMoreAction(action: string): void {
  const map: Record<string, string> = {
    memoryOn: "记忆增强 · 已开启",
    memoryOff: "记忆增强 · 已关闭",
    dialogueOn: "对话增强 · 已开启",
    dialogueOff: "对话增强 · 已关闭",
    modManage: "正在加载 Mod 管理器...",
    artistPrompt: "已注入画师串 · 二次元提示词",
  };
  if (action === "artistPrompt") {
    inputBarRef.value?.appendPrompt(
      "masterpiece, best quality, anime style, highly detailed, expressive eyes",
    );
  }
  showToast(map[action] || `已触发: ${action}`);
}

/**
 * 响应点击剧情分支按钮
 */
function onBranch(msg: { id: string }): void {
  activeBranchTargetId.value = msg.id;
  isBranchDrawerOpen.value = true;
  showToast("已打开剧情分支时间线");
}

/**
 * 响应时间轴节点回溯
 */
function handleJumpToNode(messageId: string): void {
  const idx = messages.value.findIndex((m) => m.id === messageId);
  if (idx !== -1) {
    messages.value = messages.value.slice(0, idx + 1);
    showToast("已回溯至该历史剧情节点");
  }
}

/**
 * 响应开辟新分支
 */
function handleCreateBranch(_fromId: string, name: string): void {
  showToast(`已创建新分支：${name}`);
}
</script>

<template>
  <div class="flex flex-col h-screen w-full max-w-[440px] mx-auto text-[#F5F5F4] relative shadow-2xl overflow-hidden bg-[#0F0D0C]">
    
    <!-- 1. 全屏沉浸式角色立绘大背景 (动态绑定角色封面/立绘 + 暗黑磨砂渐变遮罩) -->
    <div
      v-if="character.backgroundUrl || character.avatarUrl"
      class="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat pointer-events-none transition-all duration-700"
      :style="{ backgroundImage: `url('${character.backgroundUrl || character.avatarUrl}')` }"
    />
    <!-- 渐变暗黑磨砂玻璃蒙层 -->
    <div class="absolute inset-0 z-0 bg-gradient-to-b from-black/40 via-[#1A1511]/70 to-[#0F0D0C]/90 backdrop-blur-[2px] pointer-events-none" />

    <!-- 2. 顶部 Header (左侧返回/侧边栏 + 右侧 5 个霓虹功能按钮) -->
    <div class="relative z-20">
      <ChatHeader
        @back="handleBack"
        @open-sidebar="isSidebarOpen = true"
        @open-music="() => {}"
        @open-assistant="isAssistantOpen = true"
        @open-narrative-panel="isNarrativePanelOpen = true"
        @open-canvas="isNarrativePanelOpen = true"
        @open-apps="isControlPanelOpen = true"
        @open-control-panel="isControlPanelOpen = true"
        @settings-action="handleSettingsAction"
      />
    </div>

    <!-- 3. 中间消息滚动列表 (合规提示 + 作者的话 + 序幕 + 气泡列表) -->
    <div class="relative z-10 flex-1 overflow-hidden flex flex-col">
      <ChatChatMessageList
        :messages="messages"
        :author-note="character.authorNote"
        :prologue-title="character.prologueTitle"
        :prologue-content="character.prologueContent"
        @read-aloud="handleReadAloud"
        @regenerate="handleRegenerate"
        @rerun-memory="() => showToast('正在重跑记忆增强 RAG 索引...')"
        @continue="() => showToast('已触发 500 字剧情续写')"
        @branch="onBranch"
        @edit="handleEditMessage"
        @save-edit="handleSaveEditMessage"
        @share="() => showToast('消息链接已复制到剪贴板')"
        @delete="handleDeleteMessage"
      />
    </div>

    <!-- 4. 底部悬浮控制区 (模型栏 + 输入栏, 底部保留 28px 留白) -->
    <div class="relative z-20 w-full px-4 pb-7 pt-1 flex flex-col gap-2 bg-transparent">
      <ChatToolbar
        :current-model="currentModel"
        :current-mode="currentMode"
        @open-model-selector="isModelDrawerOpen = true"
        @switch-mode="handleSwitchMode"
      />
      <ChatInputBar
        ref="inputBarRef"
        :disabled="false"
        :is-generating="isGenerating"
        @send="handleSendMessage"
        @stop="handleStopGeneration"
        @ai-assist="() => showToast('✦ AI 灵感辅助已启动')"
        @more-action="handleMoreAction"
      />
    </div>

    <!-- 5. 右下角悬浮粉鸟吉祥物微章 -->
    <FloatingMascotBadge @click="handleSendMessage('我想了解更多关于你的故事！')" />

    <!-- 6. 聊天侧边抽屉菜单 (1:1 原型) -->
    <ChatSidebarDrawer
      v-model:open="isSidebarOpen"
      :character-id="characterId"
      :character-name="character.name"
      :avatar-url="character.avatarUrl"
    />

    <!-- 7. 模型选择抽屉 -->
    <ModelSelectorDrawer
      v-model:open="isModelDrawerOpen"
      :current-model-id="currentModel.id"
      @select-model="handleSelectModel"
    />

    <!-- 8. Naro助手浮层弹窗 (1:1 Figma 原型) -->
    <NaroAssistantModal
      v-model:open="isAssistantOpen"
      @insert-prompt="handleInsertPrompt"
    />

    <!-- 9. 主控面板抽屉 (1:1 Figma 原型 Frame 80:2307) -->
    <ControlPanelDrawer
      v-model:open="isControlPanelOpen"
    />

    <!-- 10. 叙梦面板/聊天信息面板抽屉 (1:1 Figma 原型 Frame 83:6511) -->
    <NarrativePanelDrawer
      v-model:open="isNarrativePanelOpen"
    />

    <!-- 11. 剧情分支与时间线抽屉 (方案 1: 黑金折叠时间轴抽屉) -->
    <StoryBranchDrawer
      v-model:open="isBranchDrawerOpen"
      :current-message-id="activeBranchTargetId"
      :messages="messages"
      @jump-to-node="handleJumpToNode"
      @create-branch="handleCreateBranch"
    />

    <!-- 11. 轻量浮动 Toast 反馈 -->
    <div
      v-if="toastMessage"
      class="fixed top-12 left-1/2 -translate-x-1/2 z-50 px-4 py-1.5 rounded-full bg-[#F9C86D] text-[#0C0A09] font-medium text-xs shadow-2xl animate-fade-in pointer-events-none"
    >
      {{ toastMessage }}
    </div>

  </div>
</template>
