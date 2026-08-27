/**
 * 个人历史记录、角色历史与自定义设置领域类型定义
 *
 * @packageDocumentation
 */

export type UserHistoryCategory = "story" | "tavern" | "custom" | "module";

export type UploadSubCategory = "story" | "nsfw" | "tavern";

export type HistoryTabType =
  | "active"
  | "pinned"
  | "archived"
  | "all"
  | "story"
  | "market"
  | "settings"
  | "plugins";

export interface WeekOption {
  id?: string;
  label: string;
  value?: string;
}

export type CustomSubCategory = "persona" | "command" | "artist" | "summary" | "memory";

export type ModSubCategory = "square" | "created" | "purchased" | "collection" | "settings";

export type CollectionSubTab = "mine" | "public";

export type ModSortType = "latest" | "hot" | "rating" | "likes" | "comments";

export type ModCategoryTag = "all" | "worldbook" | "system" | "command" | "regex" | "author";

export type HistoryViewMode = "grid" | "list";

export interface UserHistoryItem {
  id: string;
  characterId: string;
  title: string;
  avatar: string;
  lastMessage?: string;
  updatedAt?: string;
  category: UserHistoryCategory;
  isPinned: boolean;
  messageCount: number;
  tags?: string[];
  remark?: string;
  lastChatTime?: string;
  lastChatDate?: string;
  branchName?: string;
  isCloudBacked?: boolean;
}

export interface HistoryCardItem {
  id: string;
  characterId: string;
  title: string;
  avatar?: string;
  lastMessage?: string;
  updatedAt?: string;
  isPinned: boolean;
  messageCount: number;
  tags?: string[];
  remark?: string;
  note?: string;
  author?: string;
  avatarUrl?: string;
  customNote?: string;
  lastActiveTime?: string;
  category?: string;
}

export interface HistoryCharacterCard {
  id: string;
  name?: string;
  title?: string;
  avatar?: string;
  coverUrl?: string;
  description?: string;
  summary?: string;
  tags: string[];
  rating?: string | number;
  chatCount?: string | number;
  author?: string;
  authorName?: string;
  heat?: string | number;
  commentsCount?: string | number;
  tokenUsage?: string | number;
  updatedAt?: string;
  isPinned?: boolean;
  weekPeriod?: string;
  lastInteractedTime?: string;
}

export interface PersonaItem {
  id: string;
  name: string;
  displayName?: string;
  content: string;
  isDefault: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface CommandItem {
  id: string;
  label: string;
  content: string;
  order: number;
  createdAt?: string;
  updatedAt?: string;
}

export interface ArtistPromptItem {
  id: string;
  name: string;
  prompt: string;
  description?: string;
  negativePrompt?: string;
  isActive: boolean;
  createdAt?: string;
  updatedAt?: string;
}

export interface ModItem {
  id: string;
  title: string;
  description: string;
  author: string;
  rating: number;
  likes: number;
  commentsCount?: number;
  price: number;
  isPurchased: boolean;
  categoryTag: ModCategoryTag;
  createdAt?: string;
}

export interface CreatedModEntry {
  id: string;
  type: ModCategoryTag;
  title: string;
  content: string;
}

export interface CreatedModItem {
  id: string;
  name: string;
  description: string;
  status: "draft" | "published";
  entries: CreatedModEntry[];
  createdAt?: string;
  updatedAt?: string;
}

export interface PurchasedModItem {
  id: string;
  title: string;
  description: string;
  isActive: boolean;
  createdAt?: string;
}

export interface CollectionModEntry {
  id: string;
  title: string;
  description: string;
}

export interface ModCollectionItem {
  id: string;
  title: string;
  description: string;
  modCount: number;
  statsText: string;
  mods: CollectionModEntry[];
  author?: string;
  isPublic?: boolean;
  createdAt?: string;
  updatedAt?: string;
}
