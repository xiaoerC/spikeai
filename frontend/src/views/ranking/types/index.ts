/**
 * 等级榜 / 排行榜业务领域强类型定义
 *
 * @packageDocumentation
 */

/**
 * 榜单用户实体
 */
export interface RankingUserItem {
  rank: number;
  username: string;
  avatarUrl: string;
  title: string; // 如 "情绪共振者", "幻想同行者", "梦境驻足者"
  level: number; // 如 17, 15, 14
  xp: string; // 如 "1,647,182 XP"
  isCurrentUser?: boolean;
}
