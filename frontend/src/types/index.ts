/**
 * 前端核心通用数据类型定义模块。
 */

export type ThemeMode = "obsidian-gold" | "obsidian-purple";

export interface UserProfile {
  id: string;
  username: string;
  avatarUrl: string;
  starCoins: number; // 星元 ★ (普通对话币)
  moonGems: number; // 月华 🌙 (高级模型/画图特权币)
  vipLevel: number; // 赞助者/VIP 等级
  creatorLevel: number; // 创作者等级
  badges: string[]; // 获得的成就勋章
}

export interface CharacterSummary {
  id: string;
  name: string;
  avatarUrl: string;
  summary: string;
  tags: string[];
  category: "story" | "gentleman" | "rpg";
  authorName: string;
  authorAvatarUrl: string;
  chatCount: number;
  likeCount: number;
  rating: number;
  updatedAt: string;
}

export interface AppState {
  isMobile: boolean;
  viewportHeight: number;
  keyboardHeight: number;
  activeTab: "community" | "history" | "create" | "more" | "profile";
  currentTheme: ThemeMode;
}

export * from "./card";
