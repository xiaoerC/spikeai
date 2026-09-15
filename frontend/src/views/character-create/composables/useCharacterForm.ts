/**
 * 角色卡创建表单组合式 Hook (基于 Reactive 全深度响应式体系)
 *
 * @packageDocumentation
 */

import {
  type CharacterFormData,
  type FormValidationError,
  normalizePosition,
} from "@/views/character-create/types";
import { computed, reactive } from "vue";

/**
 * 初始空白表单数据
 */
function createInitialFormData(): CharacterFormData {
  return {
    displayMode: "full",
    activeTab: "cover",

    // 分节 1: 卡面 (Cover)
    creatorNotes: "",
    name: "",
    avatarUrl: "",
    tags: [],
    marketDescription: "",
    category: "story",
    isOriginal: true,
    isNsfw: false,
    visibility: "public",
    creatorName: "",
    version: "1.0.0",

    // 分节 2: 角色 (Character)
    description: "",
    personality: "",
    scenario: "",
    beforeChar: "",
    worldbookVersion: "v3",
    worldbookEntries: [],
    systemPrompt: "",
    postHistoryInstructions: "",

    // 分节 3: 舞台 (Stage)
    firstMes: "",
    alternateGreetings: [
      {
        id: "alt-1",
        title: "备选开场白 1",
        greetingText: "",
        responsePreview: "",
      },
    ],
    openingReplies: [],
    prologueHtml: "",
    stageExtensions: {
      bgmUrl: "",
      customCss: "",
      sidebarPanelHtml: "",
      assistantNote: "",
    },

    // 分节 4: 机制 (Mechanics)
    regexScripts: [],
    initialVariables: {},
  };
}

/**
 * 角色卡表单状态机
 */
