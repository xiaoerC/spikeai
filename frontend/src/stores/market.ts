/**
 * 叙梦 Naro 角色市场全局状态管理 Store
 *
 * @packageDocumentation
 */

import { MOCK_MARKET_CARDS } from "@/data/mockCards";
import type { CardMode, MarketCard, SortType, TimeSpan } from "@/types";
import { defineStore } from "pinia";
import { computed, ref } from "vue";

/**
 * 角色市场状态管理 Store Hook
 *
 * @example
 * ```ts
 * const marketStore = useMarketStore();
 * marketStore.setMode('story');
 * marketStore.setSortBy('trend');
 * console.log(marketStore.filteredCards);
 * ```
 */
export const useMarketStore = defineStore("market", () => {
  // --- 状态定义 ---

  /** 当前主分类模式：剧情卡 vs 绅士卡 */
  const mode = ref<CardMode>("story");

  /** 当前排序类型：热度 / 推荐 / 趋势 / 随机 / 收藏 */
  const sortBy = ref<SortType>("trend");

  /** 当前趋势周期跨度：日 / 周 / 月 */
  const timeSpan = ref<TimeSpan>("week");

  /** 当前选中的标签过滤，空字符串表示不限制 */
  const selectedTag = ref<string>("");

  /** 搜索关键词 */
  const searchKeyword = ref<string>("");

  /** 角色卡片列表数据 */
  const cards = ref<MarketCard[]>(MOCK_MARKET_CARDS);

  // --- 计算属性 ---

  /**
   * 根据当前模式、标签、关键词和排序规则计算出的最终展示卡片流
   */
  const filteredCards = computed<MarketCard[]>(() => {
    let result = [...cards.value];

    // 1. 过滤主模式（剧情卡 vs 绅士卡）
    result = result.filter((card) => card.cardType === mode.value);

    // 2. 关键词搜索（匹配标题、作者、简介或标签）
    const keyword = searchKeyword.value.trim().toLowerCase();
    if (keyword) {
      result = result.filter((card) => {
        const inTitle = card.title.toLowerCase().includes(keyword);
        const inAuthor = card.author.toLowerCase().includes(keyword);
        const inDesc = card.description.toLowerCase().includes(keyword);
        const inTags = card.tags.some((tag) => tag.toLowerCase().includes(keyword));
        return inTitle || inAuthor || inDesc || inTags;
      });
    }

    // 3. 标签筛选
    if (selectedTag.value) {
      result = result.filter((card) => card.tags.includes(selectedTag.value));
    }

    // 4. 排序规则处理
    if (sortBy.value === "favorite") {
      result = result.filter((card) => card.isFavorite);
    } else if (sortBy.value === "heat") {
      result.sort((a, b) => {
        const valA = Number.parseFloat(a.heat.replace(/[^\d.]/g, "")) || 0;
        const valB = Number.parseFloat(b.heat.replace(/[^\d.]/g, "")) || 0;
        return valB - valA;
      });
    } else if (sortBy.value === "trend") {
      result.sort((a, b) => {
        const valA = Number.parseFloat(a.trendScore) || 0;
        const valB = Number.parseFloat(b.trendScore) || 0;
        return valB - valA;
      });
    } else if (sortBy.value === "recommend") {
      result.sort((a, b) => {
        const valA = Number.parseFloat(a.rating) || 0;
        const valB = Number.parseFloat(b.rating) || 0;
        return valB - valA;
      });
    } else if (sortBy.value === "random") {
      // 保持伪随机或原始顺序打乱
      result.sort((a, b) => (a.id > b.id ? 1 : -1));
    }

    return result;
  });

  // --- 操作 Actions ---

  /**
   * 切换卡片主分类模式
   * @param newMode - 'story' | 'nsfw'
   */
  function setMode(newMode: CardMode): void {
    mode.value = newMode;
  }

  /**
   * 切换排序方式
   * @param newSort - SortType
   */
  function setSortBy(newSort: SortType): void {
    sortBy.value = newSort;
  }

  /**
   * 切换趋势时间跨度
   * @param newTimeSpan - TimeSpan
   */
  function setTimeSpan(newTimeSpan: TimeSpan): void {
    timeSpan.value = newTimeSpan;
  }

  /**
   * 切换或取消标签过滤
   * @param tag - 标签名称，如 `#二次元`
   */
  function setSelectedTag(tag: string): void {
    if (selectedTag.value === tag) {
      selectedTag.value = ""; // 再次点击取消选中
    } else {
      selectedTag.value = tag;
    }
  }

  /**
   * 更新搜索关键词
   * @param keyword - 搜索文本
   */
  function setSearchKeyword(keyword: string): void {
    searchKeyword.value = keyword;
  }

  /**
   * 切换某张卡片的收藏状态
   * @param cardId - 卡片 ID
   */
  function toggleFavorite(cardId: string): void {
    const target = cards.value.find((c) => c.id === cardId);
    if (target) {
      target.isFavorite = !target.isFavorite;
    }
  }

  return {
    mode,
    sortBy,
    timeSpan,
    selectedTag,
    searchKeyword,
    cards,
    filteredCards,
    setMode,
    setSortBy,
    setTimeSpan,
    setSelectedTag,
    setSearchKeyword,
    toggleFavorite,
  };
});
