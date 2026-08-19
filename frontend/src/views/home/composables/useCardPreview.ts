/**
 * 角色卡详情预览弹窗业务组合式逻辑
 *
 * @packageDocumentation
 */

import type { MarketCard } from "@/types";
import { ref } from "vue";

/**
 * 角色卡详情预览 Hook
 *
 * @returns 角色卡详情预览状态与控制方法
 *
 * @example
 * ```ts
 * const { activeCard, isPreviewOpen, openPreview, closePreview } = useCardPreview();
 * ```
 */
export function useCardPreview() {
  /** 当前选中的角色卡片 */
  const activeCard = ref<MarketCard | null>(null);

  /** 是否处于打开状态 */
  const isPreviewOpen = ref(false);

  /**
   * 打开角色卡详情弹窗
   * @param card - 目标角色卡数据
   */
  function openPreview(card: MarketCard): void {
    activeCard.value = card;
    isPreviewOpen.value = true;
  }

  /**
   * 关闭角色卡详情弹窗
   */
  function closePreview(): void {
    isPreviewOpen.value = false;
    activeCard.value = null;
  }

  return {
    activeCard,
    isPreviewOpen,
    openPreview,
    closePreview,
  };
}
