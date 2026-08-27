<script setup lang="ts">
/**
 * 个人中心 - 我的勋章卡片 (绑定真实勋章成就)
 *
 * @packageDocumentation
 */

import { ChevronRight, Settings, Trophy } from "lucide-vue-next";

interface Props {
  badges: Array<{
    id: string;
    name: string;
    color?: string;
    description?: string;
  }>;
}

withDefaults(defineProps<Props>(), {
  badges: () => [],
});

const emit = defineEmits<(e: "manageBadges") => void>();
</script>

<template>
  <div class="w-full p-4 rounded-lg border border-[#C0A480]/15 bg-gradient-to-br from-[#F4E8C1]/[0.04] to-[#F4E8C1]/[0.02] flex flex-col gap-3">
    <!-- 1. 头部标题与管理 -->
    <div class="flex items-center justify-between w-full">
      <div class="flex items-center gap-2">
        <Trophy class="w-4 h-4 text-[#F9C86D]" />
        <h3 class="text-[16px] font-semibold text-[#F9C86D] tracking-[-0.32px] leading-5">
          我的勋章
        </h3>
        <span class="text-xs text-[#78716C] font-mono">({{ badges.length }})</span>
      </div>

      <div class="flex items-center gap-2">
        <button
          type="button"
          @click="emit('manageBadges')"
          class="h-7 px-2.5 rounded border border-[#A8A29E]/30 flex items-center gap-1 text-xs text-[#A8A29E] hover:text-white hover:border-[#F9C86D] transition-colors cursor-pointer"
        >
          <Settings class="w-3 h-3" />
          <span>设置</span>
        </button>

        <button
          type="button"
          @click="emit('manageBadges')"
          class="w-7 h-7 rounded-full border border-[#A8A29E]/30 flex items-center justify-center text-[#A8A29E] hover:text-white transition-colors cursor-pointer"
        >
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

    <!-- 2. 勋章流列表 -->
    <div v-if="badges.length > 0" class="flex flex-wrap gap-2 pt-1">
      <div
        v-for="badge in badges"
        :key="badge.id"
        class="px-2.5 py-1 rounded-full bg-[#292524] border border-[#44403C] shadow-sm flex items-center gap-1.5 cursor-pointer hover:border-[#F9C86D]/50 transition-all select-none"
        :title="badge.description || badge.name"
      >
        <span class="w-1.5 h-1.5 rounded-full" :style="{ backgroundColor: badge.color || '#FDE68A' }" />
        <span class="text-xs font-medium" :style="{ color: badge.color || '#FDE68A' }">
          {{ badge.name }}
        </span>
      </div>
    </div>

    <!-- 3. 无勋章时的真实空状态 -->
    <div v-else class="py-3 text-center text-xs text-[#78716C]">
      暂未佩戴更多勋章，参与剧情对话与创作可解锁专属成就
    </div>
  </div>
</template>
