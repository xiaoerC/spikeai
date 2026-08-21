/**
 * 帮助中心业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_COMMANDS, MOCK_FAQS, MOCK_GUIDE_STEPS } from "@/data/mockHelp";
import type { CommandItem, FaqItem, HelpStep, HelpTabType } from "@/views/help/types";
import { ref } from "vue";

export function useHelpCenter() {
  const currentTab = ref<HelpTabType>("guide");
  const guideSteps = ref<HelpStep[]>(MOCK_GUIDE_STEPS);
  const faqs = ref<FaqItem[]>(MOCK_FAQS);
  const commands = ref<CommandItem[]>(MOCK_COMMANDS);
  const expandedFaqIds = ref<Set<string>>(new Set());
  const copyToastMessage = ref<string | null>(null);

  function setTab(tab: HelpTabType): void {
    currentTab.value = tab;
  }

  function toggleFaq(id: string): void {
    if (expandedFaqIds.value.has(id)) {
      expandedFaqIds.value.delete(id);
    } else {
      expandedFaqIds.value.add(id);
    }
  }

  /**
   * 复制指令到剪贴板
   * @param text - 指令文本
   */
  async function copyCommand(text: string): Promise<void> {
    try {
      if (navigator?.clipboard) {
        await navigator.clipboard.writeText(text);
      }
      copyToastMessage.value = "指令已复制到剪贴板";
      setTimeout(() => {
        copyToastMessage.value = null;
      }, 2000);
    } catch {
      copyToastMessage.value = "复制成功";
      setTimeout(() => {
        copyToastMessage.value = null;
      }, 2000);
    }
  }

  return {
    currentTab,
    guideSteps,
    faqs,
    commands,
    expandedFaqIds,
    copyToastMessage,
    setTab,
    toggleFaq,
    copyCommand,
  };
}
