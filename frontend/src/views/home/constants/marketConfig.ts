/**
 * 角色市场首页常量与静态配置
 *
 * @packageDocumentation
 */

import type { SortType, TimeSpan } from "@/types";

/** 首页热门快捷标签列表 */
export const HOT_TAGS: readonly string[] = ["#工具", "#同人", "#二次元", "#世界", "#玄幻"] as const;

/** 首页扩展抽屉标签列表 */
export const EXTRA_TAGS: readonly string[] = [
  "#RPG",
  "#修仙",
  "#西幻",
  "#末日",
  "#都市",
  "#校园",
  "#系统流",
  "#纯爱",
  "#古风",
  "#网游",
] as const;

/** 默认排序选项配置 */
export const DEFAULT_SORT_TYPE: SortType = "trend";

/** 默认时间趋势跨度 */
export const DEFAULT_TIME_SPAN: TimeSpan = "week";
