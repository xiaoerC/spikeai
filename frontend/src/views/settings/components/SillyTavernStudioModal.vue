<script setup lang="ts">
/**
 * SillyTavern (酒馆) 1:1 像素复刻生成设置与提示词编排控制台 (内部测试版 V5)。
 *
 * 核心升级:
 * 1. 支持用户自定义预设另存为 (Save As) 与预设库列表管理 (CRUD)；
 * 2. 宏变量引擎与叙梦 38 变量打通；
 * 3. Mod 多锚点流水线无缝融合；
 * 4. 高对比度黑金滑块与 100% 可靠自绘复选框。
 *
 * @packageDocumentation
 */

import AppButton from "@/components/common/AppButton.vue";
import { useToast } from "@/composables/useToast";
import { TavernApi, type TavernPresetConfig, type TavernPromptItem } from "@/services/tavern";
import {
  BUILTIN_PRESETS,
  DEFAULT_HAMSTER_GOD_PRESET,
} from "@/views/settings/constants/hamsterGodPreset";
import { computed, ref, watch } from "vue";

const props = defineProps<{
  modelValue: boolean;
}>();

const emit = defineEmits<(e: "update:modelValue", val: boolean) => void>();

const { showToast } = useToast();

// 1. 当前活动 Tab: "generation" (生成设置) | "prompts" (提示词排版)
const activeTab = ref<"generation" | "prompts">("prompts");

// 2. 当前预设配置状态与预设库列表
const preset = ref<TavernPresetConfig>(JSON.parse(JSON.stringify(DEFAULT_HAMSTER_GOD_PRESET)));
const presetList = ref<{ preset_name: string; is_builtin: boolean }[]>([]);
const isLoading = ref(false);
const isSaving = ref(false);

// 3. 搜索与过滤
const searchQuery = ref("");
const filterType = ref<"all" | "active" | "marker">("all");

// 4. 正在编辑的提示词弹窗
const isEditModalOpen = ref(false);
const editingPrompt = ref<TavernPromptItem | null>(null);
const isTriggerDropdownOpen = ref(false);

// 5. 另存为新预设弹窗
const isSaveAsModalOpen = ref(false);
const saveAsPresetName = ref("");

// 触发器选项清单
const triggerOptions = [
  { id: "normal", label: "正常" },
  { id: "continue", label: "续写" },
  { id: "impersonate", label: "AI 帮答" },
  { id: "swipe", label: "备选回复" },
  { id: "regenerate", label: "重新生成" },
  { id: "quiet", label: "静默" },
];

// 建立全量提示词查找表
const promptMap = computed(() => {
  const map = new Map<string, TavernPromptItem>();
  for (const p of DEFAULT_HAMSTER_GOD_PRESET.prompts) {
    map.set(p.identifier, p);
  }
  for (const p of preset.value.prompts) {
    map.set(p.identifier, p);
  }
  return map;
});

// 动态计算提示词条目按流水线先后顺序排列的列表 (全量 78 项)
const orderedPromptList = computed(() => {
  const map = promptMap.value;
  const result: {
    index: number;
    identifier: string;
    enabled: boolean;
    name: string;
    role: string;
    content: string;
    isMarker: boolean;
    isUserRole: boolean;
    forbidOverrides: boolean;
    prompt?: TavernPromptItem;
  }[] = [];

  const sourceOrder =
    preset.value.prompt_order && preset.value.prompt_order.length >= 70
      ? preset.value.prompt_order
      : DEFAULT_HAMSTER_GOD_PRESET.prompt_order;

  sourceOrder.forEach((item, idx) => {
    const p = map.get(item.identifier);
    const rawName = p?.name?.trim();
    const name = rawName && rawName.length > 0 ? rawName : getFallbackName(item.identifier);
    const role = p?.role || "system";
    const isMarker = Boolean(p?.marker || isKnownMarker(item.identifier));
    const isUserRole = role === "user";

    result.push({
      index: idx,
      identifier: item.identifier,
      enabled: item.enabled,
      name,
      role,
      content: p?.content || "",
      isMarker,
      isUserRole,
      forbidOverrides: Boolean(p?.forbid_overrides),
      prompt: p,
    });
  });

  return result;
});

// 过滤后的列表
const filteredPromptList = computed(() => {
  const list = orderedPromptList.value;
  const query = searchQuery.value.trim().toLowerCase();

  return list.filter((item) => {
    if (filterType.value === "active" && !item.enabled) return false;
    if (filterType.value === "marker" && !item.isMarker) return false;

    if (query) {
      return item.name.toLowerCase().includes(query) || item.content.toLowerCase().includes(query);
    }
    return true;
  });
});

// 统计有效 Token 与启用条目数
const activeCount = computed(() => {
  return orderedPromptList.value.filter((o) => o.enabled).length;
});

const totalTokensEstimate = computed(() => {
  let totalChars = 0;
  for (const o of orderedPromptList.value) {
    if (o.enabled && o.content) {
      totalChars += o.content.length;
    }
  }
  return Math.round(totalChars * 0.7);
});

// 判断是否为已知内置插桩锚点
function isKnownMarker(ident: string): boolean {
  const idLower = ident.toLowerCase();
  return (
    idLower.includes("personadescription") ||
    idLower.includes("chardescription") ||
    idLower.includes("charpersonality") ||
    idLower.includes("worldinfobefore") ||
    idLower.includes("worldinfoafter") ||
    idLower.includes("scenario") ||
    idLower.includes("dialogueexamples") ||
    idLower.includes("chathistory")
  );
}

