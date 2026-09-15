<script setup lang="ts">
/**
 * 模块 2: 角色卡信息组件 (1:1 原型高保真)
 *
 * 包含角色名称、立绘上传与即时预览、提示准则、20+ 热门标签选择池与自定义标签输入。
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { uploadService } from "@/services/upload";
import { PRESET_CHARACTER_TAGS } from "@/views/character-create/constants/tags";
import { Loader2, Plus, Trash2, UploadCloud, X } from "lucide-vue-next";
import { computed, ref } from "vue";

const props = defineProps<{
  /** 角色名称 */
  name: string;
  /** 立绘图片 URL */
  avatarUrl: string;
  /** 已选标签集合 (双向绑定) */
  tags: string[];
}>();

const emit = defineEmits<{
  (e: "update:name", val: string): void;
  (e: "update:avatarUrl", val: string): void;
  (e: "update:tags", val: string[]): void;
}>();

const toast = useToast();
const isUploading = ref<boolean>(false);
const avatarInputRef = ref<HTMLInputElement | null>(null);

const customTagInput = ref<string>("");
const tagCount = computed<number>(() => props.tags.length);
const isMaxTagsReached = computed<boolean>(() => props.tags.length >= 5);

function togglePresetTag(tag: string): void {
  const current = [...props.tags];
  const idx = current.indexOf(tag);
  if (idx !== -1) {
    current.splice(idx, 1);
  } else {
    if (current.length < 5) {
      current.push(tag);
    }
  }
  emit("update:tags", current);
}

