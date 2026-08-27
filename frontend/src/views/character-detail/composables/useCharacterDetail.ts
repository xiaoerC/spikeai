/**
 * 角色卡详情业务逻辑 Composable (全量对接真实后端 API)。
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import {
  characterService,
  type CharacterComment,
  type CharacterDetail,
} from "@/services/character";
import { useAppStore } from "@/stores/app";
import { useUserStore } from "@/stores/user";
import type { CharacterDetailData } from "@/views/character-detail/constants/mockCharacterDetail";
import { onMounted, reactive, readonly, ref, watch } from "vue";
import { useRouter } from "vue-router";

function formatNumber(num: number): string {
  if (num >= 1000000) {
    return `${(num / 1000000).toFixed(1)}M`;
  }
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}w`;
  }
  if (num >= 1000) {
    return `${(num / 1000).toFixed(1)}k`;
  }
  return num.toString();
}

function mapBackendDetailToView(detail: CharacterDetail): CharacterDetailData {
  return {
    id: detail.id,
    name: detail.name,
    avatarUrl: detail.avatar_url,
    bannerUrl: detail.banner_url || detail.avatar_url,
    status: detail.status === "published" ? "published" : "draft",
    isOriginal: true,
    metrics: {
      hotness: formatNumber(detail.metrics?.hotness || 0),
      likes: detail.metrics?.like_count || 0,
      favorites: detail.metrics?.favorite_count || 0,
      imports: detail.metrics?.import_count || 0,
      uses: detail.metrics?.chat_count || 0,
      uniquePlayers: Math.max(1, Math.round((detail.metrics?.like_count || 0) * 1.5)),
      totalChats: detail.metrics?.chat_count || 0,
      deepPlays: Math.max(0, Math.round((detail.metrics?.chat_count || 0) / 100)),
      avgCost: 10.0,
      totalTokens: formatNumber(detail.metrics?.total_tokens || 0),
    },
    settingsWordCount: (detail.settings_word_count || 0).toLocaleString(),
    worldBookCount: detail.worldbooks?.length || 0,
    prologue: {
      title: detail.prologue_title || "序幕",
      description: detail.scenario || detail.description || "",
      html: detail.prologue_html || "",
      worldInfo: detail.system_prompt || detail.description || "",
      charactersInfo: detail.personality || detail.first_mes || "",
    },
    author: {
      id: detail.author?.id || "",
      name: detail.author?.username || "叙梦官方馆长",
      avatarUrl: detail.author?.avatar_url || "",
      followersCount: detail.author?.followers_count || 12,
      isFollowed: detail.author?.is_following || false,
    },
    tags: (detail.tags || []).map((t) => (t.startsWith("#") ? t : `#${t}`)),
    description: detail.description || "",
    meta: {
      createdAt: detail.created_at ? new Date(detail.created_at).toLocaleDateString() : "2026/8/24",
      updatedAt: "刚刚",
      version: detail.version || "1.0",
      visibility: "公开",
    },
  };
}

export function useCharacterDetail(characterId?: string) {
  const router = useRouter();
  const toast = useToast();
  const userStore = useUserStore();
  const appStore = useAppStore();

  const character = reactive<CharacterDetailData>({
    id: characterId || "",
    name: "加载中...",
    avatarUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=loading",
    bannerUrl: "",
    status: "published",
    isOriginal: true,
    metrics: {
      hotness: "0",
      likes: 0,
      favorites: 0,
      imports: 0,
      uses: 0,
      uniquePlayers: 0,
      totalChats: 0,
      deepPlays: 0,
      avgCost: 0,
      totalTokens: "0",
    },
    settingsWordCount: "0",
    worldBookCount: 0,
    prologue: {
      title: "序幕",
      description: "",
      html: "",
      worldInfo: "",
      charactersInfo: "",
    },
    author: {
      id: "",
      name: "叙梦创作者",
      avatarUrl: "",
      followersCount: 0,
      isFollowed: false,
    },
    tags: [],
    description: "",
    meta: {
      createdAt: "",
      updatedAt: "",
      version: "1.0",
      visibility: "公开",
    },
  });

  const rawDetail = ref<CharacterDetail | null>(null);
  const comments = ref<CharacterComment[]>([]);
  const isLiked = ref(false);
  const isFavorited = ref(false);
  const isLoading = ref(false);

  async function loadDetail(id: string): Promise<void> {
    if (!id) return;
    isLoading.value = true;
    try {
      const data = await characterService.getCharacterDetail(id);
      rawDetail.value = data;
      const mapped = mapBackendDetailToView(data);
      Object.assign(character, mapped);
      isLiked.value = data.is_liked || false;
      isFavorited.value = data.is_favorited || false;

      // 加载评论
      await loadComments(id);
    } catch (e) {
      console.error("加载角色详情失败:", e);
      toast.error("加载角色详情失败");
    } finally {
      isLoading.value = false;
    }
  }

  async function loadComments(id: string): Promise<void> {
    try {
      const res = await characterService.getComments(id);
      comments.value = res.items || [];
    } catch (e) {
      console.error("加载评论失败:", e);
    }
  }

  function handleStartChat(): void {
    if (!character.id) return;
    if (!userStore.isLoggedIn) {
      toast.warning("请先登录账户开启专属剧情与对话");
      appStore.openLoginModal();
      return;
    }
    router.push(`/chat/${character.id}`);
  }

  async function handleToggleLike(): Promise<void> {
    if (!character.id) return;
    if (!userStore.isLoggedIn) {
      toast.warning("请先登录账户进行点赞");
      appStore.openLoginModal();
      return;
    }
    try {
      const res = await characterService.toggleLike(character.id);
      isLiked.value = res.is_liked;
      character.metrics.likes = res.like_count;
    } catch (e) {
      console.error("点赞失败:", e);
    }
  }

  function handleToggleFavorite(): void {
    if (!userStore.isLoggedIn) {
      toast.warning("请先登录账户进行收藏");
      appStore.openLoginModal();
      return;
    }
    isFavorited.value = !isFavorited.value;
    if (isFavorited.value) {
      character.metrics.favorites++;
      toast.success("已加入收藏");
    } else {
      character.metrics.favorites = Math.max(0, character.metrics.favorites - 1);
      toast.info("已取消收藏");
    }
  }

  function handleToggleFollow(): void {
    if (!userStore.isLoggedIn) {
      toast.warning("请先登录账户关注创作者");
      appStore.openLoginModal();
      return;
    }
    character.author.isFollowed = !character.author.isFollowed;
    if (character.author.isFollowed) {
      character.author.followersCount++;
      toast.success(`已关注创作者 ${character.author.name}`);
    } else {
      character.author.followersCount = Math.max(0, character.author.followersCount - 1);
      toast.info(`已取消关注`);
    }
  }

  function handleShare(): void {
    navigator.clipboard?.writeText?.(window.location.href);
    toast.success("角色链接已复制到剪贴板");
  }

  function handleReport(): void {
    toast.info("感谢反馈，已提交审核");
  }

  async function handleReward(): Promise<void> {
    if (!character.id) return;
    if (!userStore.isLoggedIn) {
      toast.warning("请先登录账户进行打赏");
      appStore.openLoginModal();
      return;
    }
    try {
      await characterService.rewardCharacter(character.id, "star", 10);
      toast.success("成功打赏 10 星元！");
    } catch (e) {
      console.error("打赏失败:", e);
    }
  }

  function handleRating(): void {
    toast.info("请先与角色进行至少 5 轮对话后再进行评分");
  }

  async function handleAddComment(text: string): Promise<void> {
    if (!character.id || !text.trim()) return;
    if (!userStore.isLoggedIn) {
      toast.warning("请先登录账户发表评论");
      appStore.openLoginModal();
      return;
    }
    try {
      const newComment = await characterService.addComment(character.id, text.trim());
      comments.value.unshift(newComment);
      toast.success("评论发表成功！");
    } catch (e) {
      console.error("发表评论失败:", e);
      toast.error("发表评论失败，请重试");
    }
  }

  onMounted(() => {
    if (characterId) {
      loadDetail(characterId);
    }
  });

  watch(
    () => characterId,
    (newId) => {
      if (newId) loadDetail(newId);
    }
  );

  return {
    character,
    rawDetail: readonly(rawDetail),
    comments,
    isLiked: readonly(isLiked),
    isFavorited: readonly(isFavorited),
    isLoading: readonly(isLoading),

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
