<script setup lang="ts">
/**
 * 叙梦 Naro - 帮助中心 / 新手指南 & FAQ (Smart Container 主入口)
 *
 * 1:1 像素级还原帮助中心官方文档页面，包含 6 大步骤新手教程、FAQ 常见问题与官方指令集。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import HelpCommandList from "@/views/help/components/HelpCommandList.vue";
import HelpFaqList from "@/views/help/components/HelpFaqList.vue";
import HelpHeader from "@/views/help/components/HelpHeader.vue";
import HelpStepItem from "@/views/help/components/HelpStepItem.vue";
import { useHelpCenter } from "@/views/help/composables/useHelpCenter";
import LoginModal from "@/views/login/components/LoginModal.vue";

const appStore = useAppStore();
const {
  currentTab,
  guideSteps,
  faqs,
  commands,
  expandedFaqIds,
  copyToastMessage,
  setTab,
  toggleFaq,
  copyCommand,
} = useHelpCenter();
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部 Header 与 3 分类 Tabs -->
    <HelpHeader
      :current-tab="currentTab"
      @change-tab="setTab"
    />

    <!-- 2. 主内容区 -->
    <main class="w-full max-w-[440px] mx-auto px-3.5 pt-3 pb-24 flex flex-col gap-3.5">
      <!-- 新手指南 Tab -->
      <template v-if="currentTab === 'guide'">
        <HelpStepItem
          v-for="step in guideSteps"
          :key="step.id"
          :step="step"
          @copy="copyCommand"
        />
      </template>

      <!-- FAQ 常见问题 Tab -->
      <template v-else-if="currentTab === 'faq'">
        <HelpFaqList
          :faqs="faqs"
          :expanded-faq-ids="expandedFaqIds"
          @toggle-faq="toggleFaq"
        />
      </template>

      <!-- 官方指令集 Tab -->
      <template v-else>
        <HelpCommandList
          :commands="commands"
          @copy="copyCommand"
        />
      </template>
    </main>

    <!-- 3. 复制 Toast 提示 -->
    <div
      v-if="copyToastMessage"
      class="fixed top-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full bg-[#F9C86D] text-[#0C0A09] text-xs font-bold shadow-xl animate-in fade-in zoom-in-95 duration-200"
    >
      {{ copyToastMessage }}
    </div>

    <!-- 4. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 5. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
