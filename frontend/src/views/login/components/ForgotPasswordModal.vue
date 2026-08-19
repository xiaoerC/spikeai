<script setup lang="ts">
/**
 * 叙梦 Naro - 忘记密码模态弹窗组件 (严格 1:1 还原 Figma 原型 298px 尺寸与间距)
 *
 * @packageDocumentation
 */

import { DialogClose, DialogContent, DialogOverlay, DialogPortal, DialogRoot } from "reka-ui";
import { ref } from "vue";

interface Props {
  /** 弹窗显隐状态 (支持 v-model:open) */
  open: boolean;
}

defineProps<Props>();

const emit = defineEmits<{
  (e: "update:open", value: boolean): void;
  (e: "success"): void;
  (e: "switchToLogin"): void;
}>();

const email = ref("");
const isSubmitting = ref(false);
const isSent = ref(false);

/**
 * 发送重置码
 */
function handleSendReset(): void {
  if (!email.value.trim() || isSubmitting.value) return;
  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    isSent.value = true;
    emit("success");
  }, 500);
}
</script>

<template>
  <DialogRoot :open="open" @update:open="(val: boolean) => emit('update:open', val)">
    <DialogPortal>
      <!-- 高斯模糊暗黑遮罩: 调轻暗度至 bg-black/55，透出底层微光 -->
      <DialogOverlay class="fixed inset-0 z-50 bg-black/55 backdrop-blur-sm animate-fade-in" />

      <!-- 居中视口容器 -->

      <div class="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
        <!-- 忘记密码卡片主体: width: 403px, height: 298px, padding: 16px, border-radius: 8px, border: 0.667px solid #44403C -->
        <DialogContent
          class="pointer-events-auto relative w-full max-w-[403px] h-[298px] rounded-lg border-[0.667px] border-[#44403C] p-4 flex flex-col items-center justify-between shadow-[0_10px_20px_0_rgba(0,0,0,0.60),0_6px_10px_0_rgba(0,0,0,0.50)] outline-none animate-scale-in select-none"
          style="background: linear-gradient(135deg, #1A1511 0%, #2A221A 100%), #0C0A09;"
        >
          <!-- 1. 右上角关闭按钮 (16x16) -->
          <DialogClose class="absolute right-3 top-3 p-1 text-[#78716C] hover:text-white transition-colors cursor-pointer outline-none z-10">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4L4 12" stroke="#78716C" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 4L12 12" stroke="#78716C" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </DialogClose>

          <!-- 2. 标题与副标题区 -->
          <div class="w-full flex flex-col items-center pt-1">
            <!-- 忘记密码 (Noto Serif SC, 24px, #F9C86D) -->
            <h2 class="text-[24px] font-semibold text-[#F9C86D] tracking-[-0.48px] leading-[28.8px] font-serif">
              忘记密码
            </h2>
            <!-- 输入您的邮箱地址,我们将发送重置码 (14px, #78716C, pt-2) -->
            <p class="text-[14px] font-normal text-[#78716C] tracking-[-0.176px] leading-5 pt-2 text-center">
              输入您的邮箱地址,我们将发送重置码
            </p>
          </div>

          <!-- 3. Form 邮箱输入区 (padding-top: 24px, 容器高度 60px) -->
          <div class="w-full flex flex-col items-center pt-1">
            <div class="w-full h-[60px] flex flex-col justify-center items-center relative group">
              <input
                v-model="email"
                type="email"
                placeholder="输入您的邮箱..."
                class="w-full h-10 px-3 text-center text-[16px] text-[#F4E8C1] placeholder-[#78716C] bg-transparent border-none outline-none tracking-[0.8px] font-sans"
              />
              <!-- 向两端渐隐的流光底线 -->
              <div class="w-[300px] h-[1px] bg-gradient-to-r from-transparent via-[#F4E8C1]/30 to-transparent group-focus-within:via-[#F9C86D] transition-all" />
            </div>

            <!-- 成功提示 (轻量提示) -->
            <p v-if="isSent" class="text-xs text-[#F9C86D] -mt-1 pb-1 animate-fade-in">
              ✓ 重置码已发送至您的邮箱
            </p>
          </div>

          <!-- 4. 发送重置码 按钮容器 (padding-top: 32px, 按钮宽 106px, 高 36px) -->
          <div class="w-full flex items-center justify-center pt-1">
            <button
              type="button"
              @click="handleSendReset"
              :disabled="isSubmitting"
              :class="[
                'h-9 px-3 flex items-center justify-center gap-1.5 rounded-lg bg-[#F9C86D] text-[#0C0A09] font-medium text-[12px] tracking-[0.3px] shadow-gold active:scale-95 transition-all cursor-pointer select-none',
                !email.trim() ? 'opacity-50' : 'opacity-100 hover:brightness-105'
              ]"
            >
              <!-- 纸飞机图标 (14x14, 黑色线条) -->
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7 11.0833L12.25 12.25L7 1.75L1.75 12.25L7 11.0833ZM7 11.0833V6.41667" stroke="#0C0A09" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <span>{{ isSubmitting ? "发送中..." : "发送重置码" }}</span>
            </button>
          </div>

          <!-- 5. 底部返回登录 (padding-top: 24px, height: 32px) -->
          <div class="w-full flex items-center justify-center gap-2 text-xs pt-2 pb-1">
            <span class="text-[#78716C] text-[12px] tracking-[-0.176px]">记起密码了?</span>
            <button
              type="button"
              @click="emit('switchToLogin')"
              class="text-[#A8A29E] text-[12px] tracking-[-0.176px] font-medium underline hover:text-[#F9C86D] transition-colors cursor-pointer"
            >
              返回登录
            </button>
          </div>

        </DialogContent>
      </div>
    </DialogPortal>
  </DialogRoot>
</template>
