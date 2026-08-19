/**
 * AI 聊天会话逻辑 Composable
 *
 * @packageDocumentation
 */

import {
  type AiModelItem,
  type ChatMessage,
  INITIAL_CHAT_MESSAGES,
  MOCK_AI_MODELS,
  MOCK_CHAT_CHARACTER,
} from "@/views/chat/constants/mockChatData";
import { reactive, readonly, ref } from "vue";
import { useRouter } from "vue-router";

export function useChatSession(_characterId?: string) {
  const router = useRouter();

  const character = reactive({ ...MOCK_CHAT_CHARACTER });
  const messages = ref<ChatMessage[]>([...INITIAL_CHAT_MESSAGES]);
  const currentModel = ref<AiModelItem>(MOCK_AI_MODELS[0]);
  const currentMode = ref<"story" | "room">("story");
  const isGenerating = ref(false);
  const isModelDrawerOpen = ref(false);
  const toastMessage = ref("");

  function showToast(msg: string): void {
    toastMessage.value = msg;
    setTimeout(() => {
      toastMessage.value = "";
    }, 2000);
  }

  function handleBack(): void {
    router.back();
  }

  function handleSendMessage(text: string): void {
    if (!text.trim() || isGenerating.value) return;

    // 1. 追加用户消息
    const userMsg: ChatMessage = {
      id: `user_${Date.now()}`,
      sender: "user",
      content: text.trim(),
      timestamp: new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      }),
    };
    messages.value.push(userMsg);

    // 2. 模拟 AI 生成响应
    isGenerating.value = true;
    setTimeout(() => {
      const aiMsg: ChatMessage = {
        id: `ai_${Date.now()}`,
        sender: "ai",
        characterName: character.name,
        avatarUrl: character.avatarUrl,
        content: `哼……听好了，这可是本小姐特意为你破例回答的！${text}？真是受不了你这种无聊的提问，下次再问这种傻话，小心我直接把你轰出去！`,
        timestamp: new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }),
        metrics: {
          inputTokens: Math.floor(Math.random() * 2000) + 8000,
          outputTokens: Math.floor(Math.random() * 1000) + 4000,
          isSuccess: true,
        },
      };
      messages.value.push(aiMsg);
      isGenerating.value = false;
    }, 800);
  }

  function handleRegenerate(msg: ChatMessage): void {
    showToast("正在重新生成该节点回复...");
  }

  function handleBranch(msg: ChatMessage): void {
    showToast("已在此消息节点分叉新剧情线");
  }

  function handleEditMessage(msg: ChatMessage): void {
    showToast("消息编辑功能已开启");
  }

  function handleDeleteMessage(msg: ChatMessage): void {
    messages.value = messages.value.filter((m) => m.id !== msg.id);
    showToast("消息已删除");
  }

  function handleReadAloud(msg: ChatMessage): void {
    showToast("开始语音朗读...");
  }

  function handleSelectModel(model: AiModelItem): void {
    currentModel.value = model;
    showToast(`已切换至: ${model.name}`);
  }

  function handleSwitchMode(mode: "story" | "room"): void {
    currentMode.value = mode;
    showToast(mode === "story" ? "已进入剧情模式" : "已进入聊天室模式");
  }

  return {
    character: readonly(character),
    messages,
    currentModel,
    currentMode,
    isGenerating: readonly(isGenerating),
    isModelDrawerOpen,
    toastMessage: readonly(toastMessage),
    handleBack,
    handleSendMessage,
    handleRegenerate,
    handleBranch,
    handleEditMessage,
    handleDeleteMessage,
    handleReadAloud,
    handleSelectModel,
    handleSwitchMode,
  };
}
