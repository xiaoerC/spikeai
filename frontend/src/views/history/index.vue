<script setup lang="ts">
/**
 * 叙梦 Naro - 个人历史记录 (Smart Container 主入口)
 *
 * 1:1 像素级还原个人历史记录页面，展示 4 大分类胶囊、云端备份、批量删除、卡片 5 大悬浮快捷操作。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import UserHistoryBatchBar from "@/views/history/components/UserHistoryBatchBar.vue";
import UserHistoryCardGrid from "@/views/history/components/UserHistoryCardGrid.vue";
import UserHistoryCategoryTabs from "@/views/history/components/UserHistoryCategoryTabs.vue";
import UserHistoryHeader from "@/views/history/components/UserHistoryHeader.vue";
import UserHistoryRemarkModal from "@/views/history/components/UserHistoryRemarkModal.vue";
import UserHistoryToolbar from "@/views/history/components/UserHistoryToolbar.vue";
import { useUserHistory } from "@/views/history/composables/useUserHistory";
import type { UserHistoryItem } from "@/views/history/types";
import LoginModal from "@/views/login/components/LoginModal.vue";
import { useRouter } from "vue-router";

const router = useRouter();
const appStore = useAppStore();
const {
  historyList,
  currentCategory,
  storyCount,
  tavernCount,
  customCount,
  moduleCount,
  isBatchMode,
  selectedIds,
  editingRemarkItem,
  isRemarkModalOpen,
  toastMessage,
  setCategory,
  toggleBatchMode,
  toggleSelectItem,
  togglePin,
  clearChatHistory,
  deleteHistory,
  batchDeleteSelected,
  updateCharacterCard,
  openRemarkModal,
  saveRemark,
  triggerCloudBackup,
} = useUserHistory();

function handleSelectCard(item: UserHistoryItem) {
  router.push(`/chat/${item.characterId}`);
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <main class="w-full max-w-[440px] mx-auto px-4 pb-28 flex flex-col flex-1">
      <!-- 1. 顶部 Header (大标题 "历史记录" + "云端备份" 金边按钮) -->
      <UserHistoryHeader @backup="triggerCloudBackup" />

      <!-- 2. 4 大分类切换胶囊 (📖 4 / 🏪 / ⚙️ / 🧩) -->
      <UserHistoryCategoryTabs
        :current-category="currentCategory"
        :story-count="storyCount"
        :tavern-count="tavernCount"
        :custom-count="customCount"
        :module-count="moduleCount"
        @select-category="setCategory"
      />

      <!-- 3. 操作工具栏 (宫格切换 + 批量删除按钮) -->
      <UserHistoryToolbar
        :is-batch-mode="isBatchMode"
        @toggle-batch="toggleBatchMode"
      />

      <!-- 4. 2 列个人历史角色卡片瀑布流 -->
      <div class="mt-3">
        <UserHistoryCardGrid
          v-if="historyList.length > 0"
          :history-list="historyList"
          :is-batch-mode="isBatchMode"
          :selected-ids="selectedIds"
          @select-card="handleSelectCard"
          @toggle-select="toggleSelectItem"
          @remark="openRemarkModal"
          @update-card="updateCharacterCard"
          @pin="togglePin"
          @clear="clearChatHistory"
          @delete="deleteHistory"
        />

        <!-- 空状态 -->
        <div
          v-else
          class="flex flex-col items-center justify-center py-20 text-center"
        >
          <div class="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center mb-3">
            <span class="text-2xl">📜</span>
          </div>
          <p class="text-sm text-[#A8A29E] font-medium">暂无该分类的对话历史</p>
          <p class="text-xs text-[#78716C] mt-1">去探索角色开始沉浸互动吧</p>
        </div>
      </div>
    </main>

    <!-- 5. 批量删除底部悬浮栏 -->
    <UserHistoryBatchBar
      v-if="isBatchMode"
      :selected-count="selectedIds.size"
      @cancel="toggleBatchMode"
      @delete="batchDeleteSelected"
    />

    <!-- 6. 编辑备注弹窗 -->
    <UserHistoryRemarkModal
      v-model:open="isRemarkModalOpen"
      :item="editingRemarkItem"
      @save="saveRemark"
    />

    <!-- 7. 悬浮操作 Toast 提示 -->
    <div
      v-if="toastMessage"
      class="fixed top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full bg-[#F9C86D] text-[#0C0A09] text-xs font-bold shadow-2xl animate-in fade-in zoom-in-95 duration-200"
    >
      {{ toastMessage }}
    </div>

    <!-- 8. 右下角 🐦 悬浮反馈球 -->
    <button
      type="button"
      class="fixed right-5 bottom-20 z-30 w-12 h-12 rounded-full flex items-center justify-center bg-[#292524] border-2 border-[#F9C86D] shadow-[0_4px_16px_rgba(0,0,0,0.20),0_0_0_3px_rgba(249,200,109,0.15)] active:scale-95 transition-all cursor-pointer select-none"
    >
      <span class="text-xl text-[#C0A480]">🐦</span>
    </button>

    <!-- 9. 全局底部 5-Tab Bar (高亮第 2 个 Tab) -->
    <BottomTabBar />

    <!-- 10. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
