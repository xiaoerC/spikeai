<script setup lang="ts">
/**
 * 叙梦 Naro - 原创角色卡创建与编辑器 (Smart Container 主入口)
 *
 * 1:1 还原 Figma Frame 137:1615 规范，涵盖 4 大分节手风琴 (卡面/角色/舞台/机制)、
 * 简洁/完整双模式切换、SillyTavern V3 世界书体系、正则流水线、RPG变量与发布闭环。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useToast } from "@/composables/useToast";
import { type CharacterCreatePayload, characterService } from "@/services/character";
import { useAppStore } from "@/stores/app";
import AuthorNoteModal from "@/views/character-create/components/AuthorNoteModal.vue";
import CardExportSection from "@/views/character-create/components/CardExportSection.vue";
import CharacterSection from "@/views/character-create/components/CharacterSection.vue";
import CoverSection from "@/views/character-create/components/CoverSection.vue";
import CreationNoticeSection from "@/views/character-create/components/CreationNoticeSection.vue";
import CreatorHeader from "@/views/character-create/components/CreatorHeader.vue";
import DesktopLivePreview from "@/views/character-create/components/DesktopLivePreview.vue";
import MechanicsSection from "@/views/character-create/components/MechanicsSection.vue";
import NavigationAnchorBar from "@/views/character-create/components/NavigationAnchorBar.vue";
import PreviewModal from "@/views/character-create/components/PreviewModal.vue";
import StageSection from "@/views/character-create/components/StageSection.vue";
import { useUserStore } from "@/stores/user";
import { useCharacterForm } from "@/views/character-create/composables/useCharacterForm";
import { uploadService } from "@/services/upload";
import { compressImageDataUrl, dataUrlToFile } from "@/utils/imageCompressor";
import { normalizePosition } from "@/views/character-create/types";
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { MOCK_CHARACTER_PRESETS } from "./constants/mockPresets";

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();
const userStore = useUserStore();
const toast = useToast();
const { formData, validationErrors, isValid, resetForm, importFromJson, exportToJson } =
  useCharacterForm();

const isSubmitting = ref<boolean>(false);
const isAuthorNoteOpen = ref<boolean>(false);
const isPreviewModalOpen = ref<boolean>(false);
const editId = computed(() => (route.query.edit_id as string) || null);

onMounted(async () => {
  appStore.setActiveTab("create");
  if (editId.value) {
    try {
      const char = await characterService.getCharacterDetail(editId.value);
      Object.assign(formData, {
        creatorNotes: char.creator_notes || "",
        name: char.name,
        avatarUrl: char.avatar_url,
        tags: [...char.tags],
        marketDescription: char.description?.slice(0, 200) || "",
        category: (char.category === "nsfw" ? "nsfw" : "story") as "story" | "nsfw",
        isNsfw: char.category === "nsfw",
        visibility: (char.status === "private" ? "private" : "public") as "public" | "private",
        creatorName: char.author?.username || "",
        version: char.version || "1.0.0",
        description: char.description,
        personality: char.personality,
        scenario: char.scenario,
        prologueHtml: char.prologue_html,
        firstMes: char.first_mes,
        alternateGreetings: (char.alternate_greetings || []).map((text, idx) => ({
          id: `alt-${idx}`,
          title: `开场白 ${idx + 1}`,
          greetingText: text,
        })),
        systemPrompt: char.system_prompt,
        postHistoryInstructions: char.post_history_instructions,
        worldbookEntries: char.extensions?.character_book?.entries
          ? char.extensions.character_book.entries.map((wb: any, idx: number) => ({
              id: `wb-${idx}`,
              name: wb.comment || wb.name || `设定 ${idx + 1}`,
              keys: Array.isArray(wb.keys) ? wb.keys : [],
              secondaryKeys: Array.isArray(wb.secondary_keys) ? wb.secondary_keys : [],
              content: wb.content || "",
              isEnabled: wb.enabled ?? true,
              position: wb.position || "after_char",
            }))
          : (char.worldbooks || []).map((wb, idx) => ({
              id: `wb-${idx}`,
              name: `设定 ${idx + 1}`,
              keys: wb.keys,
              content: wb.content,
              isEnabled: true,
              position: (wb.position as any) || "after_char",
            })),
      });
      toast.info(`已载入角色「${char.name}」全部设定，可直接编辑修改`);
    } catch (err) {
      console.error("载入待编辑角色失败:", err);
      toast.error("载入角色卡数据失败");
    }
  } else {
    // 恢复本地草稿 (如果有)
    const savedDraft = localStorage.getItem("naro_character_form_draft");
    if (savedDraft) {
      try {
        const draft = JSON.parse(savedDraft);
        if (draft.name) {
          Object.assign(formData, draft);
        }
      } catch {
        // 忽略无效草稿
      }
    }
  }
});

import type { CardParseResult } from "@/utils/cardParser";

async function handleImportCard(result: CardParseResult): Promise<void> {
  if (result.success && result.jsonData) {
    if (result.avatarDataUrl) {
      // 1. 快速轻量压缩（避免表单响应式状态暴增 10MB 内存）
      const compressed = await compressImageDataUrl(result.avatarDataUrl, {
        maxWidth: 1024,
        quality: 0.85,
      });
      formData.avatarUrl = compressed;

      // 2. 后台异步上传至静态对象存储，将 base64 自动换取持久化短 URL
      try {
        const file = dataUrlToFile(compressed, `${result.jsonData.name || "avatar"}.webp`);
        uploadService
          .uploadImage(file, "avatars")
          .then((url) => {
            if (url) formData.avatarUrl = url;
          })
          .catch((e) => {
            console.warn("后台预上传立绘未完成，将在发布时自动重试:", e);
          });
      } catch (e) {
        console.warn("立绘转文件失败:", e);
      }
    }
    const success = importFromJson(JSON.stringify(result.jsonData));
    if (success) {
      toast.success(`角色卡「${formData.name || "未命名"}」数据导入成功！`);
    } else {
      toast.error("角色卡数据结构不符合酒馆规范");
    }
    return;
  }

  // 未检测到有效角色卡数据 (例如普通 JPG、或没有元数据的图片)
  if (result.avatarDataUrl) {
    const compressed = await compressImageDataUrl(result.avatarDataUrl, {
      maxWidth: 1024,
      quality: 0.85,
    });
    formData.avatarUrl = compressed;
    try {
      const file = dataUrlToFile(compressed, "avatar.webp");
      uploadService
        .uploadImage(file, "avatars")
        .then((url) => {
          if (url) formData.avatarUrl = url;
        })
        .catch(() => {});
    } catch (_) {}
    toast.warning(result.errorMessage || "未检测到角色卡数据，已将图片设为角色立绘封面");
  } else {
    toast.error(result.errorMessage || "导入失败，文件格式不合法");
  }
}

function handleImportFile(jsonStr: string): void {
  const success = importFromJson(jsonStr);
  if (success) {
    toast.success("角色卡数据导入成功！");
  } else {
    toast.error("导入失败，文件格式不合法");
  }
}

function handleSaveForm(): void {
  try {
    localStorage.setItem("naro_character_form_draft", JSON.stringify(formData));
    toast.success("角色卡草稿已成功保存至本地！");
  } catch {
    toast.error("保存本地草稿失败");
  }
}

function handleClearForm(): void {
  resetForm();
  localStorage.removeItem("naro_character_form_draft");
  toast.info("已清空表单数据与本地草稿");
}

function handleOpenTutorial(): void {
  window.open("https://docs.sillytavern.app", "_blank");
}

function handleOpenAssets(): void {
  toast.info("我的素材库功能即将开放");
}

/**
 * 提交发布角色卡至社区并进入详情页
 */
