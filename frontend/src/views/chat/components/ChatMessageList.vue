<script setup lang="ts">
/**
 * AI 聊天界面 - 消息滚动列表容器 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import AuthorNoteCard from "@/views/chat/components/AuthorNoteCard.vue";
import ChatMessageItem from "@/views/chat/components/ChatMessageItem.vue";
import ChatNoticeBanner from "@/views/chat/components/ChatNoticeBanner.vue";
import ChatPrologueCard from "@/views/chat/components/ChatPrologueCard.vue";
import type { ChatMessage } from "@/views/chat/constants/mockChatData";
import { nextTick, ref, watch } from "vue";

const props = defineProps<{
  messages: ChatMessage[];
  authorNote?: string;
  prologueTitle?: string;
  prologueContent?: string;
}>();

const emit =
  defineEmits<
    (e: "readAloud" | "regenerate" | "branch" | "edit" | "delete", msg: ChatMessage) => void
  >();

const scrollContainer = ref<HTMLElement | null>(null);

function scrollToBottom(): void {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  });
}

watch(
  () => props.messages.length,
  () => {
    scrollToBottom();
  },
);
</script>

<template>
  <div
    ref="scrollContainer"
    class="flex-1 w-full overflow-y-auto overflow-x-hidden flex flex-col gap-2 pb-6 scroll-smooth"
  >
    <!-- 1. 顶部合规提示 -->
    <ChatNoticeBanner />

    <!-- 2. 作者的话卡片 -->
    <AuthorNoteCard v-if="authorNote" :note="authorNote" />

    <!-- 3. 序幕剧情卡片 -->
    <ChatPrologueCard
      v-if="prologueContent"
      :title="prologueTitle"
      :content="prologueContent"
    />

    <!-- 4. 消息气泡列表 -->
    <div class="w-full flex flex-col gap-2 pt-2">
      <ChatMessageItem
        v-for="msg in messages"
        :key="msg.id"
        :message="msg"
        @read-aloud="(m) => emit('readAloud', m)"
        @regenerate="(m) => emit('regenerate', m)"
        @branch="(m) => emit('branch', m)"
        @edit="(m) => emit('edit', m)"
        @delete="(m) => emit('delete', m)"
      />
    </div>
  </div>
</template>
