<script setup lang="ts">
/**
 * 创作者留言 / 作者的话模态编辑弹窗
 *
 * @packageDocumentation
 */

import AppButton from "@/components/common/AppButton.vue";
import AppModal from "@/components/common/AppModal.vue";
import { ref, watch } from "vue";

const props = defineProps<{
  /** 模态框显隐 */
  open: boolean;
  /** 作者的话内容 (v-model) */
  modelValue: string;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "update:modelValue", val: string): void;
}>();

const localContent = ref<string>(props.modelValue);

watch(
  () => props.modelValue,
  (val) => {
    localContent.value = val;
  },
);

function handleSave(): void {
  emit("update:modelValue", localContent.value);
  emit("update:open", false);
}
</script>

<template>
  <AppModal
    :open="open"
    @update:open="(val: boolean) => emit('update:open', val)"
    title="作者的话 (创作者寄语)"
    description="此内容将作为角色卡创作者留言展示在详情页中，支持 Markdown 排版。"
  >
    <div class="flex flex-col gap-3 py-1">
      <textarea
        v-model="localContent"
        rows="6"
        class="w-full p-3.5 rounded-xl border border-[rgba(83,71,65,0.40)] bg-[rgba(26,23,20,0.80)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D] transition-colors resize-none leading-relaxed font-sans"
        placeholder="分享你的创作心路历程、世界观构思或给玩家的游玩建议（支持 Markdown 语法）..."
      />
      <span class="text-[11px] text-[#78716C]">
        提示：良好的创作者寄语可以帮助玩家更好地进入剧情体验。
      </span>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-2 w-full pt-2">
        <AppButton variant="ghost" size="sm" @click="emit('update:open', false)">
          取消
        </AppButton>
        <AppButton variant="gold" size="sm" @click="handleSave">
          保存留言
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
