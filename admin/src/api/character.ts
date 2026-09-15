/**
 * AI 角色卡与设定集审核及治理中心 API 强类型封装
 *
 * 提供全量角色卡资产分页检索、上下架/违规下架审核、深层提示词画像与世界书词条档案透视。
 *
 * Usage:
 *   >>> import { getCharacterList, updateCharacterStatus, getCharacterDetail } from '@/api/character';
 */

import request from '@/utils/request';

export interface ICharacterQuery {
  page?: number;
  size?: number;
  keyword?: string;
  category?: string;
  status?: string;
}

export interface IWorldBookEntryItem {
  id: string;
  keys: string[];
  content: string;
  constant: boolean;
  position: string;
}

export interface IAdminCharacterItem {
  id: string;
  name: string;
  avatar_url: string;
  banner_url?: string | null;
  category: string;
  description: string;
  status: string; // published | draft | private | banned
  tags: string[];
  settings_word_count: number;
  version: string;
  author_id: string;
  author_name: string;
  author_email: string;
  chat_count: number;
  like_count: number;
  favorite_count: number;
  rating: number;
  worldbook_entry_count: number;
  created_at: string;
  updated_at: string;
}

export interface IAdminCharacterPageResult {
  total: number;
  page: number;
  size: number;
  list: IAdminCharacterItem[];
}

export interface IAdminCharacterStatusPayload {
  status: 'published' | 'private' | 'banned';
  reason?: string;
}

export interface IAdminCharacterDetail extends IAdminCharacterItem {
  personality: string;
  scenario: string;
  first_mes: string;
  system_prompt: string;
  post_history_instructions: string;
  prologue_title: string;
  creator_notes: string;
  alternate_greetings: string[];
  worldbook_entries: IWorldBookEntryItem[];
}

/** 分页多维检索角色卡列表 */
export function getCharacterList(params: ICharacterQuery): Promise<IAdminCharacterPageResult> {
  return request({
    url: '/admin/characters',
    method: 'GET',
    params,
  });
}

/** 审核或变更角色卡状态 (上架/私密/违规下架) */
export function updateCharacterStatus(
  charId: string,
  data: IAdminCharacterStatusPayload,
): Promise<{ code: number; message: string; data: { character_id: string; status: string } }> {
  return request({
    url: `/admin/characters/${charId}/status`,
    method: 'POST',
    data,
  });
}

/** 查看角色卡深层提示词档案与世界书详情 */
export function getCharacterDetail(charId: string): Promise<IAdminCharacterDetail> {
  return request({
    url: `/admin/characters/${charId}/detail`,
    method: 'GET',
  });
}

/** 软删除单张已下架角色卡 (移入回收站) */
export function deleteCharacter(charId: string): Promise<{ code: number; message: string }> {
  return request({
    url: `/admin/characters/${charId}`,
    method: 'DELETE',
  });
}

/** 批量软删除已下架角色卡 */
export function batchDeleteCharacters(
  characterIds: string[],
): Promise<{ code: number; message: string; count: number }> {
  return request({
    url: '/admin/characters/batch-delete',
    method: 'POST',
    data: { character_ids: characterIds },
  });
}

/** 从回收站恢复角色卡 */
export function restoreCharacter(charId: string): Promise<{ code: number; message: string }> {
  return request({
    url: `/admin/characters/${charId}/restore`,
    method: 'POST',
  });
}

/** 彻底物理粉碎角色卡 (不可逆) */
export function destroyCharacter(charId: string): Promise<{ code: number; message: string }> {
  return request({
    url: `/admin/characters/${charId}/destroy`,
    method: 'DELETE',
  });
}

/** 批量彻底物理粉碎角色卡 */
export function batchDestroyCharacters(
  characterIds: string[],
): Promise<{ code: number; message: string; count: number }> {
  return request({
    url: '/admin/characters/batch-destroy',
    method: 'POST',
    data: { character_ids: characterIds },
  });
}
