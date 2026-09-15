<script setup lang="ts">
/**
 * 分节 1: 【卡面】组件 (玩家在市场看到的信息)
 *
 * 遵循 Figma Frame 137:1615 规范，涵盖角色名称、立绘、市场简介、标签池与发布设置矩阵。
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { uploadService } from "@/services/upload";
import { Check, Edit3, Loader2, Plus, Sparkles, Trash2, UploadCloud, X } from "lucide-vue-next";
import { computed, ref } from "vue";
import { PRESET_CHARACTER_TAGS } from "../constants/tags";
import type { DisplayMode } from "../types";

const props = defineProps<{
  /** 角色名称 */
  name: string;
  /** 立绘头像 URL */
  avatarUrl: string;
  /** 角色标签列表 */
  tags: string[];
  /** 市场简介描述 */
  marketDescription: string;
  /** 发布分区 (story | nsfw) */
  category: "story" | "nsfw";
  /** 是否原创 */
  isOriginal: boolean;
  /** 是否成人内容 */
  isNsfw: boolean;
  /** 可见性 (public | private) */
  visibility: "public" | "private";
  /** 创作者名称 */
  creatorName: string;
  /** 版本号 */
  version: string;
  /** 作者的话存在标记 */
  hasCreatorNotes: boolean;
  /** 显示模式 (简洁 vs 完整) */
  displayMode: DisplayMode;
}>();

const emit = defineEmits<{
  (e: "update:name", val: string): void;
  (e: "update:avatarUrl", val: string): void;
  (e: "update:tags", val: string[]): void;
  (e: "update:marketDescription", val: string): void;
  (e: "update:category", val: "story" | "nsfw"): void;
  (e: "update:isOriginal", val: boolean): void;
  (e: "update:isNsfw", val: boolean): void;
  (e: "update:visibility", val: "public" | "private"): void;
  (e: "update:creatorName", val: string): void;
  (e: "update:version", val: string): void;
  (e: "open-author-note"): void;
}>();

const toast = useToast();
const isUploading = ref<boolean>(false);
const avatarInputRef = ref<HTMLInputElement | null>(null);
const customTagInput = ref<string>("");

const tagCount = computed<number>(() => props.tags.length);
const isMaxTagsReached = computed<boolean>(() => props.tags.length >= 5);

// 扩展符合 Figma 设计的热门标签池
const extendedTags = [
  ...PRESET_CHARACTER_TAGS,
  "二次元",
  "世界",
  "玄幻",
  "剧情",
  "RPG",
  "古风",
  "校园",
  "都市",
  "种田经营",
  "纯爱",
  "救赎",
  "NTR",
  "NTL",
  "后宫",
  "伦理",
  "女生视角",
  "调教",
  "熟女",
  "御姐",
  "重口",
];
const displayTags = Array.from(new Set(extendedTags));

function togglePresetTag(tag: string): void {
  const current = [...props.tags];
  const idx = current.indexOf(tag);
  if (idx !== -1) {
    current.splice(idx, 1);
  } else {
    if (current.length < 5) {
      current.push(tag);
    } else {
      toast.info("最多只能选择 5 个标签");
    }
  }
  emit("update:tags", current);
}

function addCustomTag(): void {
  const tag = customTagInput.value.trim().replace(/^#/, "");
  if (!tag) return;
  if (props.tags.includes(tag)) {
    toast.info("已添加过该标签");
    return;
  }
  if (props.tags.length >= 5) {
    toast.info("最多只能添加 5 个标签");
    return;
  }
  emit("update:tags", [...props.tags, tag]);
  customTagInput.value = "";
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
    toast.success("立绘已成功上传！");
  } catch (err) {
    console.error("立绘上传失败:", err);
    toast.error("立绘上传失败，请重试");
  } finally {
    isUploading.value = false;
    target.value = "";
  }
}
</script>

