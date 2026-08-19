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
import FloatingMascotBadge from "@/views/chat/components/FloatingMascotBadge.vue";
import ModelSelectorDrawer from "@/views/chat/components/ModelSelectorDrawer.vue";
import { useChatSession } from "@/views/chat/composables/useChatSession";
import { ref } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const characterId = (route.params.id as string) || "c1";

const isSidebarOpen = ref(false);

const {
  character,
  messages,
  currentModel,
  currentMode,
  isGenerating,
  isModelDrawerOpen,
  toastMessage,
  handleBack,
  handleSendMessage,
  handleRegenerate,
  handleBranch,
  handleEditMessage,
  handleDeleteMessage,
  handleReadAloud,
  handleSelectModel,
  handleSwitchMode,
} = useChatSession(characterId);
</script>

<template>
  <div class="flex flex-col h-screen w-full max-w-[440px] mx-auto text-[#F5F5F4] relative shadow-2xl overflow-hidden bg-[#0F0D0C]">
    
    <!-- 1. 全屏沉浸式角色立绘大背景 (炭治郎插画 + 暗黑磨砂渐变遮罩) -->
    <div
      class="absolute inset-0 z-0 bg-cover bg-center bg-no-repeat pointer-events-none"
      :style="{ backgroundImage: `url('https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&auto=format&fit=crop&q=80')` }"
    />
    <!-- 渐变暗黑磨砂玻璃蒙层 -->
    <div class="absolute inset-0 z-0 bg-gradient-to-b from-black/40 via-[#1A1511]/70 to-[#0F0D0C]/90 backdrop-blur-[2px] pointer-events-none" />

    <!-- 2. 顶部 Header (左侧返回/侧边栏 + 右侧 5 个霓虹功能按钮) -->
    <div class="relative z-20">
      <ChatHeader
        @back="handleBack"
        @open-sidebar="isSidebarOpen = true"
        @open-music="() => {}"
        @open-worldbook="() => {}"
        @open-canvas="() => {}"
        @open-apps="() => {}"
        @open-settings="() => {}"
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
        @branch="handleBranch"
        @edit="handleEditMessage"
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
        :disabled="isGenerating"
        @send="handleSendMessage"
        @ai-assist="() => {}"
        @expand="() => {}"
        @plus="() => {}"
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

    <!-- 8. 轻量浮动 Toast 反馈 -->
    <div
      v-if="toastMessage"
      class="fixed top-12 left-1/2 -translate-x-1/2 z-50 px-4 py-1.5 rounded-full bg-[#F9C86D] text-[#0C0A09] font-medium text-xs shadow-2xl animate-fade-in pointer-events-none"
    >
      {{ toastMessage }}
    </div>

  </div>
</template>
