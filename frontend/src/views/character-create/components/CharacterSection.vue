<script setup lang="ts">
/**
 * 分节 2: 【角色】组件 (AI 模型看到的设定)
 *
 * 涵盖详细描述、性格、背景情境、角色定义前插桩、世界书 V2/V3 卡片管理与前/后置提示词。
 *
 * @packageDocumentation
 */

import { AppButton, AppModal } from "@/components/common";
import { useToast } from "@/composables/useToast";
import {
  AlertTriangle,
  ArrowDown,
  ArrowUp,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Download,
  FileCode,
  Plus,
  Trash2,
  Upload,
} from "lucide-vue-next";
import { ref } from "vue";
import type { DisplayMode, WorldbookEntryItem } from "../types";

const props = defineProps<{
  /** 详细描述 */
  description: string;
  /** 性格特征 */
  personality: string;
  /** 场景背景 */
  scenario: string;
  /** 角色定义前插桩 (before_char) */
  beforeChar: string;
  /** 世界书版本 (v2 | v3) */
  worldbookVersion: "v2" | "v3";
  /** 世界书条目列表 */
  worldbookEntries: WorldbookEntryItem[];
  /** 系统前置提示词 */
  systemPrompt: string;
  /** 历史后置指令 */
  postHistoryInstructions: string;
  /** 当前显示模式 */
  displayMode: DisplayMode;
}>();

const emit = defineEmits<{
  (e: "update:description", val: string): void;
  (e: "update:personality", val: string): void;
  (e: "update:scenario", val: string): void;
  (e: "update:beforeChar", val: string): void;
  (e: "update:worldbookVersion", val: "v2" | "v3"): void;
  (e: "update:worldbookEntries", val: WorldbookEntryItem[]): void;
  (e: "update:systemPrompt", val: string): void;
  (e: "update:postHistoryInstructions", val: string): void;
}>();

const toast = useToast();
const worldbookFileInputRef = ref<HTMLInputElement | null>(null);

// 展开的条目 ID 集合
const expandedEntryIds = ref<Set<string>>(new Set());

// 删除二次确认状态
const isDeleteModalOpen = ref<boolean>(false);
const deleteTarget = ref<{ idx: number; name: string } | null>(null);

function toggleEntryExpand(id: string): void {
  if (expandedEntryIds.value.has(id)) {
    expandedEntryIds.value.delete(id);
  } else {
    expandedEntryIds.value.add(id);
  }
}

/**
 * 在列表最前面新增世界书条目
 */
function handleAddWorldbookEntry(): void {
  const nextList = [...props.worldbookEntries];
  const newId = `wb-${Date.now()}`;
  nextList.unshift({
    id: newId,
    name: `设定 ${nextList.length + 1}`,
    keys: [],
    secondaryKeys: [],
    content: "",
    isEnabled: true,
    position: "after_char",
  });
  emit("update:worldbookEntries", nextList);
  expandedEntryIds.value.add(newId);
  toast.success("已在最前面添加新设定");
}

/**
 * 触发删除二次确认
 */
function handleRequestDelete(idx: number): void {
  const entry = props.worldbookEntries[idx];
  if (!entry) return;
  deleteTarget.value = {
    idx,
    name: entry.name || `设定 ${idx + 1}`,
  };
  isDeleteModalOpen.value = true;
}

/**
 * 确认删除条目
 */
function handleConfirmDelete(): void {
  if (deleteTarget.value !== null) {
    const { idx, name } = deleteTarget.value;
    const nextList = props.worldbookEntries.filter((_, i) => i !== idx);
    emit("update:worldbookEntries", nextList);
    toast.success(`已删除设定「${name}」`);
    deleteTarget.value = null;
    isDeleteModalOpen.value = false;
  }
}

/**
 * 切换条目启用/停用状态
 */
function handleToggleEnabled(idx: number): void {
  const nextList = [...props.worldbookEntries];
  if (nextList[idx]) {
    const nextState = !(nextList[idx].isEnabled !== false);
    nextList[idx] = { ...nextList[idx], isEnabled: nextState };
    emit("update:worldbookEntries", nextList);
    if (nextState) {
      toast.success(`已启用「${nextList[idx].name || "设定"}」`);
    } else {
      toast.info(`已停用「${nextList[idx].name || "设定"}」`);
    }
  }
}

/**
 * 条目上移排序
 */
