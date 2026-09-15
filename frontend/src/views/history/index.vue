<script setup lang="ts">
/**
 * 叙梦 Naro - 个人历史记录 (Smart Container 主入口)
 *
 * 1:1 像素级还原个人历史记录页面，支持宫格/列表排版切换、4 大分类胶囊、我的上传记录、自定义设置 (人设/指令/画师串/总结提示词/记忆增强模型)、Mod模组中心 (广场/我创作的/我购买的/合集/Mod设置优先级排序)、新建/编辑Mod、合集管理与预览、云端备份、批量删除、卡片 5 大悬浮快捷操作。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import type { CharacterDetail } from "@/services/character";
import { useAppStore } from "@/stores/app";
import ArtistEditModal from "@/views/history/components/ArtistEditModal.vue";
import ArtistListSection from "@/views/history/components/ArtistListSection.vue";
import CollectionEditModal from "@/views/history/components/CollectionEditModal.vue";
import CollectionPreviewModal from "@/views/history/components/CollectionPreviewModal.vue";
import CommandEditModal from "@/views/history/components/CommandEditModal.vue";
import CommandListSection from "@/views/history/components/CommandListSection.vue";
import CustomSettingsSubTabs from "@/views/history/components/CustomSettingsSubTabs.vue";
import MemoryModelSection from "@/views/history/components/MemoryModelSection.vue";
import ModCardList from "@/views/history/components/ModCardList.vue";
import ModCategorySubTabs from "@/views/history/components/ModCategorySubTabs.vue";
import ModCollectionSection from "@/views/history/components/ModCollectionSection.vue";
import ModEditModal from "@/views/history/components/ModEditModal.vue";
import ModSettingsSection from "@/views/history/components/ModSettingsSection.vue";
import ModToolbar from "@/views/history/components/ModToolbar.vue";
import MyCreatedModSection from "@/views/history/components/MyCreatedModSection.vue";
import MyPurchasedModSection from "@/views/history/components/MyPurchasedModSection.vue";
import MyUploadedCharacterSection from "@/views/history/components/MyUploadedCharacterSection.vue";
import PersonaEditModal from "@/views/history/components/PersonaEditModal.vue";
import PersonaListSection from "@/views/history/components/PersonaListSection.vue";
import SummaryPromptSection from "@/views/history/components/SummaryPromptSection.vue";
import UploadCategorySubTabs from "@/views/history/components/UploadCategorySubTabs.vue";
import UploadHistoryEmptyPanel from "@/views/history/components/UploadHistoryEmptyPanel.vue";
import UserHistoryBatchBar from "@/views/history/components/UserHistoryBatchBar.vue";
import UserHistoryCardGrid from "@/views/history/components/UserHistoryCardGrid.vue";
import UserHistoryCardList from "@/views/history/components/UserHistoryCardList.vue";
import UserHistoryCategoryTabs from "@/views/history/components/UserHistoryCategoryTabs.vue";
import UserHistoryHeader from "@/views/history/components/UserHistoryHeader.vue";
import UserHistoryRemarkModal from "@/views/history/components/UserHistoryRemarkModal.vue";
import UserHistoryToolbar from "@/views/history/components/UserHistoryToolbar.vue";
import { useUserHistory } from "@/views/history/composables/useUserHistory";
import type { ModCollectionItem, UserHistoryItem } from "@/views/history/types";
import LoginModal from "@/views/login/components/LoginModal.vue";
import { useRouter } from "vue-router";

const router = useRouter();
const appStore = useAppStore();
const {
  historyList,
  currentCategory,
  uploadSubCategory,
  customSubCategory,
  modSubCategory,
  collectionSubTab,
  modSearchQuery,
  modSort,
  modTag,
  modList,
  myCreatedModList,
  purchasedModList,
  activeModsList,
  myCollectionList,
  publicCollectionList,
  isModEditModalOpen,
  editingCreatedMod,
  isCollectionModalOpen,
  editingCollection,
  isCollectionPreviewOpen,
  previewingCollection,
  viewMode,
  storyCount,
  tavernCount,
  customCount,
  moduleCount,
  isBatchMode,
  selectedIds,
  editingRemarkItem,
  isRemarkModalOpen,
  personaList,
  isPersonaModalOpen,
  editingPersona,
  commandList,
  isCommandModalOpen,
  editingCommand,
  artistList,
  isArtistModalOpen,
  editingArtist,
  summaryModel,
  summaryPrompt,
  memoryEnhanceModel,
  toastMessage,
  setCategory,
  setUploadSubCategory,
  setCustomSubCategory,
  setModSubCategory,
  setCollectionSubTab,
  setModSort,
  setModTag,
  buyMod,
  togglePurchasedModActive,
  deletePurchasedMod,
  moveActiveMod,
  deactivateMod,
  openCreateModModal,
  openEditCreatedModModal,
  saveCreatedMod,
  publishCreatedMod,
  deleteCreatedMod,
  openCreateCollectionModal,
  openEditCollectionModal,
  openPreviewCollectionModal,
  saveCollection,
  deleteCollection,
  shareCollection,
  toggleViewMode,
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
  claimRewards,
  uploadToCommunity,
  openCreatePersonaModal,
  openEditPersonaModal,
  savePersona,
  deletePersona,
  setDefaultPersona,
  openCreateCommandModal,
  openEditCommandModal,
  saveCommand,
  deleteCommand,
  moveCommand,
  saveCommandOrder,
  openCreateArtistModal,
  openEditArtistModal,
  saveArtist,
  deleteArtist,
  setActiveArtist,
  saveSummarySettings,
  resetSummarySettings,
  saveMemoryModel,
  resetMemoryModel,
  myUploadedCharacters,
  filteredMyUploadedCharacters,
  isLoadingMyCharacters,
  fetchMyCharacters,
  toggleCharacterStatus,
  deleteUploadedCharacter,
} = useUserHistory();

function handleSelectCard(item: UserHistoryItem) {
  router.push({
    path: `/chat/${item.characterId}`,
    query: { session_id: item.id },
  });
}

function handleCreateCharacter() {
  router.push("/create");
}

function handleEditCharacter(char: CharacterDetail) {
  router.push(`/create?edit_id=${char.id}`);
}

function handleChatCharacter(char: CharacterDetail) {
  router.push(`/chat/${char.id}`);
}

function handleApplyCollection(coll: ModCollectionItem) {
  for (const m of coll.mods) {
    const existing = purchasedModList.value.find((p) => p.title === m.title);
    if (existing) {
      existing.isActive = true;
    } else {
      purchasedModList.value.unshift({
        id: `purchased-${Date.now()}-${m.id}`,
        title: m.title,
        description: m.description,
        isActive: true,
        createdAt: new Date().toLocaleDateString(),
      });
    }
  }
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <main class="w-full max-w-[440px] mx-auto pb-28 flex flex-col flex-1 px-4">
      <!-- 1. 顶部 Header (大标题 "历史记录" + 动态右侧操作区) -->
      <UserHistoryHeader
        :current-category="currentCategory"
        @backup="triggerCloudBackup"
        @claim-rewards="claimRewards"
        @upload-community="uploadToCommunity"
        @create-character="handleCreateCharacter"
      />

      <!-- 2. 4 大分类切换胶囊 (📖 4 / 🏪 / ⚙️ / 🧩 10) -->
      <UserHistoryCategoryTabs
        :current-category="currentCategory"
        :story-count="storyCount"
        :tavern-count="tavernCount"
        :custom-count="customCount"
        :module-count="moduleCount"
        @select-category="setCategory"
      />

      <!-- 3. 条件分支 A: 当处于【⚙️ 自定义/设置】时渲染二级设置导航与子功能面板 -->
      <template v-if="currentCategory === 'custom'">
        <!-- 二级导航 (👤人设 / ⌨️指令 / 🎨画师串 / 📝总结提示词 / 🤖记忆增强模型) -->
        <CustomSettingsSubTabs
          :active-sub-category="customSubCategory"
          @select-sub="setCustomSubCategory"
        />

        <!-- ① 👤 人设管理功能面板 -->
        <PersonaListSection
          v-if="customSubCategory === 'persona'"
          :persona-list="personaList"
          @create="openCreatePersonaModal"
          @edit="openEditPersonaModal"
          @delete="deletePersona"
          @set-default="setDefaultPersona"
        />

        <!-- ② ⌨️ 指令管理功能面板 (Figma 81:2925) -->
        <CommandListSection
          v-else-if="customSubCategory === 'command'"
          :command-list="commandList"
          @create="openCreateCommandModal"
          @edit="openEditCommandModal"
          @delete="deleteCommand"
          @move="moveCommand"
          @save-order="saveCommandOrder"
        />

        <!-- ③ 🎨 画师串管理功能面板 (Figma 84:6799) -->
        <ArtistListSection
          v-else-if="customSubCategory === 'artist'"
          :artist-list="artistList"
          @create="openCreateArtistModal"
          @edit="openEditArtistModal"
          @delete="deleteArtist"
          @set-active="setActiveArtist"
        />

        <!-- ④ 📝 总结提示词功能面板 (Figma 86:8397) -->
        <SummaryPromptSection
          v-else-if="customSubCategory === 'summary'"
          :model="summaryModel"
          :prompt="summaryPrompt"
          @save="saveSummarySettings"
          @reset="resetSummarySettings"
        />

        <!-- ⑤ 🤖 AI 记忆增强模型功能面板 (Figma 90:1083) -->
        <MemoryModelSection
          v-else-if="customSubCategory === 'memory'"
          :model="memoryEnhanceModel"
          @save="saveMemoryModel"
          @reset="resetMemoryModel"
        />
      </template>

      <!-- 4. 条件分支 B: 当处于【🏪 我的上传记录】时渲染二级分类与我的上传角色管理面板 -->
      <template v-else-if="currentCategory === 'tavern'">
        <!-- 二级卡片分类 (📖 剧情卡 / ⚡ 绅士卡) -->
        <UploadCategorySubTabs
          :active-sub-category="uploadSubCategory"
          @select-sub="setUploadSubCategory"
        />

        <!-- 我的上传角色卡管理面板 -->
        <MyUploadedCharacterSection
          :characters="filteredMyUploadedCharacters"
          :is-loading="isLoadingMyCharacters"
          @edit="handleEditCharacter"
          @toggle-status="toggleCharacterStatus"
          @delete="deleteUploadedCharacter"
          @chat="handleChatCharacter"
        />
      </template>

      <!-- 5. 条件分支 C: 当处于【🧩 模组/Mod】时渲染 Mod 广场体系 (Figma 93:3270 / 106:8347 / 106:8718 / 109:12064 / 111:13235) -->
      <template v-else-if="currentCategory === 'module'">
        <!-- Mod 二级分类横向滑动栏 (🧩广场 / 🎨我创作的 / 🛍️我购买的 / 📦合集 / ⚙️Mod设置) -->
        <ModCategorySubTabs
          :active-sub-category="modSubCategory"
          @select-sub="setModSubCategory"
        />

        <!-- ① 🎨 我创作的 Mod 面板 (Figma 106:8347) -->
        <MyCreatedModSection
          v-if="modSubCategory === 'created'"
          :created-mod-list="myCreatedModList"
          @create="openCreateModModal"
          @edit="openEditCreatedModModal"
          @publish="publishCreatedMod"
          @delete="deleteCreatedMod"
        />

        <!-- ② 🛍️ 我购买的 Mod 面板 (Figma 106:8718) -->
        <MyPurchasedModSection
          v-else-if="modSubCategory === 'purchased'"
          :purchased-mod-list="purchasedModList"
          @toggle-active="togglePurchasedModActive"
          @delete="deletePurchasedMod"
        />

        <!-- ③ 📦 合集 面板 (Figma 109:12064) -->
        <ModCollectionSection
          v-else-if="modSubCategory === 'collection'"
          :active-sub-tab="collectionSubTab"
          :my-collection-list="myCollectionList"
          :public-collection-list="publicCollectionList"
          @select-sub-tab="setCollectionSubTab"
          @create="openCreateCollectionModal"
          @edit="openEditCollectionModal"
          @preview="openPreviewCollectionModal"
          @share="shareCollection"
          @delete="deleteCollection"
        />

        <!-- ④ ⚙️ Mod 设置与优先级排序面板 (Figma 111:13235) -->
        <ModSettingsSection
          v-else-if="modSubCategory === 'settings'"
          :active-mods-list="activeModsList"
          @move="moveActiveMod"
          @deactivate="deactivateMod"
        />

        <!-- ⑤ 🧩 广场 面板 (Figma 93:3270) -->
        <template v-else-if="modSubCategory === 'square'">
          <!-- Mod 搜索与双层分类筛选胶囊栏 -->
          <ModToolbar
            v-model:search-query="modSearchQuery"
            :active-sort="modSort"
            :active-tag="modTag"
            @select-sort="setModSort"
            @select-tag="setModTag"
          />

          <!-- Mod 卡片流列表 (包含 7 大 Mod 及购买状态机) -->
          <ModCardList
            :mod-list="modList"
            @buy="buyMod"
          />
        </template>
      </template>

      <!-- 6. 条件分支 D: 当处于【📖 主线历史】时渲染工具栏与卡片瀑布流 -->
      <template v-else>
        <!-- 操作工具栏 (宫格/列表排版切换 + 批量删除按钮) -->
        <UserHistoryToolbar
          :view-mode="viewMode"
          :is-batch-mode="isBatchMode"
          @toggle-view="toggleViewMode"
          @toggle-batch="toggleBatchMode"
        />

        <!-- 个人历史卡片区 (列表模式 / 宫格模式 自由切换) -->
        <div class="mt-1">
          <!-- 列表排版视图 -->
          <UserHistoryCardList
            v-if="historyList.length > 0 && viewMode === 'list'"
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

          <!-- 宫格排版视图 -->
          <div v-else-if="historyList.length > 0 && viewMode === 'grid'" class="pt-3">
            <UserHistoryCardGrid
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
          </div>

          <!-- 空状态 -->
          <div
            v-else
            class="flex flex-col items-center justify-center py-20 text-center px-4"
          >
            <div class="w-14 h-14 rounded-full bg-white/5 flex items-center justify-center mb-3">
              <span class="text-2xl">📜</span>
            </div>
            <p class="text-sm text-[#A8A29E] font-medium">暂无该分类的对话历史</p>
            <p class="text-xs text-[#78716C] mt-1">去探索角色开始沉浸互动吧</p>
          </div>
        </div>
      </template>
    </main>

    <!-- 7. 批量删除底部悬浮栏 -->
    <UserHistoryBatchBar
      v-if="isBatchMode"
      :selected-count="selectedIds.size"
      @cancel="toggleBatchMode"
      @delete="batchDeleteSelected"
    />

    <!-- 8. 编辑备注弹窗 -->
    <UserHistoryRemarkModal
      v-model:open="isRemarkModalOpen"
      :item="editingRemarkItem"
      @save="saveRemark"
    />

    <!-- 9. 新建/编辑人设 1:1 弹窗 -->
    <PersonaEditModal
      v-model:open="isPersonaModalOpen"
      :persona="editingPersona"
      @save="savePersona"
    />

    <!-- 10. 新建/编辑指令 1:1 弹框 -->
    <CommandEditModal
      v-model:open="isCommandModalOpen"
      :command="editingCommand"
      @save="saveCommand"
    />

    <!-- 11. 新建/编辑画师串 1:1 弹框 (Figma 84:7007) -->
    <ArtistEditModal
      v-model:open="isArtistModalOpen"
      :artist="editingArtist"
      @save="saveArtist"
    />

    <!-- 12. 新建/编辑 Mod 1:1 弹框 (Figma 106:8552) -->
    <ModEditModal
      v-model:open="isModEditModalOpen"
      :mod="editingCreatedMod"
      @save="saveCreatedMod"
    />

    <!-- 13. 新建/编辑合集 1:1 弹框 (Figma 109:11681) -->
    <CollectionEditModal
      v-model:open="isCollectionModalOpen"
      :collection="editingCollection"
      :all-purchased-mods="purchasedModList"
      @save="saveCollection"
    />

    <!-- 14. 预览合集 1:1 弹框 -->
    <CollectionPreviewModal
      v-model:open="isCollectionPreviewOpen"
      :collection="previewingCollection"
      @apply="handleApplyCollection"
    />

    <!-- 15. 悬浮操作 Toast 提示 -->
    <div
      v-if="toastMessage"
      class="fixed top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full bg-[#F9C86D] text-[#0C0A09] text-xs font-bold shadow-2xl animate-in fade-in zoom-in-95 duration-200"
    >
      {{ toastMessage }}
    </div>

    <!-- 16. 右下角 🐦 悬浮反馈球 -->
    <button
      type="button"
      class="fixed right-5 bottom-20 z-30 w-12 h-12 rounded-full flex items-center justify-center bg-[#292524] border-2 border-[#F9C86D] shadow-[0_4px_16px_rgba(0,0,0,0.20),0_0_0_3px_rgba(249,200,109,0.15)] active:scale-95 transition-all cursor-pointer select-none"
    >
      <span class="text-xl text-[#C0A480]">🐦</span>
    </button>

    <!-- 17. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 18. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