// 友好备选条目名
function getFallbackName(ident: string): string {
  if (ident === "personaDescription") return "Persona Description";
  if (ident === "charDescription") return "Char Description";
  if (ident === "charPersonality") return "Char Personality";
  if (ident === "worldInfoBefore") return "World Info (before)";
  if (ident === "worldInfoAfter") return "World Info (after)";
  if (ident === "scenario") return "Scenario";
  if (ident === "dialogueExamples") return "Chat Examples";
  if (ident === "chatHistory") return "Chat History";
  return "自定义提示词块";
}

// 图标匹配
function getItemIcon(item: { name: string; isMarker: boolean; isUserRole: boolean }): string {
  if (item.isMarker) return "📌";
  const n = item.name;
  if (
    n.startsWith("⭐") ||
    n.startsWith("🛡️") ||
    n.startsWith("📘") ||
    n.startsWith("✅") ||
    n.startsWith("🖋️") ||
    n.startsWith("🧭") ||
    n.startsWith("⚙️") ||
    n.startsWith("🧊") ||
    n.startsWith("➡️") ||
    n.startsWith("📙") ||
    n.startsWith("🔖") ||
    n.startsWith("🎭") ||
    n.startsWith("❄️")
  ) {
    return "";
  }
  return "❄️";
}

// 加载当前用户预设与预设列表
async function loadUserPreset() {
  isLoading.value = true;
  try {
    const [data, presets] = await Promise.all([
      TavernApi.getPreset(),
      TavernApi.listPresets().catch(() => []),
    ]);

    if (presets && presets.length > 0) {
      presetList.value = presets;
    } else {
      presetList.value = [
        { preset_name: "仓鼠之神V2", is_builtin: true },
        { preset_name: "文学沉浸创作版", is_builtin: true },
        { preset_name: "高自由度脑洞版", is_builtin: true },
      ];
    }

    if (data && data.prompts && data.prompts.length >= 100) {
      preset.value = data;
    } else {
      preset.value = JSON.parse(JSON.stringify(DEFAULT_HAMSTER_GOD_PRESET));
      await TavernApi.updatePreset(preset.value);
    }
  } catch (err) {
    console.warn("读取服务端预设异常，加载全量本地仓鼠之神V2", err);
    preset.value = JSON.parse(JSON.stringify(DEFAULT_HAMSTER_GOD_PRESET));
  } finally {
    isLoading.value = false;
  }
}

// 切换对话补全预设 (真实切换整套参数与提示词排版)
function onPresetChange(newPresetName: string) {
  const target = BUILTIN_PRESETS[newPresetName];
  if (target) {
    const currentActive = preset.value.is_active;
    preset.value = JSON.parse(JSON.stringify(target));
    preset.value.is_active = currentActive;
    showToast({
      type: "success",
      message: `已切换至「${newPresetName}」，提示词与生成设置已同步！`,
    });
  } else {
    preset.value.preset_name = newPresetName;
  }
}

// 打开另存为新预设弹窗
function openSaveAsModal() {
  saveAsPresetName.value = `${preset.value.preset_name} (副本)`;
  isSaveAsModalOpen.value = true;
}

// 执行另存为新预设
async function handleConfirmSaveAs() {
  const name = saveAsPresetName.value.trim();
  if (!name) {
    showToast({ type: "error", message: "请输入有效的预设名称" });
    return;
  }
  isSaving.value = true;
  try {
    const clone = JSON.parse(JSON.stringify(preset.value));
    clone.preset_name = name;
    await TavernApi.saveNamedPreset(clone);
    preset.value = clone;
    isSaveAsModalOpen.value = false;
    await loadUserPreset();
    showToast({ type: "success", message: `已另存为新预设「${name}」并设为当前生效！` });
  } catch (err) {
    console.error("另存为预设失败:", err);
    showToast({ type: "error", message: "另存预设失败，请稍后重试" });
  } finally {
    isSaving.value = false;
  }
}

// 删除自定义预设
async function handleDeleteCustomPreset(name: string) {
  if (!confirm(`确定要删除自定义预设「${name}」吗？`)) return;
  try {
    await TavernApi.deleteNamedPreset(name);
    showToast({ type: "success", message: `已删除预设「${name}」` });
    await loadUserPreset();
    if (preset.value.preset_name === name) {
      onPresetChange("仓鼠之神V2");
    }
  } catch (err) {
    console.error("删除预设失败:", err);
    showToast({ type: "error", message: "删除失败" });
  }
}

// 切换单项条目开关
function toggleItem(identifier: string) {
  const orderTarget = preset.value.prompt_order.find((o) => o.identifier === identifier);
  if (orderTarget) {
    orderTarget.enabled = !orderTarget.enabled;
  }
  const promptTarget = preset.value.prompts.find((p) => p.identifier === identifier);
  if (promptTarget) {
    promptTarget.enabled = !promptTarget.enabled;
  }
}

// 调整提示词位置：上移
function moveUp(index: number) {
  if (index <= 0) return;
  const list = [...preset.value.prompt_order];
  const temp = list[index];
  list[index] = list[index - 1];
  list[index - 1] = temp;
  preset.value.prompt_order = list;
}

// 调整提示词位置：下移
function moveDown(index: number) {
  if (index >= preset.value.prompt_order.length - 1) return;
  const list = [...preset.value.prompt_order];
  const temp = list[index];
  list[index] = list[index + 1];
  list[index + 1] = temp;
  preset.value.prompt_order = list;
}

