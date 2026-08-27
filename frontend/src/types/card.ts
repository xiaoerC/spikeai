/**
 * 叙梦 Naro 角色市场卡片与筛选相关强类型定义
 *
 * @packageDocumentation
 */

/**
 * 角色卡大分类模式：剧情卡 vs 绅士卡
 */
export type CardMode = "story" | "nsfw";

/**
 * 市场排序类型
 * - heat: 热度排序
 * - recommend: 推荐排序
 * - trend: 趋势增长排序
 * - random: 随机漫游
 * - favorite: 个人收藏
 */
export type SortType = "heat" | "recommend" | "trend" | "random" | "favorite";

/**
 * 趋势时间跨度周期
 * - day: 日趋势
 * - week: 周趋势
 * - month: 月趋势
 */
export type TimeSpan = "day" | "week" | "month";

/**
 * 市场角色卡片元数据完整接口
 *
 * @example
 * ```ts
 * const card: MarketCard = {
 *   id: "card-1",
 *   title: "西幻世界模拟器",
 *   author: "@萌羽不萌",
 *   heat: "5799.8k",
 *   trendScore: "5.41",
 *   chatCount: "132.1k",
 *   rating: "4.9",
 *   description: "新增11个剧情和战斗mod...",
 *   tags: ["#RPG", "#世界"],
 *   extraTags: "+3",
 *   cardType: "story",
 *   avatarUrl: "https://images.unsplash.com/photo-..."
 * };
 * ```
 */
export interface MarketCard {
  /** 唯一卡片标识符 */
  id: string;
  /** 角色卡标题 */
  title: string;
  /** 卡片创作者名称，如 `@萌羽不萌` */
  author: string;
  /** 创作者头像（可选） */
  authorAvatarUrl?: string;
  /** 角色立绘 URL */
  avatarUrl?: string;
  /** 角色背景/封面大图 URL */
  bannerUrl?: string;
  /** 总热度展示值，如 `5799.8k` */
  heat: string;
  /** 趋势增长指数，如 `5.41` */
  trendScore: string;
  /** 对话/互动消息数，如 `132.1k` */
  chatCount: string;
  /** 用户评分，如 `4.9` */
  rating: string;
  /** 角色介绍与背景摘要 */
  description: string;
  /** 标签列表，如 `["#RPG", "#世界"]` */
  tags: string[];
  /** 折叠更多标签数量标牌，如 `+3` */
  extraTags?: string;
  /** 卡片主分类：剧情卡 (story) 或 绅士卡 (nsfw) */
  cardType: CardMode;
  /** 次级所属分类标签，如 "二次元"、"修仙"、"同人" */
  category?: string;
  /** 是否已被当前用户收藏 */
  isFavorite?: boolean;
}

/**
 * 市场筛选过滤状态参数
 */
export interface MarketFilterState {
  /** 当前主分类模式 */
  mode: CardMode;
  /** 当前选中的排序方式 */
  sortBy: SortType;
  /** 趋势时间跨度 */
  timeSpan: TimeSpan;
  /** 当前选中的标签 (空字符串表示全选) */
  selectedTag: string;
  /** 搜索关键词 */
  searchKeyword: string;
}
