/**
 * 个人历史记录与角色上线历史业务领域强类型定义
 *
 * @packageDocumentation
 */

export type UserHistoryCategory = "story" | "tavern" | "custom" | "module";
export type HistoryTabType =
  | "recent"
  | "favorite"
  | "archived"
  | "all"
  | "story"
  | "market"
  | "settings"
  | "plugins";
export type HistoryViewMode = "grid" | "list";

/**
 * 个人历史对话卡片实体 (1:1 原型高保真)
 */
export interface UserHistoryItem {
  id: string;
  characterId: string;
  title: string;
  avatar: string;
  category: UserHistoryCategory;
  isPinned?: boolean;
  remark?: string;
  lastChatTime: string;
  lastChatDate?: string; // 精确时间，如 "2026/08/19 13:28"
  branchName?: string; // 分支名称，如 "《鬼灭之刃》"
  messageCount: number;
  isCloudBacked?: boolean;
}

/**
 * 周次历史回顾实体 (兼容 character-history)
 */
export interface WeekOption {
  id?: string;
  value?: string;
  label: string;
  dateRange?: string;
}

export interface HistoryCharacterCard {
  id: string;
  title: string;
  avatar?: string;
  avatarUrl?: string;
  coverUrl?: string;
  author?: string;
  authorName?: string;
  heat: string;
  comments?: string;
  commentsCount?: string;
  tokens?: string;
  tokenUsage?: string;
  rating?: number;
  tags: string[];
  week?: string;
  weekPeriod?: string;
  summary: string;
  lastInteractedTime?: string;
}

export interface HistoryCardItem {
  id: string;
  characterId?: string;
  title: string;
  avatar?: string;
  avatarUrl?: string;
  author?: string;
  authorName?: string;
  heat?: string;
  comments?: string;
  tokens?: string;
  rating?: number;
  tags?: string[];
  week?: string;
  summary?: string;
  roleCount?: number;
  isPinned?: boolean;
  customNote?: string;
  lastActiveTime?: string;
  messageCount?: number;
  category?: string;
}
