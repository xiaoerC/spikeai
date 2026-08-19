/**
 * 创作者专区业务领域强类型定义
 *
 * @packageDocumentation
 */

/**
 * 创作者旗下的代表作角色卡实体
 */
export interface CreatorCharacterWork {
  id: string;
  title: string;
  coverUrl: string;
  heat: string; // 如 "6149.3k"
  commentsCount: string; // 如 "138.4k"
  tokenUsage: string; // 如 "18157.6M"
  rating: number; // 如 4.9
  summary: string;
  tags: string[]; // 如 ["#RPG", "#世界", "+3"]
  authorName: string; // 如 "@萌羽不萌"
  rankBadge?: {
    cupName: string; // 如 "古风杯"
    rank: string; // 如 "#1"
  };
}

/**
 * 创作者实体
 */
export interface CreatorItem {
  id: string;
  username: string;
  avatarUrl: string;
  level: number; // 如 27
  levelBadgeColor?: string; // 如 "#A78BFA"
  followersCount: string; // 如 "5.2K"
  interactionsCount: string; // 如 "20.8M"
  isFollowed: boolean;
  featuredWorks: CreatorCharacterWork[];
}
