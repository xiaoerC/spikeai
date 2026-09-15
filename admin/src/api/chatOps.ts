/**
 * AI 对话会话与推理审计中心 API 强类型封装
 *
 * 提供全站 AI 会话大盘多维分页检索、消息流水全景历史回溯、推理思维链与 Token 消耗审计、违规涉密会话清理。
 *
 * Usage:
 *   >>> import { getChatSessionList, getChatTranscript, deleteChatSession } from '@/api/chatOps';
 */

import request from '@/utils/request';

export interface IChatSessionQuery {
  page?: number;
  size?: number;
  keyword?: string;
  model_id?: string;
}

export interface IAdminChatSessionItem {
  id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  user_avatar: string;
  character_id: string;
  character_name: string;
  character_avatar: string;
  current_model_id: string;
  mode: string;
  remark: string;
  is_pinned: boolean;
  message_count: number;
  total_tokens: number;
  created_at: string;
  updated_at: string;
}

export interface IAdminChatSessionPageResult {
  total: number;
  page: number;
  size: number;
  list: IAdminChatSessionItem[];
}

export interface IAdminChatMessageItem {
  id: string;
  sender: 'user' | 'ai' | 'system';
  character_name?: string | null;
  avatar_url?: string | null;
  content: string;
  thinking_content?: string;
  input_tokens: number;
  output_tokens: number;
  created_at: string;
}

export interface IAdminChatTranscriptResult {
  session: IAdminChatSessionItem;
  messages: IAdminChatMessageItem[];
}

/** 分页多维检索全站用户 AI 会话大盘 */
export function getChatSessionList(
  params: IChatSessionQuery,
): Promise<IAdminChatSessionPageResult> {
  return request({
    url: '/admin/chat/sessions',
    method: 'GET',
    params,
  });
}

/** 查看会话历史对话流与消息流水 */
export function getChatTranscript(sessionId: string): Promise<IAdminChatTranscriptResult> {
  return request({
    url: `/admin/chat/sessions/${sessionId}/transcript`,
    method: 'GET',
  });
}

/** 清理/删除涉密或违规会话 */
export function deleteChatSession(sessionId: string): Promise<{ code: number; message: string }> {
  return request({
    url: `/admin/chat/sessions/${sessionId}`,
    method: 'DELETE',
  });
}
