<script setup lang="ts">
/**
 * 个人历史记录编辑备注弹窗 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { AppModal } from "@/components/common";
import type { UserHistoryItem } from "@/views/history/types";
import { ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  item: UserHistoryItem | null;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "save", remark: string): void;
}>();

const remarkInput = ref("");

watch(
  () => props.item,
  (val) => {
    remarkInput.value = val?.remark || "";
  },
  { immediate: true },
);

function handleSave() {
  emit("save", remarkInput.value.trim());
}
</script>

<template>
  <AppModal
    :open="open"
    @update:open="emit('update:open', $event)"
    size="sm"
  >
    <div v-if="item" class="p-5 flex flex-col gap-4 text-left">
      <div class="flex flex-col gap-1 border-b border-white/10 pb-3">
        <h3 class="text-sm font-bold text-[#F5F5F4]">
          编辑角色备注
        </h3>
        <p class="text-xs text-[#A8A29E] truncate">
          {{ item.title }}
        </p>
      </div>

      <!-- 备注输入框 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs text-[#A8A29E]">自定义备注标签</label>
        <input
          v-model="remarkInput"
          type="text"
          placeholder="如：主线存档一 / 纯爱线..."
          maxlength="20"
          class="w-full px-3 py-2 rounded-lg bg-[#161412] border border-white/10 text-xs text-[#F5F5F4] placeholder-[#78716C] focus:border-[#F9C86D] focus:outline-none transition-colors"
        />
      </div>

      <!-- 底部操作按钮 -->
      <div class="flex items-center justify-end gap-2 pt-2">
        <button
          type="button"
          @click="emit('update:open', false)"
          class="px-3.5 py-1.5 rounded-lg bg-[#292524] text-xs text-[#A8A29E] hover:text-white transition-colors cursor-pointer"
        >
          取消
        </button>
        <button
          type="button"
          @click="handleSave"
          class="px-4 py-1.5 rounded-lg bg-[#F9C86D] text-[#0C0A09] text-xs font-bold hover:bg-[#FFD475] active:scale-95 transition-all cursor-pointer"
        >
          保存
        </button>
      </div>
    </div>
  </AppModal>
</template>
