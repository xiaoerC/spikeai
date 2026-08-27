<script setup lang="ts">
/**
 * 历史记录 - 我上传的角色卡管理面板 (1:1 原型与全功能交互)
 *
 * 提供用户本人创建/上传的角色卡列表展示，支持修改、下架、上架、删除及发起聊天。
 *
 * @packageDocumentation
 */

import { AppModal } from "@/components/common";
import type { CharacterDetail } from "@/services/character";
import UploadHistoryEmptyPanel from "@/views/history/components/UploadHistoryEmptyPanel.vue";
import {
  ArrowDownCircle,
  ArrowUpCircle,
  Clock,
  Edit3,
  Flame,
  MessageSquare,
  Sparkles,
  Trash2,
} from "lucide-vue-next";
import { ref } from "vue";

interface Props {
  /** 用户创建的角色列表 */
  characters: CharacterDetail[];
  /** 加载中状态 */
  isLoading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  isLoading: false,
});

const emit = defineEmits<{
  (e: "edit", char: CharacterDetail): void;
  (e: "toggle-status", char: CharacterDetail, newStatus: "published" | "draft"): void;
  (e: "delete", char: CharacterDetail): void;
  (e: "chat", char: CharacterDetail): void;
}>();

/** 待确认删除的角色 */
const deletingChar = ref<CharacterDetail | null>(null);
const isDeleteModalOpen = ref(false);

function openDeleteConfirm(char: CharacterDetail): void {
  deletingChar.value = char;
  isDeleteModalOpen.value = true;
}

