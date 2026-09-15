/**
 * 角色卡与市场领域强类型 API 服务。
 *
 * 对接后端 `/api/v1/characters` 路由，包含多维检索、详情、点赞、评论与打赏分成。
 *
 * @module services/character
 *
 * Usage:
 * ```ts
 * import { characterService } from '@/services/character'
 * const list = await characterService.getCharacters({ mode: 'story', sort: 'heat' })
 * ```
 */

import api, { type ApiResponse } from "./api";

/** 世界书单条目 */
export interface WorldBookEntry {
  id?: string;
  keys: string[];
  content: string;
  constant: boolean;
  position: string;
}

/** 角色 10 项数据指标 */
export interface CharacterMetrics {
  hotness: number;
  trend_score: number;
  chat_count: number;
  like_count: number;
  favorite_count: number;
  import_count: number;
  rating: number;
  rating_count: number;
  total_tokens: number;
}

/** 创作者简要信息 */
export interface CharacterAuthor {
  id: string;
  username: string;
  avatar_url: string;
  creator_level: number;
  followers_count: number;
  is_following: boolean;
}

/** 角色卡市场简要卡片响应项 */
export interface CharacterListItem {
  id: string;
  name: string;
  avatar_url: string;
  banner_url?: string | null;
  category: string;
  description: string;
  tags: string[];
  author: CharacterAuthor;
  metrics: CharacterMetrics;
  created_at: string;
}

/** 角色卡全量详情响应体 */
export interface CharacterDetail {
  id: string;
  name: string;
  avatar_url: string;
  banner_url?: string | null;
  category: string;
  description: string;
  personality: string;
  scenario: string;
  first_mes: string;
  alternate_greetings: string[];
  system_prompt: string;
  post_history_instructions: string;
  prologue_title: string;
  prologue_html: string;
  creator_notes?: string;
  tags: string[];
  status: string;
  settings_word_count: number;
  version: string;
  extensions?: Record<string, any>;
  created_at: string;
  author: CharacterAuthor;
  metrics: CharacterMetrics;
  worldbooks: WorldBookEntry[];
  is_liked: boolean;
  is_favorited: boolean;
  user_rating?: number | null;
}

/** 评论项响应 */
export interface CharacterComment {
  id: string;
  character_id: string;
  user_id: string;
  username: string;
  avatar_url: string;
  content: string;
  likes: number;
  created_at: string;
}

/** 市场筛选入参 */
export interface CharacterFilterParams {
  mode?: "story" | "nsfw";
  sort?: "heat" | "trend" | "recommend" | "favorite";
  tag?: string;
  keyword?: string;
  page?: number;
  page_size?: number;
}

/** 分页容器包装 */
export interface PaginatedData<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const characterService = {
  /** 获取角色市场列表 */
  async getCharacters(
    params: CharacterFilterParams = {},
  ): Promise<PaginatedData<CharacterListItem>> {
    const res = await api.get<ApiResponse<PaginatedData<CharacterListItem>>>("/characters", {
      params,
    });
    return res.data.data;
  },

  /** 获取角色卡 100% 详情与 10 项指标 */
  async getCharacterDetail(id: string): Promise<CharacterDetail> {
    const res = await api.get<ApiResponse<CharacterDetail>>(`/characters/${id}`);
    return res.data.data;
  },

  /** 切换点赞状态 */
  async toggleLike(id: string): Promise<{ is_liked: boolean; like_count: number }> {
    const res = await api.post<ApiResponse<{ is_liked: boolean; like_count: number }>>(
      `/characters/${id}/like`,
    );
    return res.data.data;
  },

  /** 获取角色评论列表 */
  async getComments(id: string, page = 1, pageSize = 20): Promise<PaginatedData<CharacterComment>> {
    const res = await api.get<ApiResponse<PaginatedData<CharacterComment>>>(
      `/characters/${id}/comments`,
      {
        params: { page, page_size: pageSize },
      },
    );
    return res.data.data;
  },

  /** 发表新评论 */
  async addComment(id: string, content: string): Promise<CharacterComment> {
    const res = await api.post<ApiResponse<CharacterComment>>(`/characters/${id}/comments`, {
      content,
    });
    return res.data.data;
  },

  /** 打赏角色 */
  async rewardCharacter(
    id: string,
    currency: "star" | "moon",
    amount: number,
  ): Promise<{ remaining_balance: number }> {
    const res = await api.post<ApiResponse<{ remaining_balance: number }>>(
      `/characters/${id}/reward`,
      {
        currency,
        amount,
      },
    );
    return res.data.data;
  },

  /** 创建并上架新的原创角色卡 */
  async createCharacter(payload: CharacterCreatePayload): Promise<CharacterDetail> {
    const res = await api.post<ApiResponse<CharacterDetail>>("/characters", payload);
    return res.data.data;
  },

  /** 查询当前登录用户创建/上传的所有角色卡列表 */
  async getMyCharacters(category?: string): Promise<CharacterDetail[]> {
    const res = await api.get<ApiResponse<CharacterDetail[]>>("/characters/mine", {
      params: category ? { category } : undefined,
    });
    return res.data.data;
  },

  /** 修改角色发布状态 (上架/下架/草稿) */
  async updateCharacterStatus(
    id: string,
    status: "draft" | "published" | "private",
  ): Promise<CharacterDetail> {
    const res = await api.patch<ApiResponse<CharacterDetail>>(`/characters/${id}/status`, {
      status,
    });
    return res.data.data;
  },

  /** 修改更新角色全量信息与世界书 */
  async updateCharacter(id: string, payload: CharacterCreatePayload): Promise<CharacterDetail> {
    const res = await api.put<ApiResponse<CharacterDetail>>(`/characters/${id}`, payload);
    return res.data.data;
  },

  /** 删除角色卡 */
  async deleteCharacter(id: string): Promise<void> {
    await api.delete<ApiResponse<{ deleted_id: string }>>(`/characters/${id}`);
  },

  /** 基于角色基础设定智能调用大模型生成序幕 HTML */
  async generatePrologue(params: {
    name: string;
    description?: string;
    personality?: string;
    scenario?: string;
    first_mes?: string;
  }): Promise<string> {
    const res = await api.post<ApiResponse<{ prologue_html: string }>>(
      "/characters/generate-prologue",
      params,
    );
    return res.data.data.prologue_html;
  },
};

/** 创建角色请求参数结构 */
export interface CharacterCreatePayload {
  name: string;
  avatar_url: string;
  banner_url?: string | null;
  category?: "story" | "nsfw" | "rpg";
  description: string;
  personality?: string;
  scenario?: string;
  first_mes: string;
  alternate_greetings?: string[];
  system_prompt?: string;
  post_history_instructions?: string;
  prologue_title?: string;
  prologue_html?: string;
  creator_notes?: string;
  tags?: string[];
  status?: "draft" | "published" | "private";
  version?: string;
  extensions?: Record<string, any>;
  worldbooks?: Array<{
    keys: string[];
    content: string;
    constant?: boolean;
    position?: string;
  }>;
}
