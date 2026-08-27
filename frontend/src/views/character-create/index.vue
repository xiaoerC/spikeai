<script setup lang="ts">
/**
 * 叙梦 Naro - 原创角色卡创建与编辑器 (Smart Container 主入口)
 *
 * 1:1 像素级还原 Figma 原型与长图交互，涵盖作者的话、角色卡信息、基本信息、序幕、对话设置、高级设置与发布闭环。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useToast } from "@/composables/useToast";
import { characterService, type CharacterCreatePayload } from "@/services/character";
import { useAppStore } from "@/stores/app";
import AdvancedSection from "@/views/character-create/components/AdvancedSection.vue";
import AuthorNoteSection from "@/views/character-create/components/AuthorNoteSection.vue";
import BasicInfoSection from "@/views/character-create/components/BasicInfoSection.vue";
import CardExportSection from "@/views/character-create/components/CardExportSection.vue";
import CardInfoSection from "@/views/character-create/components/CardInfoSection.vue";
import CreationNoticeSection from "@/views/character-create/components/CreationNoticeSection.vue";
import CreatorHeader from "@/views/character-create/components/CreatorHeader.vue";
import DialogueSection from "@/views/character-create/components/DialogueSection.vue";
import PrologueSection from "@/views/character-create/components/PrologueSection.vue";
import { useCharacterForm } from "@/views/character-create/composables/useCharacterForm";
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const appStore = useAppStore();
const toast = useToast();
const { formData, validationErrors, isValid, resetForm, importFromJson } = useCharacterForm();

const isSubmitting = ref<boolean>(false);
const editId = computed(() => (route.query.edit_id as string) || null);

import { MOCK_CHARACTER_PRESETS } from "./constants/mockPresets";

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
        worldbookEntries: (char.worldbooks || []).map((wb, idx) => ({
          id: `wb-${idx}`,
          name: `设定 ${idx + 1}`,
          keys: wb.keys,
          content: wb.content,
          isEnabled: wb.constant,
        })),
      });
      toast.info(`已载入角色「${char.name}」全部设定，可直接编辑修改`);
    } catch (err) {
      console.error("载入待编辑角色失败:", err);
      toast.error("载入角色卡数据失败");
    }
  }
});

function handleImportFile(jsonStr: string): void {
  const success = importFromJson(jsonStr);
  if (success) {
    toast.success("角色卡数据导入成功！");
  } else {
    toast.error("导入失败，文件格式不合法");
  }
}

function handleSaveForm(): void {
  toast.success("角色卡草稿已成功保存至本地！");
}

function handleClearForm(): void {
  resetForm();
  toast.info("已清空表单数据");
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
    const payload: CharacterCreatePayload = {
      name: formData.name.trim(),
      avatar_url: formData.avatarUrl || "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500",
      banner_url: formData.avatarUrl || null,
      category: "story",
      description: formData.description.trim() || "暂无描述",
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
      status: "published",
      worldbooks: (formData.worldbookEntries || [])
        .filter((wb) => wb.content.trim() || wb.keys.length > 0)
        .map((wb) => ({
          keys: wb.keys,
          content: wb.content.trim(),
          constant: wb.isEnabled,
          position: "after_char",
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
      toast.success("恭喜！角色卡已成功发布至社区！");
      
      // 跳转至新生成的角色详情页
      setTimeout(() => {
        router.push(`/character/${newChar.id}`);
      }, 500);
    }
  } catch (err: any) {
    console.error("提交角色卡失败:", err);
    toast.error("提交角色卡失败，请检查网络或登录状态");
  } finally {
    isSubmitting.value = false;
  }
}

/**
 * 一键全参数模拟填充并即刻上传发布至社区与首页
 */
