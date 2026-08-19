/**
 * 活动中心业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_ACTIVITIES } from "@/data/mockActivities";
import type { ActivityCategory, ActivityItem } from "@/views/activity/types";
import { computed, ref } from "vue";

export function useActivityList() {
  const activities = ref<ActivityItem[]>(MOCK_ACTIVITIES);
  const currentCategory = ref<ActivityCategory>("all");
  const expandedCardIds = ref<Set<string>>(new Set());

  // 分类筛选列表
  const filteredActivities = computed(() => {
    if (currentCategory.value === "all") {
      return activities.value;
    }
    return activities.value.filter((a) => a.category === currentCategory.value);
  });

  /**
   * 切换卡片展开/收起状态
   * @param id - 活动唯一标识
   */
  function toggleExpand(id: string): void {
    if (expandedCardIds.value.has(id)) {
      expandedCardIds.value.delete(id);
    } else {
      expandedCardIds.value.add(id);
    }
  }

  function setCategory(cat: ActivityCategory): void {
    currentCategory.value = cat;
  }

  return {
    activities: filteredActivities,
    currentCategory,
    expandedCardIds,
    toggleExpand,
    setCategory,
  };
}