<template>
  <section id="section-cover" class="w-full px-3 pb-4 flex flex-col gap-4">
    <!-- 隐藏的文件上传 input -->
    <input
      ref="avatarInputRef"
      type="file"
      accept="image/*"
      class="hidden"
      @change="handleAvatarChange"
    />

    <!-- 分节大标题: 卡面 (玩家在市场看到的信息) -->
    <div class="flex items-center justify-between pt-1">
      <div class="flex items-center gap-2.5">
        <div class="w-1 h-5 rounded-full bg-[#F9C86D] shadow-[0_0_10px_rgba(249,200,109,0.5)]" />
        <h2 class="text-base font-bold text-gray-100 tracking-wide select-none">
          卡面
        </h2>
        <span class="text-xs text-[#78716C] font-normal">
          玩家在市场看到的信息
        </span>
      </div>
    </div>

    <!-- 1. 角色卡信息主体卡片 -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      <!-- 角色/故事名称 * -->
      <div class="flex flex-col gap-1.5">
        <label class="flex items-center gap-1.5 text-xs font-semibold text-gray-200">
          <Sparkles class="w-3.5 h-3.5 text-[#F9C86D]" />
          <span>角色/故事名称 *</span>
        </label>
        <input
          :value="name"
          @input="emit('update:name', ($event.target as HTMLInputElement).value)"
          type="text"
          class="w-full px-3.5 py-2.5 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-sm text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D] transition-colors"
          placeholder="给你的角色取一个合适的名字吧..."
          maxlength="50"
        />
      </div>

      <!-- 立绘封面上传区 (3:4 比例) -->
      <div class="flex flex-col gap-2 pt-1">
        <div class="flex items-center justify-between text-xs text-[#78716C]">
          <span>立绘封面 (推荐 3:4，支持 JPG/PNG/GIF)</span>
          <span v-if="avatarUrl" class="text-[#F9C86D] text-[11px]">已配置封面</span>
        </div>

        <div
          v-if="!avatarUrl"
          @click="!isUploading && triggerAvatarUpload()"
          :class="[
            'w-full h-56 rounded-xl border-2 border-dashed border-[#44403C] hover:border-[#F9C86D]/60 bg-[rgba(20,18,15,0.60)] flex flex-col items-center justify-center gap-2 transition-all group',
            isUploading ? 'cursor-wait opacity-70' : 'cursor-pointer'
          ]"
        >
          <div class="w-11 h-11 rounded-full bg-[#F9C86D]/10 text-[#F9C86D] flex items-center justify-center group-hover:scale-110 transition-transform">
            <Loader2 v-if="isUploading" class="w-5 h-5 animate-spin" />
            <Plus v-else class="w-5 h-5" />
          </div>
          <span class="text-xs font-medium text-[#A8A29E] group-hover:text-[#F9C86D]">
            {{ isUploading ? "正在上传至对象存储..." : "点击上传立绘图片" }}
          </span>
        </div>

        <div
          v-else
          class="relative w-full h-64 rounded-xl overflow-hidden border border-[#F9C86D]/40 group shadow-2xl"
        >
          <img
            :src="avatarUrl"
            alt="Character Avatar"
            class="w-full h-full object-cover"
          />
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
              @click="emit('update:avatarUrl', '')"
              class="px-3 py-1.5 rounded-lg bg-red-600 text-white font-medium text-xs flex items-center gap-1 shadow cursor-pointer"
            >
              <Trash2 class="w-4 h-4" />
              <span>删除</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 市场简介 -->
      <div class="flex flex-col gap-1.5 pt-1">
        <label class="text-xs font-semibold text-gray-200">
          市场简介
        </label>
        <textarea
          :value="marketDescription"
          @input="emit('update:marketDescription', ($event.target as HTMLTextAreaElement).value)"
          rows="3"
          maxlength="200"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D] transition-colors resize-none leading-relaxed"
          placeholder="展示在市场卡片上的简短介绍（200字以内），吸引玩家点击体验..."
        />
      </div>
    </div>

    <!-- 2. 角色标签卡片 (最多5个) -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <div class="flex items-center justify-between">
        <label class="text-xs font-semibold text-gray-200">
          角色标签 <span class="text-xs text-[#78716C] font-normal">(最多5个)</span>
        </label>
        <span :class="['text-xs', tagCount >= 5 ? 'text-[#F9C86D] font-semibold' : 'text-[#78716C]']">
          {{ tagCount }} / 5
        </span>
      </div>

      <!-- 标签池 -->
      <div class="flex flex-wrap gap-1.5 max-h-36 overflow-y-auto pr-1 no-scrollbar">
        <button
          v-for="tag in displayTags"
          :key="tag"
          type="button"
          @click="togglePresetTag(tag)"
          :class="[
            'px-2.5 py-1 rounded-md text-xs transition-all duration-150 cursor-pointer select-none border',
            tags.includes(tag)
              ? 'bg-[#F9C86D] text-black border-[#F9C86D] font-medium shadow-sm'
              : 'bg-[rgba(42,37,32,0.60)] text-[#A8A29E] border-[#44403C]/60 hover:text-white'
          ]"
        >
          {{ tag }}
        </button>
      </div>

      <!-- 自定义输入 -->
      <div class="flex items-center gap-2 pt-1">
        <input
          v-model="customTagInput"
          type="text"
          class="flex-1 px-3 py-1.5 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#F9C86D]"
          placeholder="输入自定义标签后按回车或点击 + 添加"
          maxlength="20"
          :disabled="isMaxTagsReached"
          @keyup.enter="addCustomTag"
        />
        <button
          type="button"
          @click="addCustomTag"
          :disabled="isMaxTagsReached || !customTagInput.trim()"
          class="h-8 px-3 rounded-lg border border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10 disabled:opacity-40 transition-colors flex items-center justify-center cursor-pointer"
        >
          <Plus class="w-3.5 h-3.5" />
        </button>
      </div>

      <!-- 已选标签 -->
      <div v-if="tags.length > 0" class="flex flex-wrap gap-1.5 pt-1">
        <span
          v-for="tag in tags"
          :key="tag"
          class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-[#F9C86D]/15 text-[#F9C86D] border border-[#F9C86D]/30 text-xs font-medium"
        >
          <span>#{{ tag }}</span>
          <button type="button" @click="removeTag(tag)" class="hover:text-white transition-colors">
            <X class="w-3 h-3" />
          </button>
        </span>
      </div>
    </div>

    <!-- 3. 发布设置矩阵卡片 -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-semibold text-gray-200">
          发布设置
        </h3>
        <!-- 添加作者的话按钮 -->
        <button
          type="button"
          @click="emit('open-author-note')"
          class="flex items-center gap-1 px-2.5 py-1 rounded-lg border border-[#F9C86D]/50 text-[#F9C86D] hover:bg-[#F9C86D]/10 text-xs transition-colors cursor-pointer select-none"
        >
          <Edit3 class="w-3 h-3" />
          <span>{{ hasCreatorNotes ? "编辑作者的话" : "+ 添加作者的话" }}</span>
        </button>
      </div>

      <!-- 分区选择 (剧情卡 vs 绅士卡) -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs text-[#A8A29E]">分区</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            type="button"
            @click="emit('update:category', 'story')"
            :class="[
              'h-9 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition-all cursor-pointer border',
              category === 'story'
                ? 'bg-[#F9C86D] text-black border-[#F9C86D] font-semibold shadow-sm'
                : 'bg-black/40 text-[#A8A29E] border-[#44403C]/60 hover:text-white'
            ]"
          >
            <Check v-if="category === 'story'" class="w-3.5 h-3.5" />
            <span>剧情卡 (全年龄)</span>
          </button>
          <button
            type="button"
            @click="emit('update:category', 'nsfw')"
            :class="[
              'h-9 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition-all cursor-pointer border',
              category === 'nsfw'
                ? 'bg-[#F9C86D] text-black border-[#F9C86D] font-semibold shadow-sm'
                : 'bg-black/40 text-[#A8A29E] border-[#44403C]/60 hover:text-white'
            ]"
          >
            <Check v-if="category === 'nsfw'" class="w-3.5 h-3.5" />
            <span>绅士卡 (NSFW)</span>
          </button>
        </div>
      </div>

      <!-- 开关矩阵: 原创内容 & 成人内容标记 -->
      <div class="grid grid-cols-2 gap-3 pt-1">
        <!-- 原创内容 Switch -->
        <div class="flex items-center justify-between p-2.5 rounded-lg bg-black/40 border border-[#44403C]/60">
          <span class="text-xs text-stone-200">原创内容</span>
          <button
            type="button"
            @click="emit('update:isOriginal', !isOriginal)"
            :class="[
              'w-9 h-5 rounded-full p-0.5 transition-colors cursor-pointer flex items-center',
              isOriginal ? 'bg-[#F9C86D] justify-end' : 'bg-stone-700 justify-start'
            ]"
          >
            <div class="w-4 h-4 rounded-full bg-stone-900 shadow-sm" />
          </button>
        </div>

        <!-- 成人内容标记 Switch -->
        <div class="flex items-center justify-between p-2.5 rounded-lg bg-black/40 border border-[#44403C]/60">
          <span class="text-xs text-stone-200">成人内容标记</span>
          <button
            type="button"
            @click="emit('update:isNsfw', !isNsfw)"
            :class="[
              'w-9 h-5 rounded-full p-0.5 transition-colors cursor-pointer flex items-center',
              isNsfw ? 'bg-[#F9C86D] justify-end' : 'bg-stone-700 justify-start'
            ]"
          >
            <div class="w-4 h-4 rounded-full bg-stone-900 shadow-sm" />
          </button>
        </div>
      </div>

      <!-- 发布类型 (公开发布 vs 私密分享) -->
      <div class="flex flex-col gap-1.5 pt-1">
        <label class="text-xs text-[#A8A29E]">发布类型</label>
        <div class="grid grid-cols-2 gap-2">
          <button
            type="button"
            @click="emit('update:visibility', 'public')"
            :class="[
              'h-8 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition-all cursor-pointer border',
              visibility === 'public'
                ? 'bg-[#F9C86D]/20 text-[#F9C86D] border-[#F9C86D]/60 font-semibold'
                : 'bg-black/40 text-[#A8A29E] border-[#44403C]/60 hover:text-white'
            ]"
          >
            <span>公开发布 (社区可见)</span>
          </button>
          <button
            type="button"
            @click="emit('update:visibility', 'private')"
            :class="[
              'h-8 rounded-lg text-xs font-medium flex items-center justify-center gap-1.5 transition-all cursor-pointer border',
              visibility === 'private'
                ? 'bg-[#F9C86D]/20 text-[#F9C86D] border-[#F9C86D]/60 font-semibold'
                : 'bg-black/40 text-[#A8A29E] border-[#44403C]/60 hover:text-white'
            ]"
          >
            <span>私密分享 (仅链接可见)</span>
          </button>
        </div>
      </div>

      <!-- 创作者名称 & 版本号 -->
      <div class="grid grid-cols-2 gap-3 pt-1">
        <div class="flex flex-col gap-1">
          <label class="text-[11px] text-[#A8A29E]">创作者署名</label>
          <input
            :value="creatorName"
            @input="emit('update:creatorName', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="例如: 叙梦创作者"
            class="w-full px-3 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D]"
          />
        </div>
        <div class="flex flex-col gap-1">
          <label class="text-[11px] text-[#A8A29E]">版本号</label>
          <input
            :value="version"
            @input="emit('update:version', ($event.target as HTMLInputElement).value)"
            type="text"
            placeholder="1.0.0"
            class="w-full px-3 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D]"
          />
        </div>
      </div>

      <!-- 审核温馨提示 -->
      <div class="p-2.5 rounded-lg bg-[#F9C86D]/10 border border-[#F9C86D]/20 text-[11px] text-[#F9C86D] leading-normal flex items-start gap-1.5">
        <span class="font-bold">提示：</span>
        <span>编辑已公开的角色卡时，只有将可见性从私有改为公开时才需审核。其他设定编辑将立即实时更新生效。</span>
      </div>
    </div>
  </section>
</template>
