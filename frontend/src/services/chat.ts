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

export interface StoryBranchDetail {
  id: string;
  session_id: string;
  name: string;
  parent_branch_id?: string | null;
  fork_message_id?: string | null;
  is_main: boolean;
  node_count: number;
  total_path_count: number;
  created_at: string;
}

export interface DAGNode {
  id: string;
  message_id: string;
  branch_id: string;
  branch_name: string;
  sender: "user" | "ai" | "system";
  character_name?: string | null;
  avatar_url?: string | null;
  content: string;
  summary: string;
  timestamp: string;
  is_current: boolean;
  is_main: boolean;
  is_fork_point: boolean;
  parent_message_id?: string | null;
}

export interface DAGEdge {
  id: string;
  source: string;
  target: string;
  is_main: boolean;
}

export interface DAGGraph {
  nodes: DAGNode[];
  edges: DAGEdge[];
  active_branch_id: string;
  active_message_id?: string | null;
}

export interface ForkBranchPayload {
  fork_message_id: string;
  name?: string;
  switch_to?: boolean;
}

export interface RollbackPayload {
  target_message_id: string;
  mode: "fork" | "truncate";
  branch_name?: string;
}

export interface EditMessagePayload {
  content: string;
  mode: "edit_only" | "edit_and_fork";
  branch_name?: string;
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
  character_alternate_greetings?: string[];
  character_extensions?: Record<string, any>;
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
  client_message_id?: string | null;
}

export interface ControlPanelDTO {
  user_name: string;
  user_persona: string;
  custom_prompt: string;
  variables: Record<string, any>;
  memory_blocks: Array<{ id: string; title: string; content: string; enabled: boolean }>;
  text_replacements: Array<{ id: string; fromText: string; toText: string }>;
}

export interface NarrativeStateDTO {
  date_text: string;
  time_text: string;
  location: string;
  present_characters: string[];
  player_states: Array<Record<string, any>>;
  consumables: Array<Record<string, any>>;
  important_items: Array<Record<string, any>>;
  skills: Array<Record<string, any>>;
  social_relations: Array<Record<string, any>>;
  tasks: Array<Record<string, any>>;
  history_events: Array<Record<string, any>>;
}

export interface StreamUsageData {
  message_id: string;
  user_message_id?: string;
  input_tokens: number;
  output_tokens: number;
  cost: number;
  currency: "star" | "moon";
  cleaned_content?: string;
}

