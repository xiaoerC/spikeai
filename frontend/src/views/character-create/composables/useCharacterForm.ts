/**
 * 角色卡创建表单组合式 Hook (基于 Reactive 全深度响应式体系)
 *
 * @packageDocumentation
 */

import type { CharacterFormData, FormValidationError } from "@/views/character-create/types";
import { computed, reactive } from "vue";

/**
 * 初始空白表单数据
 */
function createInitialFormData(): CharacterFormData {
  return {
    creatorNotes: "",
    name: "",
    avatarUrl: "",
    tags: [],
    description: "",
    personality: "",
    scenario: "",
    prologueHtml: "",
    firstMes: "",
    alternateGreetings: [
      {
        id: "alt-1",
        title: "备选开场白 1",
        greetingText: "",
        responsePreview: "",
      },
    ],
    systemPrompt: "",
    postHistoryInstructions: "",
    worldbookEntries: [],
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

      Object.assign(formData, {
        creatorNotes: charData.creator_notes || charData.creatorNotes || "",
        name: charData.name || "",
        avatarUrl: charData.avatarUrl || charData.extensions?.naro_avatar_url || "",
        tags: Array.isArray(charData.tags) ? charData.tags.slice(0, 5) : [],
        description: charData.description || "",
        personality: charData.personality || "",
        scenario: charData.scenario || "",
        prologueHtml: charData.prologueHtml || charData.extensions?.naro_prologue_html || "",
        firstMes: charData.first_mes || charData.firstMes || "",
        alternateGreetings: Array.isArray(charData.alternate_greetings)
          ? charData.alternate_greetings.map((g: string, idx: number) => ({
              id: `alt-${idx + 1}`,
              title: `备选开场白 ${idx + 1}`,
              greetingText: typeof g === "string" ? g : (g as any).greetingText || "",
            }))
          : [],
        systemPrompt: charData.system_prompt || "",
        postHistoryInstructions: charData.post_history_instructions || "",
        worldbookEntries: charData.character_book?.entries
          ? charData.character_book.entries.map((wb: any, idx: number) => ({
              id: `wb-${idx + 1}`,
              name: wb.name || `设定 ${idx + 1}`,
              keys: wb.keys || [],
              content: wb.content || "",
              isEnabled: wb.enabled ?? true,
            }))
          : [],
      });
      return true;
    } catch (err) {
      console.error("Failed to parse imported character JSON:", err);
      return false;
    }
  }

  return {
    formData,
    validationErrors,
    isValid,
    resetForm,
    importFromJson,
  };
}
