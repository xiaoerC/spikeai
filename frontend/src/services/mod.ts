/**
 * Mod 模组生态与优先级加载流水线领域服务 (Frontend API Client)
 *
 * @packageDocumentation
 */

import api, { type ApiResponse } from "./api";

export interface ModEntryItem {
  anchor?: string; // system_prefix | before_char | after_char | top_an | bottom_an | user_suffix
  title?: string;
  content: string;
  enabled?: boolean;
  order?: number;
}

export interface ModItem {
  id: string;
  author_id: string;
  title: string;
  description: string;
  category_tag: "worldbook" | "system" | "command" | "regex" | "artist" | string;
  price: number;
  status: "draft" | "published" | string;
  entries: ModEntryItem[];
  downloads: number;
  likes: number;
  rating: number;
  created_at: string;
}

export interface UserActiveModItem {
  id: string;
  mod_id: string;
  mod_title: string;
  category_tag: string;
  priority_order: number;
  is_active: boolean;
  is_highest_priority: boolean;
  entries_count: number;
}

export interface ModPrioritySummary {
  active_count: number;
  worldbook_entries_count: number;
  worldbook_words_count: number;
  system_prompt_entries_count: number;
  system_prompt_words_count: number;
  has_performance_warning: boolean;
}

export interface CreateModPayload {
  title: string;
  description: string;
  category_tag: string;
  price?: number;
  status?: string;
  entries: ModEntryItem[];
}

export interface UpdateModPayload {
  title?: string;
  description?: string;
  category_tag?: string;
  price?: number;
  status?: string;
  entries?: ModEntryItem[];
}

export interface ModSquareFilterParams {
  category?: string;
  sort?: "heat" | "rating" | "newest" | string;
  keyword?: string;
  page?: number;
  page_size?: number;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export const modService = {
  /**
   * 分页查询 Mod 广场列表
   */
  async fetchModSquare(params: ModSquareFilterParams = {}): Promise<PaginatedResult<ModItem>> {
    const res = await api.get<ApiResponse<PaginatedResult<ModItem>>>("/mods", {
      params,
    });
    return res.data.data;
  },

  /**
   * 获取当前用户已激活 Mod 列表与优先级矩阵
   */
  async fetchActiveMods(): Promise<UserActiveModItem[]> {
    const res = await api.get<ApiResponse<UserActiveModItem[]>>("/mods/active");
    return res.data.data;
  },

  /**
   * 批量更新 Mod 激活与优先级排序
   */
  async updateModPriorities(
    activeMods: Array<{ mod_id: string; priority_order: number; is_active: boolean }>,
  ): Promise<UserActiveModItem[]> {
    const res = await api.put<ApiResponse<UserActiveModItem[]>>("/mods/priority", {
      active_mods: activeMods,
    });
    return res.data.data;
  },

  /**
   * 快捷切换特定 Mod 启停状态
   */
  async toggleModActivate(modId: string, isActive?: boolean): Promise<UserActiveModItem> {
    const res = await api.post<ApiResponse<UserActiveModItem>>(`/mods/${modId}/activate`, null, {
      params: isActive !== undefined ? { is_active: isActive } : {},
    });
    return res.data.data;
  },

  /**
   * 获取当前生效 Mod 统计横幅数据
   */
  async fetchModSummary(): Promise<ModPrioritySummary> {
    const res = await api.get<ApiResponse<ModPrioritySummary>>("/mods/summary");
    return res.data.data;
  },

  /**
   * 获取指定 Mod 详情
   */
  async fetchModDetail(modId: string): Promise<ModItem> {
    const res = await api.get<ApiResponse<ModItem>>(`/mods/${modId}`);
    return res.data.data;
  },

  /**
   * 创建自定义 Mod
   */
  async createMod(payload: CreateModPayload): Promise<ModItem> {
    const res = await api.post<ApiResponse<ModItem>>("/mods", payload);
    return res.data.data;
  },

  /**
   * 更新自定义 Mod
   */
  async updateMod(modId: string, payload: UpdateModPayload): Promise<ModItem> {
    const res = await api.put<ApiResponse<ModItem>>(`/mods/${modId}`, payload);
    return res.data.data;
  },

  /**
   * 删除自定义 Mod
   */
  async deleteMod(modId: string): Promise<{ deleted_id: string }> {
    const res = await api.delete<ApiResponse<{ deleted_id: string }>>(`/mods/${modId}`);
    return res.data.data;
  },
};