function addCustomTag(): void {
  const tag = customTagInput.value.trim().replace(/^#/, "");
  if (!tag) return;
  if (!props.tags.includes(tag) && props.tags.length < 5) {
    emit("update:tags", [...props.tags, tag]);
    customTagInput.value = "";
  }
}

function removeTag(tag: string): void {
  emit(
    "update:tags",
    props.tags.filter((t) => t !== tag),
  );
}

function triggerAvatarUpload(): void {
  avatarInputRef.value?.click();
}

async function handleAvatarChange(event: Event): Promise<void> {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  isUploading.value = true;
  try {
    const uploadedUrl = await uploadService.uploadImage(file, "avatars");
    emit("update:avatarUrl", uploadedUrl);
    toast.success("立绘已成功上传至对象存储！");
  } catch (err: any) {
    console.error("立绘上传失败:", err);
    toast.error("立绘上传失败，请重试");
  } finally {
    isUploading.value = false;
    target.value = "";
  }
}

function removeAvatar(): void {
  emit("update:avatarUrl", "");
}
</script>

<template>
  <div class="w-full px-3 pb-3">
    <!-- 隐藏的立绘上传 input -->
    <input
      ref="avatarInputRef"
      type="file"
      accept="image/*"
      class="hidden"
      @change="handleAvatarChange"
    />

    <!-- 模块外层容器 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-5 shadow-xl">
      
      <!-- 1. 模块主标题 (金黄圆柱指示条 + 角色卡信息 + 书本图标) -->
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-3">
          <!-- 金黄指示条 -->
          <div class="w-1 h-6 rounded-full bg-gradient-to-b from-[#FFD475] to-[#D1A35C] shadow-[0_0_10px_rgba(249,200,109,0.5)]" />
          <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[0.9px] leading-tight select-none">
            角色卡信息
          </h2>
        </div>

        <!-- 金黄书本图标 -->
        <svg class="w-5 h-5 text-[#F9C86D]" viewBox="0 0 21 21" fill="none">
          <path d="M10.25 6.27L10.77 17.93" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
          <path d="M3.17 15.77C2.95 15.78 2.73 15.7 2.57 15.55C2.41 15.4 2.31 15.19 2.3 14.97L1.81 4.15C1.8 3.93 1.88 3.71 2.03 3.55C2.18 3.39 2.39 3.29 2.61 3.28L6.77 3.09C7.65 3.05 8.52 3.37 9.17 3.96C9.82 4.56 10.21 5.39 10.25 6.28C10.21 5.39 10.52 4.53 11.12 3.88C11.72 3.22 12.55 2.84 13.43 2.8L17.59 2.61C17.81 2.6 18.03 2.68 18.19 2.83C18.35 2.98 18.45 3.18 18.46 3.4L18.95 14.23C18.96 14.45 18.88 14.66 18.73 14.83C18.58 14.99 18.37 15.09 18.15 15.1L13.16 15.32C12.5 15.35 11.87 15.64 11.43 16.13C10.98 16.62 10.74 17.27 10.77 17.93C10.74 17.27 10.45 16.64 9.96 16.2C9.47 15.75 8.83 15.51 8.16 15.54L3.17 15.77Z" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>

      <!-- 2. ① 角色/故事名称 * -->
      <div class="flex flex-col gap-2">
        <label class="flex items-center gap-2 text-sm font-medium text-[#F5F5F4]">
          <span class="text-[#F9C86D]">✨</span>
          <span>角色/故事名称 *</span>
        </label>
        <input
          :value="name"
          @input="emit('update:name', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full px-3.5 py-2.5 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-sm text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D] transition-colors"
          placeholder="给你的角色取一个合适的名字吧（过分可能会过不了审核哦）"
          maxlength="50"
        />
      </div>

      <!-- 3. ② 立绘封面上传区 -->
      <div class="flex flex-col gap-3 pt-1">
        <!-- 比例与格式规格提示 -->
        <div class="flex items-center gap-4 text-xs text-[#78716C]">
          <div class="flex items-center gap-1.5">
            <div class="w-1.5 h-1.5 rounded-full bg-[#F9C86D]/60" />
            <span>推荐比例 3:4</span>
          </div>
          <div class="flex items-center gap-1.5">
            <div class="w-1.5 h-1.5 rounded-full bg-[#F9C86D]/60" />
            <span>支持 JPG/PNG/GIF</span>
          </div>
        </div>

        <!-- 提示卡片 (渐变金黄暗底) -->
        <div class="p-3 rounded-lg border border-[#A8A29E]/20 bg-gradient-to-r from-[#F9C86D]/10 to-[#A8A29E]/10 flex flex-col gap-1.5 text-xs">
          <div class="flex items-center gap-1.5 text-[#F5F5F4]/90 font-medium">
            <span class="text-[#F9C86D]">✨</span>
            <span>一张好看的卡面尤为重要</span>
          </div>
          <ul class="flex flex-col gap-1 text-[#78716C] pl-2 list-disc list-inside">
            <li>不推荐抽象的卡片页面</li>
            <li>可爱和清新的风格有更多人喜欢</li>
            <li>适当的暴露可以，过分的话可能过不了审核哦</li>
          </ul>
        </div>

        <!-- 大号立绘上传与即时预览框 (3:4 比例) -->
        <div
          v-if="!avatarUrl"
          @click="!isUploading && triggerAvatarUpload()"
          :class="[
            'w-full h-64 rounded-xl border-2 border-dashed border-[#44403C] hover:border-[#F9C86D]/60 bg-[rgba(26,23,20,0.50)] flex flex-col items-center justify-center gap-2.5 transition-all group',
            isUploading ? 'cursor-wait opacity-70' : 'cursor-pointer'
          ]"
        >
          <div class="w-12 h-12 rounded-full bg-[#F9C86D]/10 text-[#F9C86D] flex items-center justify-center group-hover:scale-110 transition-transform">
            <Loader2 v-if="isUploading" class="w-6 h-6 animate-spin" />
            <Plus v-else class="w-6 h-6" />
          </div>
          <span class="text-xs font-medium text-[#A8A29E] group-hover:text-[#F9C86D]">
            {{ isUploading ? "正在上传至 MinIO 对象存储..." : "点击上传立绘图片" }}
          </span>
        </div>

        <!-- 已上传立绘预览 -->
        <div
          v-else
          class="relative w-full h-72 rounded-xl overflow-hidden border border-[#F9C86D]/40 group shadow-2xl"
        >
          <img
            :src="avatarUrl"
            alt="Character Avatar"
            class="w-full h-full object-cover"
          />
          <!-- 悬浮操作蒙层 -->
          <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-3">
            <button
              type="button"
              @click="triggerAvatarUpload"
              class="px-3 py-1.5 rounded-lg bg-[#F9C86D] text-black font-medium text-xs flex items-center gap-1 shadow cursor-pointer"
            >
              <UploadCloud class="w-4 h-4" />
              <span>更换立绘</span>
            </button>
            <button
              type="button"
              @click="removeAvatar"
              class="px-3 py-1.5 rounded-lg bg-red-600 text-white font-medium text-xs flex items-center gap-1 shadow cursor-pointer"
            >
              <Trash2 class="w-4 h-4" />
              <span>删除</span>
            </button>
          </div>
        </div>

        <!-- 底部温馨提示 -->
        <div class="flex items-start gap-1.5 text-[11px] text-[#78716C] leading-normal pt-1">
          <span class="text-[#F9C86D] font-medium shrink-0">温馨提示：</span>
          <span>创建角色卡后，您可以在编辑页面中添加对话背景图和更换头像。</span>
        </div>
      </div>

      <!-- 4. ③ 角色标签 (最多5个) -->
      <div class="flex flex-col gap-3 pt-2">
        <div class="flex items-center justify-between">
          <label class="text-sm font-medium text-[#F5F5F4]">
            角色标签 <span class="text-xs text-[#78716C] font-normal">(最多5个)</span>
          </label>
          <span :class="['text-xs', tagCount >= 5 ? 'text-[#F9C86D] font-semibold' : 'text-[#78716C]']">
            {{ tagCount }} / 5
          </span>
        </div>

        <!-- 20+ 热门预设标签池 -->
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="tag in PRESET_CHARACTER_TAGS"
            :key="tag"
            type="button"
            @click="togglePresetTag(tag)"
            :class="[
              'px-2.5 py-1 rounded-md text-xs transition-all duration-150 cursor-pointer select-none border',
              tags.includes(tag)
                ? 'bg-[#F9C86D] text-[#0C0A09] border-[#F9C86D] font-medium shadow-sm'
                : 'bg-[rgba(42,37,32,0.60)] text-[#A8A29E] border-[#44403C]/60 hover:text-white hover:border-[#666]'
            ]"
          >
            {{ tag }}
          </button>
        </div>

        <!-- 自定义标签输入框 -->
        <div class="flex items-center gap-2 pt-1">
          <input
            v-model="customTagInput"
            type="text"
            class="flex-1 px-3 py-2 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D] transition-colors"
            placeholder="输入自定义标签后按回车或点击 + 添加"
            maxlength="20"
            :disabled="isMaxTagsReached"
            @keyup.enter="addCustomTag"
          />
          <button
            type="button"
            @click="addCustomTag"
            :disabled="isMaxTagsReached || !customTagInput.trim()"
            class="h-9 px-3 rounded-lg border border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10 disabled:opacity-40 disabled:pointer-events-none transition-colors flex items-center justify-center cursor-pointer"
          >
            <Plus class="w-4 h-4" />
          </button>
        </div>

        <!-- 当前已选标签 Pills -->
        <div v-if="tags.length > 0" class="flex flex-wrap gap-1.5 pt-1">
          <span
            v-for="tag in tags"
            :key="tag"
            class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-[#F9C86D]/15 text-[#F9C86D] border border-[#F9C86D]/30 text-xs font-medium"
          >
            <span>#{{ tag }}</span>
            <button
              type="button"
              @click="removeTag(tag)"
              class="hover:text-white transition-colors"
            >
              <X class="w-3 h-3" />
            </button>
          </span>
        </div>
      </div>

    </div>
  </div>
</template>
