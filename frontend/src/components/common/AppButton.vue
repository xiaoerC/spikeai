<script setup lang="ts">
/**
 * 黑金暗黑玻璃拟物风格通用原子按钮组件。
 *
 * 遵循 Vue 3.5 响应式解构与 UnoCSS 原子类优先规范，
 * 提供多种视觉层级变体、尺寸控制、Loading 加载态与触觉按压反馈。
 *
 * Usage:
 *   <AppButton variant="gold" size="md" @click="handleClick">
 *     确认开启
 *   </AppButton>
 *
 *   <AppButton variant="ghost" :loading="isSubmitting">
 *     取消
 *   </AppButton>
 */

import { Loader2 } from "lucide-vue-next";
import { computed } from "vue";

export type ButtonVariant = "gold" | "ghost" | "danger" | "outline";
export type ButtonSize = "sm" | "md" | "lg" | "icon";

interface Props {
  /** 按钮视觉层级变体 */
  variant?: ButtonVariant;
  /** 按钮尺寸规范 */
  size?: ButtonSize;
  /** 是否处于异步加载状态 */
  loading?: boolean;
  /** 是否禁用交互 */
  disabled?: boolean;
  /** 按钮类型 */
  type?: "button" | "submit" | "reset";
  /** 额外的 UnoCSS 自定义类名 */
  customClass?: string;
}

const props = withDefaults(defineProps<Props>(), {
  variant: "gold",
  size: "md",
  loading: false,
  disabled: false,
  type: "button",
  customClass: "",
});

const emit = defineEmits<(e: "click", event: MouseEvent) => void>();

const variantClasses = computed(() => {
  switch (props.variant) {
    case "gold":
      return "btn-gold";
    case "ghost":
      return "btn-ghost";
    case "danger":
      return "bg-red-500/20 text-red-300 border border-red-500/40 hover:bg-red-500/30 active:scale-95 transition-all duration-150";
    case "outline":
      return "bg-transparent text-naro-gold border border-naro-gold/40 hover:bg-naro-gold/10 active:scale-95 transition-all duration-150";
    default:
      return "btn-gold";
  }
});

const sizeClasses = computed(() => {
  switch (props.size) {
    case "sm":
      return "text-xs px-2.5 py-1.5 rounded-lg";
    case "md":
      return "text-sm px-4 py-2 rounded-xl";
    case "lg":
      return "text-base px-6 py-3 rounded-2xl";
    case "icon":
      return "p-2 rounded-xl aspect-square flex items-center justify-center";
    default:
      return "text-sm px-4 py-2 rounded-xl";
  }
});

function handleClick(event: MouseEvent) {
  if (props.disabled || props.loading) return;
  emit("click", event);
}
</script>

<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex items-center justify-center gap-2 font-medium transition-all duration-150 select-none cursor-pointer',
      variantClasses,
      sizeClasses,
      customClass,
    ]"
    @click="handleClick"
  >
    <Loader2 v-if="loading" class="w-4 h-4 animate-spin shrink-0" />
    <slot name="icon-left" />
    <slot />
    <slot name="icon-right" />
  </button>
</template>
