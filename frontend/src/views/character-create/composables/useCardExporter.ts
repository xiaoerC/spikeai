/**
 * 角色卡导出转换与下载组合式 Hook (遵循 SillyTavern V2 / V3 Card Spec)
 *
 * @packageDocumentation
 */

import type { CharacterFormData } from "@/views/character-create/types";
import { computed } from "vue";

export function useCardExporter(formData: { value: CharacterFormData }) {
  /**
   * 转换为标准 SillyTavern V2 角色卡数据结构
   */
  const sillyTavernV2Spec = computed(() => {
    const data = formData.value;
    return {
      spec: "chara_card_v2",
      spec_version: "2.0",
      data: {
        name: data.name,
        description: data.description,
        personality: data.personality,
        scenario: data.scenario,
        first_mes: data.firstMes,
        mes_example: "",
        creator_notes: data.creatorNotes,
        system_prompt: data.systemPrompt,
        post_history_instructions: data.postHistoryInstructions,
        alternate_greetings: data.alternateGreetings.map((g) => g.greetingText).filter(Boolean),
        character_book: undefined,
        tags: data.tags,
        creator: "叙梦创作者",
        character_version: "1.0.0",
        extensions: {
          naro_prologue_html: data.prologueHtml,
        },
      },
    };
  });

  /**
   * JSON 格式化字符串
   */
  const jsonPreviewString = computed<string>(() => {
    return JSON.stringify(sillyTavernV2Spec.value, null, 2);
  });

  /**
   * 下载 JSON 角色卡文件
   */
  function downloadJsonFile(): void {
    const filename = `${formData.value.name.trim() || "character"}_v2.json`;
    const blob = new Blob([jsonPreviewString.value], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  /**
   * 复制 JSON 到剪贴板
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
