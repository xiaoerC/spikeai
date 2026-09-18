<script setup lang="ts">
/**
 * 叙梦 Naro - 首次登录强制设定用户名模态弹窗组件
 *
 * 遵循 Obsidian Gold 奢华黑金暗黑玻璃拟物风格：
 * 强阻断设计：无关闭按钮、禁用 Esc 与点击遮罩关闭；
 * 强制用户输入 2~20 字符的主角昵称，设置成功后方可进入叙梦系统。
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { useUserStore } from "@/stores/user";
import { Loader2, Sparkles, UserCheck } from "lucide-vue-next";
import { DialogContent, DialogOverlay, DialogPortal, DialogRoot } from "reka-ui";
import { computed, ref, watch } from "vue";

interface Props {
  /** 弹窗显隐状态 */
  open: boolean;
}

const props = defineProps<Props>();

const userStore = useUserStore();
const toast = useToast();

/** 用户名输入状态 (初始可读取当前邮箱前缀或空) */
const usernameInput = ref("");
const isSubmitting = ref(false);
const errorMsg = ref("");

// 监听打开状态初始化建议昵称
watch(
  () => props.open,
  (val) => {
    if (val) {
      errorMsg.value = "";
      // 若已有临时前缀且不为默认占位，可作为推荐底稿
      const currentName = userStore.profile?.username || "";
      if (currentName && !currentName.includes("@")) {
        usernameInput.value = currentName;
      }
    }
  },
  { immediate: true },
);

const trimmedLength = computed(() => usernameInput.value.trim().length);
const isValidLength = computed(() => trimmedLength.value >= 2 && trimmedLength.value <= 20);

/**
 * 提交保存用户名
 */
async function handleSubmit(): Promise<void> {
  const name = usernameInput.value.trim();
  if (name.length < 2) {
    errorMsg.value = "昵称长度至少为 2 个字符";
    return;
  }
  if (name.length > 20) {
    errorMsg.value = "昵称长度不得超过 20 个字符";
    return;
  }

  errorMsg.value = "";
  isSubmitting.value = true;
  try {
    const success = await userStore.updateProfile({ username: name });
    if (success) {
      toast.success(`欢迎来到叙梦世界，${name}！`);
    } else {
      errorMsg.value = userStore.errorMessage || "设置昵称失败，请重试";
    }
  } catch (err: any) {
    errorMsg.value = err.message || "网络异常，请重试";
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <!-- 强阻断弹窗：不可由外部点击或 Esc 键关闭 -->
  <DialogRoot :open="open">
    <DialogPortal>
      <!-- 高斯模糊暗黑奢华遮罩: 深度暗调叠加金砂微光 -->
      <DialogOverlay class="fixed inset-0 z-[999] bg-black/80 backdrop-blur-md animate-fade-in" />

      <!-- 居中模态容器 -->
      <div class="fixed inset-0 z-[1000] flex items-center justify-center p-4 pointer-events-none">
        <DialogContent
          @escape-key-down.prevent
          @pointer-down-outside.prevent
          @interact-outside.prevent
          class="pointer-events-auto relative w-full max-w-[390px] rounded-2xl border border-[#F9C86D]/30 p-6 flex flex-col items-center justify-between shadow-[0_20px_50px_rgba(0,0,0,0.9),0_0_30px_rgba(249,200,109,0.12)] outline-none animate-scale-in select-none"
          style="background: linear-gradient(145deg, #1C1814 0%, #120F0D 100%), #0A0807;"
        >
          <!-- 1. 顶部光晕徽标与标题区 -->
          <div class="w-full flex flex-col items-center text-center pt-2">
            <!-- 金色徽章图标 -->
            <div class="w-13 h-13 rounded-full bg-gradient-to-b from-[#F9C86D]/20 to-transparent border border-[#F9C86D]/40 flex items-center justify-center mb-3 shadow-[0_0_20px_rgba(249,200,109,0.2)]">
              <Sparkles class="w-6 h-6 text-[#F9C86D] animate-pulse" />
            </div>

            <h2 class="text-[20px] font-bold text-[#F9C86D] tracking-wider font-serif">
              设定你的旅者称谓
            </h2>
            <p class="text-[12px] text-[#A8A29E] mt-1.5 leading-relaxed max-w-[280px]">
              初次踏入叙梦世界，请为自己命名。该称谓将用于所有沉浸式剧情与角色对话。
            </p>
          </div>

          <!-- 2. 表单输入区 -->
          <div class="w-full flex flex-col items-center my-6">
            <div class="w-full flex flex-col justify-center items-center relative group">
              <div class="relative w-full">
                <input
                  v-model="usernameInput"
                  type="text"
                  maxlength="20"
                  placeholder="输入你的主角昵称"
                  @keydown.enter.prevent="handleSubmit"
                  class="w-full h-12 px-4 text-center text-[17px] text-[#F9C86D] placeholder-[#78716C] bg-[#26201B]/60 rounded-xl border border-[#44403C] focus:border-[#F9C86D] outline-none transition-all tracking-wide font-sans shadow-inner"
                />
                <!-- 右侧字数计数器 -->
                <span
                  :class="[
                    'absolute right-3 top-1/2 -translate-y-1/2 text-[11px] font-mono transition-colors',
                    isValidLength ? 'text-[#A8A29E]' : 'text-amber-500/70'
                  ]"
                >
                  {{ trimmedLength }}/20
                </span>
              </div>
            </div>

            <!-- 错误或提示信息 -->
            <div class="h-6 flex items-center justify-center mt-2">
              <p v-if="errorMsg" class="text-xs text-red-400 text-center animate-fade-in flex items-center gap-1">
                <span>⚠</span>
                <span>{{ errorMsg }}</span>
              </p>
              <p v-else class="text-[11px] text-[#78716C] text-center">
                支持 2~20 个字符，后续可在聊天主控面板中修改
              </p>
            </div>
          </div>

          <!-- 3. 底部提交按钮 -->
          <div class="w-full flex flex-col items-center">
            <button
              type="button"
              :disabled="!isValidLength || isSubmitting"
              @click="handleSubmit"
              :class="[
                'w-full h-11 rounded-xl font-medium text-[15px] flex items-center justify-center gap-2 transition-all cursor-pointer shadow-lg select-none',
                isValidLength && !isSubmitting
                  ? 'bg-gradient-to-r from-[#D4A359] via-[#F9C86D] to-[#D4A359] text-[#120F0D] font-bold hover:shadow-[0_0_20px_rgba(249,200,109,0.4)] active:scale-[0.98]'
                  : 'bg-[#292524] text-[#78716C] border border-[#44403C]/50 cursor-not-allowed'
              ]"
            >
              <Loader2 v-if="isSubmitting" class="w-4 h-4 animate-spin text-[#120F0D]" />
              <UserCheck v-else class="w-4 h-4" />
              <span>{{ isSubmitting ? '正在启程……' : '进入叙梦世界' }}</span>
            </button>
          </div>

        </DialogContent>
      </div>
    </DialogPortal>
  </DialogRoot>
</template>
