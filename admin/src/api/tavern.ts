/**
 * SillyTavern 全局酒馆调音台与 Prompt 流水线中枢 API 契约封装
 *
 * 负责平台级 78 项 Transformer 提示词排版流水线配置、大模型物理采样超参数调优、
 * 出厂默认一键回滚与版本历史查询。
 *
 * Usage:
 *   >>> import { getAdminTavernPreset, updateAdminTavernPreset } from '@/api/tavern';
 *   >>> const res = await getAdminTavernPreset();
 */

import request from '@/utils/request';

export interface TavernPromptItem {
  identifier: string;
  name: string;
  role?: 'system' | 'user' | 'assistant' | string;
  content?: string;
  system_prompt?: boolean;
  marker?: boolean;
  enabled?: boolean;
  injection_position?: number;
  injection_depth?: number;
  forbid_overrides?: boolean;
  injection_trigger?: string[];
  [key: string]: any;
}

export interface TavernPromptOrderItem {
  identifier: string;
  enabled: boolean;
  is_unordered_backup?: boolean;
}

export interface TavernRegexScript {
  id: string;
  scriptName: string;
  findRegex: string;
  replaceString?: string;
  trimStrings?: string[];
  placement: number[]; // 1=用户输入, 2=AI输出, 3=快捷命令, 4=世界书, 5=推理
  disabled?: boolean;
  markdownOnly?: boolean;
  promptOnly?: boolean;
  runOnEdit?: boolean;
  substituteRegex?: number;
  minDepth?: number | null;
  maxDepth?: number | null;
}

export interface TavernAdvancedFormatting {
  // 1. 思维链治理 (Reasoning & CoT)
  parse_think_tags: boolean;
  reasoning_history_depth: number;
  auto_expand_reasoning: boolean;

  // 2. 历史后置指令 (Post-History Instruction)
  enable_post_history_instruction: boolean;
  post_history_instruction: string;
  post_history_depth: number;

  // 3. 自定义停止字符串 (Stop Sequences)
  stop_sequences: string[];
  char_name_as_stop: boolean;
  user_name_as_stop: boolean;

  // 4. 文本清洗流水线 (Text Cleaning Pipeline)
  collapse_newlines: boolean;
  trim_incomplete_sentences: boolean;
  trim_whitespace: boolean;

  // 5. 回复引导 (Assistant Prefill)
  reply_prefix: string;
  show_reply_prefix: boolean;
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
  reasoning_effort: 'low' | 'medium' | 'high' | 'auto';
  squash_system_messages?: boolean;
  prompts: TavernPromptItem[];
  prompt_order: TavernPromptOrderItem[];
  regex_scripts?: TavernRegexScript[];
  advanced_formatting?: TavernAdvancedFormatting;
}

export interface TavernPresetListItem {
  id: string;
  preset_name: string;
  is_active: boolean;
  temperature: number;
  top_p: number;
  prompts_count: number;
  active_prompts_count: number;
  regex_count?: number;
  updated_at?: string | null;
  updated_by?: string | null;
  description?: string | null;
}

export type TavernPresetVersionItem = TavernPresetListItem;

/**
 * 获取全平台当前全局生效的酒馆预设
 */
export function getAdminTavernPreset(): Promise<{
  code: number;
  data: TavernPresetConfig;
  message: string;
}> {
  return request({
    url: '/admin/tavern/preset',
    method: 'get',
  });
}

/**
 * 获取官方出厂默认「仓鼠之神V2」原始预设配置 (只读基准，用于单项还原对比)
 */
export function getAdminTavernDefaultPreset(): Promise<{
  code: number;
  data: TavernPresetConfig;
  message: string;
}> {
  return request({
    url: '/admin/tavern/default-preset',
    method: 'get',
  });
}

/**
 * 保存并全平台热发布全局生效的酒馆预设
 */
export function updateAdminTavernPreset(
  data: TavernPresetConfig,
): Promise<{ code: number; data: TavernPresetConfig; message: string }> {
  return request({
    url: '/admin/tavern/preset',
    method: 'put',
    data,
  });
}

/**
 * 一键恢复全平台官方出厂原版「仓鼠之神V2」预设
 */
export function resetAdminTavernPreset(): Promise<{
  code: number;
  data: TavernPresetConfig;
  message: string;
}> {
  return request({
    url: '/admin/tavern/reset',
    method: 'post',
  });
}

/**
 * 获取平台预设库全部自导入/已保存预设列表
 */
export function listAdminTavernPresets(): Promise<{
  code: number;
  data: TavernPresetListItem[];
  message: string;
}> {
  return request({
    url: '/admin/tavern/presets',
    method: 'get',
  });
}

/**
 * 根据 ID 获取指定预设详情
 */
export function getAdminTavernPresetById(id: string): Promise<{
  code: number;
  data: TavernPresetConfig;
  message: string;
}> {
  return request({
    url: `/admin/tavern/presets/${id}`,
    method: 'get',
  });
}

/**
 * 导入或新建一个预设入库
 */
export function createAdminTavernPreset(
  data: TavernPresetConfig,
  isActive = false,
  description?: string,
): Promise<{
  code: number;
  data: {
    id: string;
    preset_name: string;
    is_active: boolean;
    description?: string;
    updated_at?: string;
    updated_by?: string;
  };
  message: string;
}> {
  return request({
    url: '/admin/tavern/presets',
    method: 'post',
    params: { is_active: isActive, description },
    data,
  });
}

/**
 * 更新指定已有预设的配置
 */
export function updateAdminTavernPresetById(
  id: string,
  data: TavernPresetConfig,
): Promise<{
  code: number;
  data: {
    id: string;
    preset_name: string;
    is_active: boolean;
    updated_at?: string;
    updated_by?: string;
  };
  message: string;
}> {
  return request({
    url: `/admin/tavern/presets/${id}`,
    method: 'put',
    data,
  });
}

/**
 * 将指定预设激活设为全平台全局生效
 */
export function activateAdminTavernPreset(id: string): Promise<{
  code: number;
  data: TavernPresetConfig;
  message: string;
}> {
  return request({
    url: `/admin/tavern/presets/${id}/activate`,
    method: 'post',
  });
}

/**
 * 删除指定非生效预设
 */
export function deleteAdminTavernPreset(id: string): Promise<{
  code: number;
  data: boolean;
  message: string;
}> {
  return request({
    url: `/admin/tavern/presets/${id}`,
    method: 'delete',
  });
}

/**
 * 重命名指定预设
 */
export function renameAdminTavernPreset(
  id: string,
  name: string,
): Promise<{
  code: number;
  data: { id: string; preset_name: string };
  message: string;
}> {
  return request({
    url: `/admin/tavern/presets/${id}/rename`,
    method: 'post',
    data: { name },
  });
}
