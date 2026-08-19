<script setup lang="ts">
/**
 * 历史卡片自定义备注编辑弹窗
 *
 * @packageDocumentation
 */

import { AppButton, AppModal } from "@/components/common";
import type { HistoryCardItem } from "@/views/history/types";
import { ref, watch } from "vue";

const props = defineProps<{
  /** 弹窗显隐状态 */
  open: boolean;
  /** 目标编辑卡片 */
  card?: HistoryCardItem | null;
}>();

const emit = defineEmits<{
  (e: "update:open", value: boolean): void;
  (e: "save", payload: { id: string; note: string }): void;
}>();

const noteText = ref<string>("");

watch(
  () => props.card,
  (newCard) => {
    if (newCard) {
      noteText.value = newCard.customNote || "";
    }
  },
  { immediate: true },
);

function handleSave(): void {
  if (!props.card) return;
  emit("save", {
    id: props.card.id,
    note: noteText.value.trim(),
  });
  emit("update:open", false);
}
</script>

<template>
  <AppModal
    :open="open"
    title="编辑角色备注"
    description="为该角色卡添加个性化别名或记忆标记，仅本地生效"
    size="sm"
    @update:open="emit('update:open', $event)"
  >
    <div class="flex flex-col gap-3 py-2">
      <div class="flex flex-col gap-1">
        <label class="text-xs text-[#A8A29E]">当前角色：{{ card?.title }}</label>
        <input
          v-model="noteText"
          type="text"
          class="w-full px-3 py-2 rounded-lg border border-[#44403C] bg-black/40 text-sm text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D] transition-colors"
          placeholder="输入自定义备注名 (如: 恶堕二周目存档...)"
          maxlength="50"
          @keyup.enter="handleSave"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 w-full">
        <AppButton
          variant="ghost"
          size="sm"
          @click="emit('update:open', false)"
        >
          取消
        </AppButton>
        <AppButton
          variant="gold"
          size="sm"
          @click="handleSave"
        >
          保存备注
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
