<script setup lang="ts">
/**
 * 叙梦 Naro - 黑金奢华登录模态弹窗组件 (严格按照 Figma 原型 442px 尺寸与大间距 1:1 还原)
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
  (e: "switchToRegister"): void;
  (e: "switchToForgot"): void;
}>();

/** 表单输入状态 */
const email = ref("1103560524@qq.com");
const password = ref("a1111111");
const isSubmitting = ref(false);

/**
 * 提交登录
 */
function handleLogin(): void {
  isSubmitting.value = true;
  setTimeout(() => {
    isSubmitting.value = false;
    emit("success");
    emit("update:open", false);
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
        <!-- 登录卡片主体: width: 403px, height: 442px, padding: 16px, border-radius: 8px, border: 0.667px solid #44403C -->
        <DialogContent
          class="pointer-events-auto relative w-full max-w-[403px] h-[442px] rounded-lg border-[0.667px] border-[#44403C] p-4 flex flex-col items-center justify-between shadow-[0_10px_20px_0_rgba(0,0,0,0.60),0_6px_10px_0_rgba(0,0,0,0.50)] outline-none animate-scale-in select-none"
          style="background: linear-gradient(135deg, #1A1511 0%, #2A221A 100%), #0C0A09;"
        >
          <!-- 1. 右上角关闭按钮 (16x16) -->
          <DialogClose class="absolute right-3 top-3 p-1 text-[#78716C] hover:text-white transition-colors cursor-pointer outline-none z-10">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M12 4L4 12" stroke="#78716C" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
              <path d="M4 4L12 12" stroke="#78716C" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </DialogClose>

          <!-- 2. 标题区: WELCOME BACK (Cinzel 24px, #F9C86D) -->
          <div class="w-full flex flex-col items-center pt-1">
            <h2 class="text-[24px] font-semibold text-[#F9C86D] tracking-[-0.48px] leading-[28.8px] font-serif uppercase">
              Welcome Back
            </h2>
          </div>

          <!-- 3. Form 表单输入区 (padding-top: 8px, 两个 60px 高度容器) -->
          <div class="w-full flex flex-col items-center pt-2">
            <!-- 邮箱输入容器: height 60px, min-height 60px -->
            <div class="w-full h-[60px] flex flex-col justify-center items-center relative group">
              <input
                v-model="email"
                type="email"
                placeholder="请输入邮箱 / 账号"
                class="w-full h-10 px-3 text-center text-[16px] text-[#F4E8C1] placeholder-[#78716C] bg-transparent border-none outline-none tracking-[0.8px] font-sans"
              />
              <!-- 向两端渐隐的流光底线 -->
              <div class="w-[300px] h-[1px] bg-gradient-to-r from-transparent via-[#F4E8C1]/30 to-transparent group-focus-within:via-[#F9C86D] transition-all" />
            </div>

            <!-- 密码输入容器: height 60px, min-height 60px -->
            <div class="w-full h-[60px] flex flex-col justify-center items-center relative group">
              <input
                v-model="password"
                type="password"
                placeholder="请输入密码"
                class="w-full h-10 px-3 text-center text-[16px] text-[#F4E8C1] placeholder-[#78716C] bg-transparent border-none outline-none tracking-[2px] font-sans"
              />
              <!-- 向两端渐隐的流光底线 -->
              <div class="w-[300px] h-[1px] bg-gradient-to-r from-transparent via-[#F4E8C1]/30 to-transparent group-focus-within:via-[#F9C86D] transition-all" />
            </div>
          </div>

          <!-- 4. Google 登录容器 (padding-top: 24px, height: 36px) -->
          <div class="w-full flex items-center justify-center pt-2">
            <button
              type="button"
              class="flex items-center gap-1.5 px-3 py-1 text-xs text-[#A8A29E] hover:text-white transition-colors cursor-pointer select-none"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path opacity="0.9" d="M18.8 10.2083C18.8 9.55833 18.7417 8.93333 18.6333 8.33333H10V11.8833H14.9333C14.7167 13.025 14.0667 13.9917 13.0917 14.6417V16.95H16.0667C17.8 15.35 18.8 13 18.8 10.2083Z" fill="#A8A29E"/>
                <path opacity="0.8" d="M10 19.1667C12.475 19.1667 14.55 18.35 16.0667 16.95L13.0917 14.6417C12.275 15.1917 11.2333 15.525 10 15.525C7.61667 15.525 5.59167 13.9167 4.86667 11.75H1.81667V14.1167C3.325 17.1083 6.41667 19.1667 10 19.1667Z" fill="#A8A29E"/>
                <path opacity="0.7" d="M4.86667 11.7417C4.68333 11.1917 4.575 10.6083 4.575 10C4.575 9.39167 4.68333 8.80833 4.86667 8.25833V5.89167H1.81667C1.19167 7.125 0.833332 8.51667 0.833332 10C0.833332 11.4833 1.19167 12.875 1.81667 14.1083L4.19167 12.2583L4.86667 11.7417Z" fill="#A8A29E"/>
                <path opacity="0.85" d="M10 4.48333C11.35 4.48333 12.55 4.95 13.5083 5.85L16.1333 3.225C14.5417 1.74167 12.475 0.833332 10 0.833332C6.41667 0.833332 3.325 2.89167 1.81667 5.89167L4.86667 8.25833C5.59167 6.09167 7.61667 4.48333 10 4.48333Z" fill="#A8A29E"/>
              </svg>
              <span class="text-[12px] leading-4 tracking-[0.3px] font-medium">使用 Google 登录</span>
            </button>
          </div>

          <!-- 5. 登录按钮容器 (height: 52px, padding-top: 16px, button height: 36px) -->
          <div class="w-full flex items-center justify-center pt-2">
            <button
              type="button"
              @click="handleLogin"
              :disabled="isSubmitting"
              class="h-9 px-4 flex items-center justify-center gap-1.5 rounded-lg bg-[#F9C86D] text-[#0C0A09] font-medium text-[12px] shadow-gold active:scale-95 transition-all cursor-pointer select-none"
            >
              <span>登录</span>
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M7.58333 9.91667L10.5 7L7.58333 4.08333M10.5 7H3.5" stroke="#0C0A09" stroke-width="1.16667" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </button>
          </div>

          <!-- 6. 注册与忘记密码链接 (height: 32px) -->
          <div class="w-full flex items-center justify-center gap-2 text-xs pt-2">
            <span class="text-[#78716C]">没有账户？</span>
            <button
              type="button"
              @click="emit('switchToRegister')"
              class="text-[#A8A29E] underline hover:text-[#F9C86D] transition-colors cursor-pointer"
            >
              立即注册
            </button>
            <span class="text-[#78716C]">•</span>
            <button
              type="button"
              @click="emit('switchToForgot')"
              class="text-[#A8A29E] underline hover:text-[#F9C86D] transition-colors cursor-pointer"
            >
              忘记密码?
            </button>
          </div>

          <!-- 7. 底部协议声明 (height: 68px, padding-top: 16px) -->
          <div class="w-full flex flex-col items-center gap-1 text-[12px] text-[#78716C] pt-2 pb-1">
            <span>继续即表示您同意我们的</span>
            <div class="flex items-center gap-2">
              <button type="button" class="text-[#A8A29E] underline hover:text-white transition-colors cursor-pointer">
                服务条款
              </button>
              <span>•</span>
              <button type="button" class="text-[#A8A29E] underline hover:text-white transition-colors cursor-pointer">
                隐私政策
              </button>
            </div>
          </div>

        </DialogContent>
      </div>
    </DialogPortal>
  </DialogRoot>
</template>
