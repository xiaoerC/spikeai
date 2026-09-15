/**
 * 世界书 (World Book / Character Lorebook) 领域服务与 API 契约
 *
 * @packageDocumentation
 */

import api, { type ApiResponse } from "./api";

export interface WorldBookEntryItem {
  id: string;
  world_book_id: string;
  keys: string[];
  secondary_keys: string[];
  selective_logic: number; // 0: AND ANY, 1: NOT ALL, 2: NOT ANY
  content: string;
  comment: string;
  constant: boolean;
  enabled: boolean;
  insertion_order: number;
  position: string;
  created_at: string;
  updated_at: string;
}

export interface WorldBookItem {
  id: string;
  user_id: string;
  character_id?: string | null;
  name: string;
  description: string;
  entry_count: number;
  is_public: boolean;
  scan_depth: number;
  token_budget: number;
  created_at: string;
  updated_at: string;
}

export interface WorldBookDetail extends WorldBookItem {
  entries: WorldBookEntryItem[];
}

export interface CreateWorldBookEntryPayload {
  keys: string[];
  secondary_keys?: string[];
  selective_logic?: number;
  content: string;
  comment?: string;
  constant?: boolean;
  enabled?: boolean;
  insertion_order?: number;
  position?: string;
}

export interface UpdateWorldBookEntryPayload {
  keys?: string[];
  secondary_keys?: string[];
  selective_logic?: number;
  content?: string;
  comment?: string;
  constant?: boolean;
  enabled?: boolean;
  insertion_order?: number;
  position?: string;
}

export interface CreateWorldBookPayload {
  name: string;
  description?: string;
  character_id?: string | null;
  is_public?: boolean;
  scan_depth?: number;
  token_budget?: number;
  entries?: CreateWorldBookEntryPayload[];
}

export interface UpdateWorldBookPayload {
  name?: string;
  description?: string;
  is_public?: boolean;
  scan_depth?: number;
  token_budget?: number;
  character_id?: string | null;
}

export const worldBookService = {
  /**
   * 获取世界书列表
   */
  async listWorldBooks(characterId?: string): Promise<WorldBookItem[]> {
    const params = characterId ? { character_id: characterId } : {};
    const res = await api.get<ApiResponse<WorldBookItem[]>>("/world-books", { params });
    return (res.data as any).data || (res.data as any);
  },

  /**
   * 获取世界书详情 (包含全部条目)
   */
  async getWorldBookDetail(worldBookId: string): Promise<WorldBookDetail> {
    const res = await api.get<ApiResponse<WorldBookDetail>>(`/world-books/${worldBookId}`);
    return (res.data as any).data || (res.data as any);
  },

  /**
   * 创建新世界书
   */
  async createWorldBook(payload: CreateWorldBookPayload): Promise<WorldBookDetail> {
    const res = await api.post<ApiResponse<WorldBookDetail>>("/world-books", payload);
    return (res.data as any).data || (res.data as any);
  },

  /**
   * 更新世界书元数据
   */
  async updateWorldBook(
    worldBookId: string,
    payload: UpdateWorldBookPayload,
  ): Promise<WorldBookItem> {
    const res = await api.put<ApiResponse<WorldBookItem>>(`/world-books/${worldBookId}`, payload);
    return (res.data as any).data || (res.data as any);
  },

  /**
   * 删除世界书
   */
  async deleteWorldBook(worldBookId: string): Promise<void> {
    await api.delete(`/world-books/${worldBookId}`);
  },

  /**
   * 为世界书追加新条目
   */
  async addEntry(
    worldBookId: string,
    payload: CreateWorldBookEntryPayload,
  ): Promise<WorldBookEntryItem> {
    const res = await api.post<ApiResponse<WorldBookEntryItem>>(
      `/world-books/${worldBookId}/entries`,
      payload,
    );
    return (res.data as any).data || (res.data as any);
  },

  /**
   * 更新单个条目
   */
  async updateEntry(
    entryId: string,
    payload: UpdateWorldBookEntryPayload,
  ): Promise<WorldBookEntryItem> {
    const res = await api.put<ApiResponse<WorldBookEntryItem>>(
      `/world-books/entries/${entryId}`,
      payload,
    );
    return (res.data as any).data || (res.data as any);
  },

  /**
   * 删除单个条目
   */
  async deleteEntry(entryId: string): Promise<void> {
    await api.delete(`/world-books/entries/${entryId}`);
  },

  /**
   * 导入 SillyTavern JSON 格式世界书
   */
  async importSillyTavern(payload: {
    name: string;
    description?: string;
    character_id?: string | null;
    entries: any;
  }): Promise<WorldBookDetail> {
    const res = await api.post<ApiResponse<WorldBookDetail>>(
      "/world-books/import-sillytavern",
      payload,
    );
    return (res.data as any).data || (res.data as any);
  },

  /**
   * 导出为 SillyTavern JSON 格式
   */
  async exportSillyTavern(worldBookId: string): Promise<any> {
    const res = await api.get<ApiResponse<any>>(`/world-books/${worldBookId}/export-sillytavern`);
    return (res.data as any).data || (res.data as any);
  },
};
