<script setup lang="ts">
/**
 * 原创角色卡 PC 桌面端吸顶实时预览卡片组件 (DesktopLivePreview.vue)
 *
 * 1:1 对齐参考截图 4 右侧【实时预览】挂件：
 * 实时响应左侧表单中输入的角色名称、上传的立绘封面、标签等元数据，
 * 呈现所见即所得的黑金高奢角色卡片效果。
 *
 * @packageDocumentation
 */

import { Sparkles, User } from "lucide-vue-next";

defineProps<{
  name: string;
  avatarUrl: string;
  tags: string[];
  category: "story" | "nsfw";
  authorName?: string;
}>();
</script>

<template>
  <div class="sticky top-20 flex flex-col gap-3 w-72 shrink-0 select-none">
    <!-- 标题 -->
    <div class="flex items-center gap-1.5 text-xs font-bold text-[#F5F5F4]">
      <span class="w-1 h-3.5 bg-[#F9C86D] rounded-full" />
      <span>实时预览</span>
    </div>

    <!-- 模拟卡片容器 (1:1 对齐截图 4 右侧卡片框) -->
    <div
      class="relative w-full aspect-[3/4.2] rounded-xl border border-[#3A2E22] bg-[#1A1511] overflow-hidden shadow-2xl flex flex-col justify-end p-3 group"
    >
      <!-- 背景立绘图 / 占位图 -->
      <img
        v-if="avatarUrl"
        :src="avatarUrl"
        :alt="name || '角色头像'"
        class="absolute inset-0 w-full h-full object-cover object-center"
      />
      <div
        v-else
        class="absolute inset-0 w-full h-full bg-gradient-to-b from-[#251E18] to-[#14100C] flex flex-col items-center justify-center text-[#574F47] gap-2"
      >
        <User class="w-12 h-12 opacity-40" />
        <span class="text-xs text-[#78716C]">暂无立绘封面</span>
      </div>

      <!-- 暗黑半透明渐变遮罩 -->
      <div class="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-black/90 via-black/50 to-transparent pointer-events-none" />

      <!-- 顶部浮层标签 -->
      <div class="absolute top-2.5 inset-x-2.5 flex items-center justify-between z-10">
        <!-- 分类徽标 -->
        <span
          class="text-[10px] px-1.5 py-0.5 rounded font-medium border"
          :class="
            category === 'nsfw'
              ? 'bg-[#8A2BE2]/20 border-[#8A2BE2]/40 text-[#D8B4FE]'
              : 'bg-[#F9C86D]/20 border-[#F9C86D]/40 text-[#F9C86D]'
          "
        >
          {{ category === "nsfw" ? "绅士卡" : "剧情卡" }}
        </span>

        <!-- 作者 -->
        <span class="text-[10px] text-[#A8A29E] bg-black/50 px-1.5 py-0.5 rounded backdrop-blur-sm">
          {{ authorName || "创作者" }}
        </span>
      </div>

      <!-- 底部信息浮层 -->
      <div class="relative z-10 flex flex-col gap-1">
        <h4 class="text-sm font-bold text-white truncate drop-shadow-md">
          {{ name || "角色名称" }}
        </h4>

        <!-- 标签胶囊列表 (最多展示 3 个) -->
        <div v-if="tags.length > 0" class="flex items-center gap-1 flex-wrap">
          <span
            v-for="tag in tags.slice(0, 3)"
            :key="tag"
            class="text-[9px] px-1.5 py-0.2 rounded bg-white/10 text-gray-300 border border-white/10 truncate max-w-[70px]"
          >
            #{{ tag }}
          </span>
          <span v-if="tags.length > 3" class="text-[9px] text-[#78716C]">
            +{{ tags.length - 3 }}
          </span>
        </div>
        <span v-else class="text-[10px] text-[#78716C]">
          未选择标签
        </span>
      </div>
    </div>

    <!-- 提示文本 -->
    <p class="text-[11px] text-[#78716C] leading-relaxed">
      此处为发布至角色市场后的卡片展示缩略图，在保存发布前可实时确认视觉效果。
    </p>
  </div>
</template>
