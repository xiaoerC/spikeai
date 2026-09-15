/**
 * C 端用户治理与资产中心 API 强类型封装
 *
 * 提供 C 端用户画像检索、账号状态封禁/解冻、钱包明细查询及管理员人工调账功能。
 *
 * Usage:
 *   >>> import { getCUserList, updateCUserStatus, getWalletTransactions, adjustUserWallet } from '@/api/cUser';
 */

import request from '@/utils/request';

export interface ICUserQuery {
  page?: number;
  size?: number;
  keyword?: string;
  status?: string;
}

export interface ICUserItem {
  id: string;
  email: string;
  username: string;
  avatar_url: string;
  status: string; // active | banned | suspended
  invite_code: string;
  vip_level: number;
  player_level: number;
  player_xp: number;
  creator_level: number;
  creator_xp: number;
  star_coins: number;
  moon_gems: number;
  character_count: number;
  chat_session_count: number;
  created_at: string;
  updated_at: string;
}

export interface ICUserPageResult {
  total: number;
  page: number;
  size: number;
  list: ICUserItem[];
}

export interface ICUserStatusPayload {
  status: 'active' | 'banned' | 'suspended';
  reason?: string;
}

export interface IWalletTransactionItem {
  id: string;
  user_id: string;
  type: string;
  currency: 'star' | 'moon';
  amount: number;
  balance_after: number;
  description: string | null;
  created_at: string;
}

export interface IWalletTransactionPageResult {
  total: number;
  page: number;
  size: number;
  list: IWalletTransactionItem[];
}

export interface IWalletAdjustPayload {
  currency: 'star' | 'moon';
  action: 'add' | 'sub';
  amount: number;
  reason: string;
}

/** 分页查询 C 端用户画像列表 */
export function getCUserList(params: ICUserQuery): Promise<ICUserPageResult> {
  return request({
    url: '/admin/c-users',
    method: 'GET',
    params,
  });
}

/** 变更 C 端用户状态 (封禁/解冻) */
export function updateCUserStatus(
  userId: string,
  data: ICUserStatusPayload,
): Promise<{ code: number; message: string; data: { user_id: string; status: string } }> {
  return request({
    url: `/admin/c-users/${userId}/status`,
    method: 'POST',
    data,
  });
}

/** 查询指定 C 端用户钱包变动流水 */
export function getWalletTransactions(
  userId: string,
  params: { page?: number; size?: number; currency?: string },
): Promise<IWalletTransactionPageResult> {
  return request({
    url: `/admin/c-users/${userId}/wallet-transactions`,
    method: 'GET',
    params,
  });
}

/** 管理员人工调账 (增扣星元或月华) */
export function adjustUserWallet(
  userId: string,
  data: IWalletAdjustPayload,
): Promise<{
  code: number;
  message: string;
  data: { user_id: string; currency: string; delta: number; balance_after: number };
}> {
  return request({
    url: `/admin/c-users/${userId}/wallet/adjust`,
    method: 'POST',
    data,
  });
}
