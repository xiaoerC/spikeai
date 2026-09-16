<script setup lang="ts">
/**
 * 叙梦 Naro - 角色卡详情主页面 (Smart Container 主入口)
 *
 * 1:1 严格还原 Figma 原型《深夜甜品店｜知性前辈×慌张店员 - 角色卡详情 - Naro叙梦》全部视觉与交互。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import CharacterActionButtons from "@/views/character-detail/components/CharacterActionButtons.vue";
import CharacterAuthorCard from "@/views/character-detail/components/CharacterAuthorCard.vue";
import CharacterCommentsCard from "@/views/character-detail/components/CharacterCommentsCard.vue";
import CharacterDescriptionCard from "@/views/character-detail/components/CharacterDescriptionCard.vue";
import CharacterHeroHeader from "@/views/character-detail/components/CharacterHeroHeader.vue";
import CharacterMetaInfoCard from "@/views/character-detail/components/CharacterMetaInfoCard.vue";
import CharacterPrologueCard from "@/views/character-detail/components/CharacterPrologueCard.vue";
import CharacterTagsCard from "@/views/character-detail/components/CharacterTagsCard.vue";
import FloatingMascotBadge from "@/views/character-detail/components/FloatingMascotBadge.vue";
import { useCharacterDetail } from "@/views/character-detail/composables/useCharacterDetail";
import { useRoute } from "vue-router";

const route = useRoute();
const characterId = (route.params.id as string) || "c1";

const {
  character,
  comments,
  isLiked,
  isFavorited,
  handleStartChat,
  handleToggleLike,
  handleToggleFavorite,
  handleToggleFollow,
  handleShare,
  handleReport,
  handleReward,
  handleRating,
  handleAddComment,
} = useCharacterDetail(characterId);
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] md:bg-none md:bg-[#15120E] text-[#F5F5F4] relative pb-28 md:pb-12">
    
    <!-- 移动端单列流式排版 (< 768px) -->
    <div class="flex md:hidden flex-col w-full max-w-[440px] mx-auto">
      <!-- 1. 顶部 Hero (大封面 + 标题 + 10项数据指标 + 设定字数/世界书) -->
      <CharacterHeroHeader :character="character" />

      <!-- 2. 核心操作按钮组 (开始聊天 / 点赞 / 收藏 / 评分 / 分享 / 举报 / 打赏) -->
      <CharacterActionButtons
        :is-liked="isLiked"
        :is-favorited="isFavorited"
        @start-chat="handleStartChat"
        @toggle-like="handleToggleLike"
        @toggle-favorite="handleToggleFavorite"
        @open-rating="handleRating"
        @share="handleShare"
        @report="handleReport"
        @reward="handleReward"
      />

      <!-- 3. 序幕剧情拟物卡片 (Dolce Notte 复古纸张风格) -->
      <CharacterPrologueCard :prologue="character.prologue" />

      <!-- 4. 作者信息卡片 (XXYY, 粉丝数, +关注) -->
      <CharacterAuthorCard
        :author="character.author"
        @toggle-follow="handleToggleFollow"
      />

      <!-- 5. 标签流卡片 (#都市 #纯爱 #御姐 #校园 #NTR) -->
      <CharacterTagsCard :tags="character.tags" />

      <!-- 6. 角色描述卡片 (展开折叠全文) -->
      <CharacterDescriptionCard :description="character.description" />

      <!-- 7. 详细信息元数据卡片 (创建/更新/版本/公开性) -->
      <CharacterMetaInfoCard :meta="character.meta" />

      <!-- 8. 评论区输入与真实评论列表 -->
      <CharacterCommentsCard :comments="comments" @submit-comment="handleAddComment" />

      <!-- 9. 右下角悬浮粉鸟吉祥物徽章 -->
      <FloatingMascotBadge @click="handleStartChat" />
    </div>

    <!-- PC 桌面端左右分栏高奢展示布局 (>= 768px) -->
    <main class="hidden md:grid grid-cols-[380px_1fr] gap-8 items-start w-full max-w-[1600px] mx-auto px-8 pt-6">
      
      <!-- 左栏: 粘性挂起的大立绘、操作按钮组、作者卡片与元数据指标 -->
      <div class="sticky top-6 flex flex-col gap-5">
        <CharacterHeroHeader :character="character" />
        <CharacterActionButtons
          :is-liked="isLiked"
          :is-favorited="isFavorited"
          @start-chat="handleStartChat"
          @toggle-like="handleToggleLike"
          @toggle-favorite="handleToggleFavorite"
          @open-rating="handleRating"
          @share="handleShare"
          @report="handleReport"
          @reward="handleReward"
        />
        <CharacterAuthorCard
          :author="character.author"
          @toggle-follow="handleToggleFollow"
        />
        <CharacterMetaInfoCard :meta="character.meta" />
      </div>

      <!-- 右栏: 角色开场白序幕、详细设定、标签与用户评论区 -->
      <div class="flex flex-col gap-5 min-w-0">
        <CharacterPrologueCard :prologue="character.prologue" />
        <CharacterDescriptionCard :description="character.description" />
        <CharacterTagsCard :tags="character.tags" />
        <CharacterCommentsCard :comments="comments" @submit-comment="handleAddComment" />
      </div>

    </main>

    <!-- 全局底部导航栏 (自动在桌面端隐藏) -->
    <BottomTabBar />

  </div>
</template>