function handleMoveUp(idx: number): void {
  if (idx <= 0) return;
  const nextList = [...props.worldbookEntries];
  const item = nextList[idx];
  nextList[idx] = nextList[idx - 1];
  nextList[idx - 1] = item;
  emit("update:worldbookEntries", nextList);
}

/**
 * 条目下移排序
 */
function handleMoveDown(idx: number): void {
  if (idx >= props.worldbookEntries.length - 1) return;
  const nextList = [...props.worldbookEntries];
  const item = nextList[idx];
  nextList[idx] = nextList[idx + 1];
  nextList[idx + 1] = item;
  emit("update:worldbookEntries", nextList);
}

function handleUpdateEntry(idx: number, patch: Partial<WorldbookEntryItem>): void {
  const nextList = [...props.worldbookEntries];
  if (nextList[idx]) {
    nextList[idx] = { ...nextList[idx], ...patch };
    emit("update:worldbookEntries", nextList);
  }
}

function triggerImportWorldbook(): void {
  worldbookFileInputRef.value?.click();
}

function handleWorldbookFileChange(event: Event): void {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const text = e.target?.result as string;
      const parsed = JSON.parse(text);
      const entries = parsed.entries || parsed.character_book?.entries || [];
      if (!Array.isArray(entries)) {
        toast.error("未识别到有效的世界书条目数据");
        return;
      }
      const imported: WorldbookEntryItem[] = entries.map((item: any, i: number) => ({
        id: `wb-${Date.now()}-${i}`,
        name: item.comment || item.name || `导入设定 ${i + 1}`,
        keys: Array.isArray(item.keys)
          ? item.keys
          : typeof item.keys === "string"
            ? item.keys.split(",")
            : [],
        secondaryKeys: Array.isArray(item.secondary_keys) ? item.secondary_keys : [],
        content: item.content || "",
        isEnabled: item.enabled ?? true,
        position: item.position || "after_char",
      }));
      emit("update:worldbookEntries", [...props.worldbookEntries, ...imported]);
      toast.success(`成功导入 ${imported.length} 条世界书设定！`);
    } catch (err) {
      console.error("解析世界书文件失败:", err);
      toast.error("导入世界书失败，请检查 JSON 格式");
    } finally {
      target.value = "";
    }
  };
  reader.readAsText(file);
}

