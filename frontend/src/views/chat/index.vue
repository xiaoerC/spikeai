<script setup lang="ts">
/**
 * 叙梦 Naro - AI 对话交互界面主页面 (Smart Container 主入口)
 *
 * 1:1 严格还原 Figma 原型《Naro叙梦 - AI聊天》全部交互与高奢黑金视觉。
 *
 * @packageDocumentation
 */

import { useResponsiveLayout } from "@/composables/useResponsiveLayout";
import BgmPlayerDrawer from "@/views/chat/components/BgmPlayerDrawer.vue";
import ChatHeader from "@/views/chat/components/ChatHeader.vue";
import ChatInputBar from "@/views/chat/components/ChatInputBar.vue";
import ChatChatMessageList from "@/views/chat/components/ChatMessageList.vue";
import ChatSidebarDrawer from "@/views/chat/components/ChatSidebarDrawer.vue";
import ChatToolbar from "@/views/chat/components/ChatToolbar.vue";
import ControlPanelDrawer from "@/views/chat/components/ControlPanelDrawer.vue";
import DesktopChatView from "@/views/chat/components/DesktopChatView.vue";
import ModManagerDrawer from "@/views/chat/components/ModManagerDrawer.vue";
import ModelSelectorDrawer from "@/views/chat/components/ModelSelectorDrawer.vue";
import NaroAssistantModal from "@/views/chat/components/NaroAssistantModal.vue";
import NarrativePanelDrawer from "@/views/chat/components/NarrativePanelDrawer.vue";
import StoryBranchCanvasModal from "@/views/chat/components/StoryBranchCanvasModal.vue";
import StoryBranchDrawer from "@/views/chat/components/StoryBranchDrawer.vue";
import WorldBookDrawer from "@/views/chat/components/WorldBookDrawer.vue";
import { useChatSession } from "@/views/chat/composables/useChatSession";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const characterId = computed(() => (route.params.id as string) || "c1");
const { isMobile } = useResponsiveLayout();

const isSidebarOpen = ref(false);
const isAssistantOpen = ref(false);
const isControlPanelOpen = ref(false);
const isNarrativePanelOpen = ref(false);
const isWorldBookOpen = ref(false);
const isModDrawerOpen = ref(false);
const isBgmOpen = ref(false);
const inputBarRef = ref<{ appendPrompt: (text: string) => void } | null>(null);
const desktopChatRef = ref<{ appendPrompt: (text: string) => void } | null>(null);

const {
  character,
  sessionId,
  messages,
  alternateGreetings,
  currentGreetingIndex,
  openingReplies,
  bgmUrl,
  branches,
  currentBranchId,
  isBranchDrawerOpen,
  isCanvasModalOpen,
  selectedForkMessageId,
  currentModel,
  currentMode,
  isGenerating,
  isModelDrawerOpen,
  toastMessage,
  showToast,
  loadBranches,
  handleBack,
  handleSendMessage,
  handleStopGeneration,
  handleRegenerate,
  handleBranch,
  handleSwitchBranch,
  handleCreateBranch,
  handleDeleteBranch,
  handleRollback,
  handleEditMessage,
  handleSaveEditMessage,
  handleDeleteMessage,
  handleReadAloud,
  handleSwitchGreeting,
  handleSelectModel,
  handleSwitchMode,
  controlPanel,
  narrativeState,
  loadControlPanel,
  loadNarrativeState,
  saveControlPanel,
  saveNarrativeState,
} = useChatSession(characterId);

/**
 * 响应 Naro 助手指令注入
 */
function handleInsertPrompt(text: string): void {
  if (isMobile.value) {
    inputBarRef.value?.appendPrompt(text);
  } else {
    desktopChatRef.value?.appendPrompt(text);
  }
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
  if (action === "modManage") {
    isModDrawerOpen.value = true;
    return;
  }
  const map: Record<string, string> = {
    memoryOn: "记忆增强 · 已开启",
    memoryOff: "记忆增强 · 已关闭",
    dialogueOn: "对话增强 · 已开启",
    dialogueOff: "对话增强 · 已关闭",
    artistPrompt: "已注入画师串 · 二次元提示词",
  };
  if (action === "artistPrompt") {
    inputBarRef.value?.appendPrompt(
      "masterpiece, best quality, anime style, highly detailed, expressive eyes",
    );
  }
  showToast(map[action] || `已触发: ${action}`);
}
</script>

