<script setup lang="ts">
/**
 * 黑金暗黑玻璃拟物风格移动端手势抽屉 (BottomSheet / Drawer) 组件。
 *
 * 基于 Vaul Vue 封装，具备原生 iOS 物理阻尼拖拽感、多档位吸附 (Snap Points)、
 * 下拉手势关闭、遮罩模糊与 Safe Area 底部贴合。
 *
 * Usage:
 *   <AppDrawer v-model:open="isDrawerOpen" title="模型渠道选择">
 *     <div class="p-4 space-y-3">
 *       <!-- 模型列表 -->
 *     </div>
 *   </AppDrawer>
 */

import { X } from "lucide-vue-next";
import {
  DrawerClose,
  DrawerContent,
  DrawerDescription,
  DrawerHandle,
  DrawerOverlay,
  DrawerPortal,
  DrawerRoot,
  DrawerTitle,
} from "vaul-vue";

interface Props {
  /** 抽屉显隐状态 (支持 v-model:open) */
  open: boolean;
  /** 抽屉标题文本 */
  title?: string;
  /** 抽屉辅助描述文本 */
  description?: string;
  /** 是否显示拖拽顶部指示条 (Handle) */
  showHandle?: boolean;
  /** 是否显示右上角关闭按钮 */
  showClose?: boolean;
  /** 吸附档位设置 (例如: ['300px', '600px', 1]) */
  snapPoints?: (string | number)[];
  /** 自定义内容类名 */
  customClass?: string;
}

withDefaults(defineProps<Props>(), {
  title: "",
  description: "",
  showHandle: true,
  showClose: false,
  snapPoints: undefined,
  customClass: "",
});

const emit = defineEmits<(e: "update:open", value: boolean) => void>();
</script>

<template>
  <DrawerRoot
    :open="open"
    :snap-points="snapPoints"
    @update:open="(val: boolean) => emit('update:open', val)"
  >
    <DrawerPortal>
      <!-- 高斯模糊暗黑遮罩 -->
      <DrawerOverlay class="drawer-overlay" />

      <!-- 黑金抽屉内容面板 -->
      <DrawerContent
        :class="[
          'drawer-content',
          customClass
        ]"
      >
        <!-- 拖拽手势顶部把手条 -->
        <DrawerHandle v-if="showHandle" class="drawer-handle" />

        <!-- 抽屉头部 -->
        <div v-if="title || $slots.header" class="px-5 pt-1 pb-3 flex items-center justify-between border-b border-obsidian-border/50 shrink-0">
          <slot name="header">
            <div>
              <DrawerTitle class="text-base font-bold text-naro-gold tracking-wide font-serif">
                {{ title }}
              </DrawerTitle>
              <DrawerDescription v-if="description" class="text-xs text-naro-muted mt-0.5">
                {{ description }}
              </DrawerDescription>
            </div>
          </slot>

          <DrawerClose
            v-if="showClose"
            class="w-7 h-7 rounded-lg bg-obsidian-card hover:bg-obsidian-border text-naro-muted hover:text-white flex items-center justify-center transition-colors cursor-pointer"
          >
            <X class="w-4 h-4" />
          </DrawerClose>
        </div>

        <!-- 抽屉滚动主内容区域 (Safe Area 底部贴合) -->
        <div class="flex-1 overflow-y-auto px-5 py-4 text-sm text-gray-200 pb-safe">
          <slot />
        </div>

        <!-- 抽屉底部固定操作区 (可选) -->
        <div v-if="$slots.footer" class="p-4 border-t border-obsidian-border/60 bg-obsidian-surface/95 pb-safe shrink-0">
          <slot name="footer" />
        </div>
      </DrawerContent>
    </DrawerPortal>
  </DrawerRoot>
</template>
