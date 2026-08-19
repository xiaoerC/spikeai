/**
 * 公告中心业务领域强类型定义
 *
 * @packageDocumentation
 */

export type NoticeType = "update" | "activity" | "system";
export type NoticeCategory = "all" | "activity" | "system" | "update";

/**
 * 官方公告实体
 */
export interface NoticeItem {
  id: string;
  type: NoticeType;
  typeText: string; // 如 "更新", "活动", "系统"
  title: string;
  publishedAt: string; // 如 "2026/08/05 15:05"
  content: string;
  isImportant?: boolean;
}
