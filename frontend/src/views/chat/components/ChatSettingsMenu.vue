<script setup lang="ts">
/**
 * AI 聊天界面 - 设置下拉菜单 (1:1 Figma 原型 Frame 95:6578)
 *
 * 严格按照 Figma 原型构建：
 * 尺寸: 宽度 192px
 * 边框: 0.667px solid #44403C
 * 圆角: 6px
 * 阴影: 0 10px 20px 0 rgba(0, 0, 0, 0.60), 0 6px 10px 0 rgba(0, 0, 0, 0.50)
 * 背景: #292524
 * 全部项严格左对齐 (px-4 16px 左内边距，16x16 原生 SVG，8px 间距，14px 文字左对齐)
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

// 声音状态 (默认关闭)
const isMuted = ref(true);

function handleSelect(action: string): void {
  if (action === "toggleSound") {
    isMuted.value = !isMuted.value;
  }
  emit("select", action);
  emit("update:open", false);
}

function handleClose(): void {
  emit("update:open", false);
}
</script>

<template>
  <!-- 点击外部透明蒙层 -->
  <div
    v-if="open"
    @click="handleClose"
    class="fixed inset-0 z-40 bg-transparent"
  />

  <!-- 1:1 Figma Dropdown Menu (top: 40px, right: 0, w: 192px) -->
  <Transition name="menu-pop">
    <nav
      v-if="open"
      class="absolute right-0 top-[40px] z-50 w-[192px] rounded-[6px] border border-[#44403C] bg-[#292524] shadow-[0_10px_20px_0_rgba(0,0,0,0.60),0_6px_10px_0_rgba(0,0,0,0.50)] overflow-hidden select-none py-1 flex flex-col items-start"
    >
      <!-- 组 1: 语言 / 声音关闭 / 选择主题 -->
      <div class="w-full flex flex-col items-start">
        
        <!-- 1. 语言 -->
        <button
          type="button"
          @click="handleSelect('language')"
          class="w-full h-9 px-4 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M3.33333 5.33333L7.33333 9.33333" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M2.66667 9.33333L6.66667 5.33333L8 3.33333" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M1.33333 3.33333H9.33333" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.66667 1.33333H5.33333" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M14.6667 14.6667L11.3333 8L8 14.6667" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 12H13.3333" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[14px] text-[#A8A29E] group-hover:text-[#F5F5F4] font-normal leading-5 text-left">
            语言
          </span>
        </button>

        <!-- 2. 声音关闭 / 开启 -->
        <button
          type="button"
          @click="handleSelect('toggleSound')"
          class="w-full h-9 px-4 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <!-- 声音关闭 SVG -->
          <svg v-if="isMuted" width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M7.33333 3.33333L4 6H1.33333V10H4L7.33333 12.6667V3.33333Z" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M10.36 5.64C10.9849 6.26509 11.336 7.11279 11.336 7.99667C11.336 8.88055 10.9849 9.72824 10.36 10.3533" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.7133 3.28667C13.9631 4.53685 14.6652 6.23224 14.6652 8C14.6652 9.76776 13.9631 11.4631 12.7133 12.7133" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <!-- 声音开启 SVG -->
          <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M7.33333 3.33333L4 6H1.33333V10H4L7.33333 12.6667V3.33333Z" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M12.6667 4.66667C13.6667 5.66667 14.3333 7.33333 14.3333 9C14.3333 10.6667 13.6667 12.3333 12.6667 13.3333" stroke="#F9C86D" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[14px] text-[#A8A29E] group-hover:text-[#F5F5F4] font-normal leading-5 text-left">
            {{ isMuted ? '声音关闭' : '声音开启' }}
          </span>
        </button>

        <!-- 3. 选择主题 -->
        <button
          type="button"
          @click="handleSelect('theme')"
          class="w-full h-9 px-4 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M9 4.66667C9.1841 4.66667 9.33333 4.51743 9.33333 4.33334C9.33333 4.14924 9.1841 4 9 4C8.81591 4 8.66667 4.14924 8.66667 4.33334C8.66667 4.51743 8.81591 4.66667 9 4.66667Z" fill="#A8A29E" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M11.6667 7.33333C11.8508 7.33333 12 7.1841 12 7C12 6.81591 11.8508 6.66667 11.6667 6.66667C11.4826 6.66667 11.3333 6.81591 11.3333 7C11.3333 7.1841 11.4826 7.33333 11.6667 7.33333Z" fill="#A8A29E" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M5.66667 5.33333C5.85076 5.33333 6 5.1841 6 5C6 4.81591 5.85076 4.66667 5.66667 4.66667C5.48257 4.66667 5.33333 4.81591 5.33333 5C5.33333 5.1841 5.48257 5.33333 5.66667 5.33333Z" fill="#A8A29E" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.33333 8.66667C4.51743 8.66667 4.66667 8.51743 4.66667 8.33334C4.66667 8.14924 4.51743 8 4.33333 8C4.14924 8 4 8.14924 4 8.33334C4 8.51743 4.14924 8.66667 4.33333 8.66667Z" fill="#A8A29E" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M8 1.33333C4.33333 1.33333 1.33333 4.33333 1.33333 8C1.33333 11.6667 4.33333 14.6667 8 14.6667C8.61733 14.6667 9.09867 14.1693 9.09867 13.5413C9.09867 13.25 8.97867 12.9847 8.80733 12.7913C8.614 12.5987 8.51533 12.3567 8.51533 12.0413C8.51281 11.8946 8.53984 11.7489 8.59483 11.6128C8.64982 11.4768 8.73164 11.3532 8.8354 11.2494C8.93917 11.1456 9.06276 11.0638 9.19882 11.0088C9.33487 10.9538 9.48061 10.9268 9.62733 10.9293H10.958C12.992 10.9293 14.6613 9.26067 14.6613 7.22667C14.6433 4.008 11.6407 1.33333 8 1.33333Z" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[14px] text-[#A8A29E] group-hover:text-[#F5F5F4] font-normal leading-5 text-left">
            选择主题
          </span>
        </button>
      </div>

      <!-- 组 2: 高级设置 (上方带 0.667px 细分割线) -->
      <div class="w-full pt-1 mt-1 border-t border-[#44403C] flex flex-col items-start">
        <button
          type="button"
          @click="handleSelect('advanced')"
          class="w-full h-9 px-4 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M8 13.3333H14" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M11 2.33333C11.2652 2.06812 11.6249 1.91912 12 1.91912C12.1857 1.91912 12.3696 1.9557 12.5412 2.02677C12.7128 2.09784 12.8687 2.20201 13 2.33333C13.1313 2.46466 13.2355 2.62056 13.3066 2.79214C13.3776 2.96372 13.4142 3.14762 13.4142 3.33333C13.4142 3.51905 13.3776 3.70295 13.3066 3.87453C13.2355 4.04611 13.1313 4.20201 13 4.33333L4.66667 12.6667L2 13.3333L2.66667 10.6667L11 2.33333Z" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[14px] text-[#A8A29E] group-hover:text-[#F5F5F4] font-normal leading-5 text-left">
            高级设置
          </span>
        </button>
      </div>

      <!-- 组 3: 新手攻略 (上方带 0.667px 细分割线) -->
      <div class="w-full pt-1 mt-1 border-t border-[#44403C] flex flex-col items-start">
        <button
          type="button"
          @click="handleSelect('guide')"
          class="w-full h-9 px-4 flex items-center justify-start gap-2 hover:bg-white/5 active:bg-white/10 transition-colors cursor-pointer group text-left"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="shrink-0">
            <path d="M2.66667 13C2.66667 12.558 2.84226 12.134 3.15482 11.8215C3.46738 11.5089 3.89131 11.3333 4.33333 11.3333H13.3333" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M4.33333 1.33333H13.3333V14.6667H4.33333C3.89131 14.6667 3.46738 14.4911 3.15482 14.1785C2.84226 13.8659 2.66667 13.442 2.66667 13V2.99999C2.66667 2.55797 2.84226 2.13404 3.15482 1.82148C3.46738 1.50892 3.89131 1.33333 4.33333 1.33333Z" stroke="#A8A29E" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[14px] text-[#A8A29E] group-hover:text-[#F5F5F4] font-normal leading-5 text-left">
            新手攻略
          </span>
        </button>
      </div>

    </nav>
  </Transition>
</template>

<style scoped>
.menu-pop-enter-active,
.menu-pop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s cubic-bezier(0.16, 1, 0.3, 1);
  transform-origin: top right;
}
.menu-pop-enter-from,
.menu-pop-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-4px);
}
</style>
