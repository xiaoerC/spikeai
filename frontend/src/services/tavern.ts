/**
 * SillyTavern (酒馆) 预设与调音台前端服务接口。
 *
 * @packageDocumentation
 */

import api, { type ApiResponse } from "@/services/api";

export interface TavernPromptItem {
  identifier: string;
  name: string;
  role?: "system" | "user" | "assistant" | string;
  content?: string;
  system_prompt?: boolean;
  marker?: boolean;
  enabled?: boolean;
  injection_position?: number;
  injection_depth?: number;
  forbid_overrides?: boolean;
  [key: string]: any;
}

export interface TavernPromptOrderItem {
  identifier: string;
  enabled: boolean;
}

export interface TavernPresetConfig {
  preset_name: string;
  is_active: boolean;
  temperature: number;
  frequency_penalty: number;
  presence_penalty: number;
  top_p: number;
  top_k?: number;
  top_a?: number;
  min_p?: number;
  repetition_penalty?: number;
  max_context_unlocked: boolean;
  openai_max_context: number;
  openai_max_tokens: number;
  stream_openai: boolean;
  seed: number;
  reasoning_effort: "low" | "medium" | "high" | "auto";
  squash_system_messages?: boolean;
  prompts: TavernPromptItem[];
  prompt_order: TavernPromptOrderItem[];
}

export const TavernApi = {
  /**
   * 获取当前生效的酒馆预设 (若未自定义则自动返回官方仓鼠之神V2默认)
   */
  async getPreset(): Promise<TavernPresetConfig> {
    const res = await api.get<ApiResponse<TavernPresetConfig>>("/tavern/preset");
    return res.data.data;
  },

  /**
   * 更新或保存酒馆预设
   */
  async updatePreset(preset: TavernPresetConfig): Promise<TavernPresetConfig> {
    const res = await api.put<ApiResponse<TavernPresetConfig>>("/tavern/preset", preset);
    return res.data.data;
  },

  /**
   * 一键恢复为官方原版「仓鼠之神V2」预设
   */
  async resetPreset(): Promise<TavernPresetConfig> {
    const res = await api.post<ApiResponse<TavernPresetConfig>>("/tavern/reset");
    return res.data.data;
  },

  /**
   * 获取预设库列表 (含官方与自建)
   */
  async listPresets(): Promise<any[]> {
    const res = await api.get<ApiResponse<any[]>>("/tavern/presets");
    return res.data.data;
  },

  /**
   * 另存为自定义命名预设
   */
  async saveNamedPreset(preset: TavernPresetConfig): Promise<TavernPresetConfig> {
    const res = await api.post<ApiResponse<TavernPresetConfig>>("/tavern/presets", preset);
    return res.data.data;
  },

  /**
   * 删除自定义预设
   */
  async deleteNamedPreset(presetName: string): Promise<boolean> {
    const res = await api.delete<ApiResponse<boolean>>(
      `/tavern/presets/${encodeURIComponent(presetName)}`,
    );
    return res.data.data;
  },
};
