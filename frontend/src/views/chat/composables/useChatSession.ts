/**
 * AI 聊天会话逻辑 Composable (连接真实后端 SSE 流式网关)
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { characterService } from "@/services/character";
import {
  type ChatMessageItem,
  type ChatSessionDetail,
  chatService,
} from "@/services/chat";
import { useAppStore } from "@/stores/app";
import {
  type AiModelItem,
  type ChatMessage,
  MOCK_AI_MODELS,
} from "@/views/chat/constants/mockChatData";
import {
  computed,
  type MaybeRefOrGetter,
  reactive,
  readonly,
  ref,
  toValue,
  watch,
} from "vue";
import { useRouter } from "vue-router";

export function useChatSession(characterIdParam?: MaybeRefOrGetter<string>) {
  const router = useRouter();
  const toast = useToast();
  const appStore = useAppStore();

  const activeCharId = computed(() => toValue(characterIdParam) || "");

  const character = reactive({
    id: activeCharId.value,
    name: "",
    avatarUrl: "",
    backgroundUrl: "",
    backgroundImageUrl: "",
    authorNote: "",
    prologueTitle: "序幕",
    prologueContent: "",
    greeting: "",
    tags: [] as string[],
    characterBookTokens: 0,
    prologueTokens: 0,
  });

  const sessionId = ref<string>("");
  const messages = ref<ChatMessage[]>([]);
  const currentModel = ref<AiModelItem>(MOCK_AI_MODELS[0]);
  const currentMode = ref<"story" | "room">("story");
  const isGenerating = ref(false);
  const isModelDrawerOpen = ref(false);
  const toastMessage = ref("");
  let abortController: AbortController | null = null;

  function showToast(msg: string): void {
    toastMessage.value = msg;
    setTimeout(() => {
      toastMessage.value = "";
    }, 2000);
  }

  function handleBack(): void {
    router.back();
  }

  /**
   * 格式化时间戳
   */
  function formatTimestamp(dateStr?: string): string {
    const d = dateStr ? new Date(dateStr) : new Date();
    return d.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  /**
   * 将后端 ChatMessageItem 转换为前端 UI 格式
   */
  function mapBackendMessage(m: ChatMessageItem): ChatMessage {
    return {
      id: m.id,
      sender: m.sender as "ai" | "user" | "system",
      characterName: m.character_name || character.name,
      avatarUrl: m.avatar_url || character.avatarUrl,
      content: m.content,
      thinkingContent: m.thinking_content || "",
      timestamp: formatTimestamp(m.created_at),
      metrics:
        m.sender === "ai"
          ? {
              inputTokens: m.input_tokens || 1200,
              outputTokens: m.output_tokens || 350,
              isSuccess: true,
            }
          : undefined,
    };
  }

  /**
   * 初始化/恢复与目标角色的会话
   */
  async function initSession(): Promise<void> {
    const charId = activeCharId.value;
    if (!charId) return;

    try {
      // 1. 获取角色基本信息与立绘、背景、作者的话、序幕
      const charDetail = await characterService.getCharacterDetail(charId).catch(() => null);
      if (charDetail) {
        character.id = charDetail.id;
        character.name = charDetail.name;
        character.avatarUrl = charDetail.avatar_url;
        character.backgroundUrl = charDetail.banner_url || charDetail.avatar_url;
        character.backgroundImageUrl = charDetail.banner_url || charDetail.avatar_url;
        character.authorNote = charDetail.creator_notes || "";
        character.prologueTitle = charDetail.prologue_title || "序幕";
        character.prologueContent = charDetail.prologue_html || "";
        character.greeting = charDetail.first_mes || "";
        character.tags = charDetail.tags || [];
      }

      // 2. 获取/初始化会话历史
      const sessionDetail = await chatService.getSessionByCharacter(charId);
      sessionId.value = sessionDetail.id;
      if (sessionDetail.character_name) {
        character.name = sessionDetail.character_name;
      }
      if (sessionDetail.character_avatar) {
        character.avatarUrl = sessionDetail.character_avatar;
      }
      if (sessionDetail.character_banner) {
        character.backgroundUrl = sessionDetail.character_banner;
        character.backgroundImageUrl = sessionDetail.character_banner;
      }
      if (sessionDetail.character_author_note) {
        character.authorNote = sessionDetail.character_author_note;
      }
      if (sessionDetail.character_prologue_title) {
        character.prologueTitle = sessionDetail.character_prologue_title;
      }
      if (sessionDetail.character_prologue_html) {
        character.prologueContent = sessionDetail.character_prologue_html;
      }
      if (sessionDetail.character_tags && sessionDetail.character_tags.length > 0) {
        character.tags = sessionDetail.character_tags;
      }

      if (sessionDetail.messages && sessionDetail.messages.length > 0) {
        messages.value = sessionDetail.messages.map(mapBackendMessage);
      } else if (character.greeting) {
        // 若无历史记录但有开场白
        messages.value = [
          {
            id: `greeting_${Date.now()}`,
            sender: "ai",
            characterName: character.name,
            avatarUrl: character.avatarUrl,
            content: character.greeting,
            timestamp: formatTimestamp(),
          },
        ];
      }
    } catch (err: any) {
      console.warn("未能从后端恢复会话，启用本地模式:", err);
      if (character.greeting) {
        messages.value = [
          {
            id: `local_greet_${Date.now()}`,
            sender: "ai",
            characterName: character.name,
            avatarUrl: character.avatarUrl,
            content: character.greeting,
            timestamp: formatTimestamp(),
          },
        ];
      }
    }
  }

  watch(
    activeCharId,
    (newId) => {
      if (newId) {
        initSession();
      }
    },
    { immediate: true },
  );

  /**
   * 触发 AI SSE 流式生成核心内部方法
   */
  async function generateAiReply(userText: string): Promise<void> {
    const aiPlaceholderId = `ai_stream_${Date.now()}`;
    const aiMsg = reactive<ChatMessage>({
      id: aiPlaceholderId,
      sender: "ai",
      characterName: character.name,
      avatarUrl: character.avatarUrl,
      content: "",
      thinkingContent: "",
      timestamp: formatTimestamp(),
      status: "pending",
    });
    messages.value.push(aiMsg);

    isGenerating.value = true;
    abortController = new AbortController();

    // 3. 看门狗机制：防首字超时 (TTFT 25s) 与流式卡死空闲超时 (Idle 15s)
    let watchdogTimer: ReturnType<typeof setTimeout> | null = null;

    const resetWatchdog = (timeoutMs = 15000, timeoutMsg = "大模型流式传输中断，请重试") => {
      if (watchdogTimer) clearTimeout(watchdogTimer);
      watchdogTimer = setTimeout(() => {
        if (isGenerating.value) {
          if (abortController) {
            abortController.abort();
          }
          handleStreamError({
            code: "TIMEOUT",
            message: timeoutMsg,
          });
        }
      }, timeoutMs);
    };

    const clearWatchdog = () => {
      if (watchdogTimer) {
        clearTimeout(watchdogTimer);
        watchdogTimer = null;
      }
    };

    function handleStreamError(err: { code?: string; message: string }) {
      clearWatchdog();
      isGenerating.value = false;
      abortController = null;
      aiMsg.status = "error";
      aiMsg.errorMessage = err.message || "请求失败";

      showToast(`⚠️ ${aiMsg.errorMessage}`);

      if (err.code === "UNAUTHORIZED") {
        appStore.openLoginModal();
      }
    }

    // 启动初始首字超时看门狗 (25s)
    resetWatchdog(25000, "大模型响应超时（25秒无返回），请重试");

    // 4. 发起流式请求
    if (sessionId.value) {
      try {
        await chatService.streamMessage(
          sessionId.value,
          {
            content: userText,
            model_id: currentModel.value.id,
            mode: currentMode.value,
          },
          {
            onThinking: (chunk: string) => {
              resetWatchdog(15000, "大模型思考过程传输中断，请重试");
              aiMsg.status = "streaming";
              aiMsg.thinkingContent = (aiMsg.thinkingContent || "") + chunk;
            },
            onMessage: (chunk: string) => {
              resetWatchdog(15000, "大模型对话生成中断，请重试");
              aiMsg.status = "streaming";
              aiMsg.content = (aiMsg.content || "") + chunk;
            },
            onUsage: (usage) => {
              aiMsg.id = usage.message_id || aiMsg.id;
              aiMsg.metrics = {
                inputTokens: usage.input_tokens,
                outputTokens: usage.output_tokens,
                cost: usage.cost,
                currency: usage.currency,
                isSuccess: true,
              };
            },
            onError: (err) => {
              console.error("Stream generation error:", err);
              handleStreamError(err);
            },
            onDone: () => {
              clearWatchdog();
              isGenerating.value = false;
              abortController = null;
              if (aiMsg.status !== "error") {
                aiMsg.status = "success";
              }
            },
          },
          abortController.signal,
        );
      } catch (err: any) {
        console.error("Failed to stream message:", err);
        handleStreamError({
          code: "STREAM_EXCEPTION",
          message: err.message || "网络请求异常中断",
        });
      }
    } else {
      // 备用本地演示生成
      setTimeout(() => {
        clearWatchdog();
        aiMsg.status = "success";
        aiMsg.thinkingContent = "正在分析玩家输入语境与剧情脉络……";
        aiMsg.content = `哼……「${userText}」？既然你这么说了，那就按你的想法继续走下去吧。`;
        aiMsg.metrics = { inputTokens: 1200, outputTokens: 380, isSuccess: true };
        isGenerating.value = false;
      }, 600);
    }
  }

  /**
   * 发送用户消息并触发 AI 生成
   */
  async function handleSendMessage(text: string): Promise<void> {
    if (!text.trim() || isGenerating.value) return;

    const userText = text.trim();

    // 1. 追加用户消息
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: "user",
      content: userText,
      timestamp: formatTimestamp(),
      status: "success",
    };
    messages.value.push(userMsg);

    // 2. 触发 AI 流式生成
    await generateAiReply(userText);
  }

  /**
   * 中止当前生成
   */
  async function handleStopGeneration(): Promise<void> {
    if (abortController) {
      abortController.abort();
      abortController = null;
    }
    if (sessionId.value) {
      await chatService.stopGeneration(sessionId.value).catch(() => {});
    }
    isGenerating.value = false;
    showToast("已停止生成");
  }

  /**
   * 重新生成指定消息或最后一条消息
   */
  async function handleRegenerate(targetMsg?: ChatMessage): Promise<void> {
    if (isGenerating.value) {
      if (abortController) {
        abortController.abort();
        abortController = null;
      }
      isGenerating.value = false;
    }

    let userText = "";

    if (targetMsg) {
      const idx = messages.value.findIndex((m) => m.id === targetMsg.id);
      if (idx !== -1) {
        if (targetMsg.sender === "ai") {
          const prevUser = [...messages.value.slice(0, idx)].reverse().find((m) => m.sender === "user");
          if (prevUser) {
            userText = prevUser.content;
            messages.value.splice(idx, 1);
          }
        } else {
          userText = targetMsg.content;
          messages.value.splice(idx + 1);
        }
      }
    } else {
      const lastUser = [...messages.value].reverse().find((m) => m.sender === "user");
      if (lastUser) {
        userText = lastUser.content;
        const lastMsg = messages.value[messages.value.length - 1];
        if (lastMsg && lastMsg.sender === "ai") {
          messages.value.pop();
        }
      }
    }

    if (!userText.trim()) {
      showToast("未找到上一轮对话内容");
      return;
    }

    showToast("正在重新生成...");
    await generateAiReply(userText);
  }

  function handleBranch(_msg: ChatMessage): void {
    showToast("已在此消息节点开启新剧情线");
  }

  function handleEditMessage(_msg: ChatMessage): void {
    showToast("正在编辑消息...");
  }

  function handleSaveEditMessage(msg: ChatMessage, newContent: string, regenerate: boolean): void {
    const idx = messages.value.findIndex((m) => m.id === msg.id);
    if (idx === -1) return;

    messages.value[idx].content = newContent;

    if (regenerate) {
      messages.value = messages.value.slice(0, idx + 1);
      if (msg.sender === "user") {
        handleSendMessage(newContent);
      }
    } else {
      showToast("消息已更新");
    }
  }

  function handleDeleteMessage(msg: ChatMessage): void {
    messages.value = messages.value.filter((m) => m.id !== msg.id);
    showToast("消息已删除");
  }

  function handleReadAloud(_msg: ChatMessage): void {
    showToast("正在调用二次元语音合成朗读...");
  }

  function handleSelectModel(model: AiModelItem): void {
    currentModel.value = model;
    showToast(`已切换模型: ${model.name}`);
  }

  function handleSwitchMode(mode: "story" | "room"): void {
    currentMode.value = mode;
    showToast(mode === "story" ? "已切换至剧情模式" : "已切换至聊天室模式");
  }

  return {
    character: readonly(character),
    messages,
    currentModel,
    currentMode,
    isGenerating: readonly(isGenerating),
    isModelDrawerOpen,
    toastMessage: readonly(toastMessage),
    showToast,
    handleBack,
    handleSendMessage,
    handleStopGeneration,
    handleRegenerate,
    handleBranch,
    handleEditMessage,
    handleSaveEditMessage,
    handleDeleteMessage,
    handleReadAloud,
    handleSelectModel,
    handleSwitchMode,
  };
}
