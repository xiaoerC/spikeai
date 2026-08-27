/**
 * 叙梦 Naro 角色市场全局状态管理 Store (对接真实后端 API)。
 *
 * @packageDocumentation
 */

import { characterService, type CharacterListItem } from "@/services/character";
import type { CardMode, MarketCard, SortType, TimeSpan } from "@/types";
import { defineStore } from "pinia";
import { computed, ref, watch } from "vue";

function formatNumber(num: number): string {
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}w`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}k`;
  }
  return num.toString();
}

function mapListItemToCard(item: CharacterListItem): MarketCard {
  return {
    id: item.id,
    title: item.name,
    author: item.author?.username ? `@${item.author.username}` : "@叙梦创作者",
    authorAvatarUrl: item.author?.avatar_url,
    avatarUrl: item.avatar_url,
    bannerUrl: item.banner_url || item.avatar_url,
    heat: `${formatNumber(item.metrics?.hotness || 0)}`,
    trendScore: (item.metrics?.trend_score || 0).toFixed(2),
    chatCount: `${formatNumber(item.metrics?.chat_count || 0)}`,
    rating: (item.metrics?.rating || 5.0).toFixed(1),
    description: item.description,
    tags: item.tags || [],
    extraTags: item.tags?.length > 2 ? `+${item.tags.length - 2}` : undefined,
    cardType: item.category === "nsfw" ? "nsfw" : "story",
    category: item.category,
    isFavorite: item.metrics?.favorite_count > 0,
  };
}

export const useMarketStore = defineStore("market", () => {
  // --- 状态定义 ---
  const mode = ref<CardMode>("story");
  const sortBy = ref<SortType>("heat");
  const timeSpan = ref<TimeSpan>("week");
  const selectedTag = ref<string>("");
  const searchKeyword = ref<string>("");
  const cards = ref<MarketCard[]>([]);
  const total = ref<number>(0);
  const page = ref<number>(1);
  const isLoading = ref<boolean>(false);

  // --- Actions ---

  async function fetchCards(): Promise<void> {
    isLoading.value = true;
    try {
      const res = await characterService.getCharacters({
        mode: mode.value,
        sort: sortBy.value === "heat" ? "heat" : sortBy.value === "trend" ? "trend" : sortBy.value === "recommend" ? "recommend" : "favorite",
        tag: selectedTag.value || undefined,
        keyword: searchKeyword.value || undefined,
        page: page.value,
        page_size: 30,
      });
      cards.value = (res.items || []).map(mapListItemToCard);
      total.value = res.total || 0;
    } catch (e) {
      console.error("加载角色市场卡片失败:", e);
      cards.value = [];
      total.value = 0;
    } finally {
      isLoading.value = false;
    }
  }

  function setMode(newMode: CardMode): void {
    mode.value = newMode;
    page.value = 1;
    fetchCards();
  }

  function setSortBy(newSort: SortType): void {
    sortBy.value = newSort;
    page.value = 1;
    fetchCards();
  }

  function setTimeSpan(newTimeSpan: TimeSpan): void {
    timeSpan.value = newTimeSpan;
    fetchCards();
  }

  function setSelectedTag(tag: string): void {
    if (selectedTag.value === tag) {
      selectedTag.value = "";
    } else {
      selectedTag.value = tag;
    }
    page.value = 1;
    fetchCards();
  }

  let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null;
  function setSearchKeyword(keyword: string): void {
    searchKeyword.value = keyword;
    if (searchDebounceTimer) clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => {
      page.value = 1;
      fetchCards();
    }, 300);
  }

  // 初始加载
  fetchCards();

  const filteredCards = computed<MarketCard[]>(() => cards.value);

  return {
    mode,
    sortBy,
    timeSpan,
    selectedTag,
    searchKeyword,
    cards,
    filteredCards,
    total,
    page,
    isLoading,
    fetchCards,
    setMode,
    setSortBy,
    setTimeSpan,
    setSelectedTag,
    setSearchKeyword,
  };
});
