/**
 * AI 沉浸式对话与 SSE 流式生成服务
 *
 * @packageDocumentation
 */

import api, { type ApiResponse } from "./api";

export interface ChatMessageItem {
  id: string;
  session_id: string;
  branch_id: string;
  sender: "user" | "ai" | "system";
  character_name?: string | null;
  avatar_url?: string | null;
  content: string;
  thinking_content?: string;
  input_tokens?: number;
  output_tokens?: number;
  parent_message_id?: string | null;
  created_at: string;
}

export interface StoryBranchItem {
  id: string;
  session_id: string;
  name: string;
  parent_branch_id?: string | null;
  fork_message_id?: string | null;
  is_main: boolean;
  created_at: string;
}

export interface ChatSessionDetail {
  id: string;
  character_id: string;
  character_name: string;
  character_avatar: string;
  character_banner?: string | null;
  character_author_note?: string;
  character_prologue_title?: string;
  character_prologue_html?: string;
  character_tags?: string[];
  current_branch_id: string;
  current_model_id: string;
  mode: "story" | "room";
  branches: StoryBranchItem[];
  messages: ChatMessageItem[];
  created_at: string;
  updated_at: string;
}

export interface ChatSessionListItem {
  id: string;
  character_id: string;
  title: string;
  avatar: string;
  banner_url?: string | null;
  last_message: string;
  last_message_time: string;
  message_count: number;
  is_pinned: boolean;
  remark: string;
  updated_at: string;
}

export interface SendMessagePayload {
  content: string;
  model_id: string;
  mode?: "story" | "room";
  parent_message_id?: string | null;
}

export interface StreamUsageData {
  message_id: string;
  input_tokens: number;
  output_tokens: number;
  cost: number;
  currency: "star" | "moon";
}

export interface StreamCallbacks {
  onThinking?: (chunk: string) => void;
  onMessage?: (chunk: string) => void;
  onUsage?: (usage: StreamUsageData) => void;
  onError?: (error: { code?: string; message: string }) => void;
  onDone?: () => void;
}

export const chatService = {
  /**
   * 获取或初始化与角色的对话会话
   */
  async getSessionByCharacter(characterId: string): Promise<ChatSessionDetail> {
    const res = await api.get<ApiResponse<ChatSessionDetail>>(
      `/chat/sessions/by-character/${characterId}`,
    );
    return res.data.data;
  },

  /**
   * 获取指定会话详情
   */
  async getSessionDetail(sessionId: string): Promise<ChatSessionDetail> {
    const res = await api.get<ApiResponse<ChatSessionDetail>>(`/chat/sessions/${sessionId}`);
    return res.data.data;
  },

  /**
   * 发起 SSE 流式对话并实时消费
   */
  async streamMessage(
    sessionId: string,
    payload: SendMessagePayload,
    callbacks: StreamCallbacks,
    signal?: AbortSignal,
  ): Promise<void> {
    const token = localStorage.getItem("naro_access_token");
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
    };
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    let hasError = false;

    let response: Response;
    try {
      response = await fetch(`/api/v1/chat/sessions/${sessionId}/stream`, {
        method: "POST",
        headers,
        body: JSON.stringify(payload),
        signal,
      });
    } catch (err: any) {
      if (err.name === "AbortError") {
        callbacks.onDone?.();
        return;
      }
      callbacks.onError?.({
        code: "NETWORK_ERROR",
        message: "网络连接失败，请检查网络连接或后端服务状态",
      });
      return;
    }

    if (!response.ok) {
      hasError = true;
      let errCode = "HTTP_ERROR";
      let errMsg = `请求失败 (${response.status})`;

      try {
        const errJson = await response.json();
        errMsg = errJson.message || errJson.detail || errMsg;
        errCode = errJson.code ? String(errJson.code) : errCode;
      } catch {
        const text = await response.text().catch(() => "");
        if (text) errMsg = text;
      }

      if (response.status === 401) {
        errCode = "UNAUTHORIZED";
        errMsg = "登录状态已失效，请重新登录";
      } else if (response.status === 403 || response.status === 402) {
        errCode = "INSUFFICIENT_BALANCE";
        errMsg = "星元余额不足，请领取每日福利或充值";
      } else if (response.status === 429) {
        errCode = "RATE_LIMIT";
        errMsg = "当前大模型请求过于频繁，请稍候再试";
      } else if (response.status >= 500) {
        errCode = "SERVER_ERROR";
        errMsg = "大模型服务网关响应异常，请稍后重试";
      }

      callbacks.onError?.({ code: errCode, message: errMsg });
      return;
    }

    if (!response.body) {
      callbacks.onError?.({ code: "EMPTY_BODY", message: "未获取到 SSE 响应流数据" });
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const block of lines) {
          if (!block.trim()) continue;

          let eventType = "message";
          let dataStr = "";

          const subLines = block.split("\n");
          for (const l of subLines) {
            if (l.startsWith("event: ")) {
              eventType = l.slice(7).trim();
            } else if (l.startsWith("data: ")) {
              dataStr = l.slice(6).trim();
            }
          }

          if (!dataStr) continue;

          try {
            const parsed = JSON.parse(dataStr);
            if (eventType === "thinking") {
              callbacks.onThinking?.(parsed.chunk || "");
            } else if (eventType === "message") {
              callbacks.onMessage?.(parsed.chunk || "");
            } else if (eventType === "usage") {
              callbacks.onUsage?.(parsed as StreamUsageData);
            } else if (eventType === "error") {
              hasError = true;
              callbacks.onError?.(parsed);
            } else if (eventType === "done") {
              callbacks.onDone?.();
            }
          } catch {
            if (eventType === "message") {
              callbacks.onMessage?.(dataStr);
            }
          }
        }
      }
    } catch (err: any) {
      if (err.name === "AbortError") {
        callbacks.onDone?.();
      } else {
        hasError = true;
        callbacks.onError?.({ code: "STREAM_ABORTED", message: err.message || "流式传输异常中断" });
      }
    } finally {
      if (!hasError) {
        callbacks.onDone?.();
      }
    }
  },

  /**
   * 中止当前生成
   */
  async stopGeneration(sessionId: string): Promise<void> {
    await api.post(`/chat/sessions/${sessionId}/stop`);
  },

  /**
   * 获取当前用户的所有历史聊天会话列表
   */
  async getChatSessions(): Promise<ChatSessionListItem[]> {
    const res = await api.get<ApiResponse<ChatSessionListItem[]>>("/chat/sessions");
    return res.data.data;
  },

  /**
   * 置顶/取消置顶会话
   */
  async togglePinSession(sessionId: string): Promise<boolean> {
    const res = await api.put<ApiResponse<{ is_pinned: boolean }>>(`/chat/sessions/${sessionId}/pin`);
    return res.data.data.is_pinned;
  },

  /**
   * 更新会话用户备注
   */
  async updateSessionRemark(sessionId: string, remark: string): Promise<string> {
    const res = await api.put<ApiResponse<{ remark: string }>>(`/chat/sessions/${sessionId}/remark`, { remark });
    return res.data.data.remark;
  },

  /**
   * 删除指定会话
   */
  async deleteSession(sessionId: string): Promise<void> {
    await api.delete(`/chat/sessions/${sessionId}`);
  },

  /**
   * 清空会话历史消息
   */
  async clearSessionMessages(sessionId: string): Promise<void> {
    await api.post(`/chat/sessions/${sessionId}/clear`);
  },
};
