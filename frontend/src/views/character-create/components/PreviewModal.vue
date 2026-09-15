<script setup lang="ts">
/**
 * 角色卡市场展示与开局体验实时预览弹窗
 *
 * @packageDocumentation
 */

import AppButton from "@/components/common/AppButton.vue";
import AppModal from "@/components/common/AppModal.vue";
import type { CharacterFormData } from "../types";

const props = defineProps<{
  /** 模态框显隐 */
  open: boolean;
  /** 当前全量表单数据 */
  formData: CharacterFormData;
}>();

const emit = defineEmits<(e: "update:open", val: boolean) => void>();
</script>

<template>
  <AppModal
    :open="open"
    @update:open="(val: boolean) => emit('update:open', val)"
    title="实时预览 · 角色卡"
    description="模拟玩家在市场详情与首次开局对话中看到的真实样貌。"
    custom-class="max-w-md w-full"
  >
    <div class="flex flex-col gap-4 py-2 max-h-[70vh] overflow-y-auto no-scrollbar">
      <!-- 1. 模拟市场卡片效果 -->
      <div class="rounded-xl overflow-hidden border border-[#F9C86D]/30 bg-gradient-to-b from-[#2A221A] to-[#1A1511] shadow-xl flex flex-col">
        <!-- 立绘封面 -->
        <div class="relative w-full h-56 bg-black/60 overflow-hidden">
          <img
            v-if="formData.avatarUrl"
            :src="formData.avatarUrl"
            alt="Preview Avatar"
            class="w-full h-full object-cover"
          />
          <div v-else class="w-full h-full flex items-center justify-center text-xs text-stone-500">
            暂无立绘
          </div>
          <!-- 渐变阴影蒙层 -->
          <div class="absolute inset-0 bg-gradient-to-t from-[#1A1511] via-transparent to-black/30" />
          
          <!-- 标签浮层 -->
          <div class="absolute top-2.5 left-2.5 flex items-center gap-1.5">
            <span class="px-2 py-0.5 rounded-md bg-black/70 backdrop-blur-md border border-[#F9C86D]/40 text-[#F9C86D] text-[10px] font-semibold">
              {{ formData.category === 'nsfw' ? '绅士卡' : '剧情卡' }}
            </span>
            <span class="px-1.5 py-0.5 rounded bg-black/50 text-[10px] text-stone-300 font-mono">
              v{{ formData.version || '1.0.0' }}
            </span>
          </div>
        </div>

        <!-- 卡面详情描述 -->
        <div class="p-3.5 flex flex-col gap-2">
          <div class="flex items-center justify-between">
            <h3 class="text-base font-bold text-gray-100">
              {{ formData.name || '未命名角色' }}
            </h3>
            <span class="text-[11px] text-[#A8A29E]">
              by {{ formData.creatorName || '匿名创作者' }}
            </span>
          </div>

          <p class="text-xs text-[#A8A29E] line-clamp-2 leading-relaxed">
            {{ formData.marketDescription || formData.description || '暂无描述' }}
          </p>

          <!-- 标签 Pill -->
          <div v-if="formData.tags.length > 0" class="flex flex-wrap gap-1 pt-1">
            <span
              v-for="tag in formData.tags"
              :key="tag"
              class="px-2 py-0.5 rounded bg-[#F9C86D]/10 text-[#F9C86D] text-[10px]"
            >
              #{{ tag }}
            </span>
          </div>
        </div>
      </div>

      <!-- 2. 模拟开局序幕呈现 -->
      <div v-if="formData.prologueHtml" class="flex flex-col gap-1.5">
        <span class="text-[11px] font-medium text-[#F9C86D]">✦ 故事序幕 (首次开局渲染)</span>
        <div class="p-3 rounded-xl border border-dashed border-[#F9C86D]/40 bg-black/50 overflow-hidden">
          <div v-html="formData.prologueHtml" class="text-xs" />
        </div>
      </div>

      <!-- 3. 模拟首次问候气泡 -->
      <div class="flex flex-col gap-1.5">
        <span class="text-[11px] font-medium text-[#A8A29E]">✦ 首次问候台词</span>
        <div class="flex items-start gap-2.5 p-3 rounded-xl bg-stone-900/80 border border-stone-800">
          <div class="w-8 h-8 rounded-full overflow-hidden shrink-0 border border-[#F9C86D]/40 bg-black">
            <img
              v-if="formData.avatarUrl"
              :src="formData.avatarUrl"
              alt="Avatar"
              class="w-full h-full object-cover"
            />
          </div>
          <div class="flex-1 flex flex-col gap-1">
            <span class="text-[11px] font-medium text-stone-400">
              {{ formData.name || '角色' }}
            </span>
            <p class="text-xs text-stone-200 leading-relaxed whitespace-pre-wrap">
              {{ formData.firstMes || '（等待输入首次问候台词...）' }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end w-full pt-1">
        <AppButton variant="gold" size="sm" @click="emit('update:open', false)">
          完成预览
        </AppButton>
      </div>
    </template>
  </AppModal>
</template>
