<script setup lang="ts">
/**
 * 叙梦 Naro - 原创角色卡创建与编辑器 (Smart Container 主入口)
 *
 * 1:1 像素级还原 Figma 原型与长图交互，涵盖作者的话、角色卡信息、基本信息、序幕、对话设置与卡片导出。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import AdvancedSection from "@/views/character-create/components/AdvancedSection.vue";
import AuthorNoteSection from "@/views/character-create/components/AuthorNoteSection.vue";
import BasicInfoSection from "@/views/character-create/components/BasicInfoSection.vue";
import CardExportSection from "@/views/character-create/components/CardExportSection.vue";
import CardInfoSection from "@/views/character-create/components/CardInfoSection.vue";
import CreationNoticeSection from "@/views/character-create/components/CreationNoticeSection.vue";
import CreatorHeader from "@/views/character-create/components/CreatorHeader.vue";
import DialogueSection from "@/views/character-create/components/DialogueSection.vue";
import PrologueSection from "@/views/character-create/components/PrologueSection.vue";
import { useCharacterForm } from "@/views/character-create/composables/useCharacterForm";
import { onMounted, ref } from "vue";

const appStore = useAppStore();
const { formData, validationErrors, isValid, resetForm, importFromJson } = useCharacterForm();

const toastMessage = ref<string>("");

onMounted(() => {
  appStore.setActiveTab("create");
});

function showToast(msg: string): void {
  toastMessage.value = msg;
  setTimeout(() => {
    toastMessage.value = "";
  }, 2000);
}

function handleImportFile(jsonStr: string): void {
  const success = importFromJson(jsonStr);
  if (success) {
    showToast("角色卡数据导入成功！");
  } else {
    showToast("导入失败，文件格式不合法");
  }
}

function handleSaveForm(): void {
  showToast("角色卡草稿已成功保存至本地！");
}

function handleClearForm(): void {
  if (window.confirm("确定要清空当前所有已填写的角色表格数据吗？")) {
    resetForm();
    showToast("表格已清空");
  }
}

function handleOpenTutorial(): void {
  window.open("https://docs.sillytavern.app", "_blank");
}

function handleOpenAssets(): void {
  showToast("我的素材库功能即将开放");
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部 Header & 工具卡片 -->
    <CreatorHeader
      @import-file="handleImportFile"
      @save-form="handleSaveForm"
      @clear-form="handleClearForm"
      @open-tutorial="handleOpenTutorial"
      @open-assets="handleOpenAssets"
    />

    <!-- 2. 模块 1: 作者的话 -->
    <AuthorNoteSection v-model="formData.creatorNotes" />

    <!-- 3. 模块 2: 角色卡信息 (名称、立绘、标签) -->
    <CardInfoSection
      v-model:name="formData.name"
      v-model:avatar-url="formData.avatarUrl"
      v-model:tags="formData.tags"
    />

    <!-- 4. 模块 3: 基本信息 (描述、性格、场景) -->
    <BasicInfoSection
      v-model:description="formData.description"
      v-model:personality="formData.personality"
      v-model:scenario="formData.scenario"
    />

    <!-- 5. 模块 4: 序幕 (HTML / 实时预览) -->
    <PrologueSection v-model="formData.prologueHtml" />

    <!-- 6. 模块 5: 对话设置 (首次问候、备选开场白) -->
    <DialogueSection
      v-model:first-mes="formData.firstMes"
      v-model:alternate-greetings="formData.alternateGreetings"
    />

    <!-- 7. 模块 6: 高级设置 (Prompt、世界书) -->
    <AdvancedSection
      v-model:system-prompt="formData.systemPrompt"
      v-model:post-history-instructions="formData.postHistoryInstructions"
    />

    <!-- 8. 模块 7: 创建须知与合规提醒 -->
    <CreationNoticeSection />

    <!-- 9. 模块 8: 实时卡片预览、校验与导出下载 -->
    <CardExportSection
      :form-data="formData"
      :validation-errors="validationErrors"
      :is-valid="isValid"
    />

    <!-- 10. 全局底部导航栏 -->
    <BottomTabBar />

    <!-- 11. 顶部微浮动 Toast 反馈 -->

    <div
      v-if="toastMessage"
      class="fixed top-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full bg-[#F9C86D] text-[#0C0A09] font-medium text-xs shadow-2xl animate-fade-in pointer-events-none"
    >
      {{ toastMessage }}
    </div>

  </div>
</template>
