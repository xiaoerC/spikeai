/**
 * 问卷调查业务领域强类型定义
 *
 * @packageDocumentation
 */

export type SurveyTabType = "list" | "records";

/**
 * 问卷实体
 */
export interface SurveyItem {
  id: string;
  title: string;
  description: string;
  rewardCoins: number; // 奖励星元数，如 50
  estimatedMinutes: number; // 预计耗时分钟，如 3
  status: "active" | "completed" | "expired";
  createdAt: string;
  completedAt?: string;
}
