/**
 * 角色卡导出转换与下载组合式 Hook (遵循 SillyTavern V2 / V3 Card Spec 规范)
 *
 * @packageDocumentation
 */

import type { CharacterFormData } from "@/views/character-create/types";
import { computed, toValue, type MaybeRefOrGetter } from "vue";

/**
 * 角色卡导出 Hook
 * @param formData - 表单数据 (支持 Ref / ComputedRef / Getter 函数以保证响应式追踪)
 */
export function useCardExporter(formData: MaybeRefOrGetter<CharacterFormData>) {
  /**
   * 转换为标准 SillyTavern V2 角色卡规范数据结构 (实时响应式计算)
   */
  const sillyTavernV2Spec = computed(() => {
    const data = toValue(formData);
    if (!data) {
      return {
        spec: "chara_card_v2",
        spec_version: "2.0",
        data: {
          name: "",
          description: "",
          personality: "",
          scenario: "",
          first_mes: "",
          mes_example: "",
          creator_notes: "",
          system_prompt: "",
          post_history_instructions: "",
          alternate_greetings: [],
          tags: [],
          creator: "叙梦创作者",
          character_version: "1.0.0",
          extensions: {},
        },
      };
    }

    // 构建世界书 (Character Book)
    const characterBook =
      data.worldbookEntries && data.worldbookEntries.length > 0
        ? {
            name: `${data.name || "character"}_worldbook`,
            description: `Worldbook for ${data.name || "character"}`,
            entries: data.worldbookEntries.map((wb, idx) => ({
              id: idx + 1,
              keys: wb.keys || [],
              content: wb.content || "",
              enabled: wb.isEnabled ?? true,
              insertion_order: 100,
              case_sensitive: false,
              name: wb.name || `条目 ${idx + 1}`,
              priority: 10,
              position: 1,
            })),
          }
        : undefined;

    return {
      spec: "chara_card_v2",
      spec_version: "2.0",
      data: {
        name: data.name || "",
        description: data.description || "",
        personality: data.personality || "",
        scenario: data.scenario || "",
        first_mes: data.firstMes || "",
        mes_example: "",
        creator_notes: data.creatorNotes || "",
        system_prompt: data.systemPrompt || "",
        post_history_instructions: data.postHistoryInstructions || "",
        alternate_greetings: (data.alternateGreetings || [])
          .map((g) => g.greetingText)
          .filter((t) => Boolean(t && t.trim())),
        character_book: characterBook,
        tags: data.tags || [],
        creator: "叙梦创作者",
        character_version: "1.0.0",
        extensions: {
          naro_prologue_html: data.prologueHtml || "",
          naro_avatar_url: data.avatarUrl || "",
        },
      },
    };
  });

  /**
   * JSON 格式化字符串 (2 空格缩进)
   */
  const jsonPreviewString = computed<string>(() => {
    return JSON.stringify(sillyTavernV2Spec.value, null, 2);
  });

  /**
   * 下载 JSON 角色卡文件
   */
  function downloadJsonFile(): void {
    const data = toValue(formData);
    const filename = `${data?.name?.trim() || "character"}_v2.json`;
    const blob = new Blob([jsonPreviewString.value], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  /**
   * 复制 JSON 到系统剪贴板
   */
  async function copyJsonToClipboard(): Promise<boolean> {
    try {
      await navigator.clipboard.writeText(jsonPreviewString.value);
      return true;
    } catch (err) {
      console.error("Failed to copy JSON:", err);
      return false;
    }
  }

  return {
    sillyTavernV2Spec,
    jsonPreviewString,
    downloadJsonFile,
    copyJsonToClipboard,
  };
}
