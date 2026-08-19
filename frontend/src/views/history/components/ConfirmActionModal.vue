<script setup lang="ts">
/**
 * 历史记录危险操作二次确认弹窗
 *
 * @packageDocumentation
 */

import { AppButton, AppModal } from "@/components/common";
import { AlertTriangle } from "lucide-vue-next";

defineProps<{
  /** 弹窗是否打开 */
  open: boolean;
  /** 弹窗操作类型 ('delete' | 'clear' | 'batch-delete') */
  actionType: "delete" | "clear" | "batch-delete";
  /** 关联对象名称或数量描述 */
  targetLabel?: string;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "confirm"): void;
}>();
</script>

<template>
  <AppModal
    :open="open"
    :title="actionType === 'clear' ? '清空历史对话' : (actionType === 'batch-delete' ? '批量删除确认' : '删除历史卡片')"
    :description="actionType === 'clear' ? '清空后将无法恢复已产生的多轮对话历史，但角色卡配置将保留。' : '删除后将从本地历史列表中移除该角色，且不可恢复。'"
    size="sm"
    @update:open="emit('update:open', $event)"
  >
    <div class="flex items-center gap-3 p-3 rounded-xl border border-red-500/20 bg-red-950/20 text-red-300">
      <AlertTriangle class="w-5 h-5 text-red-400 shrink-0" />
      <div class="text-xs leading-relaxed">
        确认对 <span class="font-bold text-red-200">{{ targetLabel || "选定项目" }}</span> 执行该操作吗？
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
          variant="danger"
          size="sm"
          @click="emit('confirm')"
        >
          确认执行
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
