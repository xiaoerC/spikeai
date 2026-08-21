/**
 * 问卷调查业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_ACTIVE_SURVEYS, MOCK_SURVEY_RECORDS } from "@/data/mockSurveys";
import type { SurveyItem, SurveyTabType } from "@/views/survey/types";
import { ref } from "vue";

export function useSurveyList() {
  const activeTab = ref<SurveyTabType>("list");
  const activeSurveys = ref<SurveyItem[]>(MOCK_ACTIVE_SURVEYS);
  const surveyRecords = ref<SurveyItem[]>(MOCK_SURVEY_RECORDS);

  function setActiveTab(tab: SurveyTabType): void {
    activeTab.value = tab;
  }

  return {
    activeTab,
    activeSurveys,
    surveyRecords,
    setActiveTab,
  };
}
