<script setup lang="ts">
/**
 * 全局黑金高奢 Toast 消息容器组件 (置顶浮动，自适应 Safe Area)
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { AlertCircle, AlertTriangle, CheckCircle2, Info, X } from "lucide-vue-next";

const { toasts, removeToast } = useToast();
</script>

<template>
  <div class="fixed top-4 left-0 right-0 z-[100] flex flex-col items-center gap-2 pointer-events-none px-4 max-w-[440px] mx-auto">
    <transition-group
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="transform -translate-y-3 opacity-0 scale-95"
      enter-to-class="transform translate-y-0 opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="transform translate-y-0 opacity-100 scale-100"
      leave-to-class="transform -translate-y-2 opacity-0 scale-95"
    >
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-center gap-2.5 px-4 py-2.5 rounded-full border shadow-[0_8px_20px_rgba(0,0,0,0.6)] backdrop-blur-xl transition-all"
        :class="[
          toast.type === 'success' && 'bg-[#1C1814]/90 border-[#F9C86D]/40 text-[#F9C86D]',
          toast.type === 'error' && 'bg-[#201012]/90 border-[#EF4444]/40 text-[#F87171]',
          toast.type === 'warning' && 'bg-[#22180E]/90 border-[#F59E0B]/40 text-[#FBBF24]',
          toast.type === 'info' && 'bg-[#14161E]/90 border-[#60A5FA]/40 text-[#93C5FD]',
        ]"
      >
        <!-- 图标 -->
        <CheckCircle2 v-if="toast.type === 'success'" class="w-4 h-4 text-[#F9C86D] shrink-0" />
        <AlertCircle v-else-if="toast.type === 'error'" class="w-4 h-4 text-[#EF4444] shrink-0" />
        <AlertTriangle v-else-if="toast.type === 'warning'" class="w-4 h-4 text-[#F59E0B] shrink-0" />
        <Info v-else class="w-4 h-4 text-[#60A5FA] shrink-0" />

        <!-- 消息文案 -->
        <span class="text-xs font-medium text-[#F5F5F4] tracking-wide">
          {{ toast.message }}
        </span>

        <!-- 关闭微按钮 -->
        <button
          type="button"
          @click="removeToast(toast.id)"
          class="p-0.5 ml-1 text-[#78716C] hover:text-white transition-colors cursor-pointer"
        >
          <X class="w-3.5 h-3.5" />
        </button>
      </div>
    </transition-group>
  </div>
</template>
