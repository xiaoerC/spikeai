/**
 * 历史记录业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_HISTORY_CARDS, MOCK_WEEK_OPTIONS } from "@/data/mockHistory";
import type { HistoryCharacterCard, WeekOption } from "@/views/history/types";
import { computed, ref } from "vue";

export function useHistoryList() {
  const cards = ref<HistoryCharacterCard[]>(MOCK_HISTORY_CARDS);
  const weekOptions = ref<WeekOption[]>(MOCK_WEEK_OPTIONS);
  const selectedWeek = ref<string>("all");
  const isWeekSelectorOpen = ref<boolean>(false);

  // 筛选后的列表
  const filteredCards = computed(() => {
    if (selectedWeek.value === "all") {
      return cards.value;
    }
    return cards.value.filter((c) => c.weekPeriod === selectedWeek.value);
  });

  // 当前选中周次文案
  const currentWeekLabel = computed(() => {
    const found = weekOptions.value.find((w) => w.id === selectedWeek.value);
    return found ? found.label : "选择周次";
  });

  function setWeek(weekId: string) {
    selectedWeek.value = weekId;
    isWeekSelectorOpen.value = false;
  }

  function toggleWeekSelector() {
    isWeekSelectorOpen.value = !isWeekSelectorOpen.value;
  }

  function clearHistory() {
    cards.value = [];
  }

  return {
    cards: filteredCards,
    weekOptions,
    selectedWeek,
    currentWeekLabel,
    isWeekSelectorOpen,
    setWeek,
    toggleWeekSelector,
    clearHistory,
  };
}
