/**
 * 问卷调查高保真 Mock 数据源
 *
 * @packageDocumentation
 */

import type { SurveyItem } from "@/views/survey/types";

export const MOCK_ACTIVE_SURVEYS: SurveyItem[] = [];

export const MOCK_SURVEY_RECORDS: SurveyItem[] = [
  {
    id: "survey-rec-001",
    title: "叙梦 Naro 移动端体验与分支剧情满意度问卷",
    description: "感谢参与前期版本体验调研，已发放奖励！",
    rewardCoins: 50,
    estimatedMinutes: 3,
    status: "completed",
    createdAt: "2026/08/10",
    completedAt: "2026/08/12 18:30",
  },
];
