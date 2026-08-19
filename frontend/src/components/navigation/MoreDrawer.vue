<script setup lang="ts">
/**
 * 底部“更多”功能抽屉弹框组件 (1:1 原型高保真)
 *
 * 包含创作者、榜单、历史、活动、我的画廊、聊天室、关注动态、公告、问卷、帮助中心 10 项功能入口。
 *
 * @packageDocumentation
 */

import { useAppStore } from "@/stores/app";
import { useRouter } from "vue-router";

const appStore = useAppStore();
const router = useRouter();

function handleItemClick(action: string) {
  appStore.closeMoreDrawer();
  if (action === "history") {
    router.push("/history");
  } else if (action === "creator") {
    router.push("/creator");
  } else if (action === "ranking") {
    router.push("/ranking");
  } else if (action === "activity") {
    router.push("/activity");
  } else if (action === "notice") {
    router.push("/notice");
  } else {
    // 其他功能反馈
  }
}
</script>

<template>
  <!-- 抽屉遮罩与内容包装器 -->
  <Teleport to="body">
    <Transition name="drawer-fade">
      <div
        v-if="appStore.isMoreDrawerOpen"
        class="fixed inset-0 z-50 flex flex-col justify-end"
      >
        <!-- 1. 暗黑背景遮罩 (点击可关闭) -->
        <div
          class="absolute inset-0 bg-black/60 backdrop-blur-[2px] transition-opacity"
          @click="appStore.closeMoreDrawer()"
        />

        <!-- 2. 抽屉卡片主体: width: 440px max; border-radius: 12px 12px 0 0; bg: #1A1714; border-top: 0.667px solid rgba(68, 64, 60, 0.50); -->
        <div
          class="relative w-full max-w-[440px] mx-auto p-3 pb-6 rounded-t-xl border-t border-[rgba(68,64,60,0.50)] bg-[#1A1714] shadow-2xl z-10 flex flex-col select-none animate-slide-up"
        >
          <!-- 顶部拖拽条 Handle: width: 32px; height: 2px; border-radius: 9999px; background: rgba(120, 113, 108, 0.40); -->
          <div class="w-8 h-[2px] rounded-full bg-[rgba(120,113,108,0.40)] mx-auto mb-3" />

          <!-- 3 行 4 列功能网格: row-gap: 8px; column-gap: 8px; -->
          <div class="grid grid-cols-4 gap-2 w-full">
            
            <!-- Row 1: Col 1 & 2 为空，Col 3 创作者，Col 4 榜单 -->
            <div class="hidden col-span-2 sm:block" /> <!-- 空占位让第 1 行从第 3 列开始 -->
            <div class="col-span-2 grid grid-cols-2 gap-2 col-start-3">
              <!-- 1. 创作者 -->
              <button
                type="button"
                @click="handleItemClick('creator')"
                class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M13.3333 17.5V15.8333C13.3333 14.9493 12.9821 14.1014 12.357 13.4763C11.7319 12.8512 10.8841 12.5 10 12.5H4.16667C3.28261 12.5 2.43476 12.8512 1.80964 13.4763C1.18452 14.1014 0.833332 14.9493 0.833332 15.8333V17.5" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M7.08333 9.16667C8.92428 9.16667 10.4167 7.67428 10.4167 5.83333C10.4167 3.99238 8.92428 2.5 7.08333 2.5C5.24238 2.5 3.75 3.99238 3.75 5.83333C3.75 7.67428 5.24238 9.16667 7.08333 9.16667Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>创作者</span>
              </button>

              <!-- 2. 榜单 -->
              <button
                type="button"
                @click="handleItemClick('ranking')"
                class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M7.5 15.8333V10.8333C7.5 10.3913 7.3244 9.96738 7.01184 9.65482C6.69928 9.34226 6.27536 9.16667 5.83333 9.16667H4.16667C3.72464 9.16667 3.30072 9.34226 2.98816 9.65482C2.67559 9.96738 2.5 10.3913 2.5 10.8333V15.8333C2.5 16.2754 2.67559 16.6993 2.98816 17.0118C3.30072 17.3244 3.72464 17.5 4.16667 17.5H5.83333C6.27536 17.5 6.69928 17.3244 7.01184 17.0118C7.3244 16.6993 7.5 16.2754 7.5 15.8333ZM7.5 15.8333V7.5C7.5 7.05797 7.67559 6.63405 7.98816 6.32149C8.30072 6.00893 8.72464 5.83333 9.16667 5.83333H10.8333C11.2754 5.83333 11.6993 6.00893 12.0118 6.32149C12.3244 6.63405 12.5 7.05797 12.5 7.5V15.8333M7.5 15.8333C7.5 16.2754 7.67559 16.6993 7.98816 17.0118C8.30072 17.3244 8.72464 17.5 9.16667 17.5H10.8333C11.2754 17.5 11.6993 17.3244 12.0118 17.0118C12.3244 16.6993 12.5 16.2754 12.5 15.8333M12.5 15.8333V4.16667C12.5 3.72464 12.6756 3.30072 12.9882 2.98816C13.3007 2.67559 13.7246 2.5 14.1667 2.5H15.8333C16.2754 2.5 16.6993 2.67559 17.0118 2.98816C17.3244 3.30072 17.5 3.72464 17.5 4.16667V15.8333C17.5 16.2754 17.3244 16.6993 17.0118 17.0118C16.6993 17.3244 16.2754 17.5 15.8333 17.5H14.1667C13.7246 17.5 13.3007 17.3244 12.9882 17.0118C12.6756 16.6993 12.5 16.2754 12.5 15.8333Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span>榜单</span>
              </button>
            </div>

            <!-- Row 2: 历史、活动、我的画廊、聊天室 -->
            <!-- 3. 历史 -->
            <button
              type="button"
              @click="handleItemClick('history')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 6.66667V10L12.5 12.5M17.5 10C17.5 10.9849 17.306 11.9602 16.9291 12.8701C16.5522 13.7801 15.9997 14.6069 15.3033 15.3033C14.6069 15.9997 13.7801 16.5522 12.8701 16.9291C11.9602 17.306 10.9849 17.5 10 17.5C9.01509 17.5 8.03982 17.306 7.12987 16.9291C6.21993 16.5522 5.39314 15.9997 4.6967 15.3033C4.00026 14.6069 3.44781 13.7801 3.0709 12.8701C2.69399 11.9602 2.5 10.9849 2.5 10C2.5 8.01088 3.29018 6.10322 4.6967 4.6967C6.10322 3.29018 8.01088 2.5 10 2.5C11.9891 2.5 13.8968 3.29018 15.3033 4.6967C16.7098 6.10322 17.5 8.01088 17.5 10Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>历史</span>
            </button>

            <!-- 4. 活动 -->
            <button
              type="button"
              @click="handleItemClick('activity')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10.8333 8.33333V2.5L3.33333 11.6667H9.16667V17.5L16.6667 8.33333H10.8333Z" fill="#F9C86D"/>
              </svg>
              <span>活动</span>
            </button>

            <!-- 5. 我的画廊 -->
            <button
              type="button"
              @click="handleItemClick('gallery')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M15.8333 2.5H4.16667C3.24619 2.5 2.5 3.24619 2.5 4.16667V15.8333C2.5 16.7538 3.24619 17.5 4.16667 17.5H15.8333C16.7538 17.5 17.5 16.7538 17.5 15.8333V4.16667C17.5 3.24619 16.7538 2.5 15.8333 2.5Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7.08333 8.33334C7.77369 8.33334 8.33333 7.7737 8.33333 7.08334C8.33333 6.39299 7.77369 5.83334 7.08333 5.83334C6.39298 5.83334 5.83333 6.39299 5.83333 7.08334C5.83333 7.7737 6.39298 8.33334 7.08333 8.33334Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M17.5 12.5L13.3333 8.33334L4.16667 17.5" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>我的画廊</span>
            </button>

            <!-- 6. 聊天室 -->
            <button
              type="button"
              @click="handleItemClick('chatroom')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M17.5 12.5C17.5 12.942 17.3244 13.366 17.0118 13.6785C16.6993 13.9911 16.2754 14.1667 15.8333 14.1667H5.83333L2.5 17.5V4.16667C2.5 3.72464 2.67559 3.30072 2.98816 2.98816C3.30072 2.67559 3.72464 2.5 4.16667 2.5H15.8333C16.2754 2.5 16.6993 2.67559 17.0118 2.98816C17.3244 3.30072 17.5 3.72464 17.5 4.16667V12.5Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>聊天室</span>
            </button>

            <!-- Row 3: 关注动态、公告、问卷、帮助中心 -->
            <!-- 7. 关注动态 -->
            <button
              type="button"
              @click="handleItemClick('following')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M13.3333 17.5V15.8333C13.3333 14.9493 12.9821 14.1014 12.357 13.4763C11.7319 12.8512 10.884 12.5 9.99999 12.5H4.16666C3.28261 12.5 2.43476 12.8512 1.80964 13.4763C1.18452 14.1014 0.833328 14.9493 0.833328 15.8333V17.5" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7.08333 9.16667C8.92428 9.16667 10.4167 7.67428 10.4167 5.83333C10.4167 3.99238 8.92428 2.5 7.08333 2.5C5.24238 2.5 3.75 3.99238 3.75 5.83333C3.75 7.67428 5.24238 9.16667 7.08333 9.16667Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M16.6667 6.66666V11.6667M19.1667 9.16666H14.1667" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>关注动态</span>
            </button>

            <!-- 8. 公告 -->
            <button
              type="button"
              @click="handleItemClick('announcement')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M9.16667 15.8333C9.16667 16.4964 8.90327 17.1323 8.43443 17.6011C7.96559 18.07 7.32971 18.3333 6.66667 18.3333C6.00363 18.3333 5.36774 18.07 4.8989 17.6011C4.43006 17.1323 4.16667 16.4964 4.16667 15.8333V10.8333M2.5 9.16668L17.5 3.33334V16.6667L2.5 10.8333V9.16668Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>公告</span>
            </button>

            <!-- 9. 问卷 -->
            <button
              type="button"
              @click="handleItemClick('survey')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M12.5 1.66666H7.5C7.03976 1.66666 6.66667 2.03975 6.66667 2.49999V4.16666C6.66667 4.62689 7.03976 4.99999 7.5 4.99999H12.5C12.9602 4.99999 13.3333 4.62689 13.3333 4.16666V2.49999C13.3333 2.03975 12.9602 1.66666 12.5 1.66666Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M13.3333 3.33334H15C15.442 3.33334 15.8659 3.50894 16.1785 3.8215C16.4911 4.13406 16.6667 4.55798 16.6667 5.00001V16.6667C16.6667 17.1087 16.4911 17.5326 16.1785 17.8452C15.8659 18.1577 15.442 18.3333 15 18.3333H5C4.55797 18.3333 4.13405 18.1577 3.82149 17.8452C3.50893 17.5326 3.33333 17.1087 3.33333 16.6667V5.00001C3.33333 4.55798 3.50893 4.13406 3.82149 3.8215C4.13405 3.50894 4.55797 3.33334 5 3.33334H6.66667" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7.5 9.16666H12.5" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7.5 12.5H10.8333" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>问卷</span>
            </button>

            <!-- 10. 帮助中心 -->
            <button
              type="button"
              @click="handleItemClick('help')"
              class="h-[59.25px] p-1 flex flex-col items-center justify-center gap-1 rounded-md bg-[#292524] hover:bg-[#383330] active:scale-95 transition-all text-[#F5F5F4] text-[9px] cursor-pointer"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 18.3333C14.6024 18.3333 18.3333 14.6024 18.3333 9.99999C18.3333 5.39762 14.6024 1.66666 10 1.66666C5.39763 1.66666 1.66667 5.39762 1.66667 9.99999C1.66667 14.6024 5.39763 18.3333 10 18.3333Z" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M7.575 7.49999C7.77092 6.94304 8.15762 6.47341 8.66663 6.17426C9.17563 5.87512 9.77408 5.76577 10.356 5.86558C10.9379 5.96539 11.4657 6.26792 11.8459 6.71959C12.2261 7.17126 12.4342 7.74292 12.4333 8.33332C12.4333 9.99999 9.93333 10.8333 9.93333 10.8333" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M10 14.1667H10.0083" stroke="#F9C86D" stroke-width="1.66667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>帮助中心</span>
            </button>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.drawer-fade-enter-active,
.drawer-fade-leave-active {
  transition: opacity 0.2s ease;
}

.drawer-fade-enter-from,
.drawer-fade-leave-to {
  opacity: 0;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.animate-slide-up {
  animation: slideUp 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