export interface StreamCallbacks {
  onThinking?: (chunk: string) => void;
  onMessage?: (chunk: string) => void;
  onUsage?: (usage: StreamUsageData) => void;
  onStateUpdated?: (data: { narrative_state?: NarrativeStateDTO; control_panel?: ControlPanelDTO }) => void;
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
            } else if (eventType === "state_updated") {
              callbacks.onStateUpdated?.(parsed as { narrative_state?: NarrativeStateDTO; control_panel?: ControlPanelDTO });
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
    const res = await api.put<ApiResponse<{ is_pinned: boolean }>>(
      `/chat/sessions/${sessionId}/pin`,
    );
    return res.data.data.is_pinned;
  },

  /**
   * 更新会话用户备注
   */
  async updateSessionRemark(sessionId: string, remark: string): Promise<string> {
    const res = await api.put<ApiResponse<{ remark: string }>>(
      `/chat/sessions/${sessionId}/remark`,
      { remark },
    );
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

  /**
   * 切换会话开场白 (支持在 default first_mes 与 alternate_greetings 间轮换)
   */
  async switchGreeting(sessionId: string, greetingIndex: number): Promise<ChatMessageItem> {
    const res = await api.post<ApiResponse<ChatMessageItem>>(
      `/chat/sessions/${sessionId}/greeting`,
      { greeting_index: greetingIndex },
    );
    return res.data.data;
  },

  /**
   * 获取指定会话的所有剧情分支列表及节点统计
   */
  async getBranches(sessionId: string): Promise<StoryBranchDetail[]> {
    const res = await api.get<ApiResponse<StoryBranchDetail[]>>(
      `/chat/sessions/${sessionId}/branches`,
    );
    return res.data.data;
  },

  /**
   * 从指定历史消息节点派生新分支
   */
  async forkBranch(sessionId: string, payload: ForkBranchPayload): Promise<StoryBranchDetail> {
    const res = await api.post<ApiResponse<StoryBranchDetail>>(
      `/chat/sessions/${sessionId}/branches/fork`,
      payload,
    );
    return res.data.data;
  },

  /**
   * 切换活跃剧情分支
   */
  async switchBranch(sessionId: string, branchId: string): Promise<ChatSessionDetail> {
    const res = await api.put<ApiResponse<ChatSessionDetail>>(
      `/chat/sessions/${sessionId}/branches/${branchId}/switch`,
    );
    return res.data.data;
  },

  /**
   * 删除非主线剧情分支
   */
  async deleteBranch(sessionId: string, branchId: string): Promise<void> {
    await api.delete(`/chat/sessions/${sessionId}/branches/${branchId}`);
  },

  /**
   * 回溯至指定消息节点
   */
  async rollbackToMessage(sessionId: string, payload: RollbackPayload): Promise<ChatSessionDetail> {
    const res = await api.post<ApiResponse<ChatSessionDetail>>(
      `/chat/sessions/${sessionId}/rollback`,
      payload,
    );
    return res.data.data;
  },

  /**
   * 从指定消息节点分叉并创建全新独立聊天会话 (多历史记录)
   */
  async forkSession(
    sessionId: string,
    payload: { fork_message_id: string; remark?: string },
  ): Promise<ChatSessionDetail> {
    const res = await api.post<ApiResponse<ChatSessionDetail>>(
      `/chat/sessions/${sessionId}/fork-session`,
      payload,
    );
    return res.data.data;
  },

  /**
   * 编辑消息 (支持原位保存与分叉派生)
   */
  async editMessage(
    sessionId: string,
    messageId: string,
    payload: EditMessagePayload,
  ): Promise<ChatSessionDetail> {
    const res = await api.put<ApiResponse<ChatSessionDetail>>(
      `/chat/sessions/${sessionId}/messages/${messageId}`,
      payload,
    );
    return res.data.data;
  },

  /**
   * 获取 Vue Flow 全景剧情树拓扑图
   */
  async getStoryTree(sessionId: string): Promise<DAGGraph> {
    const res = await api.get<ApiResponse<DAGGraph>>(`/chat/sessions/${sessionId}/tree`);
    return res.data.data;
  },

  /**
   * 获取指定会话的主控面板配置 (38 变量矩阵与指令)
   */
  async getControlPanel(sessionId: string): Promise<ControlPanelDTO> {
    const res = await api.get<ApiResponse<ControlPanelDTO>>(
      `/chat/sessions/${sessionId}/control-panel`,
    );
    return res.data.data;
  },

  /**
   * 更新指定会话的主控面板配置
   */
  async updateControlPanel(sessionId: string, payload: ControlPanelDTO): Promise<ControlPanelDTO> {
    const res = await api.put<ApiResponse<ControlPanelDTO>>(
      `/chat/sessions/${sessionId}/control-panel`,
      payload,
    );
    return res.data.data;
  },

  /**
   * 获取指定会话的叙梦 6 大 Tab 状态机
   */
  async getNarrativeState(sessionId: string): Promise<NarrativeStateDTO> {
    const res = await api.get<ApiResponse<NarrativeStateDTO>>(
      `/chat/sessions/${sessionId}/narrative-state`,
    );
    return res.data.data;
  },

  /**
   * 更新指定会话的叙梦 6 大 Tab 状态机
   */
  async updateNarrativeState(
    sessionId: string,
    payload: NarrativeStateDTO,
  ): Promise<NarrativeStateDTO> {
    const res = await api.put<ApiResponse<NarrativeStateDTO>>(
      `/chat/sessions/${sessionId}/narrative-state`,
      payload,
    );
    return res.data.data;
  },

  /**
   * 获取后台配置并上架至客户端的大模型列表
   */
  async getAvailableModels(): Promise<ClientAvailableModel[]> {
    const res = await api.get<ApiResponse<ClientAvailableModel[]>>("/chat/models");
    return res.data.data;
  },
};

export interface ClientAvailableModel {
  id: string;
  name: string;
  familyId: string;
  category: "normal" | "advanced" | "infinite";
  health: number;
  cost: number;
  starCost: number;
  moonCost: number;
  freeCountText: string;
  isStreaming: boolean;
  supportsReasoning: boolean;
  isFavorite: boolean;
  isDefault: boolean;
}
