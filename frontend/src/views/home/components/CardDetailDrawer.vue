<script setup lang="ts">
/**
 * 角色卡沉浸详情预览抽屉组件 (基于 AppDrawer 与 AppButton 规范重构)
 *
 * @packageDocumentation
 */

import { AppButton, AppDrawer } from "@/components/common";
import type { MarketCard } from "@/types";
import { Flame, MessageSquare, Star, TrendingUp } from "lucide-vue-next";
import { computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

/** 组件 Props 接口定义 */
interface Props {
  /** 当前选中的角色卡片 */
  card: MarketCard | null;
  /** 抽屉显隐状态 */
  open: boolean;
}

const props = defineProps<Props>();

/** 组件 Emits 事件 */
const emit = defineEmits<{
  (e: "update:open", value: boolean): void;
  (e: "close"): void;
  (e: "startChat", card: MarketCard): void;
}>();

const isDrawerOpen = computed({
  get: () => props.open && props.card !== null,
  set: (val: boolean) => {
    emit("update:open", val);
    if (!val) {
      emit("close");
    }
  },
});
</script>

<template>
  <AppDrawer
    v-if="card"
    v-model:open="isDrawerOpen"
    :title="card.title"
    :description="`作者: ${card.author.startsWith('@') ? card.author : '@' + card.author}`"
    :show-close="true"
  >

    <div class="space-y-4 pt-1">
      <!-- 封面与核心指标 -->
      <div class="flex gap-3 items-start">
        <div class="w-20 h-24 rounded-xl bg-[#292524] border border-[#44403C] overflow-hidden flex-shrink-0 flex items-center justify-center shadow-md">
          <img
            v-if="card.avatarUrl"
            :src="card.avatarUrl"
            :alt="card.title"
            class="w-full h-full object-cover"
          />
          <span v-else class="text-2xl opacity-20">✨</span>
        </div>

        <div class="flex flex-col gap-2 flex-1">
          <!-- 三合一指标 -->
          <div class="flex items-center gap-3 text-xs">
            <span class="flex items-center gap-1 text-[#EAB308] font-bold">
              <Flame class="w-3.5 h-3.5" /> {{ card.heat }}
            </span>
            <span class="flex items-center gap-1 text-[#F9C86D] font-bold">
              <Star class="w-3.5 h-3.5 fill-[#F9C86D] text-[#F9C86D]" /> {{ card.rating }}
            </span>
            <span class="flex items-center gap-1 text-[#FF9F43] font-semibold">
              <TrendingUp class="w-3.5 h-3.5" /> {{ card.trendScore }}
            </span>
          </div>

          <!-- 标签胶囊列表 -->
          <div class="flex flex-wrap gap-1.5 pt-1">
            <span
              v-for="t in card.tags"
              :key="t"
              class="text-[11px] px-2 py-0.5 rounded-full bg-[#292524] border border-[#44403C] text-gray-300 font-medium"
            >
              {{ t }}
            </span>
            <span
              v-if="card.extraTags"
              class="text-[11px] px-2 py-0.5 rounded-full bg-[#292524] border border-dashed border-[#44403C] text-gray-400"
            >
              {{ card.extraTags }}
            </span>
          </div>
        </div>
      </div>

      <!-- 简介文案描述卡片 -->
      <div class="p-3.5 rounded-xl bg-[#241F1B] border border-[#44403C]/50 text-xs text-gray-300 leading-relaxed max-h-40 overflow-y-auto">
        <p class="font-medium text-gray-200 mb-1">角色背景与世界观：</p>
        <p>{{ card.description }}</p>
      </div>
    </div>

    <!-- 底部操作按钮 -->
    <template #footer>
      <div class="flex items-center gap-2.5">
        <AppButton
          variant="ghost"
          class="flex-1"
          @click="router.push(`/character/${card.id}`)"
        >
          完整详情
        </AppButton>
        <AppButton
          variant="gold"
          class="flex-2"
          @click="emit('startChat', card)"
        >
          <template #icon-left>
            <MessageSquare class="w-4 h-4" />
          </template>
          开启沉浸对话
        </AppButton>
      </div>
    </template>

  </AppDrawer>
</template>