function handleExportWorldbook(): void {
  if (props.worldbookEntries.length === 0) {
    toast.info("当前暂无世界书条目可导出");
    return;
  }
  const payload = {
    name: "Worldbook Export",
    entries: props.worldbookEntries.map((wb, idx) => ({
      id: idx + 1,
      keys: wb.keys,
      secondary_keys: wb.secondaryKeys || [],
      content: wb.content,
      enabled: wb.isEnabled,
      insertion_order: idx,
      comment: wb.name,
      position: wb.position || "after_char",
    })),
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `worldbook_v3_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  toast.success("世界书已成功导出为 JSON！");
}
</script>

<template>
  <section id="section-character" class="w-full px-3 pb-4 flex flex-col gap-4">
    <!-- 隐藏的世界书导入 input -->
    <input
      ref="worldbookFileInputRef"
      type="file"
      accept=".json"
      class="hidden"
      @change="handleWorldbookFileChange"
    />

    <!-- 分节大标题: 角色 (AI 模型看到的设定) -->
    <div class="flex items-center justify-between pt-1">
      <div class="flex items-center gap-2.5">
        <div class="w-1 h-5 rounded-full bg-[#38BDF8] shadow-[0_0_10px_rgba(56,189,248,0.5)]" />
        <h2 class="text-base font-bold text-gray-100 tracking-wide select-none">
          角色
        </h2>
        <span class="text-xs text-[#78716C] font-normal">
          AI 模型看到的设定
        </span>
      </div>
    </div>

    <!-- 1. 基本信息卡片 -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      <h3 class="text-xs font-semibold text-gray-200">
        基本信息
      </h3>

      <!-- 详细描述 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs text-[#A8A29E]">详细描述 (设定正文)</label>
        <textarea
          :value="description"
          @input="emit('update:description', ($event.target as HTMLTextAreaElement).value)"
          rows="4"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#38BDF8] transition-colors resize-none leading-relaxed"
          placeholder="详细描写角色的外貌、身世经历、关键动机与核心人设..."
        />
      </div>

      <!-- 性格特征 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs text-[#A8A29E]">性格特征</label>
        <textarea
          :value="personality"
          @input="emit('update:personality', ($event.target as HTMLTextAreaElement).value)"
          rows="2"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#38BDF8] transition-colors resize-none leading-relaxed"
          placeholder="例如: 傲娇、高冷但内心温柔、面对背叛时极为决绝..."
        />
      </div>

      <!-- 背景场景 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs text-[#A8A29E]">背景场景 (世界观时空)</label>
        <textarea
          :value="scenario"
          @input="emit('update:scenario', ($event.target as HTMLTextAreaElement).value)"
          rows="2"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs text-gray-100 placeholder-[#78716C] focus:border-[#38BDF8] transition-colors resize-none leading-relaxed"
          placeholder="例如: 忍界大战前夕的阴雨木叶村；或末世废土被风雪封锁的庇护所..."
        />
      </div>

      <!-- 角色定义前 (before_char) - 仅在完整模式下呈现 -->
      <div v-if="displayMode === 'full'" class="flex flex-col gap-1.5 pt-1 border-t border-[#44403C]/40">
        <div class="flex items-center justify-between">
          <label class="text-xs text-[#A8A29E]">
            角色定义前 (Before Character 提示词锚点)
          </label>
          <span class="text-[10px] text-[#F9C86D]">SillyTavern 核心插桩</span>
        </div>
        <textarea
          :value="beforeChar"
          @input="emit('update:beforeChar', ($event.target as HTMLTextAreaElement).value)"
          rows="2"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs font-mono text-gray-100 placeholder-[#78716C] focus:border-[#38BDF8] transition-colors resize-none leading-relaxed"
          placeholder="注入在主角色人设之前的核心全局规则（如玩家自主权、沉郁江湖文风限制）..."
        />
      </div>
    </div>

    <!-- 2. 世界书设定卡片 (仅完整模式呈现全量控制) -->
    <div v-if="displayMode === 'full'" class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <BookOpen class="w-4 h-4 text-[#F9C86D]" />
          <h3 class="text-xs font-semibold text-gray-200">
            世界书设定
          </h3>
        </div>

        <!-- 旧版 vs 新版 v3 胶囊切换 -->
        <div class="flex items-center p-0.5 rounded-full bg-black/50 border border-[#44403C]/50 text-[10px]">
          <button
            type="button"
            @click="emit('update:worldbookVersion', 'v2')"
            :class="[
              'px-2 py-0.5 rounded-full transition-colors cursor-pointer',
              worldbookVersion === 'v2' ? 'bg-stone-700 text-white font-medium' : 'text-stone-400'
            ]"
          >
            旧版
          </button>
          <button
            type="button"
            @click="emit('update:worldbookVersion', 'v3')"
            :class="[
              'px-2 py-0.5 rounded-full transition-colors cursor-pointer',
              worldbookVersion === 'v3' ? 'bg-[#F9C86D] text-black font-semibold shadow' : 'text-stone-400'
            ]"
          >
            ✨ 新版 v3
          </button>
        </div>
      </div>

      <!-- 快捷工具按钮组: 导入 / 导出 / 添加 -->
      <div class="flex items-center justify-between pt-1">
        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="triggerImportWorldbook"
            class="flex items-center gap-1 px-2 py-1 rounded bg-stone-800/80 hover:bg-stone-700 border border-stone-700 text-[11px] text-stone-300 transition-colors cursor-pointer select-none"
          >
            <Upload class="w-3 h-3" />
            <span>导入世界书</span>
          </button>
          <button
            type="button"
            @click="handleExportWorldbook"
            class="flex items-center gap-1 px-2 py-1 rounded bg-stone-800/80 hover:bg-stone-700 border border-stone-700 text-[11px] text-stone-300 transition-colors cursor-pointer select-none"
          >
            <Download class="w-3 h-3" />
            <span>导出世界书</span>
          </button>
        </div>

        <button
          type="button"
          @click="handleAddWorldbookEntry"
          class="flex items-center gap-1 text-xs text-[#F9C86D] hover:underline cursor-pointer select-none font-medium"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>+ 添加设定</span>
        </button>
      </div>

      <!-- 条目列表 (Card List) -->
      <div v-if="worldbookEntries.length > 0" class="flex flex-col gap-2.5 pt-1">
        <div
          v-for="(wb, idx) in worldbookEntries"
          :key="wb.id"
          :class="[
            'p-3 rounded-lg border flex flex-col gap-2 transition-all shadow',
            wb.isEnabled !== false
              ? 'border-[#44403C]/80 bg-[#1F1C18]/90'
              : 'border-[#332F2B]/60 bg-[#171513]/70 opacity-70'
          ]"
        >
          <!-- 卡片头部: 序号、标题、排序、启停开关、删除与展开 -->
          <div class="flex items-center justify-between gap-2">
            <!-- 左侧: 序号与标题编辑 -->
            <div
              @click="toggleEntryExpand(wb.id)"
              class="flex items-center gap-1.5 cursor-pointer select-none flex-1 min-w-0"
            >
              <span class="text-[10px] font-mono text-[#F9C86D]/80 bg-[#F9C86D]/10 px-1.5 py-0.5 rounded border border-[#F9C86D]/20 shrink-0">
                #{{ idx + 1 }}
              </span>
              <FileCode class="w-3.5 h-3.5 text-[#F9C86D] shrink-0" />
              <input
                :value="wb.name"
                @click.stop
                @input="handleUpdateEntry(idx, { name: ($event.target as HTMLInputElement).value })"
                type="text"
                class="bg-transparent border-b border-transparent hover:border-stone-600 focus:border-[#F9C86D] text-xs font-semibold text-gray-200 outline-none px-1 flex-1 min-w-0"
                placeholder="设定名称"
              />
            </div>

            <!-- 右侧: 排序按钮组、启停胶囊、删除二次确认与展开折叠 -->
            <div class="flex items-center gap-1 shrink-0">
              <!-- 上移 / 下移 排序按钮 -->
              <div class="flex items-center bg-black/40 rounded border border-stone-800 p-0.5 mr-0.5">
                <button
                  type="button"
                  @click.stop="handleMoveUp(idx)"
                  :disabled="idx === 0"
                  :class="[
                    'p-1 rounded transition-colors',
                    idx === 0
                      ? 'text-stone-700 cursor-not-allowed'
                      : 'text-stone-400 hover:text-[#F9C86D] hover:bg-stone-800/80 cursor-pointer'
                  ]"
                  title="上移"
                >
                  <ArrowUp class="w-3 h-3" />
                </button>
                <button
                  type="button"
                  @click.stop="handleMoveDown(idx)"
                  :disabled="idx === worldbookEntries.length - 1"
                  :class="[
                    'p-1 rounded transition-colors',
                    idx === worldbookEntries.length - 1
                      ? 'text-stone-700 cursor-not-allowed'
                      : 'text-stone-400 hover:text-[#F9C86D] hover:bg-stone-800/80 cursor-pointer'
                  ]"
                  title="下移"
                >
                  <ArrowDown class="w-3 h-3" />
                </button>
              </div>

              <!-- 启用 / 停用 切换胶囊 -->
              <button
                type="button"
                @click.stop="handleToggleEnabled(idx)"
                :class="[
                  'flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-medium transition-all cursor-pointer border select-none',
                  wb.isEnabled !== false
                    ? 'bg-[#F9C86D]/15 text-[#F9C86D] border-[#F9C86D]/40 hover:bg-[#F9C86D]/25 shadow-[0_0_8px_rgba(249,200,109,0.15)]'
                    : 'bg-stone-900/90 text-stone-500 border-stone-800 hover:border-stone-700 hover:text-stone-400'
                ]"
                :title="wb.isEnabled !== false ? '点击停用' : '点击启用'"
              >
                <span
                  class="w-1.5 h-1.5 rounded-full transition-all"
                  :class="wb.isEnabled !== false ? 'bg-[#F9C86D] shadow-[0_0_4px_#F9C86D]' : 'bg-stone-600'"
                />
                <span>{{ wb.isEnabled !== false ? "启用" : "停用" }}</span>
              </button>

              <!-- 删除按钮 (带二次确认) -->
              <button
                type="button"
                @click.stop="handleRequestDelete(idx)"
                class="text-stone-400 hover:text-red-400 p-1 rounded hover:bg-red-950/30 transition-colors cursor-pointer"
                title="删除设定"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>

              <!-- 展开 / 折叠 -->
              <button
                type="button"
                @click.stop="toggleEntryExpand(wb.id)"
                class="text-stone-400 hover:text-white p-1 rounded hover:bg-stone-800/60 transition-colors cursor-pointer"
                title="展开/收起"
              >
                <ChevronUp v-if="expandedEntryIds.has(wb.id)" class="w-3.5 h-3.5" />
                <ChevronDown v-else class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <!-- 折叠内容: 触发词与正文 -->
          <div v-if="expandedEntryIds.has(wb.id)" class="flex flex-col gap-2 pt-1.5 border-t border-stone-800">
            <!-- 主要关键词 -->
            <div class="flex flex-col gap-1">
              <label class="text-[10px] text-stone-400">触发关键词 (逗号分隔)</label>
              <input
                :value="wb.keys.join(', ')"
                @input="handleUpdateEntry(idx, { keys: ($event.target as HTMLInputElement).value.split(/[,，\s]+/).filter(Boolean) })"
                type="text"
                placeholder="例如: 查克拉, 雷遁, 咒印"
                class="w-full px-2.5 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D]"
              />
            </div>

            <!-- V3 次要关键词 (Secondary Keys) -->
            <div v-if="worldbookVersion === 'v3'" class="flex flex-col gap-1">
              <label class="text-[10px] text-stone-400">次要关键词 (逻辑与联合触发)</label>
              <input
                :value="(wb.secondaryKeys || []).join(', ')"
                @input="handleUpdateEntry(idx, { secondaryKeys: ($event.target as HTMLInputElement).value.split(/[,，\s]+/).filter(Boolean) })"
                type="text"
                placeholder="例如: 战斗, 爆发"
                class="w-full px-2.5 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D]"
              />
            </div>

            <!-- 设定正文 -->
            <div class="flex flex-col gap-1">
              <label class="text-[10px] text-stone-400">设定正文</label>
              <textarea
                :value="wb.content"
                @input="handleUpdateEntry(idx, { content: ($event.target as HTMLTextAreaElement).value })"
                rows="3"
                placeholder="详细说明此设定词条在命中时的背景定义..."
                class="w-full p-2.5 rounded bg-black/40 border border-[#44403C] text-xs text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D] resize-none leading-relaxed font-sans"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-3 text-xs text-[#78716C]">
        暂无世界书设定条目，点击“+ 添加设定”可扩展专有名词与规则。
      </div>
    </div>

    <!-- 3. 高级提示词折叠卡片 (仅完整模式) -->
    <div v-if="displayMode === 'full'" class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <h3 class="text-xs font-semibold text-gray-200">
        系统提示词与历史指令
      </h3>

      <!-- 前置 System Prompt -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs text-[#A8A29E]">前置 System Prompt</label>
        <textarea
          :value="systemPrompt"
          @input="emit('update:systemPrompt', ($event.target as HTMLTextAreaElement).value)"
          rows="2"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs font-mono text-gray-100 placeholder-[#78716C] focus:border-[#38BDF8] transition-colors resize-none leading-relaxed"
          placeholder="覆盖全局系统指令的前置提示词..."
        />
      </div>

      <!-- 历史后置指令 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs text-[#A8A29E]">历史指令 Post-History Instructions</label>
        <textarea
          :value="postHistoryInstructions"
          @input="emit('update:postHistoryInstructions', ($event.target as HTMLTextAreaElement).value)"
          rows="2"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-xs font-mono text-gray-100 placeholder-[#78716C] focus:border-[#38BDF8] transition-colors resize-none leading-relaxed"
          placeholder="注入在对话历史末尾用于强化人设或防出戏的指令..."
        />
      </div>
    </div>

    <!-- 删除世界书条目二次确认弹窗 (符合零原生弹窗规范) -->
    <AppModal
      :open="isDeleteModalOpen"
      title="删除世界书设定"
      size="sm"
      @update:open="isDeleteModalOpen = $event"
    >
      <div class="flex items-center gap-3 p-3.5 rounded-xl border border-red-500/20 bg-red-950/20 text-red-300">
        <AlertTriangle class="w-5 h-5 text-red-400 shrink-0" />
        <div class="text-xs leading-relaxed">
          确定要删除设定 <span class="font-bold text-red-200">「{{ deleteTarget?.name }}」</span> 吗？此操作无法撤销。
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2 w-full">
          <AppButton
            variant="ghost"
            size="sm"
            @click="isDeleteModalOpen = false"
          >
            取消
          </AppButton>
          <AppButton
            variant="danger"
            size="sm"
            @click="handleConfirmDelete"
          >
            确认删除
          </AppButton>
        </div>
      </template>
    </AppModal>
  </section>
</template>
