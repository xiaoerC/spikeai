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
  alternateGreetings?: readonly string[];
  currentGreetingIndex?: number;
}>();

const emit = defineEmits<{
  (
    e:
      | "readAloud"
      | "regenerate"
      | "rerunMemory"
      | "continue"
      | "branch"
      | "edit"
      | "share"
      | "delete",
    msg: ChatMessage,
  ): void;
  (e: "saveEdit", msg: ChatMessage, newContent: string, regenerate: boolean): void;
  (e: "switchGreeting", index: number): void;
}>();

const scrollContainer = ref<HTMLElement | null>(null);
const isUserPinnedAtBottom = ref(true);

/**
 * 监听滚动事件：检测用户是否手动向上翻阅历史消息
 */
function handleScroll(): void {
  if (!scrollContainer.value) return;
  const { scrollTop, scrollHeight, clientHeight } = scrollContainer.value;
  // 若距离底部小于 90px，则判定为处于底部跟随态
  const atBottom = scrollHeight - scrollTop - clientHeight < 90;
  isUserPinnedAtBottom.value = atBottom;
}

/**
 * 滚动触底 (若用户正在向上翻阅则不强制打扰)
 */
function scrollToBottom(force = false): void {
  if (!force && !isUserPinnedAtBottom.value) return;
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  });
}

// 监听消息列表长度变动，强制吸底
watch(
  () => props.messages.length,
  () => {
    scrollToBottom(true);
  },
);

// 监听最后一条消息内容动态变动 (打字机吐字中)
watch(
  () => {
    const last = props.messages[props.messages.length - 1];
    return last ? `${last.content?.length || 0}_${last.thinkingContent?.length || 0}` : "";
  },
  () => {
    scrollToBottom(false);
  },
);
</script>

<template>
  <div
    ref="scrollContainer"
    @scroll.passive="handleScroll"
    class="flex-1 w-full overflow-y-auto overflow-x-hidden flex flex-col gap-2 pb-6 scroll-smooth will-change-scroll"
    style="contain: content;"
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
        v-for="(msg, index) in messages"
        :key="msg.id"
        :message="msg"
        :is-first-message="index === 0"
        :alternate-greetings="alternateGreetings"
        :current-greeting-index="currentGreetingIndex"
        @switch-greeting="(idx) => emit('switchGreeting', idx)"
        @read-aloud="(m) => emit('readAloud', m)"
        @regenerate="(m) => emit('regenerate', m)"
        @rerun-memory="(m) => emit('rerunMemory', m)"
        @continue="(m) => emit('continue', m)"
        @branch="(m) => emit('branch', m)"
        @edit="(m) => emit('edit', m)"
        @save-edit="(m, text, regen) => emit('saveEdit', m, text, regen)"
        @share="(m) => emit('share', m)"
        @delete="(m) => emit('delete', m)"
      />
    </div>
  </div>
</template>
