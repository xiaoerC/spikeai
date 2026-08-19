/**
 * 标签选择器组合式 Hook (上限 5 个限制)
 *
 * @packageDocumentation
 */

import { type Ref, computed, ref } from "vue";

/**
 * 标签选择操作 Hook
 *
 * @param selectedTags - 外部双向绑定的选定标签列表 Ref
 */
export function useTagSelector(selectedTags: Ref<string[]>) {
  const customTagInput = ref<string>("");

  const tagCount = computed<number>(() => selectedTags.value.length);
  const isMaxTagsReached = computed<boolean>(() => tagCount.value >= 5);

  /**
   * 切换预设标签选中状态
   * @param tag - 标签名称
   */
  function togglePresetTag(tag: string): void {
    const idx = selectedTags.value.indexOf(tag);
    if (idx !== -1) {
      selectedTags.value.splice(idx, 1);
    } else {
      if (!isMaxTagsReached.value) {
        selectedTags.value.push(tag);
      }
    }
  }

  /**
   * 添加自定义标签
   */
  function addCustomTag(): void {
    const tag = customTagInput.value.trim().replace(/^#/, "");
    if (!tag) return;
    if (!selectedTags.value.includes(tag) && !isMaxTagsReached.value) {
      selectedTags.value.push(tag);
      customTagInput.value = "";
    }
  }

  /**
   * 移除指定标签
   * @param tag - 标签名称
   */
  function removeTag(tag: string): void {
    const idx = selectedTags.value.indexOf(tag);
    if (idx !== -1) {
      selectedTags.value.splice(idx, 1);
    }
  }

  return {
    customTagInput,
    tagCount,
    isMaxTagsReached,
    togglePresetTag,
    addCustomTag,
    removeTag,
  };
}