async function handlePublishCharacter(): Promise<void> {
  if (!isValid.value) {
    toast.error("请完善必填项后再发布");
    return;
  }

  isSubmitting.value = true;
  try {
    // 关键防御：若立绘仍为 base64 格式，优先上传至静态对象存储，将 10MB 巨型图片换取轻量短 URL
    let finalAvatarUrl = formData.avatarUrl ? formData.avatarUrl.trim() : "";
    if (finalAvatarUrl.startsWith("data:image/")) {
      try {
        const compressed = await compressImageDataUrl(finalAvatarUrl, {
          maxWidth: 1024,
          quality: 0.85,
        });
        const file = dataUrlToFile(compressed, `${formData.name.trim() || "avatar"}.webp`);
        const uploadedUrl = await uploadService.uploadImage(file, "avatars");
        if (uploadedUrl) {
          finalAvatarUrl = uploadedUrl;
          formData.avatarUrl = uploadedUrl;
        }
      } catch (uploadErr) {
        console.warn("发布前上传立绘失败，降级为轻量压缩 base64:", uploadErr);
        finalAvatarUrl = await compressImageDataUrl(finalAvatarUrl, { maxWidth: 800, quality: 0.8 });
      }
    }

    const payload: CharacterCreatePayload = {
      name: formData.name.trim(),
      avatar_url:
        finalAvatarUrl || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500",
      banner_url: finalAvatarUrl || null,
      category: formData.category,
      description: formData.description.trim() || formData.marketDescription.trim() || "暂无描述",
      personality: formData.personality.trim(),
      scenario: formData.scenario.trim(),
      first_mes: formData.firstMes.trim(),
      alternate_greetings: formData.alternateGreetings
        .map((g) => g.greetingText.trim())
        .filter(Boolean),
      system_prompt: formData.systemPrompt.trim(),
      post_history_instructions: formData.postHistoryInstructions.trim(),
      prologue_title: "序幕",
      prologue_html: formData.prologueHtml.trim(),
      creator_notes: formData.creatorNotes.trim(),
      tags: formData.tags,
      status: formData.visibility === "private" ? "private" : "published",
      version: formData.version || "1.0.0",
      extensions: {
        variables: formData.initialVariables || {},
        regex_scripts: formData.regexScripts || [],
        opening_replies: formData.openingReplies || [],
        bgm_url: formData.stageExtensions?.bgmUrl || "",
        custom_css: formData.stageExtensions?.customCss || "",
        before_char: formData.beforeChar || "",
        character_book: {
          entries: (formData.worldbookEntries || []).map((wb, idx) => ({
            id: idx + 1,
            name: wb.name,
            comment: wb.name,
            keys: wb.keys,
            secondary_keys: wb.secondaryKeys || [],
            content: wb.content,
            enabled: wb.isEnabled !== false,
            insertion_order: idx + 1,
            position: normalizePosition(wb.position),
          })),
        },
      },
      worldbooks: (formData.worldbookEntries || [])
        .filter((wb) => (wb.content.trim() || wb.keys.length > 0) && wb.isEnabled !== false)
        .map((wb) => ({
          keys: wb.keys,
          content: wb.content.trim(),
          constant: false,
          position: normalizePosition(wb.position),
        })),
    };

    if (editId.value) {
      await characterService.updateCharacter(editId.value, payload);
      toast.success("角色卡已成功保存修改！");
      setTimeout(() => {
        router.push("/history");
      }, 500);
    } else {
      const newChar = await characterService.createCharacter(payload);
      // 清理草稿
      localStorage.removeItem("naro_character_form_draft");
      toast.success("恭喜！角色卡已成功发布至社区！");

      setTimeout(() => {
        router.push(`/character/${newChar.id}`);
      }, 500);
    }
  } catch (err: any) {
    console.error("提交角色卡失败:", err);
    const errorMsg =
      err.response?.data?.message ||
      err.response?.data?.detail ||
      err.message ||
      "提交角色卡失败，请检查网络或登录状态";
    toast.error(errorMsg);
  } finally {
    isSubmitting.value = false;
  }
}

