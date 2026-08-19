<script setup lang="ts">
/**
 * 黑金暗黑玻璃拟物风格模态对话框 (Modal / Dialog) 组件。
 *
 * 基于 Reka UI (原 Radix Vue) 无头状态机封装，具备原生无障碍 (A11y)、
 * 键盘 ESC 监听、焦点锁定 (Focus Trap) 与 Portal 挂载能力。
 *
 * Usage:
 *   <AppModal v-model:open="isOpen" title="欢迎回来">
 *     <p>请登录以同步您的云端角色卡与剧情分支。</p>
 *     <template #footer>
 *       <AppButton variant="ghost" @click="isOpen = false">取消</AppButton>
 *       <AppButton variant="gold" @click="handleLogin">登录</AppButton>
 *     </template>
 *   </AppModal>
 */

import { X } from "lucide-vue-next";
import {
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogOverlay,
  DialogPortal,
  DialogRoot,
  DialogTitle,
} from "reka-ui";

interface Props {
  /** 弹窗显隐状态 (支持 v-model:open) */
  open: boolean;
  /** 弹窗标题文本 */
  title?: string;
  /** 弹窗辅助描述文本 */
  description?: string;
  /** 是否显示右上角关闭按钮 */
  showClose?: boolean;
  /** 自定义容器类名 */
  customClass?: string;
}

withDefaults(defineProps<Props>(), {
  title: "",
  description: "",
  showClose: true,
  customClass: "",
});

const emit = defineEmits<(e: "update:open", value: boolean) => void>();
</script>

<template>
  <DialogRoot :open="open" @update:open="(val: boolean) => emit('update:open', val)">
    <DialogPortal>
      <!-- 高斯模糊暗黑遮罩 -->
      <DialogOverlay class="modal-overlay" />

      <!-- 黑金居中卡片容器 -->
      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <DialogContent
          :class="[
            'modal-content pointer-events-auto animate-scale-in',
            customClass
          ]"
        >

          <!-- 弹窗头部 -->
          <div v-if="title || $slots.header" class="flex items-center justify-between pb-2 border-b border-obsidian-border/60">
            <slot name="header">
              <div>
                <DialogTitle class="text-base font-bold text-naro-gold tracking-wide font-serif">
                  {{ title }}
                </DialogTitle>
                <DialogDescription v-if="description" class="text-xs text-naro-muted mt-0.5">
                  {{ description }}
                </DialogDescription>
              </div>
            </slot>

            <DialogClose
              v-if="showClose"
              class="w-7 h-7 rounded-lg bg-obsidian-card hover:bg-obsidian-border text-naro-muted hover:text-white flex items-center justify-center transition-colors cursor-pointer"
            >
              <X class="w-4 h-4" />
            </DialogClose>
          </div>

          <!-- 弹窗主内容插槽 -->
          <div class="py-2 text-sm text-gray-200 leading-relaxed">
            <slot />
          </div>

          <!-- 弹窗底部操作区 -->
          <div v-if="$slots.footer" class="flex items-center justify-end gap-2.5 pt-3 border-t border-obsidian-border/50">
            <slot name="footer" />
          </div>
        </DialogContent>
      </div>
    </DialogPortal>
  </DialogRoot>
</template>