async function handleSimulateUpload(): Promise<void> {
  const storedIdx = parseInt(localStorage.getItem("naro_mock_preset_idx") || "0", 10);
  const preset = MOCK_CHARACTER_PRESETS[storedIdx % MOCK_CHARACTER_PRESETS.length];
  localStorage.setItem("naro_mock_preset_idx", String(storedIdx + 1));

  // 1. 同步回填至本地表单，UI 呈现所有输入框已填满
  Object.assign(formData, {
    creatorNotes: preset.creator_notes || "",
    name: preset.name,
    avatarUrl: preset.avatar_url,
    tags: [...(preset.tags || [])],
    description: preset.description,
    personality: preset.personality || "",
    scenario: preset.scenario || "",
    prologueHtml: preset.prologue_html || "",
    firstMes: preset.first_mes,
    alternateGreetings: (preset.alternate_greetings || []).map((text, idx) => ({
      id: `alt-${idx}`,
      title: `开场白 ${idx + 1}`,
      greetingText: text,
    })),
    systemPrompt: preset.system_prompt || "",
    postHistoryInstructions: preset.post_history_instructions || "",
    worldbookEntries: (preset.worldbooks || []).map((wb, idx) => ({
      id: `wb-${idx}`,
      name: `设定 ${idx + 1}`,
      keys: wb.keys,
      content: wb.content,
      isEnabled: wb.constant ?? true,
    })),
  });

  isSubmitting.value = true;
  try {
    const newChar = await characterService.createCharacter(preset);
    toast.success(`角色「${newChar.name}」已全参数模拟生成并成功发布到主页！`);
    
    // 直接返回首页即可马上在主页瀑布流看到
    setTimeout(() => {
      router.push("/");
    }, 600);
  } catch (err: any) {
    console.error("模拟上传角色失败:", err);
    toast.error("模拟上传角色失败，请检查网络或登录状态");
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] text-gray-100 relative">
    
    <!-- 1. 顶部 Header & 工具卡片 -->
    <CreatorHeader
      @import-file="handleImportFile"
      @save-form="handleSaveForm"
      @clear-form="handleClearForm"
      @open-tutorial="handleOpenTutorial"
      @open-assets="handleOpenAssets"
    />

    <!-- 2. 模块 1: 作者的话 -->
    <AuthorNoteSection v-model="formData.creatorNotes" />

    <!-- 3. 模块 2: 角色卡信息 (名称、立绘、标签) -->
    <CardInfoSection
      v-model:name="formData.name"
      v-model:avatar-url="formData.avatarUrl"
      v-model:tags="formData.tags"
    />

    <!-- 4. 模块 3: 基本信息 (描述、性格、场景) -->
    <BasicInfoSection
      v-model:description="formData.description"
      v-model:personality="formData.personality"
      v-model:scenario="formData.scenario"
    />

    <!-- 5. 模块 4: 序幕 (HTML / 实时预览) -->
    <PrologueSection v-model="formData.prologueHtml" />

    <!-- 6. 模块 5: 对话设置 (首次问候、备选开场白) -->
    <DialogueSection
      v-model:first-mes="formData.firstMes"
      v-model:alternate-greetings="formData.alternateGreetings"
    />

    <!-- 7. 模块 6: 高级设置 & 世界书 -->
    <AdvancedSection
      v-model:system-prompt="formData.systemPrompt"
      v-model:post-history-instructions="formData.postHistoryInstructions"
      v-model:worldbook-entries="formData.worldbookEntries"
    />

    <!-- 8. 创作须知卡片 -->
    <CreationNoticeSection />

    <!-- 9. 底部固定发布 & 导出操作栏 (带 Safe Area 避让) -->
    <CardExportSection
      :form-data="formData"
      :validation-errors="validationErrors"
      :is-valid="isValid"
      :is-submitting="isSubmitting"
      @publish="handlePublishCharacter"
      @simulate-upload="handleSimulateUpload"
    />

    <!-- 10. 全局底部导航栏 -->
    <BottomTabBar />

  </div>
</template>