function handleConfirmDelete(): void {
  if (deletingChar.value) {
    emit("delete", deletingChar.value);
    deletingChar.value = null;
    isDeleteModalOpen.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col w-full gap-3 pt-2">
    <!-- 1. 加载中骨架 -->
    <div v-if="isLoading" class="flex flex-col items-center justify-center py-16 gap-3">
      <div class="w-8 h-8 rounded-full border-2 border-[#F9C86D] border-t-transparent animate-spin" />
      <span class="text-xs text-[#A8A29E]">正在加载我的角色卡...</span>
    </div>

    <!-- 2. 空状态面板 -->
    <UploadHistoryEmptyPanel v-else-if="characters.length === 0" />

    <!-- 3. 上传角色卡列表 -->
    <div v-else class="flex flex-col gap-3">
      <div
        v-for="char in characters"
        :key="char.id"
        class="w-full rounded-2xl border border-[rgba(83,71,65,0.35)] bg-[rgba(26,25,21,0.75)] backdrop-blur-md p-3.5 flex flex-col gap-3 shadow-xl transition-all hover:border-[#F9C86D]/40"
      >
        <!-- 头部主信息区: 立绘封面 + 标题/数据 + 状态徽章 -->
        <div class="flex items-start gap-3 w-full">
          <!-- 3:4 比例立体封面 -->
          <div
            @click="emit('chat', char)"
            class="relative w-16 h-20 rounded-xl overflow-hidden flex-shrink-0 border border-[#F9C86D]/30 shadow-md cursor-pointer group"
          >
            <img
              :src="char.avatar_url || char.banner_url || ''"
              :alt="char.name"
              class="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-300"
              loading="lazy"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          </div>

          <!-- 中间文本信息 -->
          <div class="flex flex-col flex-1 min-w-0 justify-between gap-1">
            <div class="flex items-center justify-between gap-2">
              <h3
                @click="emit('chat', char)"
                class="text-sm font-bold text-white/95 truncate hover:text-[#F9C86D] cursor-pointer transition-colors"
              >
                {{ char.name }}
              </h3>

              <!-- 上下架状态徽章 -->
              <span
                v-if="char.status === 'published'"
                class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-950/70 border border-emerald-500/50 text-emerald-400 flex items-center gap-1 flex-shrink-0 shadow-sm"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                已上架
              </span>
              <span
                v-else
                class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-950/70 border border-amber-500/50 text-amber-300 flex items-center gap-1 flex-shrink-0 shadow-sm"
              >
                <span class="w-1.5 h-1.5 rounded-full bg-amber-400" />
                已下架 / 草稿
              </span>
            </div>

            <!-- 描述摘要 -->
            <p class="text-[11px] text-[#A8A29E] line-clamp-2 leading-relaxed">
              {{ char.description }}
            </p>

            <!-- 数据行: 设定字数 / 热度 / 消息数 / 创建时间 -->
            <div class="flex items-center gap-3 text-[10px] text-[#78716C] pt-1">
              <span class="flex items-center gap-1 text-[#F9C86D]">
                <Flame class="w-3 h-3 text-[#EAB308]" />
                {{ char.metrics?.hotness || 10 }}
              </span>
              <span class="flex items-center gap-1 text-[#FF9F43]">
                <MessageSquare class="w-3 h-3 text-[#FF9F43]" />
                {{ char.metrics?.chat_count || 0 }}
              </span>
              <span class="flex items-center gap-1 ml-auto text-neutral-400">
                <Clock class="w-3 h-3" />
                {{ new Date(char.created_at).toLocaleDateString() }}
              </span>
            </div>
          </div>
        </div>

        <!-- 底部 4 大功能操作栏: 修改 | 下架/上架 | 互动 | 删除 -->
        <div class="flex items-center justify-end gap-2 pt-2 border-t border-[rgba(83,71,65,0.25)]">
          <!-- 1. 修改按钮 -->
          <button
            type="button"
            @click="emit('edit', char)"
            class="px-3 py-1.5 rounded-lg border border-[#57534E] bg-[#292524]/60 text-xs font-semibold text-gray-200 hover:border-[#F9C86D] hover:text-[#F9C86D] transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 select-none"
          >
            <Edit3 class="w-3.5 h-3.5" />
            <span>修改</span>
          </button>

          <!-- 2. 下架 / 上架按钮 -->
          <button
            v-if="char.status === 'published'"
            type="button"
            @click="emit('toggle-status', char, 'draft')"
            class="px-3 py-1.5 rounded-lg border border-amber-600/40 bg-amber-950/25 text-xs font-semibold text-amber-300 hover:bg-amber-950/40 transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 select-none"
          >
            <ArrowDownCircle class="w-3.5 h-3.5" />
            <span>下架</span>
          </button>
          <button
            v-else
            type="button"
            @click="emit('toggle-status', char, 'published')"
            class="px-3 py-1.5 rounded-lg border border-emerald-600/40 bg-emerald-950/25 text-xs font-semibold text-emerald-300 hover:bg-emerald-950/40 transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 select-none"
          >
            <ArrowUpCircle class="w-3.5 h-3.5" />
            <span>上架</span>
          </button>

          <!-- 3. 对话互动按钮 -->
          <button
            type="button"
            @click="emit('chat', char)"
            class="px-3 py-1.5 rounded-lg border border-[#F9C86D]/40 bg-[#F9C86D]/15 text-xs font-semibold text-[#F9C86D] hover:bg-[#F9C86D]/25 transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 select-none"
          >
            <Sparkles class="w-3.5 h-3.5" />
            <span>去聊天</span>
          </button>

          <!-- 4. 删除按钮 -->
          <button
            type="button"
            @click="openDeleteConfirm(char)"
            class="px-3 py-1.5 rounded-lg border border-red-900/40 bg-red-950/20 text-xs font-semibold text-red-400 hover:bg-red-950/40 transition-all flex items-center gap-1.5 cursor-pointer active:scale-95 select-none ml-auto"
          >
            <Trash2 class="w-3.5 h-3.5" />
            <span>删除</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 删除二次确认弹窗 -->
    <AppModal
      v-model:open="isDeleteModalOpen"
      title="确认删除角色卡"
      description="删除后该角色卡及其所有世界书、统计指标和历史配置将被彻底清除，不可恢复。"
    >
      <div class="flex flex-col gap-3 text-xs text-gray-300 py-2">
        <p>您确定要永久删除角色卡「<strong class="text-[#F9C86D]">{{ deletingChar?.name }}</strong>」吗？</p>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2.5 w-full">
          <button
            type="button"
            @click="isDeleteModalOpen = false"
            class="px-4 py-2 rounded-xl text-xs font-semibold border border-neutral-700 bg-neutral-800 text-gray-300 hover:bg-neutral-700 transition-all cursor-pointer"
          >
            取消
          </button>
          <button
            type="button"
            @click="handleConfirmDelete"
            class="px-4 py-2 rounded-xl text-xs font-semibold border border-red-600 bg-red-600 text-white hover:bg-red-500 transition-all cursor-pointer shadow-lg"
          >
            确认删除
          </button>
        </div>
      </template>
    </AppModal>
  </div>
</template>
