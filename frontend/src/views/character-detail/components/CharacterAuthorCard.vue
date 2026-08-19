<script setup lang="ts">
/**
 * 角色卡详情 - 作者信息卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

defineProps<{
  author: {
    id: string;
    name: string;
    avatarUrl: string;
    followersCount: number;
    isFollowed: boolean;
  };
}>();

const emit = defineEmits<(e: "toggleFollow") => void>();
</script>

<template>
  <div class="w-full px-3 pt-4 select-none">
    <div class="w-full p-4 rounded-lg border border-[#292524] bg-[#1A1714]/95 flex flex-col gap-3">
      
      <!-- 标题: 作者信息 -->
      <h3 class="text-[16px] font-semibold text-[#F5F5F4] tracking-[-0.32px] leading-5">
        作者信息
      </h3>

      <!-- 作者资料行 (40x40 头像 + XXYY + 178 粉丝) -->
      <div class="flex items-center gap-3 py-1">
        <div class="w-10 h-10 rounded-full border border-[#44403C] overflow-hidden bg-[#292524] flex items-center justify-center shrink-0">
          <img :src="author.avatarUrl" :alt="author.name" class="w-full h-full object-cover" />
        </div>

        <div class="flex flex-col">
          <span class="text-sm font-semibold text-[#F5F5F4] leading-tight">
            {{ author.name }}
          </span>
          <span class="text-xs text-[#78716C] mt-0.5">
            {{ author.followersCount }} 粉丝
          </span>
        </div>
      </div>

      <!-- 全宽 + 关注 按钮 -->
      <button
        type="button"
        @click="emit('toggleFollow')"
        :class="[
          'w-full h-9 rounded-lg border flex items-center justify-center gap-1.5 text-xs font-medium transition-all active:scale-98 cursor-pointer select-none',
          author.isFollowed
            ? 'bg-[#A8A29E]/10 border-[#A8A29E]/30 text-[#A8A29E]'
            : 'border-[#F9C86D] text-[#F9C86D] hover:bg-[#F9C86D]/10 shadow-sm'
        ]"
      >
        <span>{{ author.isFollowed ? "已关注" : "+ 关注" }}</span>
      </button>

    </div>
  </div>
</template>
