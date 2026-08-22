/**
 * 个人历史记录业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_USER_HISTORY } from "@/data/mockUserHistory";
import type { HistoryViewMode, UserHistoryCategory, UserHistoryItem } from "@/views/history/types";
import { computed, ref } from "vue";

export function useUserHistory() {
  const historyList = ref<UserHistoryItem[]>(MOCK_USER_HISTORY);
  const currentCategory = ref<UserHistoryCategory>("story");
  const viewMode = ref<HistoryViewMode>("list"); // 默认为列表视图
  const isBatchMode = ref<boolean>(false);
  const selectedIds = ref<Set<string>>(new Set());
  const editingRemarkItem = ref<UserHistoryItem | null>(null);
  const isRemarkModalOpen = ref<boolean>(false);
  const toastMessage = ref<string | null>(null);

  function showToast(msg: string) {
    toastMessage.value = msg;
    setTimeout(() => {
      toastMessage.value = null;
    }, 2000);
  }

  // 数量统计
  const storyCount = computed(() => historyList.value.filter((h) => h.category === "story").length);
  const tavernCount = computed(
    () => historyList.value.filter((h) => h.category === "tavern").length,
  );
  const customCount = computed(
    () => historyList.value.filter((h) => h.category === "custom").length,
  );
  const moduleCount = computed(
    () => historyList.value.filter((h) => h.category === "module").length,
  );

  // 过滤与排序列表 (置顶优先)
  const filteredList = computed(() => {
    const list = historyList.value.filter((h) => h.category === currentCategory.value);
    return [...list].sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return 0;
    });
  });

  function setCategory(cat: UserHistoryCategory): void {
    currentCategory.value = cat;
    selectedIds.value.clear();
  }

  function toggleViewMode(): void {
    viewMode.value = viewMode.value === "grid" ? "list" : "grid";
  }

  function toggleBatchMode(): void {
    isBatchMode.value = !isBatchMode.value;
    selectedIds.value.clear();
  }

  function toggleSelectItem(id: string): void {
    if (selectedIds.value.has(id)) {
      selectedIds.value.delete(id);
    } else {
      selectedIds.value.add(id);
    }
  }

  /**
   * 置顶/取消置顶
   * @param id - 历史项ID
   */
  function togglePin(id: string): void {
    const item = historyList.value.find((h) => h.id === id);
    if (item) {
      item.isPinned = !item.isPinned;
      showToast(item.isPinned ? "已置顶该角色" : "已取消置顶");
    }
  }

  /**
   * 清空该角色的对话历史消息
   * @param id - 历史项ID
   */
  function clearChatHistory(id: string): void {
    const item = historyList.value.find((h) => h.id === id);
    if (item) {
      item.messageCount = 0;
      showToast(`已清空《${item.title}》对话历史`);
    }
  }

  /**
   * 删除单条个人历史
   * @param id - 历史项ID
   */
  function deleteHistory(id: string): void {
    const idx = historyList.value.findIndex((h) => h.id === id);
    if (idx !== -1) {
      historyList.value.splice(idx, 1);
      showToast("已从历史记录中移除");
    }
  }

  /**
   * 批量删除已选项目
   */
  function batchDeleteSelected(): void {
    if (selectedIds.value.size === 0) {
      showToast("请先选择要删除的历史记录");
      return;
    }
    historyList.value = historyList.value.filter((h) => !selectedIds.value.has(h.id));
    showToast(`已成功删除 ${selectedIds.value.size} 项历史`);
    selectedIds.value.clear();
    isBatchMode.value = false;
  }

  /**
   * 更新角色卡 (从服务器拉取最新卡片设定)
   */
  function updateCharacterCard(item: UserHistoryItem): void {
    showToast(`已同步《${item.title}》最新设定`);
  }

  /**
   * 打开备注编辑弹窗
   */
  function openRemarkModal(item: UserHistoryItem): void {
    editingRemarkItem.value = item;
    isRemarkModalOpen.value = true;
  }

  function saveRemark(remark: string): void {
    if (editingRemarkItem.value) {
      editingRemarkItem.value.remark = remark;
      showToast("备注保存成功");
    }
    isRemarkModalOpen.value = false;
    editingRemarkItem.value = null;
  }

  function triggerCloudBackup(): void {
    showToast("云端备份同步完成");
  }

  return {
    historyList: filteredList,
    currentCategory,
    viewMode,
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
  };
}
