<script setup lang="ts">
/**
 * AI 聊天界面 - 聊天信息操作菜单 (1:1 Figma 原型 Frame 104:8282)
 *
 * 尺寸: 120px 宽度
 * 边框: 0.667px solid #44403C
 * 背景: #292524
 * 圆角: 8px
 * 阴影: 0 10px 20px 0 rgba(0, 0, 0, 0.60), 0 6px 10px 0 rgba(0, 0, 0, 0.50)
 * 7 大操作:
 * - 组 1: 重新生成、重跑记忆增强、续写 (带 500/500 角标)
 * - 分割线: #44403C
 * - 组 2: 编辑、分享、开新档、删除
 *
 * @packageDocumentation
 */

import { ref } from "vue";

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "select", action: string): void;
}>();

function handleSelect(action: string): void {
  emit("select", action);
  emit("update:open", false);
}

function handleClose(): void {
  emit("update:open", false);
}
</script>

<template>
  <!-- 点击外部透明遮罩 -->
  <div
    v-if="open"
    @click.stop="handleClose"
    class="fixed inset-0 z-40 bg-transparent"
  />

  <!-- 1:1 聊天信息悬浮菜单 (120px 宽，向上弹出) -->
  <Transition name="menu-pop-up">
    <nav
      v-if="open"
      @click.stop
      class="absolute left-0 bottom-full mb-1.5 z-50 w-[120px] min-w-[120px] rounded-[8px] border border-[#44403C] bg-[#292524] shadow-[0_10px_20px_0_rgba(0,0,0,0.60),0_6px_10px_0_rgba(0,0,0,0.50)] select-none py-1 flex flex-col items-start"
    >
      <!-- 组 1: 重新生成 / 重跑记忆增强 / 续写 -->
      <div class="w-full flex flex-col items-start">
        
        <!-- 1. 重新生成 -->
        <button
          type="button"
          @click="handleSelect('regenerate')"
          class="w-full px-3 py-2 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <g clip-path="url(#clip0_104_8284)">
              <path d="M8.5 0.5L10.5 2.5L8.5 4.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M1.5 5.5V4.5C1.5 3.96957 1.71071 3.46086 2.08579 3.08579C2.46086 2.71071 2.96957 2.5 3.5 2.5H10.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M3.5 11.5L1.5 9.5L3.5 7.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M10.5 6.5V7.5C10.5 8.03043 10.2893 8.53914 9.91421 8.91421C9.53914 9.28929 9.03043 9.5 8.5 9.5H1.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
              <clipPath id="clip0_104_8284">
                <rect width="12" height="12" fill="white"/>
              </clipPath>
            </defs>
          </svg>
          <span class="text-xs text-white/95 group-hover:text-white font-normal leading-4 text-left">
            重新生成
          </span>
        </button>

        <!-- 2. 重跑记忆增强 -->
        <button
          type="button"
          @click="handleSelect('rerunMemory')"
          class="w-full px-3 py-2 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M1.5 6C1.5 4.80653 1.97411 3.66193 2.81802 2.81802C3.66193 1.97411 4.80653 1.5 6 1.5C7.25802 1.50473 8.46552 1.99561 9.37 2.87L10.5 4" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.5 1.5V4H8" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.5 6C10.5 7.19347 10.0259 8.33807 9.18198 9.18198C8.33807 10.0259 7.19347 10.5 6 10.5C4.74198 10.4953 3.53448 10.0044 2.63 9.13L1.5 8" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4 8H1.5V10.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-xs text-white/95 group-hover:text-white font-normal leading-4 text-left">
            重跑记忆增强
          </span>
        </button>

        <!-- 3. 续写 (带 500/500) -->
        <button
          type="button"
          @click="handleSelect('continue')"
          class="w-full px-3 py-2 flex items-center justify-between hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <div class="flex items-center gap-2">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
              <path d="M6 10H10.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8.25 1.74999C8.44891 1.55108 8.7187 1.43933 9 1.43933C9.13929 1.43933 9.27721 1.46677 9.4059 1.52007C9.53458 1.57337 9.65151 1.6515 9.75 1.74999C9.84849 1.84848 9.92662 1.96541 9.97992 2.09409C10.0332 2.22278 10.0607 2.3607 10.0607 2.49999C10.0607 2.63928 10.0332 2.7772 9.97992 2.90589C9.92662 3.03457 9.84849 3.1515 9.75 3.24999L3.5 9.49999L1.5 9.99999L2 7.99999L8.25 1.74999Z" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="text-xs text-white/95 group-hover:text-white font-normal leading-4 text-left">
              续写
            </span>
          </div>
          <span class="text-[10px] text-white/70 font-mono">
            500/500
          </span>
        </button>
      </div>

      <!-- 分割线 -->
      <div class="w-full px-2 py-1">
        <div class="w-full h-[1px] bg-[#44403C]" />
      </div>

      <!-- 组 2: 编辑 / 分享 / 开新档 / 删除 -->
      <div class="w-full flex flex-col items-start">
        
        <!-- 4. 编辑 -->
        <button
          type="button"
          @click="handleSelect('edit')"
          class="w-full px-3 py-2 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <g clip-path="url(#clip0_104_8314)">
              <path d="M5.5 2H2C1.73478 2 1.48043 2.10536 1.29289 2.29289C1.10536 2.48043 1 2.73478 1 3V10C1 10.2652 1.10536 10.5196 1.29289 10.7071C1.48043 10.8946 1.73478 11 2 11H9C9.26522 11 9.51957 10.8946 9.70711 10.7071C9.89464 10.5196 10 10.2652 10 10V6.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9.25 1.24999C9.44891 1.05108 9.7187 0.939331 10 0.939331C10.2813 0.939331 10.5511 1.05108 10.75 1.24999C10.9489 1.4489 11.0607 1.71869 11.0607 1.99999C11.0607 2.2813 10.9489 2.55108 10.75 2.74999L6 7.49999L4 7.99999L4.5 5.99999L9.25 1.24999Z" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
              <clipPath id="clip0_104_8314">
                <rect width="12" height="12" fill="white"/>
              </clipPath>
            </defs>
          </svg>
          <span class="text-xs text-white/95 group-hover:text-white font-normal leading-4 text-left">
            编辑
          </span>
        </button>

        <!-- 5. 分享 -->
        <button
          type="button"
          @click="handleSelect('share')"
          class="w-full px-3 py-2 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <g clip-path="url(#clip0_104_8321)">
              <path d="M2 6V10C2 10.2652 2.10536 10.5196 2.29289 10.7071C2.48043 10.8946 2.73478 11 3 11H9C9.26522 11 9.51957 10.8946 9.70711 10.7071C9.89464 10.5196 10 10.2652 10 10V6" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M8 3L6 1L4 3" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M6 1V7.5" stroke="white" stroke-opacity="0.95" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
              <clipPath id="clip0_104_8321">
                <rect width="12" height="12" fill="white"/>
              </clipPath>
            </defs>
          </svg>
          <span class="text-xs text-white/95 group-hover:text-white font-normal leading-4 text-left">
            分享
          </span>
        </button>

        <!-- 6. 开新档 (剧情分支) -->
        <button
          type="button"
          @click="handleSelect('branch')"
          class="w-full px-3 py-2 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="12" height="12" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M3.5 1.75V8.75" stroke="white" stroke-opacity="0.95" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.5 5.25C11.4665 5.25 12.25 4.4665 12.25 3.5C12.25 2.5335 11.4665 1.75 10.5 1.75C9.5335 1.75 8.75 2.5335 8.75 3.5C8.75 4.4665 9.5335 5.25 10.5 5.25Z" stroke="white" stroke-opacity="0.95" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3.5 12.25C4.4665 12.25 5.25 11.4665 5.25 10.5C5.25 9.5335 4.4665 8.75 3.5 8.75C2.5335 8.75 1.75 9.5335 1.75 10.5C1.75 11.4665 2.5335 12.25 3.5 12.25Z" stroke="white" stroke-opacity="0.95" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.5 5.25C10.5 6.64239 9.94688 7.97774 8.96231 8.96231C7.97774 9.94688 6.64239 10.5 5.25 10.5" stroke="white" stroke-opacity="0.95" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-xs text-white/95 group-hover:text-white font-normal leading-4 text-left">
            开新档
          </span>
        </button>

        <!-- 7. 删除 -->
        <button
          type="button"
          @click="handleSelect('delete')"
          class="w-full px-3 py-2 flex items-center justify-start gap-2 hover:bg-red-500/10 active:bg-red-500/20 transition-colors cursor-pointer group text-left text-red-400/90 hover:text-red-400"
        >
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <g clip-path="url(#clip0_104_8338)">
              <path d="M1.5 3H2.5H10.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M9.5 3V10C9.5 10.2652 9.39464 10.5196 9.20711 10.7071C9.01957 10.8946 8.76522 11 8.5 11H3.5C3.23478 11 2.98043 10.8946 2.79289 10.7071C2.60536 10.5196 2.5 10.2652 2.5 10V3M4 3V2C4 1.73478 4.10536 1.48043 4.29289 1.29289C4.48043 1.10536 4.73478 1 5 1H7C7.26522 1 7.51957 1.10536 7.70711 1.29289C7.89464 1.48043 8 1.73478 8 2V3" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M5 5.5V8.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M7 5.5V8.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
            <defs>
              <clipPath id="clip0_104_8338">
                <rect width="12" height="12" fill="white"/>
              </clipPath>
            </defs>
          </svg>
          <span class="text-xs font-normal leading-4 text-left">
            删除
          </span>
        </button>

      </div>
    </nav>
  </Transition>
</template>

<style scoped>
.menu-pop-up-enter-active,
.menu-pop-up-leave-active {
  transition: opacity 0.15s ease, transform 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: bottom left;
}
.menu-pop-up-enter-from,
.menu-pop-up-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(4px);
}
</style>
