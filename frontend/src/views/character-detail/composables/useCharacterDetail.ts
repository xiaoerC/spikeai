/**
 * 角色卡详情业务逻辑 Composable
 *
 * @packageDocumentation
 */

import {
  type CharacterDetailData,
  MOCK_CHARACTER_DETAIL,
} from "@/views/character-detail/constants/mockCharacterDetail";
import { reactive, readonly, ref } from "vue";
import { useRouter } from "vue-router";

export function useCharacterDetail(_characterId?: string) {
  const router = useRouter();
  const character = reactive<CharacterDetailData>({ ...MOCK_CHARACTER_DETAIL });

  const isLiked = ref(false);
  const isFavorited = ref(false);
  const toastMessage = ref("");

  function showToast(msg: string): void {
    toastMessage.value = msg;
    setTimeout(() => {
      toastMessage.value = "";
    }, 2000);
  }

  function handleStartChat(): void {
    router.push(`/chat/${character.id}`);
  }

  function handleToggleLike(): void {
    isLiked.value = !isLiked.value;
    if (isLiked.value) {
      character.metrics.likes++;
      showToast("点赞成功");
    } else {
      character.metrics.likes--;
    }
  }

  function handleToggleFavorite(): void {
    isFavorited.value = !isFavorited.value;
    if (isFavorited.value) {
      character.metrics.favorites++;
      showToast("已加入收藏");
    } else {
      character.metrics.favorites--;
    }
  }

  function handleToggleFollow(): void {
    character.author.isFollowed = !character.author.isFollowed;
    if (character.author.isFollowed) {
      character.author.followersCount++;
      showToast(`已关注创作者 ${character.author.name}`);
    } else {
      character.author.followersCount--;
    }
  }

  function handleShare(): void {
    navigator.clipboard.writeText(window.location.href);
    showToast("链接已复制到剪贴板");
  }

  function handleReport(): void {
    showToast("感谢反馈，已提交审核");
  }

  function handleReward(): void {
    showToast("打赏功能暂未开启");
  }

  function handleRating(): void {
    showToast("请先与角色进行至少 5 轮对话后再进行评分");
  }

  function handleAddComment(text: string): void {
    showToast(`评论发表成功: ${text.slice(0, 10)}...`);
  }

  return {
    character,
    isLiked: readonly(isLiked),
    isFavorited: readonly(isFavorited),
    toastMessage: readonly(toastMessage),

    handleStartChat,
    handleToggleLike,
    handleToggleFavorite,
    handleToggleFollow,
    handleShare,
    handleReport,
    handleReward,
    handleRating,
    handleAddComment,
  };
}