export function useCharacterForm() {
  const formData = reactive<CharacterFormData>(createInitialFormData());

  /**
   * 表单完善度校验
   */
  const validationErrors = computed<FormValidationError[]>(() => {
    const errors: FormValidationError[] = [];
    if (!formData.name.trim()) {
      errors.push({ field: "name", message: "角色/故事名称不能为空" });
    }
    if (formData.tags.length === 0) {
      errors.push({ field: "tags", message: "请至少选择一个标签" });
    }
    if (!formData.firstMes.trim()) {
      errors.push({ field: "firstMes", message: "首次问候语不能为空" });
    }
    return errors;
  });

  const isValid = computed<boolean>(() => validationErrors.value.length === 0);

  /**
   * 重置清空表单
   */
  function resetForm(): void {
    Object.assign(formData, createInitialFormData());
  }

  /**
   * 从 JSON 文本导入数据
   * @param jsonStr - 原始 JSON 字符串
   */
  function importFromJson(jsonStr: string): boolean {
    try {
      const parsed = JSON.parse(jsonStr);
      // 兼容 SillyTavern V2 (parsed.data) 与普通格式
      const charData = parsed.data || parsed;
      const extensions = charData.extensions || {};

      Object.assign(formData, {
        creatorNotes: charData.creator_notes || charData.creatorNotes || "",
        name: charData.name || "",
        avatarUrl: charData.avatarUrl || extensions.naro_avatar_url || formData.avatarUrl || "",
        tags: Array.isArray(charData.tags) ? charData.tags.slice(0, 5) : [],
        marketDescription: charData.description?.slice(0, 200) || "",
        category: charData.category || (charData.is_nsfw ? "nsfw" : "story"),
        isOriginal: charData.is_original ?? true,
        isNsfw: charData.is_nsfw ?? charData.category === "nsfw",
        visibility: charData.visibility || (charData.status === "private" ? "private" : "public"),
        creatorName: charData.creator || extensions.creator || "",
        version: charData.character_version || charData.version || "1.0.0",

        description: charData.description || "",
        personality: charData.personality || "",
        scenario: charData.scenario || "",
        beforeChar: extensions.depth_prompt?.prompt || charData.before_char || "",
        worldbookVersion: charData.character_book ? "v3" : "v2",

        prologueHtml:
          charData.prologueHtml || extensions.naro_prologue_html || charData.screen || "",
        firstMes: charData.first_mes || charData.firstMes || "",
        alternateGreetings: Array.isArray(charData.alternate_greetings)
          ? charData.alternate_greetings.map((g: any, idx: number) => ({
              id: `alt-${idx + 1}`,
              title: `备选开场白 ${idx + 1}`,
              greetingText: typeof g === "string" ? g : g.greetingText || "",
              responsePreview: typeof g === "object" ? g.responsePreview || "" : "",
            }))
          : [],
        openingReplies: Array.isArray(extensions.opening_replies) ? extensions.opening_replies : [],
        stageExtensions: {
          bgmUrl: extensions.bgm_url || extensions.bgm || "",
          customCss: extensions.custom_css || "",
          sidebarPanelHtml: extensions.sidebar_panel || "",
          assistantNote: extensions.assistant_note || "",
        },

        systemPrompt: charData.system_prompt || "",
        postHistoryInstructions: charData.post_history_instructions || "",
        worldbookEntries: charData.character_book?.entries
          ? charData.character_book.entries.map((wb: any, idx: number) => ({
              id: `wb-${idx + 1}`,
              name: wb.comment || wb.name || `设定 ${idx + 1}`,
              keys: Array.isArray(wb.keys) ? wb.keys : [],
              secondaryKeys: Array.isArray(wb.secondary_keys) ? wb.secondary_keys : [],
              content: wb.content || "",
              isEnabled: wb.enabled ?? true,
              position: normalizePosition(wb.position),
              order: wb.insertion_order ?? idx,
            }))
          : [],

        regexScripts: Array.isArray(extensions.regex_scripts)
          ? extensions.regex_scripts.map((rs: any, idx: number) => ({
              id: rs.id || `regex-${idx + 1}`,
              scriptName: rs.scriptName || `脚本 ${idx + 1}`,
              findRegex: rs.findRegex || "",
              replaceString: rs.replaceString || "",
              trimStrings: rs.trimStrings || [],
              placement: rs.placement || [2],
              disabled: rs.disabled ?? false,
            }))
          : [],
        initialVariables: extensions.variables || {},
      });
      return true;
    } catch (err) {
      console.error("Failed to parse imported character JSON:", err);
      return false;
    }
  }

  /**
   * 导出为标准化 SillyTavern V2 / V3 格式 JSON
   */
  function exportToJson(): string {
    const card = {
      spec: "chara_card_v2",
      spec_version: "2.0",
      data: {
        name: formData.name,
        description: formData.description,
        personality: formData.personality,
        scenario: formData.scenario,
        first_mes: formData.firstMes,
        mes_example: "",
        creator_notes: formData.creatorNotes,
        system_prompt: formData.systemPrompt,
        post_history_instructions: formData.postHistoryInstructions,
        alternate_greetings: formData.alternateGreetings.map((g) => g.greetingText).filter(Boolean),
        tags: formData.tags,
        creator: formData.creatorName,
        character_version: formData.version,
        character_book:
          formData.worldbookEntries.length > 0
            ? {
                name: `${formData.name}的世界书`,
                entries: formData.worldbookEntries.map((wb, idx) => ({
                  id: idx + 1,
                  keys: wb.keys,
                  secondary_keys: wb.secondaryKeys || [],
                  content: wb.content,
                  enabled: wb.isEnabled,
                  insertion_order: wb.order ?? idx,
                  comment: wb.name,
                  position: normalizePosition(wb.position),
                })),
              }
            : undefined,
        extensions: {
          naro_avatar_url: formData.avatarUrl,
          naro_prologue_html: formData.prologueHtml,
          category: formData.category,
          is_original: formData.isOriginal,
          is_nsfw: formData.isNsfw,
          regex_scripts: formData.regexScripts,
          variables: formData.initialVariables,
          opening_replies: formData.openingReplies,
          bgm_url: formData.stageExtensions.bgmUrl,
          custom_css: formData.stageExtensions.customCss,
          sidebar_panel: formData.stageExtensions.sidebarPanelHtml,
        },
      },
    };
    return JSON.stringify(card, null, 2);
  }

  return {
    formData,
    validationErrors,
    isValid,
    resetForm,
    importFromJson,
    exportToJson,
  };
}