// 打开条目详情编辑
function openEditModal(prompt?: TavernPromptItem, fallbackName?: string) {
  isTriggerDropdownOpen.value = false;
  if (prompt) {
    const clone = JSON.parse(JSON.stringify(prompt));
    if (clone.injection_position === undefined) clone.injection_position = 0;
    if (clone.injection_depth === undefined) clone.injection_depth = 4;
    if (clone.forbid_overrides === undefined) clone.forbid_overrides = false;
    if (!clone.injection_trigger) clone.injection_trigger = [];
    editingPrompt.value = clone;
  } else {
    editingPrompt.value = {
      identifier: "custom-" + Date.now(),
      name: fallbackName || "自定义条目",
      role: "system",
      content: "",
      system_prompt: true,
      enabled: true,
      injection_position: 0,
      injection_depth: 4,
      forbid_overrides: false,
      injection_trigger: [],
    };
  }
  isEditModalOpen.value = true;
}

// 切换触发器勾选项
function toggleTrigger(triggerId: string) {
  if (!editingPrompt.value) return;
  if (!editingPrompt.value.injection_trigger) {
    editingPrompt.value.injection_trigger = [];
  }
  const arr = editingPrompt.value.injection_trigger;
  const idx = arr.indexOf(triggerId);
  if (idx > -1) {
    arr.splice(idx, 1);
  } else {
    arr.push(triggerId);
  }
}

// 保存单个条目修改
function saveEditingPrompt() {
  if (!editingPrompt.value) return;
  const idx = preset.value.prompts.findIndex(
    (p) => p.identifier === editingPrompt.value!.identifier,
  );
  if (idx !== -1) {
    preset.value.prompts[idx] = JSON.parse(JSON.stringify(editingPrompt.value));
  } else {
    preset.value.prompts.push(JSON.parse(JSON.stringify(editingPrompt.value)));
  }
  isEditModalOpen.value = false;
  showToast({ type: "success", message: `已保存「${editingPrompt.value.name}」` });
}

// 保存预设到服务端并全局生效
async function handleSavePreset() {
  isSaving.value = true;
  try {
    await TavernApi.updatePreset(preset.value);
    showToast({ type: "success", message: "酒馆调音台预设已成功保存并在聊天中全局生效！" });
    emit("update:modelValue", false);
  } catch (err) {
    console.error("保存预设失败:", err);
    showToast({ type: "error", message: "保存失败，请检查网络或后端服务" });
  } finally {
    isSaving.value = false;
  }
}

// 一键恢复官方原版全量 78 项预设
async function handleResetDefault() {
  if (!confirm("确定要恢复为官方原版「仓鼠之神V2」(全量 78 项排版流水线) 吗？")) return;
  isLoading.value = true;
  try {
    const fresh = await TavernApi.resetPreset();
    preset.value = fresh;
    showToast({ type: "success", message: "已恢复官方原版「仓鼠之神V2」(全量 78 项)" });
  } catch (_) {
    preset.value = JSON.parse(JSON.stringify(DEFAULT_HAMSTER_GOD_PRESET));
    showToast({ type: "success", message: "已恢复本地全量默认预设" });
  } finally {
    isLoading.value = false;
  }
}

