<template>
  <el-drawer
    v-model="visible"
    title="角色卡全景提示词与设定集档案"
    size="700px"
    destroy-on-close
    class="custom-drawer"
  >
    <div v-if="detail" v-loading="loading" class="flex flex-col gap-5">
      <!-- 1. 顶部立绘与身份卡片 -->
      <div class="relative overflow-hidden rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)]">
        <div
          v-if="detail.banner_url"
          class="h-28 w-full bg-cover bg-center opacity-60"
          :style="{ backgroundImage: `url(${detail.banner_url})` }"
        />
        <div class="p-4 flex items-start gap-4">
          <el-image
            :src="detail.avatar_url"
            fit="cover"
            class="w-20 h-20 rounded-xl shadow-md border border-[var(--el-border-color-lighter)] flex-shrink-0"
          >
            <template #error>
              <div class="w-full h-full flex items-center justify-center bg-gray-200 text-gray-500 font-bold">
                {{ detail.name.slice(0, 1) }}
              </div>
            </template>
          </el-image>

          <div class="flex flex-col flex-1 gap-1">
            <div class="flex items-center justify-between">
              <span class="text-lg font-bold text-[var(--el-text-color-primary)]">
                {{ detail.name }}
              </span>
              <el-tag
                :type="detail.status === 'published' ? 'success' : detail.status === 'banned' ? 'danger' : 'info'"
                size="small"
              >
                {{ detail.status === 'published' ? '已上架' : detail.status === 'banned' ? '已违规下架' : '私密/未上架' }}
              </el-tag>
            </div>
            <span class="text-xs text-[var(--el-text-color-secondary)]">
              创作者: {{ detail.author_name }} · 设定总字数: {{ detail.settings_word_count }} 字 · 版本: v{{ detail.version }}
            </span>
            <div class="flex flex-wrap gap-1 mt-1">
              <el-tag size="small" type="primary" effect="plain">{{ detail.category }}</el-tag>
              <el-tag
                v-for="tag in detail.tags"
                :key="tag"
                size="small"
                type="info"
                effect="plain"
              >
                #{{ tag }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 2. 数据热度与互动指标 -->
      <div class="grid grid-cols-4 gap-2">
        <div class="flex flex-col items-center p-2 rounded-lg bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)]">
          <span class="text-xs text-[var(--el-text-color-secondary)]">累计对话</span>
          <span class="text-base font-bold text-[var(--el-color-primary)] mt-1">{{ detail.chat_count }}</span>
        </div>
        <div class="flex flex-col items-center p-2 rounded-lg bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)]">
          <span class="text-xs text-[var(--el-text-color-secondary)]">点赞</span>
          <span class="text-base font-bold text-rose-500 mt-1">{{ detail.like_count }}</span>
        </div>
        <div class="flex flex-col items-center p-2 rounded-lg bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)]">
          <span class="text-xs text-[var(--el-text-color-secondary)]">收藏</span>
          <span class="text-base font-bold text-amber-500 mt-1">{{ detail.favorite_count }}</span>
        </div>
        <div class="flex flex-col items-center p-2 rounded-lg bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)]">
          <span class="text-xs text-[var(--el-text-color-secondary)]">评分</span>
          <span class="text-base font-bold text-emerald-500 mt-1">{{ detail.rating }} ★</span>
        </div>
      </div>

      <!-- 3. 核心提示词与角色剧本档案 -->
      <el-tabs type="border-card" class="rounded-xl overflow-hidden shadow-none border-[var(--el-border-color-lighter)]">
        <!-- 基础设定 -->
        <el-tab-pane label="角色描述与性格">
          <div class="flex flex-col gap-3 p-2 text-xs">
            <div>
              <span class="font-bold text-[var(--el-text-color-primary)]">故事背景简介:</span>
              <p class="mt-1 text-[var(--el-text-color-regular)] whitespace-pre-wrap leading-relaxed bg-[var(--el-fill-color-light)] p-2 rounded-lg">
                {{ detail.description || '暂无简介' }}
              </p>
            </div>
            <div>
              <span class="font-bold text-[var(--el-text-color-primary)]">性格特征 (Personality):</span>
              <p class="mt-1 text-[var(--el-text-color-regular)] whitespace-pre-wrap leading-relaxed bg-[var(--el-fill-color-light)] p-2 rounded-lg">
                {{ detail.personality || '暂无性格特征设定' }}
              </p>
            </div>
            <div>
              <span class="font-bold text-[var(--el-text-color-primary)]">时空背景情境 (Scenario):</span>
              <p class="mt-1 text-[var(--el-text-color-regular)] whitespace-pre-wrap leading-relaxed bg-[var(--el-fill-color-light)] p-2 rounded-lg">
                {{ detail.scenario || '暂无情境设定' }}
              </p>
            </div>
          </div>
        </el-tab-pane>

        <!-- System Prompt -->
        <el-tab-pane label="系统前置指令 (System Prompt)">
          <div class="p-2">
            <pre class="m-0 p-3 rounded-lg text-xs font-mono bg-zinc-900 text-zinc-100 dark:bg-black/40 overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-96">
              {{ detail.system_prompt || '未定义专属系统前置指令' }}
            </pre>
          </div>
        </el-tab-pane>

        <!-- 开场白 -->
        <el-tab-pane label="首发问候与开场白">
          <div class="flex flex-col gap-3 p-2 text-xs">
            <div>
              <span class="font-bold text-[var(--el-text-color-primary)]">默认首次开场白 (First Message):</span>
              <div class="mt-1 text-[var(--el-text-color-regular)] whitespace-pre-wrap leading-relaxed bg-[var(--el-fill-color-light)] p-3 rounded-lg border border-[var(--el-border-color-lighter)]">
                {{ detail.first_mes }}
              </div>
            </div>

            <div v-if="detail.alternate_greetings?.length">
              <span class="font-bold text-[var(--el-text-color-primary)]">
                备选开场白 ({{ detail.alternate_greetings.length }} 个):
              </span>
              <div class="flex flex-col gap-2 mt-2">
                <div
                  v-for="(alt, idx) in detail.alternate_greetings"
                  :key="idx"
                  class="p-2 rounded-lg bg-[var(--el-fill-color-light)] text-[var(--el-text-color-secondary)]"
                >
                  <span class="font-semibold text-amber-500 mr-1">#{{ idx + 1 }}</span>
                  {{ alt }}
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- 世界书词条 -->
        <el-tab-pane :label="`设定集/世界书词条 (${detail.worldbook_entries?.length || 0})`">
          <div v-if="!detail.worldbook_entries?.length" class="p-6 text-center text-xs text-[var(--el-text-color-placeholder)]">
            该角色卡未绑定世界书扩展条目
          </div>
          <div v-else class="flex flex-col gap-3 p-2">
            <div
              v-for="entry in detail.worldbook_entries"
              :key="entry.id"
              class="p-3 rounded-lg border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)] flex flex-col gap-2 text-xs"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-1 flex-wrap">
                  <span class="font-semibold text-[var(--el-text-color-primary)]">触发词:</span>
                  <el-tag
                    v-for="k in entry.keys"
                    :key="k"
                    size="small"
                    type="warning"
                    effect="light"
                  >
                    {{ k }}
                  </el-tag>
                </div>
                <div class="flex items-center gap-2">
                  <el-tag v-if="entry.constant" size="small" type="danger">常驻注入</el-tag>
                  <el-tag size="small" type="info" effect="plain">位置: {{ entry.position }}</el-tag>
                </div>
              </div>
              <p class="m-0 text-[var(--el-text-color-regular)] leading-relaxed whitespace-pre-wrap">
                {{ entry.content }}
              </p>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>

      <!-- 底部审核操作按钮 -->
      <div class="flex justify-end gap-3 pt-2">
        <el-button @click="visible = false">关闭</el-button>
        <el-button type="primary" @click="handleOpenAudit">
          审核 / 上下架处置
        </el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import {
  type IAdminCharacterDetail,
  type IAdminCharacterItem,
  getCharacterDetail,
} from '@/api/character';
import { ElMessage } from 'element-plus';
import { ref } from 'vue';

const emit = defineEmits<(e: 'audit', char: IAdminCharacterItem) => void>();

const visible = ref(false);
const loading = ref(false);
const detail = ref<IAdminCharacterDetail | null>(null);

async function open(char: IAdminCharacterItem) {
  visible.value = true;
  loading.value = true;
  try {
    const res = await getCharacterDetail(char.id);
    detail.value = res;
  } catch (error: any) {
    ElMessage.error(error?.message || '获取角色卡档案详情失败');
    visible.value = false;
  } finally {
    loading.value = false;
  }
}

function handleOpenAudit() {
  if (detail.value) {
    emit('audit', detail.value);
  }
}

defineExpose({
  open,
});
</script>
