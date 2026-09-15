/**
 * 用户认证与个人中心 API 服务
 *
 * @packageDocumentation
 */

import api, { type ApiResponse } from "./api";

export interface UserWalletData {
  star_coins: number;
  moon_gems: number;
}

export interface UserProfileData {
  id: string;
  email: string;
  username: string;
  is_custom_username?: boolean;
  avatar_url: string;
  vip_level: number;
  player_level: number;
  player_xp: number;
  creator_level: number;
  creator_xp: number;
  invite_code: string;
  badges: Array<{
    id: string;
    name: string;
    color?: string;
    description?: string;
  }>;
  wallet: UserWalletData;
}

export interface AuthSuccessData {
  access_token: string;
  token_type: string;
  user: UserProfileData;
}

export interface DailyRewardData {
  reward_star_coins: number;
  new_balance: number;
  consecutive_days: number;
  message: string;
}

export interface WalletTransactionItem {
  id: string;
  type: string;
  currency: string;
  amount: number;
  balance_after: number;
  model_id?: string;
  target_character_id?: string;
  description?: string;
  created_at: string;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface InviteInfoData {
  invite_code: string;
  invite_url: string;
  invited_count: number;
  reward_earned_star: number;
}

export const authService = {
  /** 用户注册 */
  async register(payload: {
    email: string;
    password: string;
    code?: string;
    invite_code?: string;
  }) {
    const res = await api.post<ApiResponse<AuthSuccessData>>("/auth/register", {
      code: "888888",
      ...payload,
    });
    return res.data;
  },

  /** 用户登录 */
  async login(payload: { email: string; password: string }) {
    const res = await api.post<ApiResponse<AuthSuccessData>>("/auth/login", payload);
    return res.data;
  },

  /** 退出登录 */
  async logout() {
    const res = await api.post<ApiResponse<null>>("/auth/logout");
    return res.data;
  },

  /** 获取当前登录用户完整资料 */
  async getProfile() {
    const res = await api.get<ApiResponse<UserProfileData>>("/user/profile");
    return res.data;
  },

  /** 更新当前用户个人资料（昵称、头像） */
  async updateProfile(payload: { username: string; avatar_url?: string }) {
    const res = await api.put<ApiResponse<UserProfileData>>("/user/profile", payload);
    return res.data;
  },

  /** 每日签到领星元 */
  async claimDailyReward() {
    const res = await api.post<ApiResponse<DailyRewardData>>("/user/daily-reward");
    return res.data;
  },

  /** 获取资产交易明细 */
  async getTransactions(page = 1, pageSize = 20) {
    const res = await api.get<ApiResponse<PaginatedResult<WalletTransactionItem>>>(
      `/user/wallet/transactions?page=${page}&page_size=${pageSize}`,
    );
    return res.data;
  },

  /** 获取邀请活动与统计数据 */
  async getInviteInfo() {
    const res = await api.get<ApiResponse<InviteInfoData>>("/user/invite-info");
    return res.data;
  },
};