<template>
  <!-- 1. PC 桌面端 (>= 768px): 1:1 还原 media_1789565500457.png 的沉浸 Visual Novel 剧场 -->
  <DesktopChatView
    v-if="!isMobile"
    ref="desktopChatRef"
    :character="character"
    :messages="messages"
    :current-model="currentModel"
    :current-mode="currentMode"
    :is-generating="isGenerating"
    :opening-replies="openingReplies"
    :alternate-greetings="alternateGreetings"
    :current-greeting-index="currentGreetingIndex"
    @back="handleBack"
    @send="handleSendMessage"
    @stop="handleStopGeneration"
    @regenerate="handleRegenerate"
    @rerun-memory="() => showToast('正在重跑记忆增强 RAG 索引...')"
    @continue="() => showToast('已触发 500 字剧情续写')"
    @branch="handleBranch"
    @edit="handleEditMessage"
    @save-edit="handleSaveEditMessage"
    @delete="handleDeleteMessage"
    @read-aloud="handleReadAloud"
    @switch-greeting="handleSwitchGreeting"
    @open-assistant="isAssistantOpen = true"
    @open-branch-canvas="isCanvasModalOpen = true"
    @open-branch-drawer="isBranchDrawerOpen = true"
    @open-narrative-panel="() => { isNarrativePanelOpen = true; loadNarrativeState(); }"
    @open-control-panel="() => { isControlPanelOpen = true; loadControlPanel(); }"
    @open-model-selector="isModelDrawerOpen = true"
    @open-mod-manager="isModDrawerOpen = true"
    @settings-action="handleSettingsAction"
  />

  <!-- 2. 移动端视口 (< 768px): 保持基准 440px 手机原生手势与气泡布局 (仅中间消息区内部滚动) -->
  <div
    v-else
    class="flex flex-col h-full max-h-full w-full max-w-[440px] mx-auto text-[#F5F5F4] relative shadow-2xl overflow-hidden bg-[#0F0D0C] select-none"
  >
    
    <!-- 1. 全屏沉浸式角色立绘大背景 (动态绑定角色封面/立绘 + 暗黑磨砂渐变遮罩) -->
    <div
      v-if="character.backgroundUrl || character.avatarUrl"
      class="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat pointer-events-none transition-all duration-700 opacity-80"
      :style="{ backgroundImage: `url('${character.backgroundUrl || character.avatarUrl}')` }"
    />
    <!-- 渐变暗黑磨砂玻璃蒙层 -->
    <div class="absolute inset-0 z-0 bg-gradient-to-b from-black/40 via-[#1A1511]/70 to-[#0F0D0C]/90 backdrop-blur-[2px] pointer-events-none" />

    <!-- 2. 顶部 Header (固定在顶部，不参与页面滚动) -->
    <div class="relative z-20 shrink-0">
      <ChatHeader
        @back="handleBack"
        @open-sidebar="isSidebarOpen = true"
        @open-music="isBgmOpen = true"
        @open-assistant="isAssistantOpen = true"
        @open-narrative-panel="() => { isNarrativePanelOpen = true; loadNarrativeState(); }"
        @open-worldbook="isWorldBookOpen = true"
        @open-canvas="isCanvasModalOpen = true"
        @open-apps="() => { isControlPanelOpen = true; loadControlPanel(); }"
        @open-control-panel="() => { isControlPanelOpen = true; loadControlPanel(); }"
        @settings-action="handleSettingsAction"
      />
    </div>

    <!-- 3. 中间消息滚动列表 (自适应剩余视口空间，仅内部独立滚动) -->
    <div class="relative z-10 flex-1 min-h-0 overflow-hidden flex flex-col w-full">
      <ChatChatMessageList
        :messages="messages"
        :author-note="character.authorNote"
        :prologue-title="character.prologueTitle"
        :prologue-content="character.prologueContent"
        :alternate-greetings="alternateGreetings"
        :current-greeting-index="currentGreetingIndex"
        @switch-greeting="handleSwitchGreeting"
        @read-aloud="handleReadAloud"
        @regenerate="handleRegenerate"
        @rerun-memory="() => showToast('正在重跑记忆增强 RAG 索引...')"
        @continue="() => showToast('已触发 500 字剧情续写')"
        @branch="handleBranch"
        @edit="handleEditMessage"
        @save-edit="handleSaveEditMessage"
        @share="() => showToast('消息链接已复制到剪贴板')"
        @delete="handleDeleteMessage"
      />
    </div>

    <!-- 4. 底部悬浮控制区 (固定在底部，不参与页面滚动) -->
    <div class="relative z-20 w-full px-4 pb-7 pt-1 flex flex-col gap-2 bg-transparent shrink-0">
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
        :opening-replies="openingReplies"
        @send="handleSendMessage"
        @stop="handleStopGeneration"
        @ai-assist="() => showToast('✦ AI 灵感辅助已启动')"
        @more-action="handleMoreAction"
      />
    </div>

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
      :control-panel="controlPanel"
      @save="saveControlPanel"
    />

    <!-- 10. 叙梦面板/聊天信息面板抽屉 (1:1 Figma 原型 Frame 83:6511) -->
    <NarrativePanelDrawer
      v-model:open="isNarrativePanelOpen"
      :session-id="sessionId"
      :narrative-state="narrativeState"
      @save="saveNarrativeState"
    />

    <!-- 10.5 世界书设定集抽屉 (Phase 6 RAG 引擎) -->
    <WorldBookDrawer
      v-model:open="isWorldBookOpen"
      :character-id="characterId"
      :character-name="character.name"
    />

    <!-- 10.6 Mod 优先级矩阵与扩展管理器抽屉 (Phase 7) -->
    <ModManagerDrawer
      v-model:open="isModDrawerOpen"
    />

    <!-- 10.7 BGM 场景氛围音律抽屉 (Phase 9) -->
    <BgmPlayerDrawer
      :is-open="isBgmOpen"
      :character-bgm-url="bgmUrl"
      :character-name="character.name"
      @close="isBgmOpen = false"
    />

    <!-- 11. 剧情分支与时间线抽屉 (方案 1: 黑金折叠时间轴抽屉) -->
    <StoryBranchDrawer
      v-model:open="isBranchDrawerOpen"
      :current-branch-id="currentBranchId"
      :branches="branches"
      :current-message-id="selectedForkMessageId"
      :messages="messages"
      @switch-branch="handleSwitchBranch"
      @create-branch="handleCreateBranch"
      @delete-branch="handleDeleteBranch"
      @jump-to-node="handleRollback"
      @rollback="handleRollback"
      @open-canvas="isCanvasModalOpen = true"
    />

    <!-- 12. 全景剧情树拓扑图画布 (方案 2: Vue Flow 全景图) -->
    <StoryBranchCanvasModal
      v-model:open="isCanvasModalOpen"
      :session-id="sessionId"
      :current-branch-id="currentBranchId"
      @switch-branch="handleSwitchBranch"
      @fork-branch="handleCreateBranch"
      @rollback="handleRollback"
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
