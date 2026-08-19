/**
 * 历史记录业务领域强类型定义
 *
 * @packageDocumentation
 */

/**
 * 历史记录角色卡片实体 (Figma 原型)
 */
export interface HistoryCharacterCard {
  id: string;
  title: string;
  coverUrl: string;
  heat: string; // 如 "63.8k"
  commentsCount: string; // 如 "1.6k"
  tokenUsage: string; // 如 "146.6M"
  rating?: number; // 如 5.0
  summary: string;
  tags: string[]; // 如 ["#世界", "#玄幻", "+3"]
  authorName: string; // 如 "@路过的hfs101"
  weekPeriod?: string; // 如 "2026-W33"
  lastInteractedTime?: string; // 如 "2小时前"
}

/**
 * 周次选项
 */
export interface WeekOption {
  id: string;
  label: string; // 如 "全部周次", "本周", "第33周 (08.11-08.17)"
}

/**
 * 兼容历史项类型
 */
export interface HistoryCardItem {
  id: string;
  characterId?: string;
  title?: string;
  coverUrl?: string;
  avatarUrl?: string;
  author?: string;
  summary?: string;
  tags?: string[];
  type?: "character" | "story" | "worldbook";
  lastChatTime?: string;
  lastActiveTime?: string;
  messageCount?: number;
  isFavorite?: boolean;
  isPinned?: boolean;
  note?: string;
  customNote?: string;
  category?: string;
}

export type HistoryTabType =
  | "all"
  | "character"
  | "story"
  | "favorite"
  | "market"
  | "settings"
  | "plugins";
export type HistoryViewMode = "grid" | "list";