// 导出 JSON
function exportPresetJson() {
  const jsonStr = JSON.stringify(preset.value, null, 2);
  const blob = new Blob([jsonStr], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `SillyTavern_${preset.value.preset_name || "Preset"}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
  showToast({ type: "success", message: "预设 JSON 已导出" });
}

watch(
  () => props.modelValue,
  (val) => {
    if (val) {
      loadUserPreset();
    }
  },
  { immediate: true },
);
</script>

<template>
  <Teleport to="body">
    <div
      v-if="modelValue"
      class="fixed inset-0 z-[100] flex items-center justify-center p-2 sm:p-4"
    >
      <!-- 背景遮罩 -->
      <div
        class="absolute inset-0 bg-black/85 backdrop-blur-md transition-opacity"
        @click="emit('update:modelValue', false)"
      />

      <!-- 弹窗主体 -->
      <div
        class="relative w-full max-w-[620px] h-[92vh] max-h-[880px] flex flex-col rounded-2xl border border-[rgba(249,200,109,0.30)] bg-[#141210] shadow-[0_16px_56px_rgba(0,0,0,0.90)] z-10 overflow-hidden text-[#F5F5F4]"
      >
        <!-- 顶部 Header -->
        <div class="px-4 py-3 border-b border-[#292524] bg-[#1A1714] flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-xl">🎛️</span>
            <div>
              <div class="flex items-center gap-2">
                <h2 class="text-sm font-semibold tracking-wide text-[#F9C86D]">SillyTavern 酒馆调音台</h2>
                <span class="px-1.5 py-0.2 rounded text-[10px] font-mono font-medium bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/40">
                  全功能 · {{ preset.preset_name }}
                </span>
              </div>
              <p class="text-[11px] text-[#A8A29E]">78 项生成设置与 Transformer 提示词排版流水线 (1:1 像素复刻)</p>
            </div>
          </div>
          <button
            type="button"
            @click="emit('update:modelValue', false)"
            class="w-7 h-7 flex items-center justify-center rounded-md hover:bg-[#292524] text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
          >
            ✕
          </button>
        </div>

        <!-- 激活全局生效横幅 (高保真自绘复选框) -->
        <div class="px-4 py-2.5 bg-[#1F1B17] border-b border-[#292524] flex items-center justify-between text-xs">
          <div
            @click="preset.is_active = !preset.is_active"
            class="flex items-center gap-2.5 cursor-pointer select-none group"
          >
            <div
              :class="[
                'w-4 h-4 rounded flex items-center justify-center border transition-all',
                preset.is_active
                  ? 'bg-[#F9C86D] border-[#F9C86D] text-[#141210]'
                  : 'bg-[#292524] border-[#57534E] text-transparent group-hover:border-[#78716C]'
              ]"
            >
              <svg class="w-3 h-3 stroke-current stroke-[2.5]" viewBox="0 0 24 24" fill="none">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <span class="font-medium text-[#F5F5F4] group-hover:text-[#F9C86D] transition-colors">
              设为当前对话全局生效 (接管所有大模型请求)
            </span>
          </div>
          <div class="flex items-center gap-2 text-[11px] text-[#A8A29E]">
            <span>启用条目: <strong class="text-[#F9C86D]">{{ activeCount }}</strong> / {{ orderedPromptList.length }}</span>
            <span>|</span>
            <span>预估 Token: <strong class="text-[#F9C86D]">{{ totalTokensEstimate }}</strong></span>
          </div>
        </div>

        <!-- 双 Tab 切换栏 -->
        <div class="grid grid-cols-2 bg-[#171412] border-b border-[#292524] p-1 gap-1">
          <button
            type="button"
            @click="activeTab = 'prompts'"
            :class="[
              'py-1.5 text-xs font-medium rounded-lg transition-all cursor-pointer flex items-center justify-center gap-1.5',
              activeTab === 'prompts'
                ? 'bg-[#292524] text-[#F9C86D] shadow-sm border border-[#44403C]'
                : 'text-[#A8A29E] hover:text-[#F5F5F4]'
            ]"
          >
            <span>📝</span> 提示词排版管理器 ({{ orderedPromptList.length }})
          </button>
          <button
            type="button"
            @click="activeTab = 'generation'"
            :class="[
              'py-1.5 text-xs font-medium rounded-lg transition-all cursor-pointer flex items-center justify-center gap-1.5',
              activeTab === 'generation'
                ? 'bg-[#292524] text-[#F9C86D] shadow-sm border border-[#44403C]'
                : 'text-[#A8A29E] hover:text-[#F5F5F4]'
            ]"
          >
            <span>⚙️</span> 对话补全生成设置
          </button>
        </div>

        <!-- 内容区域 -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4">

          <!-- TAB 2: 提示词排版编排 (1:1 像素复刻酒馆原生 78 项流水线) -->
          <div v-if="activeTab === 'prompts'" class="space-y-3">
            
            <!-- 顶部工具栏 (1:1 酒馆原生排版工具栏) -->
            <div class="p-2.5 rounded-xl bg-[#1A1714] border border-[#292524] flex flex-col gap-2">
              <div class="flex items-center justify-between text-xs">
                <div class="flex items-center gap-2 flex-1">
                  <span class="text-[#A8A29E] shrink-0 text-[11px]">偏置预设:</span>
                  <select
                    @change="(e) => onPresetChange((e.target as HTMLSelectElement).value)"
                    :value="preset.preset_name"
                    class="px-2 py-1 rounded bg-[#292524] border border-[#44403C] text-[11px] text-[#F9C86D] focus:outline-none"
                  >
                    <option
                      v-for="p in presetList"
                      :key="p.preset_name"
                      :value="p.preset_name"
                    >
                      {{ p.is_builtin ? '⚙️ ' : '👤 ' }}{{ p.preset_name }}
                    </option>
                  </select>
                </div>
                <div class="flex items-center gap-1.5">
                  <AppButton variant="outline" size="sm" @click="handleResetDefault">
                    恢复全量官方默认
                  </AppButton>
                </div>
              </div>

              <!-- 搜索与快速过滤 -->
              <div class="flex items-center gap-2">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="搜索 78 项提示词条目..."
                  class="flex-1 px-3 py-1 rounded-lg bg-[#292524] border border-[#44403C] text-xs text-[#F5F5F4] placeholder-[#78716C] focus:outline-none focus:border-[#F9C86D]"
                />
                <div class="flex items-center gap-1 text-[11px]">
                  <button
                    type="button"
                    @click="filterType = 'all'"
                    :class="['px-2 py-1 rounded cursor-pointer', filterType === 'all' ? 'bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/40' : 'text-[#A8A29E]']"
                  >
                    全部 ({{ orderedPromptList.length }})
                  </button>
                  <button
                    type="button"
                    @click="filterType = 'active'"
                    :class="['px-2 py-1 rounded cursor-pointer', filterType === 'active' ? 'bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/40' : 'text-[#A8A29E]']"
                  >
                    已启用 ({{ activeCount }})
                  </button>
                  <button
                    type="button"
                    @click="filterType = 'marker'"
                    :class="['px-2 py-1 rounded cursor-pointer', filterType === 'marker' ? 'bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/40' : 'text-[#A8A29E]']"
                  >
                    📌 锚点
                  </button>
                </div>
              </div>
            </div>

            <!-- 条目流水线列表 (全量 78 项，绝对无 UUID) -->
            <div class="space-y-1.5">
              <div
                v-for="item in filteredPromptList"
                :key="item.identifier"
                :class="[
                  'px-3 py-2 rounded-lg border transition-all flex items-center justify-between gap-2 select-none',
                  item.enabled
                    ? 'bg-[#1C1815] border-[#44403C] text-[#F5F5F4]'
                    : 'bg-[#141210] border-[#292524] text-[#78716C] opacity-55'
                ]"
              >
                <!-- 左侧：图标 + 序号 + 名称 + 角色 -->
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <span class="text-[10px] font-mono text-[#78716C] w-5 shrink-0 text-right">
                    {{ item.index + 1 }}.
                  </span>

                  <span class="text-sm shrink-0">
                    {{ getItemIcon(item) }}
                  </span>

                  <div class="flex-1 min-w-0 flex items-center gap-1.5">
                    <span class="text-xs font-medium truncate text-[#F5F5F4]">
                      {{ item.name }}
                    </span>

                    <span
                      v-if="item.isMarker"
                      class="px-1 py-0.2 rounded text-[8px] bg-amber-500/15 text-amber-400 border border-amber-500/25 shrink-0"
                    >
                      锚点
                    </span>

                    <span
                      v-if="item.isUserRole"
                      class="text-[11px] text-[#A8A29E] shrink-0"
                      title="User 角色"
                    >
                      👤
                    </span>

                    <span
                      v-if="item.forbidOverrides"
                      class="text-[10px] text-red-400/80 shrink-0"
                      title="禁止覆盖"
                    >
                      🚫
                    </span>
                  </div>
                </div>

                <!-- 右侧操作区：升降序 + 编辑 + 开关 + Token -->
                <div class="flex items-center gap-1.5 shrink-0">
                  <button
                    type="button"
                    :disabled="item.index === 0"
                    @click="moveUp(item.index)"
                    class="w-5 h-5 flex items-center justify-center rounded bg-[#292524] hover:bg-[#383330] disabled:opacity-20 disabled:cursor-not-allowed text-[9px] text-[#F5F5F4] cursor-pointer"
                    title="上移优先级"
                  >
                    ▲
                  </button>
                  <button
                    type="button"
                    :disabled="item.index === preset.prompt_order.length - 1"
                    @click="moveDown(item.index)"
                    class="w-5 h-5 flex items-center justify-center rounded bg-[#292524] hover:bg-[#383330] disabled:opacity-20 disabled:cursor-not-allowed text-[9px] text-[#F5F5F4] cursor-pointer"
                    title="下移优先级"
                  >
                    ▼
                  </button>

                  <button
                    type="button"
                    @click="openEditModal(item.prompt, item.name)"
                    class="w-5 h-5 flex items-center justify-center rounded bg-[#292524] hover:bg-[#383330] text-[10px] text-[#F9C86D] cursor-pointer"
                    title="查看/编辑正文"
                  >
                    ✏️
                  </button>

                  <button
                    type="button"
                    @click="toggleItem(item.identifier)"
                    :class="[
                      'w-9 h-4.5 rounded-full p-0.5 transition-colors cursor-pointer flex items-center',
                      item.enabled ? 'bg-[#F9C86D] justify-end' : 'bg-[#44403C] justify-start'
                    ]"
                  >
                    <div class="w-3.5 h-3.5 rounded-full bg-[#141210]" />
                  </button>

                  <span class="text-[10px] font-mono text-[#78716C] w-6 text-right">
                    {{ item.content ? Math.round(item.content.length * 0.7) : '-' }}
                  </span>
                </div>
              </div>
            </div>

          </div>

          <!-- TAB 1: 生成设置 (高对比度黑金滑块矩阵 + 多预设库管理) -->
          <div v-else class="space-y-4">
            
            <!-- 预设选择器与另存为操作栏 -->
            <div class="p-3.5 rounded-xl bg-[#1A1714] border border-[#292524] space-y-2.5">
              <div class="flex items-center justify-between">
                <span class="text-xs font-semibold text-[#F5F5F4]">对话补全预设库</span>
                <span class="text-[11px] text-[#F9C86D]">当前: {{ preset.preset_name }}</span>
              </div>
              <div class="flex items-center gap-2">
                <select
                  :value="preset.preset_name"
                  @change="(e) => onPresetChange((e.target as HTMLSelectElement).value)"
                  class="flex-1 px-3 py-1.5 rounded-lg bg-[#292524] border border-[#44403C] text-xs text-[#F5F5F4] focus:outline-none focus:border-[#F9C86D]"
                >
                  <option
                    v-for="p in presetList"
                    :key="p.preset_name"
                    :value="p.preset_name"
                  >
                    {{ p.is_builtin ? '⚙️ ' : '👤 ' }}{{ p.preset_name }}
                  </option>
                </select>

                <!-- 另存为按钮 -->
                <AppButton variant="outline" size="sm" @click="openSaveAsModal">
                  另存为...
                </AppButton>

                <!-- 自定义预设删除按钮 -->
                <button
                  v-if="presetList.find(p => p.preset_name === preset.preset_name && !p.is_builtin)"
                  type="button"
                  @click="handleDeleteCustomPreset(preset.preset_name)"
                  class="px-2 py-1.5 rounded-lg bg-red-950/40 hover:bg-red-900/60 border border-red-500/40 text-red-300 text-xs cursor-pointer"
                  title="删除当前自定义预设"
                >
                  🗑️
                </button>

                <AppButton variant="outline" size="sm" @click="handleResetDefault">
                  恢复默认
                </AppButton>
              </div>
            </div>

            <!-- 上下文上限与回复限制 -->
            <div class="p-3.5 rounded-xl bg-[#1A1714] border border-[#292524] space-y-3">
              <div class="flex items-center justify-between text-xs">
                <div
                  @click="preset.max_context_unlocked = !preset.max_context_unlocked"
                  class="flex items-center gap-2 cursor-pointer select-none"
                >
                  <div
                    :class="[
                      'w-3.5 h-3.5 rounded flex items-center justify-center border transition-all',
                      preset.max_context_unlocked
                        ? 'bg-[#F9C86D] border-[#F9C86D] text-[#141210]'
                        : 'bg-[#292524] border-[#57534E] text-transparent'
                    ]"
                  >
                    <svg class="w-2.5 h-2.5 stroke-current stroke-[2.5]" viewBox="0 0 24 24" fill="none">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                  <span>解锁上下文上限</span>
                </div>
                <span class="text-[11px] text-[#A8A29E]">移除最大值限制</span>
              </div>

              <!-- 上下文长度 -->
              <div>
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-[#A8A29E]">上下文长度 (Token)</span>
                  <span class="font-mono text-[#F9C86D]">{{ preset.openai_max_context.toLocaleString() }}</span>
                </div>
                <input
                  type="range"
                  min="4096"
                  max="2000000"
                  step="4096"
                  v-model.number="preset.openai_max_context"
                  class="tavern-range-slider cursor-pointer"
                />
              </div>

              <!-- 最大回复长度 -->
              <div>
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-[#A8A29E]">最大回复长度 (Token)</span>
                  <span class="font-mono text-[#F9C86D]">{{ preset.openai_max_tokens.toLocaleString() }}</span>
                </div>
                <input
                  type="number"
                  min="500"
                  max="64000"
                  v-model.number="preset.openai_max_tokens"
                  class="w-full px-3 py-1.5 rounded-lg bg-[#292524] border border-[#44403C] text-xs font-mono text-[#F5F5F4] focus:outline-none focus:border-[#F9C86D]"
                />
              </div>

              <!-- 流式传输 -->
              <div
                @click="preset.stream_openai = !preset.stream_openai"
                class="flex items-center gap-2 pt-1 cursor-pointer select-none"
              >
                <div
                  :class="[
                    'w-3.5 h-3.5 rounded flex items-center justify-center border transition-all',
                    preset.stream_openai
                      ? 'bg-[#F9C86D] border-[#F9C86D] text-[#141210]'
                      : 'bg-[#292524] border-[#57534E] text-transparent'
                  ]"
                >
                  <svg class="w-2.5 h-2.5 stroke-current stroke-[2.5]" viewBox="0 0 24 24" fill="none">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <span class="text-xs text-[#F5F5F4]">
                  流式传输 (逐字打字机显示结果)
                </span>
              </div>
            </div>

            <!-- 采样物理参数滑块群 (清晰底色与黑金轨道) -->
            <div class="p-3.5 rounded-xl bg-[#1A1714] border border-[#292524] space-y-3.5">
              <h3 class="text-xs font-semibold text-[#F9C86D]">采样超参数调音台</h3>

              <!-- 温度 -->
              <div>
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-[#A8A29E]">温度 (Temperature)</span>
                  <span class="font-mono text-[#F9C86D] font-medium">{{ preset.temperature.toFixed(2) }}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="2.0"
                  step="0.01"
                  v-model.number="preset.temperature"
                  class="tavern-range-slider cursor-pointer"
                />
              </div>

              <!-- 频率惩罚 -->
              <div>
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-[#A8A29E]">频率惩罚 (Frequency Penalty)</span>
                  <span class="font-mono text-[#F9C86D] font-medium">{{ preset.frequency_penalty.toFixed(2) }}</span>
                </div>
                <input
                  type="range"
                  min="-2.0"
                  max="2.0"
                  step="0.05"
                  v-model.number="preset.frequency_penalty"
                  class="tavern-range-slider cursor-pointer"
                />
              </div>

              <!-- 存在惩罚 -->
              <div>
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-[#A8A29E]">存在惩罚 (Presence Penalty)</span>
                  <span class="font-mono text-[#F9C86D] font-medium">{{ preset.presence_penalty.toFixed(2) }}</span>
                </div>
                <input
                  type="range"
                  min="-2.0"
                  max="2.0"
                  step="0.05"
                  v-model.number="preset.presence_penalty"
                  class="tavern-range-slider cursor-pointer"
                />
              </div>

              <!-- Top P -->
              <div>
                <div class="flex justify-between text-xs mb-1.5">
                  <span class="text-[#A8A29E]">Top P (核采样)</span>
                  <span class="font-mono text-[#F9C86D] font-medium">{{ preset.top_p.toFixed(2) }}</span>
                </div>
                <input
                  type="range"
                  min="0.0"
                  max="1.0"
                  step="0.01"
                  v-model.number="preset.top_p"
                  class="tavern-range-slider cursor-pointer"
                />
              </div>
            </div>

            <!-- 高级模型行为 -->
            <div class="p-3.5 rounded-xl bg-[#1A1714] border border-[#292524] space-y-3">
              <h3 class="text-xs font-semibold text-[#F9C86D]">高级模型行为</h3>
              
              <div class="grid grid-cols-2 gap-3 text-xs">
                <div>
                  <span class="text-[#A8A29E] block mb-1">推理强度 (Reasoning Effort)</span>
                  <select
                    v-model="preset.reasoning_effort"
                    class="w-full px-3 py-1.5 rounded-lg bg-[#292524] border border-[#44403C] text-xs text-[#F5F5F4] focus:outline-none"
                  >
                    <option value="high">高 (完整深度推演)</option>
                    <option value="medium">中</option>
                    <option value="low">低</option>
                    <option value="auto">自动</option>
                  </select>
                </div>
                <div>
                  <span class="text-[#A8A29E] block mb-1">随机种子 (Seed)</span>
                  <input
                    type="number"
                    v-model.number="preset.seed"
                    class="w-full px-3 py-1.5 rounded-lg bg-[#292524] border border-[#44403C] text-xs font-mono text-[#F5F5F4] focus:outline-none"
                    placeholder="-1 随机"
                  />
                </div>
              </div>
            </div>

          </div>

        </div>

        <!-- 底部 Footer 操作栏 -->
        <div class="p-3 bg-[#1A1714] border-t border-[#292524] flex items-center justify-between gap-2">
          <div class="flex items-center gap-2">
            <AppButton variant="outline" size="sm" @click="exportPresetJson">
              导出 JSON
            </AppButton>
          </div>
          <div class="flex items-center gap-2">
            <AppButton variant="outline" size="sm" @click="emit('update:modelValue', false)">
              取消
            </AppButton>
            <AppButton variant="gold" size="sm" :loading="isSaving" @click="handleSavePreset">
              保存并在聊天中全局生效
            </AppButton>
          </div>
        </div>

      </div>

      <!-- 单条目 1:1 像素复刻酒馆原生【编辑】弹窗 -->
      <div
        v-if="isEditModalOpen && editingPrompt"
        class="fixed inset-0 z-[110] flex items-center justify-center p-3"
      >
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="isEditModalOpen = false" />

        <div
          class="relative w-full max-w-[620px] max-h-[88vh] flex flex-col rounded-xl bg-[#121110] border border-[#383330] p-5 z-20 space-y-4 text-[#E7E5E4] shadow-2xl overflow-y-auto"
        >
          <div class="flex items-center justify-between pb-1">
            <h3 class="text-base font-medium text-[#F5F5F4]">编辑</h3>
            <button
              type="button"
              @click="isEditModalOpen = false"
              class="text-sm text-[#A8A29E] hover:text-white cursor-pointer px-1"
            >
              ✕
            </button>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div class="space-y-1">
              <label class="block font-medium text-[#D6D3D1]">姓名</label>
              <input
                v-model="editingPrompt.name"
                class="w-full px-2.5 py-1.5 rounded bg-[#1C1A17] border border-[#44403C] text-xs text-white focus:outline-none focus:border-[#F9C86D]"
              />
              <p class="text-[11px] text-[#78716C]">此提示词的名称。</p>
            </div>

            <div class="space-y-1">
              <label class="block font-medium text-[#D6D3D1]">身份</label>
              <select
                v-model="editingPrompt.role"
                class="w-full px-2.5 py-1.5 rounded bg-[#1C1A17] border border-[#44403C] text-xs text-white focus:outline-none focus:border-[#F9C86D]"
              >
                <option value="system">系统</option>
                <option value="user">用户</option>
                <option value="assistant">AI 助手</option>
              </select>
              <p class="text-[11px] text-[#78716C]">此消息应归于谁。</p>
            </div>

            <div class="space-y-1 relative">
              <label class="block font-medium text-[#D6D3D1]">触发器</label>
              <div
                @click="isTriggerDropdownOpen = !isTriggerDropdownOpen"
                class="w-full px-2.5 py-1.5 rounded bg-[#1C1A17] border border-[#44403C] text-xs text-white cursor-pointer flex items-center justify-between select-none"
              >
                <span class="truncate">
                  {{
                    editingPrompt.injection_trigger && editingPrompt.injection_trigger.length > 0
                      ? `已选 ${editingPrompt.injection_trigger.length} 项`
                      : '所有类型（默认）'
                  }}
                </span>
                <span class="text-[10px] text-[#78716C]">▼</span>
              </div>
              <p class="text-[11px] text-[#78716C]">筛选到特定的生成类型。</p>

              <div
                v-if="isTriggerDropdownOpen"
                class="absolute left-0 right-0 top-14 mt-1 bg-[#1A1714] border border-[#44403C] rounded-lg shadow-xl p-2 z-30 space-y-1.5 text-xs"
              >
                <div
                  v-for="opt in triggerOptions"
                  :key="opt.id"
                  @click="toggleTrigger(opt.id)"
                  class="flex items-center gap-2.5 px-1.5 py-1 hover:bg-[#292524] rounded cursor-pointer select-none"
                >
                  <div
                    :class="[
                      'w-3.5 h-3.5 rounded flex items-center justify-center border transition-all shrink-0',
                      editingPrompt.injection_trigger?.includes(opt.id)
                        ? 'bg-[#F9C86D] border-[#F9C86D] text-[#141210]'
                        : 'bg-[#292524] border-[#57534E] text-transparent'
                    ]"
                  >
                    <svg class="w-2.5 h-2.5 stroke-current stroke-[2.5]" viewBox="0 0 24 24" fill="none">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  </div>
                  <span>{{ opt.label }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs items-start">
            <div class="sm:col-span-2 space-y-1">
              <label class="block font-medium text-[#D6D3D1]">位置</label>
              <div class="flex items-center gap-2">
                <select
                  v-model.number="editingPrompt.injection_position"
                  class="flex-1 px-2.5 py-1.5 rounded bg-[#1C1A17] border border-[#44403C] text-xs text-white focus:outline-none focus:border-[#F9C86D]"
                >
                  <option :value="0">相对</option>
                  <option :value="1">聊天中</option>
                </select>
                <div v-if="editingPrompt.injection_position === 1" class="flex items-center gap-1">
                  <span class="text-[#78716C]">深度:</span>
                  <input
                    type="number"
                    v-model.number="editingPrompt.injection_depth"
                    class="w-16 px-2 py-1 rounded bg-[#1C1A17] border border-[#44403C] text-xs text-white font-mono"
                  />
                </div>
              </div>
              <p class="text-[11px] text-[#78716C]">
                相对（相对于提示词管理器中的其他提示词）或在聊天中的指定深度。
              </p>
            </div>

            <!-- 禁止覆盖 (高保真自绘复选框) -->
            <div class="pt-5 sm:pt-6 flex justify-start sm:justify-end">
              <div
                @click="editingPrompt.forbid_overrides = !editingPrompt.forbid_overrides"
                class="flex items-center gap-2.5 cursor-pointer select-none bg-[#1C1A17] hover:bg-[#25221E] px-3 py-2 rounded-lg border border-[#383330] hover:border-[#F9C86D]/60 transition-all"
              >
                <div
                  :class="[
                    'w-4.5 h-4.5 rounded flex items-center justify-center border transition-all shrink-0',
                    editingPrompt.forbid_overrides
                      ? 'bg-[#F9C86D] border-[#F9C86D] text-[#141210]'
                      : 'bg-[#292524] border-[#57534E] text-transparent hover:border-[#78716C]'
                  ]"
                >
                  <svg class="w-3.5 h-3.5 stroke-current stroke-[2.5]" viewBox="0 0 24 24" fill="none">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                </div>
                <span class="text-xs font-medium text-[#F5F5F4]">禁止覆盖</span>
              </div>
            </div>
          </div>

          <div class="space-y-1 text-xs">
            <label class="block font-medium text-[#D6D3D1]">提示词</label>
            <textarea
              v-model="editingPrompt.content"
              rows="10"
              class="w-full p-3 rounded-lg bg-[#0C0B0A] border border-[#2E2A27] text-xs text-[#E7E5E4] font-mono leading-relaxed focus:outline-none focus:border-[#F9C86D]"
              placeholder="输入提示词正文..."
            />
          </div>

          <div class="flex justify-end gap-2 pt-2 border-t border-[#292524]">
            <AppButton variant="outline" size="sm" @click="isEditModalOpen = false">取消</AppButton>
            <AppButton variant="gold" size="sm" @click="saveEditingPrompt">确认保存</AppButton>
          </div>
        </div>
      </div>

      <!-- 另存为新预设 Modal -->
      <div
        v-if="isSaveAsModalOpen"
        class="fixed inset-0 z-[120] flex items-center justify-center p-3"
      >
        <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="isSaveAsModalOpen = false" />
        <div class="relative w-full max-w-[400px] rounded-xl bg-[#141210] border border-[#44403C] p-5 z-30 space-y-4 text-[#F5F5F4] shadow-2xl">
          <h3 class="text-sm font-semibold text-[#F9C86D]">另存为新预设方案</h3>
          <div class="space-y-1.5 text-xs">
            <label class="text-[#A8A29E]">预设名称</label>
            <input
              v-model="saveAsPresetName"
              placeholder="例如: 我的深度沉浸预设"
              class="w-full px-3 py-2 rounded-lg bg-[#292524] border border-[#57534E] text-xs text-white focus:outline-none focus:border-[#F9C86D]"
            />
            <p class="text-[11px] text-[#78716C]">另存后将保存在您的个人预设库中，可在下拉框随时切换。</p>
          </div>
          <div class="flex justify-end gap-2 pt-2 border-t border-[#292524]">
            <AppButton variant="outline" size="sm" @click="isSaveAsModalOpen = false">取消</AppButton>
            <AppButton variant="gold" size="sm" :loading="isSaving" @click="handleConfirmSaveAs">确认另存</AppButton>
          </div>
        </div>
      </div>

    </div>
  </Teleport>
</template>

<style scoped>
/* 🌟 黑金奢华高对比度滑块轨道与手柄 */
.tavern-range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 9999px;
  background: #292524 !important;
  border: 1px solid #44403C;
  outline: none;
  transition: all 0.2s ease;
}

.tavern-range-slider:hover {
  border-color: #78716C;
  background: #322D28 !important;
}

.tavern-range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #F9C86D;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(249, 200, 109, 0.5), inset 0 0 2px rgba(0, 0, 0, 0.4);
  border: 2px solid #141210;
  transition: transform 0.1s ease, box-shadow 0.1s ease;
}

.tavern-range-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 0 14px rgba(249, 200, 109, 0.8);
}

.tavern-range-slider::-webkit-slider-thumb:active {
  transform: scale(0.95);
}

.tavern-range-slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #F9C86D;
  cursor: pointer;
  box-shadow: 0 0 10px rgba(249, 200, 109, 0.5);
  border: 2px solid #141210;
}

.tavern-range-slider::-moz-range-track {
  background: #292524;
  height: 8px;
  border-radius: 9999px;
  border: 1px solid #44403C;
}
</style>
