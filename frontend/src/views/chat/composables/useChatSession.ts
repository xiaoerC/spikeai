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
  type ControlPanelDTO,
  type NarrativeStateDTO,
  type StoryBranchDetail,
  chatService,
} from "@/services/chat";
import { chatStorage } from "@/services/storage/chatStorage";
import { useAppStore } from "@/stores/app";
import { useUserStore } from "@/stores/user";
import { useRafTypewriter } from "@/views/chat/composables/useRafTypewriter";
import type { AiModelItem, ChatMessage } from "@/views/chat/constants/mockChatData";
import { type MaybeRefOrGetter, computed, reactive, readonly, ref, toValue, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

export function useChatSession(characterIdParam?: MaybeRefOrGetter<string>) {
  const router = useRouter();
  const route = useRoute();
  const toast = useToast();
  const appStore = useAppStore();
  const userStore = useUserStore();

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
  const alternateGreetings = ref<string[]>([]);
  const currentGreetingIndex = ref<number>(0);
  const openingReplies = ref<string[]>([]);
  const bgmUrl = ref<string>("");
  const branches = ref<StoryBranchDetail[]>([]);
  const currentBranchId = ref<string>("");
  const isBranchDrawerOpen = ref(false);
  const isCanvasModalOpen = ref(false);
  const selectedForkMessageId = ref<string | undefined>(undefined);
  const currentModel = ref<AiModelItem>({
    id: "default",
    name: "加载模型中...",
    health: 99,
    billingType: "fixed",
    starCost: 1,
    moonCost: 1,
    cost: 1,
    freeCountText: "★ 1 / 次",
    isStreaming: true,
    isFavorite: false,
  });
  const currentMode = ref<"story" | "room">("story");
  const isGenerating = ref(false);
  const isModelDrawerOpen = ref(false);
  const toastMessage = ref("");
  let abortController: AbortController | null = null;

  // Phase 8: 60fps 平滑打字机 (分别平滑消费正文与思考流)
  const currentTargetAiMsg = ref<ChatMessage | null>(null);
  const messageTypewriter = useRafTypewriter({
    onTick: (text) => {
      if (currentTargetAiMsg.value) {
        currentTargetAiMsg.value.content = text;
      }
    },
  });

  const thinkingTypewriter = useRafTypewriter({
    onTick: (text) => {
      if (currentTargetAiMsg.value) {
        currentTargetAiMsg.value.thinkingContent = text;
      }
    },
  });

  // Phase 5: RPG 主控面板 38 变量矩阵与叙梦 6 大 Tab 状态机
  const controlPanel = ref<ControlPanelDTO>({
    user_name: userStore.profile?.username || "{{user}}",
    user_persona: "",
    custom_prompt: "",
    variables: {},
    memory_blocks: [],
    text_replacements: [],
  });

  const narrativeState = ref<NarrativeStateDTO>({
    date_text: "第一幕",
    time_text: "清晨",
    location: "起始之境",
    present_characters: [],
    player_states: [],
    consumables: [],
    important_items: [],
    skills: [],
    social_relations: [],
    tasks: [],
    history_events: [],
  });

  const isLoadingControlPanel = ref(false);
  const isLoadingNarrativeState = ref(false);

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
   * 净化消息文本中残留的增量状态标签与裸 JSON 字典 (彻底消除图 2 裸 JSON 泄漏)
   */
  function cleanDeltaJson(text: string): string {
    if (!text) return "";
    return text
      .replace(/<narrative_delta>[\s\S]*?<\/narrative_delta>/gi, "")
      .replace(/<narrative_delta>[\s\S]*?$/gi, "")
      .replace(/```(?:json)?\s*\{[\s\S]*?"(?:new_event|history_events|player_states|variables|location|date_text|time_text|tasks|consumables|social_relations)"[\s\S]*?\}\s*```\s*$/gi, "")
      .replace(/\{\s*"(?:new_event|history_events|player_states|variables|location|date_text|time_text|tasks|consumables|social_relations)"[\s\S]*?\}\s*$/gi, "")
      .trim();
  }

  /**
   * 将后端 ChatMessageItem 转换为前端 UI 格式
   */
  function mapBackendMessage(m: ChatMessageItem): ChatMessage {
    const isGreeting = !m.parent_message_id;
    const hasTokens = (m.input_tokens ?? 0) > 0 || (m.output_tokens ?? 0) > 0;

    return {
      id: m.id,
      sender: m.sender as "ai" | "user" | "system",
      characterName: m.character_name || character.name,
      avatarUrl: m.avatar_url || character.avatarUrl,
      content: cleanDeltaJson(m.content),
      thinkingContent: m.thinking_content || "",
      timestamp: formatTimestamp(m.created_at),
      metrics:
        m.sender === "ai" && !isGreeting && hasTokens
          ? {
              inputTokens: m.input_tokens || 0,
              outputTokens: m.output_tokens || 0,
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
      // Phase 8: 阶段 0 - 检查本地 IndexedDB (0ms 极速秒开挂载)
      const querySessionId = route.query.session_id as string | undefined;
      const offlineLookupKey = querySessionId || (charId ? `char_${charId}` : null);
      if (offlineLookupKey) {
        const [cachedMsgs, cachedBranches, cachedCp, cachedNs] = await Promise.all([
          chatStorage.getCachedMessages(offlineLookupKey),
          chatStorage.getCachedBranches(offlineLookupKey),
          chatStorage.getCachedControlPanel(offlineLookupKey),
          chatStorage.getCachedNarrativeState(offlineLookupKey),
        ]);
        if (cachedMsgs && cachedMsgs.length > 0 && messages.value.length === 0) {
          messages.value = cachedMsgs;
        }
        if (cachedBranches && cachedBranches.length > 0 && branches.value.length === 0) {
          branches.value = cachedBranches;
        }
        if (cachedCp) {
          controlPanel.value = cachedCp;
        }
        if (cachedNs) {
          narrativeState.value = cachedNs;
        }
      }

      // 1. 第一阶段：并发拉取角色设定与会话详情 (耗时由 T1+T2 缩短为 max(T1, T2))
      const [charDetail, sessionDetail] = await Promise.all([
        characterService.getCharacterDetail(charId).catch(() => null),
        querySessionId
          ? chatService
              .getSessionDetail(querySessionId)
              .catch(() => chatService.getSessionByCharacter(charId))
          : chatService.getSessionByCharacter(charId),
      ]);

      // 快速组装角色基础展示（立绘、背景、开场白）
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

      // 快速组装会话历史消息（首屏即刻可交互）
      sessionId.value = sessionDetail.id;
      currentBranchId.value = sessionDetail.current_branch_id;

      // 动态拉取后台真实上架模型，并恢复/自愈用户偏好模型
      try {
        const models = await chatService.getAvailableModels();
        if (models && models.length > 0) {
          const savedModelStr = localStorage.getItem("naro_selected_model");
          let targetModelItem: any = null;
          if (savedModelStr) {
            try {
              const parsed = JSON.parse(savedModelStr);
              // 必须在当前真实上架模型中真实存在
              const matched = models.find((m) => m.id === parsed.id);
              if (matched) {
                targetModelItem = {
                  id: matched.id,
                  name: matched.name,
                  health: matched.health || 99,
                  billingType: "fixed",
                  starCost: matched.starCost ?? matched.cost ?? 1,
                  moonCost: matched.moonCost ?? matched.cost ?? 1,
                  cost: matched.cost ?? 1,
                  freeCountText: matched.freeCountText || `★ ${matched.cost || 1} / 次`,
                  isStreaming: matched.isStreaming ?? true,
                  isFavorite: parsed.isFavorite ?? false,
                };
              }
            } catch {
              targetModelItem = null;
            }
          }

          if (!targetModelItem) {
            // 自愈选用当前系统默认上架模型或首选模型
            const def = models.find((m) => m.isDefault) || models[0];
            targetModelItem = {
              id: def.id,
              name: def.name,
              health: def.health || 99,
              billingType: "fixed",
              starCost: def.starCost ?? def.cost ?? 1,
              moonCost: def.moonCost ?? def.cost ?? 1,
              cost: def.cost ?? 1,
              freeCountText: def.freeCountText || `★ ${def.cost || 1} / 次`,
              isStreaming: def.isStreaming ?? true,
              isFavorite: def.isFavorite ?? false,
            };
            localStorage.setItem("naro_selected_model", JSON.stringify(targetModelItem));
          }

          currentModel.value = targetModelItem;
        }
      } catch (e) {
        console.warn("拉取并恢复真实模型失败:", e);
      }

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

      // 提取备选开场白 (支持首句与 alternate_greetings 轮换)
      if (sessionDetail.character_alternate_greetings && sessionDetail.character_alternate_greetings.length > 0) {
        alternateGreetings.value = sessionDetail.character_alternate_greetings;
      } else if (charDetail) {
        const gList: string[] = [];
        if (charDetail.first_mes) gList.push(charDetail.first_mes);
        if (Array.isArray(charDetail.alternate_greetings)) {
          for (const item of charDetail.alternate_greetings) {
            if (typeof item === "string" && item.trim()) {
              gList.push(item);
            } else if (item && typeof item === "object" && (item as any).greetingText) {
              gList.push((item as any).greetingText);
            }
          }
        }
        alternateGreetings.value = gList;
      }

      // 提取快捷回复引导 (opening_replies) 与 场景 BGM (bgm_url)
      const ext = sessionDetail.character_extensions || (charDetail as any)?.extensions || {};
      if (Array.isArray(ext.opening_replies)) {
        openingReplies.value = ext.opening_replies.filter((r: any) => typeof r === "string" && r.trim());
      }
      if (typeof ext.bgm_url === "string" && ext.bgm_url.trim()) {
        bgmUrl.value = ext.bgm_url.trim();
      }

      if (sessionDetail.messages && sessionDetail.messages.length > 0) {
        messages.value = sessionDetail.messages.map(mapBackendMessage);
        // Phase 8: 异步保存至本地 IndexedDB 供后续离线秒开
        chatStorage.saveMessages(sessionDetail.id, messages.value);
        if (charId) {
          chatStorage.saveMessages(`char_${charId}`, messages.value);
        }

        // 智能匹配当前首句开场白索引
        if (messages.value.length > 0 && alternateGreetings.value.length > 0) {
          const firstContent = messages.value[0].content.trim();
          const matchedIdx = alternateGreetings.value.findIndex((g) => g.trim() === firstContent);
          if (matchedIdx !== -1) {
            currentGreetingIndex.value = matchedIdx;
          }
        }
      } else if (character.greeting) {
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

      // 2. 第二阶段：全量并发拉取「分支树」、「主控面板 38 变量」与「叙梦 6 大 Tab 状态机」
      await Promise.all([
        loadBranches(sessionDetail.id),
        loadControlPanel(sessionDetail.id),
        loadNarrativeState(sessionDetail.id),
      ]);
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

  /**
   * 加载指定会话的主控面板配置
   */
  async function loadControlPanel(customSessionId?: string): Promise<void> {
    const sId = customSessionId || sessionId.value;
    if (!sId) return;
    try {
      isLoadingControlPanel.value = true;
      const data = await chatService.getControlPanel(sId);
      controlPanel.value = data;
    } catch (err) {
      console.warn("加载主控面板失败，使用默认值:", err);
    } finally {
      isLoadingControlPanel.value = false;
    }
  }

  /**
   * 保存主控面板配置 (38 变量矩阵、人设、指令、记忆区块与正则替换链)
   */
  async function saveControlPanel(payload?: ControlPanelDTO): Promise<void> {
    const sId = sessionId.value;
    if (!sId) return;
    try {
      const dataToSave = payload || controlPanel.value;
      const updated = await chatService.updateControlPanel(sId, dataToSave);
      controlPanel.value = updated;
      showToast("主控面板已保存");
    } catch (err: any) {
      console.error("保存主控面板失败:", err);
      showToast("保存主控面板失败，请重试");
    }
  }

  /**
   * 加载指定会话的叙梦 6 大 Tab 状态机
   */
  async function loadNarrativeState(customSessionId?: string): Promise<void> {
    const sId = customSessionId || sessionId.value;
    if (!sId) return;
    try {
      isLoadingNarrativeState.value = true;
      const data = await chatService.getNarrativeState(sId);
      narrativeState.value = data;
    } catch (err) {
      console.warn("加载叙梦面板失败，使用默认值:", err);
    } finally {
      isLoadingNarrativeState.value = false;
    }
  }

  /**
   * 保存叙梦 6 大 Tab 状态机数据
   */
  async function saveNarrativeState(payload?: NarrativeStateDTO): Promise<void> {
    const sId = sessionId.value;
    if (!sId) return;
    try {
      const dataToSave = payload || narrativeState.value;
      const updated = await chatService.updateNarrativeState(sId, dataToSave);
      narrativeState.value = updated;
      showToast("叙梦面板状态已保存");
    } catch (err: any) {
      console.error("保存叙梦状态机失败:", err);
      showToast("保存叙梦状态失败，请重试");
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
  async function generateAiReply(userText: string, clientUserMsgId?: string): Promise<void> {
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
    currentTargetAiMsg.value = aiMsg;
    messageTypewriter.reset();
    thinkingTypewriter.reset();

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

    // 启动初始首字超时看门狗 (45s，适配大 Prompt/RAG 首字加载)
    resetWatchdog(45000, "大模型响应超时（45秒无返回），请重试");

    // 4. 发起流式请求
    if (sessionId.value) {
      let latestCleanedContent = "";
      try {
        await chatService.streamMessage(
          sessionId.value,
          {
            content: userText,
            model_id: currentModel.value.id,
            mode: currentMode.value,
            client_message_id: clientUserMsgId,
          },
          {
            onThinking: (chunk: string) => {
              resetWatchdog(25000, "大模型思考过程传输中断，请重试");
              aiMsg.status = "streaming";
              thinkingTypewriter.pushChunk(chunk);
            },
            onMessage: (chunk: string) => {
              resetWatchdog(25000, "大模型对话生成中断，请重试");
              aiMsg.status = "streaming";
              messageTypewriter.pushChunk(chunk);
            },
            onUsage: (usage) => {
              aiMsg.id = usage.message_id || aiMsg.id;
              if (usage.user_message_id && clientUserMsgId) {
                const targetUserMsg = messages.value.find((m) => m.id === clientUserMsgId);
                if (targetUserMsg) {
                  targetUserMsg.id = usage.user_message_id;
                }
              }
              if (usage.cleaned_content) {
                latestCleanedContent = usage.cleaned_content;
                aiMsg.content = usage.cleaned_content;
              }
              aiMsg.metrics = {
                inputTokens: usage.input_tokens,
                outputTokens: usage.output_tokens,
                cost: usage.cost,
                currency: usage.currency,
                isSuccess: true,
              };
            },
            onStateUpdated: (stateData) => {
              if (stateData.narrative_state) {
                narrativeState.value = stateData.narrative_state;
                if (sessionId.value) {
                  chatStorage.saveNarrativeState(sessionId.value, stateData.narrative_state);
                }
              }
              if (stateData.control_panel) {
                controlPanel.value = stateData.control_panel;
                if (sessionId.value) {
                  chatStorage.saveControlPanel(sessionId.value, stateData.control_panel);
                }
              }
              showToast("✨ 叙梦与角色状态已自动同步");
            },
            onError: (err) => {
              console.error("Stream generation error:", err);
              handleStreamError(err);
            },
            onDone: () => {
              clearWatchdog();
              // Phase 8: 瞬间排空缓冲区并完成渲染
              thinkingTypewriter.flush();
              messageTypewriter.flush();
              // 彻底切除任何尾部残留的增量 JSON
              if (latestCleanedContent) {
                aiMsg.content = latestCleanedContent;
              } else {
                aiMsg.content = cleanDeltaJson(aiMsg.content);
              }
              isGenerating.value = false;
              abortController = null;
              if (aiMsg.status !== "error") {
                aiMsg.status = "success";
              }
              // Phase 8: 自动持久化写入本地 IndexedDB
              if (sessionId.value) {
                chatStorage.saveMessages(sessionId.value, messages.value);
                if (activeCharId.value) {
                  chatStorage.saveMessages(`char_${activeCharId.value}`, messages.value);
                }
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
      // 备用本地演示生成：同样采用 60fps 平滑打字机
      setTimeout(() => {
        clearWatchdog();
        aiMsg.status = "streaming";
        messageTypewriter.pushChunk(
          `哼……「${userText}」？既然你这么说了，那就按你的想法继续走下去吧。`,
        );
        setTimeout(() => {
          messageTypewriter.flush();
          aiMsg.status = "success";
          aiMsg.metrics = { inputTokens: 1200, outputTokens: 380, isSuccess: true };
          isGenerating.value = false;
          const storageKey =
            sessionId.value ||
            (activeCharId.value ? `char_${activeCharId.value}` : "default_session");
          chatStorage.saveMessages(storageKey, messages.value);
        }, 600);
      }, 200);
    }
  }

  /**
   * 发送用户消息并触发 AI 生成
   */
  async function handleSendMessage(text: string): Promise<void> {
    if (!text.trim() || isGenerating.value) return;

    const userText = text.trim();
    const userMsgId =
      typeof crypto !== "undefined" && typeof crypto.randomUUID === "function"
        ? crypto.randomUUID()
        : `user_${Date.now()}`;

    // 1. 追加用户消息
    const userMsg: ChatMessage = {
      id: userMsgId,
      sender: "user",
      content: userText,
      timestamp: formatTimestamp(),
      status: "success",
    };
    messages.value.push(userMsg);
    // Phase 8: 乐观持久化用户输入至 IndexedDB
    const storageKey =
      sessionId.value || (activeCharId.value ? `char_${activeCharId.value}` : "default_session");
    chatStorage.saveMessages(storageKey, messages.value);

    // 2. 触发 AI 流式生成
    await generateAiReply(userText, userMsgId);
  }

  /**
   * 中止当前生成
   */
  async function handleStopGeneration(): Promise<void> {
    // Phase 8: 停止生成时立刻排空打字机并保留已吐字符
    thinkingTypewriter.flush();
    messageTypewriter.flush();
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
          const prevUser = [...messages.value.slice(0, idx)]
            .reverse()
            .find((m) => m.sender === "user");
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

  async function loadBranches(customSessionId?: string): Promise<void> {
    const sId = customSessionId || sessionId.value;
    if (!sId) return;
    try {
      const list = await chatService.getBranches(sId);
      branches.value = list;
    } catch (err) {
      console.error("加载分支列表失败:", err);
    }
  }

  async function handleSwitchBranch(branchId: string): Promise<void> {
    if (!sessionId.value) return;
    try {
      const detail = await chatService.switchBranch(sessionId.value, branchId);
      currentBranchId.value = detail.current_branch_id;
      messages.value = detail.messages.map(mapBackendMessage);
      await loadBranches();
      const b = branches.value.find((x) => x.id === branchId);
      showToast(`已切换至分支: ${b?.name || "未知分支"}`);
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || "切换分支失败");
    }
  }

  async function handleCreateBranch(fromMessageId?: string, branchName?: string): Promise<void> {
    if (!sessionId.value) return;
    const targetMsgId =
      fromMessageId || selectedForkMessageId.value || messages.value[messages.value.length - 1]?.id;

    if (!targetMsgId) {
      showToast("无法定位分叉起点消息");
      return;
    }

    try {
      const newSession = await chatService.forkSession(sessionId.value, {
        fork_message_id: targetMsgId,
        remark: branchName,
      });
      sessionId.value = newSession.id;
      currentBranchId.value = newSession.current_branch_id;
      messages.value = newSession.messages.map(mapBackendMessage);
      await loadBranches();

      // 更新路由 Query 同步 session_id
      router.replace({
        query: { ...route.query, session_id: newSession.id },
      });

      showToast("已派生全新独立对话记录！可在历史记录中随时查看");
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || "开辟新对话失败");
    }
  }

  async function handleDeleteBranch(branchId: string): Promise<void> {
    if (!sessionId.value) return;
    try {
      await chatService.deleteBranch(sessionId.value, branchId);
      if (currentBranchId.value === branchId) {
        const main = branches.value.find((b) => b.is_main);
        if (main) {
          await handleSwitchBranch(main.id);
        }
      } else {
        await loadBranches();
      }
      showToast("分支已成功删除");
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || "删除分支失败");
    }
  }

  async function handleRollback(
    targetMessageId: string,
    mode: "fork" | "truncate" = "fork",
  ): Promise<void> {
    if (!sessionId.value) return;
    try {
      const detail = await chatService.rollbackToMessage(sessionId.value, {
        target_message_id: targetMessageId,
        mode,
      });
      currentBranchId.value = detail.current_branch_id;
      messages.value = detail.messages.map(mapBackendMessage);
      await loadBranches();
      showToast("已成功回溯至目标节点");
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || "回溯失败");
    }
  }

  function handleBranch(msg: ChatMessage): void {
    selectedForkMessageId.value = msg.id;
    isBranchDrawerOpen.value = true;
  }

  function handleEditMessage(_msg: ChatMessage): void {
    showToast("正在编辑消息...");
  }

  async function handleSaveEditMessage(
    msg: ChatMessage,
    newContent: string,
    regenerate: boolean,
  ): Promise<void> {
    if (!sessionId.value) {
      const idx = messages.value.findIndex((m) => m.id === msg.id);
      if (idx !== -1) {
        messages.value[idx].content = newContent;
      }
      return;
    }

    const mode = regenerate ? "edit_and_fork" : "edit_only";
    try {
      const detail = await chatService.editMessage(sessionId.value, msg.id, {
        content: newContent,
        mode,
      });
      currentBranchId.value = detail.current_branch_id;
      messages.value = detail.messages.map(mapBackendMessage);
      await loadBranches();

      if (regenerate) {
        showToast("已派生新平行分支，正在重新生成后续剧情...");
        await generateAiReply(newContent);
      } else {
        showToast("消息修改已保存");
      }
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || "编辑消息失败");
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
    try {
      localStorage.setItem("naro_selected_model", JSON.stringify(model));
    } catch {
      // 容错处理
    }
    showToast(`已切换模型: ${model.name}`);
  }

  function handleSwitchMode(mode: "story" | "room"): void {
    currentMode.value = mode;
    showToast(mode === "story" ? "已切换至剧情模式" : "已切换至聊天室模式");
  }

  /**
   * 切换当前开场白 (支持在 default first_mes 与 alternate_greetings 间轮换)
   */
  async function handleSwitchGreeting(index: number): Promise<void> {
    if (!sessionId.value) return;
    try {
      const updatedMsg = await chatService.switchGreeting(sessionId.value, index);
      currentGreetingIndex.value = index;
      if (messages.value.length > 0 && messages.value[0].sender === "ai") {
        messages.value[0] = mapBackendMessage(updatedMsg);
      } else {
        messages.value.unshift(mapBackendMessage(updatedMsg));
      }
      showToast(`已切换开场白 (${index + 1}/${alternateGreetings.value.length || 1})`);
    } catch (err: any) {
      showToast(err.response?.data?.message || err.message || "切换开场白失败");
    }
  }

  return {
    character: readonly(character),
    sessionId,
    messages,
    alternateGreetings: readonly(alternateGreetings),
    currentGreetingIndex: readonly(currentGreetingIndex),
    openingReplies: readonly(openingReplies),
    bgmUrl: readonly(bgmUrl),
    branches,
    currentBranchId,
    isBranchDrawerOpen,
    isCanvasModalOpen,
    selectedForkMessageId,
    currentModel,
    currentMode,
    isGenerating: readonly(isGenerating),
    isModelDrawerOpen,
    toastMessage: readonly(toastMessage),
    showToast,
    loadBranches,
    handleBack,
    handleSendMessage,
    handleStopGeneration,
    handleRegenerate,
    handleBranch,
    handleSwitchBranch,
    handleCreateBranch,
    handleDeleteBranch,
    handleRollback,
    handleEditMessage,
    handleSaveEditMessage,
    handleDeleteMessage,
    handleReadAloud,
    handleSwitchGreeting,
    controlPanel,
    narrativeState,
    isLoadingControlPanel: readonly(isLoadingControlPanel),
    isLoadingNarrativeState: readonly(isLoadingNarrativeState),
    loadControlPanel,
    saveControlPanel,
    loadNarrativeState,
    saveNarrativeState,
    handleSelectModel,
    handleSwitchMode,
  };
}
