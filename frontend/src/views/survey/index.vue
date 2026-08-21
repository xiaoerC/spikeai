<script setup lang="ts">
/**
 * 叙梦 Naro - 问卷调查 (Smart Container 主入口)
 *
 * 1:1 像素级还原问卷调查页面，展示问卷列表/我的记录 Tabs、高保真空状态与右下角 🐦 悬浮反馈球。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import LoginModal from "@/views/login/components/LoginModal.vue";
import SurveyEmptyState from "@/views/survey/components/SurveyEmptyState.vue";
import SurveyFloatingButton from "@/views/survey/components/SurveyFloatingButton.vue";
import SurveyHeader from "@/views/survey/components/SurveyHeader.vue";
import SurveyTabs from "@/views/survey/components/SurveyTabs.vue";
import { useSurveyList } from "@/views/survey/composables/useSurveyList";

const appStore = useAppStore();
const { activeTab, activeSurveys, surveyRecords, setActiveTab } = useSurveyList();

function handleFeedbackClick() {
  // 可提示或唤起 Discord 社区
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部 Header 与奖励介绍 -->
    <SurveyHeader />

    <!-- 2. 分类切换 Tabs (问卷列表 / 我的记录) -->
    <main class="w-full max-w-[440px] mx-auto flex flex-col flex-1 pb-24">
      <SurveyTabs
        :active-tab="activeTab"
        @change-tab="setActiveTab"
      />

      <!-- Tab 内容区 -->
      <div class="px-4 py-2">
        <!-- 问卷列表 Tab -->
        <template v-if="activeTab === 'list'">
          <div v-if="activeSurveys.length === 0">
            <SurveyEmptyState text="目前暂无可参与的问卷" />
          </div>
          <div v-else class="flex flex-col gap-3">
            <!-- 问卷列表渲染 -->
          </div>
        </template>

        <!-- 我的记录 Tab -->
        <template v-else>
          <div v-if="surveyRecords.length === 0">
            <SurveyEmptyState text="暂无已完成的问卷记录" />
          </div>
          <div v-else class="flex flex-col gap-3 pt-2">
            <div
              v-for="rec in surveyRecords"
              :key="rec.id"
              class="p-4 rounded-xl bg-[rgba(26,21,16,0.85)] border border-white/5 flex flex-col gap-2 shadow-md"
            >
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold text-[#F5F5F4]">{{ rec.title }}</span>
                <span class="px-2 py-0.5 rounded-full bg-[#F9C86D]/15 text-[#F9C86D] text-xs font-bold">+{{ rec.rewardCoins }} 星元</span>
              </div>
              <p class="text-xs text-[#A8A29E]">{{ rec.description }}</p>
              <div class="flex items-center justify-between text-[11px] text-[#78716C] pt-2 border-t border-white/5">
                <span>完成时间：{{ rec.completedAt }}</span>
                <span class="text-emerald-400 font-medium">已发放</span>
              </div>
            </div>
          </div>
        </template>
      </div>
    </main>

    <!-- 3. 右下角 🐦 悬浮反馈按钮 -->
    <SurveyFloatingButton @click="handleFeedbackClick" />

    <!-- 4. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 5. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
