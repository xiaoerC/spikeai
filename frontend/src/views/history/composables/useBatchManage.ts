/**
 * 历史记录批量管理模式组合式 Hook
 *
 * @packageDocumentation
 */

import { computed, ref } from "vue";

/**
 * 批量选择与管理状态 Hook
 *
 * @example
 * ```ts
 * const {
 *   isBatchMode,
 *   selectedIds,
 *   selectedCount,
 *   enterBatchMode,
 *   exitBatchMode,
 *   toggleSelect,
 *   selectAll,
 *   clearSelection,
 * } = useBatchManage();
 * ```
 */
export function useBatchManage() {
  // 是否处于批量管理模式
  const isBatchMode = ref<boolean>(false);

  // 当前选中的卡片 ID 集合
  const selectedIds = ref<Set<string>>(new Set());

  // 当前选中总数
  const selectedCount = computed<number>(() => selectedIds.value.size);

  /**
   * 进入批量管理模式
   */
  function enterBatchMode(): void {
    isBatchMode.value = true;
    selectedIds.value.clear();
  }

  /**
   * 退出批量管理模式
   */
  function exitBatchMode(): void {
    isBatchMode.value = false;
    selectedIds.value.clear();
  }

  /**
   * 切换卡片选中状态
   * @param id - 卡片 ID
   */
  function toggleSelect(id: string): void {
    const nextSet = new Set(selectedIds.value);
    if (nextSet.has(id)) {
      nextSet.delete(id);
    } else {
      nextSet.add(id);
    }
    selectedIds.value = nextSet;
  }

  /**
   * 全选指定卡片列表
   * @param allIds - 所有卡片 ID 数组
   */
  function selectAll(allIds: string[]): void {
    selectedIds.value = new Set(allIds);
  }

  /**
   * 清空选中
   */
  function clearSelection(): void {
    selectedIds.value = new Set();
  }

  return {
    isBatchMode,
    selectedIds,
    selectedCount,
    enterBatchMode,
    exitBatchMode,
    toggleSelect,
    selectAll,
    clearSelection,
  };
}
