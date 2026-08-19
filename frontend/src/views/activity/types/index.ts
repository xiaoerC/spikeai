/**
 * 活动中心业务领域强类型定义
 *
 * @packageDocumentation
 */

export type ActivityStatus = "ongoing" | "upcoming" | "ended";
export type ActivityCategory = "all" | "character" | "creation" | "welfare";

/**
 * 官方活动卡片实体
 */
export interface ActivityItem {
  id: string;
  title: string;
  category: ActivityCategory;
  status: ActivityStatus;
  statusText: string; // 如 "进行中"
  isNew?: boolean; // 是否显示 "新" 角标
  dateRange: string; // 如 "2026/03/10 - 2027/01/10"
  summary: string;
  fullHtmlContent: string;
  rewardsSummary?: string; // 如 "200星元", "生图次数 × 100", "USDT 返利"
}