/**
 * 一键模拟全字段并填充角色 (快速生成与测试)
 */
function handleSimulateUpload(): void {
  const preset = MOCK_CHARACTER_PRESETS[0];
  if (!preset) return;
  importFromJson(JSON.stringify(preset));
  toast.info("已自动填充高保真角色全参数，您可以继续微调或直接发布！");
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] md:bg-none md:bg-[#15120E] text-gray-100 relative">
    
    <!-- 1. 顶部 Header & 工具箱卡片 (1:1 还原截图 4 顶部工具栏) -->
    <div class="w-full max-w-[440px] md:max-w-[1600px] mx-auto px-3 md:px-8 pt-4">
      <CreatorHeader
        @import-card="handleImportCard"
        @import-file="handleImportFile"
        @save-form="handleSaveForm"
        @clear-form="handleClearForm"
        @open-tutorial="handleOpenTutorial"
        @open-assets="handleOpenAssets"
      />
    </div>

    <!-- 2. 主表单与实时预览工作台 (桌面端双栏排版，1:1 对齐截图 4) -->
    <main class="w-full max-w-[440px] md:max-w-[1600px] mx-auto px-3 md:px-8 pb-32 md:pb-24 flex flex-col mt-2">
      <div class="flex flex-col md:flex-row items-start gap-8 w-full">
        
        <!-- 左侧/中间: 核心表单区域 -->
        <div class="flex-1 flex flex-col gap-4 w-full min-w-0">
          <!-- 吸顶分节锚点导航与简洁/完整双模式切换 -->
          <NavigationAnchorBar
            v-model:active-tab="formData.activeTab"
            v-model:display-mode="formData.displayMode"
            @open-preview="isPreviewModalOpen = true"
          />

          <!-- 分节 1: 【卡面】(面向市场) -->
          <CoverSection
            v-model:name="formData.name"
            v-model:avatar-url="formData.avatarUrl"
            v-model:tags="formData.tags"
            v-model:market-description="formData.marketDescription"
            v-model:category="formData.category"
            v-model:is-original="formData.isOriginal"
            v-model:is-nsfw="formData.isNsfw"
            v-model:visibility="formData.visibility"
            v-model:creator-name="formData.creatorName"
            v-model:version="formData.version"
            :has-creator-notes="Boolean(formData.creatorNotes.trim())"
            :display-mode="formData.displayMode"
            @open-author-note="isAuthorNoteOpen = true"
          />

          <!-- 分节 2: 【角色】(面向模型设定) -->
          <CharacterSection
            v-model:description="formData.description"
            v-model:personality="formData.personality"
            v-model:scenario="formData.scenario"
            v-model:before-char="formData.beforeChar"
            v-model:worldbook-version="formData.worldbookVersion"
            v-model:worldbook-entries="formData.worldbookEntries"
            v-model:system-prompt="formData.systemPrompt"
            v-model:post-history-instructions="formData.postHistoryInstructions"
            :display-mode="formData.displayMode"
          />

          <!-- 分节 3: 【舞台】(面向对话与开局) -->
          <StageSection
            :name="formData.name"
            :description="formData.description"
            :personality="formData.personality"
            :scenario="formData.scenario"
            v-model:first-mes="formData.firstMes"
            v-model:alternate-greetings="formData.alternateGreetings"
            v-model:opening-replies="formData.openingReplies"
            v-model:prologue-html="formData.prologueHtml"
            v-model:stage-extensions="formData.stageExtensions"
            :display-mode="formData.displayMode"
          />

          <!-- 分节 4: 【机制】(面向引擎执行脚本与变量) -->
          <MechanicsSection
            v-if="formData.displayMode === 'full'"
            v-model:regex-scripts="formData.regexScripts"
            v-model:initial-variables="formData.initialVariables"
          />

          <!-- 创作须知卡片 -->
          <CreationNoticeSection />
        </div>

        <!-- 右侧: PC 桌面端吸顶实时预览卡片 (1:1 还原截图 4) -->
        <div class="hidden md:block">
          <DesktopLivePreview
            :name="formData.name"
            :avatar-url="formData.avatarUrl"
            :tags="formData.tags"
            :category="formData.category"
            :author-name="formData.creatorName || userStore.profile?.username"
          />
        </div>

      </div>
    </main>

    <!-- 8. 底部固定发布 & 导出操作栏 (带 Safe Area 避让) -->
    <CardExportSection
      :form-data="formData"
      :validation-errors="validationErrors"
      :is-valid="isValid"
      :is-submitting="isSubmitting"
      @publish="handlePublishCharacter"
      @simulate-upload="handleSimulateUpload"
    />

    <!-- 9. 全局底部导航栏 -->
    <BottomTabBar />

    <!-- 10. 作者的话弹窗 (AppModal 规范) -->
    <AuthorNoteModal
      v-model:open="isAuthorNoteOpen"
      v-model="formData.creatorNotes"
    />

    <!-- 11. 实时预览弹窗 (AppModal 规范) -->
    <PreviewModal
      v-model:open="isPreviewModalOpen"
      :form-data="formData"
    />

  </div>
</template>
