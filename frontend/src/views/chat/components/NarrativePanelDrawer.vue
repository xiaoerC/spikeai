<script setup lang="ts">
/**
 * AI 聊天界面 - 叙梦面板/聊天信息面板抽屉 (1:1 Figma 原型高保真)
 *
 * 严格按照 Figma 原型 (83:6511 / 85:7316 / 88:2 / 91:1327 / 92:2745 / 94:4096) 构建：
 * 包含 6 大 Tab 选项卡（状态/背包/技能/社交/任务/历史）：
 * 1. 👤 状态: 时空背景 + 玩家状态 (5项) + 时空表格 + 玩家状态表
 * 2. 🎒 背包: 消耗品/道具 + 重要物品（带红条）+ 消耗品/道具表格 + 重要物品表格
 * 3. ⚔️ 技能: 未装备技能（极限控精/金色进度条）+ 所有技能 + 技能表 (11列)
 * 4. 👥 社交: 社交关系 2x2 四宫格总览 + 4 大 NPC 角色好感度卡片 + 角色特征表格 + 角色与<user>社交表格
 * 5. 📜 任务: 进行中的任务（普通/进行中三联栏）+ 任务/命令/约定表格
 * 6. 📖 历史: 33 个总事件、5 天跨度、9 种角色筛选药丸、按日期分组的真实时间轴事件流 (周一/周日/周六/周五) + 历史事件表格
 *
 * @packageDocumentation
 */

import { type NarrativeStateDTO, chatService } from "@/services/chat";
import {
  Backpack,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Clock,
  Database,
  Edit2,
  Plus,
  Scroll,
  Sparkles,
  Swords,
  Trash2,
  User,
  Users,
  X,
} from "lucide-vue-next";
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();

const props = defineProps<{
  open: boolean;
  sessionId?: string;
  narrativeState?: NarrativeStateDTO;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "save", payload: NarrativeStateDTO): void;
}>();

// 记忆增强状态
const isMemoryEnhanced = ref(true);

// 6 大分类选项卡 (1: 状态, 2: 背包, 3: 技能, 4: 社交, 5: 任务, 6: 历史)
const tabs = [
  { id: 1, name: "状态", icon: User },
  { id: 2, name: "背包", icon: Backpack },
  { id: 3, name: "技能", icon: Swords },
  { id: 4, name: "社交", icon: Users },
  { id: 5, name: "任务", icon: Scroll },
  { id: 6, name: "历史", icon: BookOpen },
];
const activeTab = ref(1); // 默认打开状态 Tab

// 时空背景数据 (Tab 1 顶部)
const spatioTemporal = ref({
  date: props.narrativeState?.date_text || "第一幕 · 初始篇",
  time: props.narrativeState?.time_text || "清晨",
  location: props.narrativeState?.location || "起始之境",
  characters: props.narrativeState?.present_characters || [],
});

// 是否展开原始表格数据
const isRawTablesExpanded = ref(true);

// 玩家状态数据 (Tab 1)
const playerStates = ref<any[]>(props.narrativeState?.player_states || []);

// 背包数据 (Tab 2)
const consumables = ref<any[]>(props.narrativeState?.consumables || []);
const importantItems = ref<any[]>(props.narrativeState?.important_items || []);

// 技能数据 (Tab 3)
const skills = ref<any[]>(props.narrativeState?.skills || []);

// 社交关系数据 (Tab 4)
const socialCharacters = ref<any[]>(props.narrativeState?.social_relations || []);

// 社交四宫格统计计算
const intimateCount = computed(
  () => socialCharacters.value.filter((c) => (c.favorability || 0) >= 80).length,
);
const friendlyCount = computed(
  () =>
    socialCharacters.value.filter((c) => (c.favorability || 0) >= 50 && (c.favorability || 0) < 80)
      .length,
);
const hostileCount = computed(
  () => socialCharacters.value.filter((c) => (c.favorability || 0) < 50).length,
);
const totalSocialCount = computed(() => socialCharacters.value.length);

// 任务数据 (Tab 5)
const ongoingTasks = ref<any[]>(props.narrativeState?.tasks || []);

// 历史剧情事件时间轴按日期分组数据 (Tab 6)
const historyDateGroups = ref<any[]>(props.narrativeState?.history_events || []);

// 扁平化全部事件供表格使用
const allHistoryFlat = computed(() => {
  const list: Array<{
    id: number;
    dateText: string;
    characters: string;
    location: string;
    mood: string;
    desc: string;
  }> = [];
  let index = 1;
  for (const group of historyDateGroups.value) {
    for (const ev of group.events || []) {
      list.push({
        id: index++,
        dateText: group.dateText,
        characters: ev.characters,
        location: ev.location,
        mood: ev.mood,
        desc: ev.desc,
      });
    }
  }
  return list;
});

// 历史 Tab 角色筛选选项 (动态计算)
const activeFilter = ref("all");
const characterFilters = computed(() => {
  const charSet = new Set<string>();
  for (const group of historyDateGroups.value) {
    for (const ev of group.events || []) {
      if (ev.characters) charSet.add(ev.characters);
    }
  }
  const result = [{ id: "all", name: "全部", count: allHistoryFlat.value.length }];
  let idx = 1;
  charSet.forEach((name) => {
    const count = allHistoryFlat.value.filter((e) => e.characters.includes(name)).length;
    result.push({ id: `c_${idx++}`, name, count });
  });
  return result;
});

function syncFromNarrativeState(newVal?: NarrativeStateDTO | null): void {
  if (!newVal) return;
  spatioTemporal.value = {
    date: newVal.date_text || "第一幕 · 初始篇",
    time: newVal.time_text || "清晨",
    location: newVal.location || "木叶村残破废墟",
    characters:
      Array.isArray(newVal.present_characters) && newVal.present_characters.length > 0
        ? [...newVal.present_characters]
        : ["{{user}}", "漩涡博人"],
  };
  playerStates.value = Array.isArray(newVal.player_states) ? [...newVal.player_states] : [];
  consumables.value = Array.isArray(newVal.consumables) ? [...newVal.consumables] : [];
  importantItems.value = Array.isArray(newVal.important_items) ? [...newVal.important_items] : [];
  skills.value = Array.isArray(newVal.skills) ? [...newVal.skills] : [];
  socialCharacters.value = Array.isArray(newVal.social_relations)
    ? [...newVal.social_relations]
    : [];
  ongoingTasks.value = Array.isArray(newVal.tasks) ? [...newVal.tasks] : [];
  historyDateGroups.value = Array.isArray(newVal.history_events) ? [...newVal.history_events] : [];
}

async function fetchAndSyncState(): Promise<void> {
  if (props.narrativeState) {
    syncFromNarrativeState(props.narrativeState);
    return;
  }
  const sId = props.sessionId;
  if (sId) {
    try {
      const remote = await chatService.getNarrativeState(sId);
      if (remote) {
        syncFromNarrativeState(remote);
      }
    } catch {}
  }
}

// 监听外部传入的真实 NarrativeStateDTO 数据
watch(
  () => props.narrativeState,
  (newVal) => syncFromNarrativeState(newVal),
  { immediate: true, deep: true },
);

// 每次打开抽屉时自动同步最新传入的 props.narrativeState 或主动拉取后端最新状态兜底
watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      fetchAndSyncState();
    }
  },
);

// 快捷条目添加方法
function addPlayerState(): void {
  const newId = playerStates.value.length + 1;
  playerStates.value.push({
    id: newId,
    type: "新增状态",
    name: `状态属性 ${newId}`,
    currentVal: 50,
    maxVal: "100",
    desc: "在此输入当前状态描述...",
  });
  handleSaveNarrative();
}

function addConsumable(): void {
  const newId = consumables.value.length + 1;
  consumables.value.push({
    id: newId,
    name: `新物品 ${newId}`,
    count: 1,
    type: "道具",
    effect: "恢复或增益效果",
    source: "随身携带",
    desc: "物品详情描述",
  });
  handleSaveNarrative();
}

function addImportantItem(): void {
  const newId = importantItems.value.length + 1;
  importantItems.value.push({
    id: newId,
    owner: "{{user}}",
    name: `重要信物 ${newId}`,
    desc: "关键物品背景",
    importance: "影响剧情走向的关键道具",
  });
  handleSaveNarrative();
}

function addSkill(): void {
  const newId = skills.value.length + 1;
  skills.value.push({
    id: newId,
    name: `新技能 ${newId}`,
    type: "主动/被动",
    level: "LV.1",
    proficiency: "10%",
    proficiencyCurrent: 10,
    proficiencyMax: 100,
    cost: "精力",
    cooldown: "无",
    effect: "技能详细作用",
    source: "剧情领悟",
    status: "已掌握",
    isEquipped: false,
  });
  handleSaveNarrative();
}

function addSocialRelation(): void {
  const newId = socialCharacters.value.length + 1;
  socialCharacters.value.push({
    id: newId,
    name: `新NPC ${newId}`,
    relationTag: "结识",
    tagColor: "bg-[#F9C86D]",
    favorability: 50,
    favorBarColor: "bg-[#F9C86D]",
    relation: "新结识的朋友",
    location: spatioTemporal.value.location || "当前场景",
    attitude: "友善",
    bodyFeature: "外表描述",
    personality: "性格特征",
    job: "职业",
    hobby: "爱好",
    favorite: "喜好",
    residence: "居所",
    otherInfo: "其他背景信息",
  });
  handleSaveNarrative();
}

function addTask(): void {
  const newId = ongoingTasks.value.length + 1;
  ongoingTasks.value.push({
    id: newId,
    role: "{{user}}",
    task: `新任务 ${newId}`,
    typeTag: "支线",
    statusTag: "进行中",
    location: spatioTemporal.value.location || "当前场景",
    duration: "阶段性",
    desc: "任务目标与背景",
    reward: "经验与好感度",
  });
  handleSaveNarrative();
}

function addHistoryEvent(): void {
  const currentGroup = historyDateGroups.value[0];
  if (currentGroup) {
    currentGroup.events = currentGroup.events || [];
    currentGroup.events.push({
      id: Date.now(),
      time: spatioTemporal.value.time || "此刻",
      characters: spatioTemporal.value.characters.join("、") || "{{user}}",
      location: spatioTemporal.value.location || "当前场景",
      mood: "探索",
      desc: "发生了新的剧情事件...",
    });
  } else {
    historyDateGroups.value.push({
      id: `d_${Date.now()}`,
      dateText: spatioTemporal.value.date || "第一幕",
      eventCount: "1 个事件",
      events: [
        {
          id: Date.now(),
          time: spatioTemporal.value.time || "此刻",
          characters: spatioTemporal.value.characters.join("、") || "{{user}}",
          location: spatioTemporal.value.location || "当前场景",
          mood: "探索",
          desc: "发生了新的剧情事件...",
        },
      ],
    });
  }
  handleSaveNarrative();
}

function constructNarrativePayload(): NarrativeStateDTO {
  return {
    date_text: spatioTemporal.value.date,
    time_text: spatioTemporal.value.time,
    location: spatioTemporal.value.location,
    present_characters: spatioTemporal.value.characters,
    player_states: playerStates.value,
    consumables: consumables.value,
    important_items: importantItems.value,
    skills: skills.value,
    social_relations: socialCharacters.value,
    tasks: ongoingTasks.value,
    history_events: historyDateGroups.value,
  };
}

function handleSaveNarrative(): void {
  emit("save", constructNarrativePayload());
}

function handleClose(): void {
  emit("update:open", false);
}
</script>

<template>
  <!-- 抽屉蒙层 -->
  <Transition name="fade">
    <div
      v-if="open"
      @click="handleClose"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm transition-opacity"
    />
  </Transition>

  <!-- 右侧抽屉 (1:1 Figma 规格: width: 100%, max-w-[440px], background: #292524) -->
  <Transition name="slide-right">
    <aside
      v-if="open"
      class="fixed top-0 right-0 bottom-0 z-50 w-full max-w-[440px] bg-[#292524] text-[#F5F5F4] flex flex-col shadow-[0_8px_32px_rgba(249,200,109,0.15)] border-t-2 border-b-2 border-[#F9C86D] overflow-hidden select-none"
    >
      <!-- 1. 顶部 Header 与控制区 (双行黑金磨砂，对称 py-3.5 px-4) -->
      <header class="w-full bg-gradient-to-br from-[#F9C86D]/15 via-[#44403C]/80 to-[#292524] border-b border-[#F9C86D] backdrop-blur-md px-4 py-3.5 flex flex-col gap-2.5 shrink-0">
        
        <!-- 第一行: 标题「叙梦面板」+「记忆增强·ON」胶囊 + 关闭按钮 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Swords class="w-4 h-4 text-[#F9C86D]" />
            <h2 class="text-[15px] font-bold text-[#F9C86D] tracking-wide">
              叙梦面板
            </h2>
          </div>

          <div class="flex items-center gap-2">
            <!-- 记忆增强 ON/OFF 胶囊按钮 -->
            <button
              type="button"
              @click="isMemoryEnhanced = !isMemoryEnhanced"
              class="h-[30px] px-2.5 rounded-lg border border-[#F9C86D] bg-[#F9C86D]/20 hover:bg-[#F9C86D]/30 active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span
                class="w-2 h-2 rounded-full transition-colors"
                :class="isMemoryEnhanced ? 'bg-[#22C55E]' : 'bg-[#78716C]'"
              />
              <BookOpen class="w-3.5 h-3.5 text-[#F9C86D]" />
              <span class="text-[11px] font-semibold text-[#F9C86D]">
                记忆增强 · {{ isMemoryEnhanced ? 'ON' : 'OFF' }}
              </span>
            </button>

            <!-- 方形关闭按钮 -->
            <button
              type="button"
              @click="handleClose"
              class="w-[30px] h-[30px] rounded-lg border border-[#D1A35C] bg-[#F9C86D]/15 hover:bg-[#F9C86D]/25 active:scale-95 transition-all flex items-center justify-center text-[#F9C86D] cursor-pointer"
              title="关闭"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- 第二行: 右对齐的「保存状态」、「整理」与「备份与恢复」操作按钮 -->
        <div class="flex items-center justify-end gap-2 pt-0.5">
          <button
            type="button"
            @click="handleSaveNarrative"
            class="h-7 px-3 rounded-[7px] border border-[#F9C86D] bg-[#F9C86D] hover:bg-[#F9C86D]/90 active:scale-95 transition-all flex items-center gap-1 text-xs font-bold text-[#1C1917] cursor-pointer"
          >
            <span>保存状态</span>
          </button>

          <button
            type="button"
            class="h-7 px-2.5 rounded-[7px] border border-[#F9C86D]/20 bg-[#44403C]/80 hover:border-[#F9C86D]/50 active:scale-95 transition-all flex items-center gap-1.5 text-xs text-[#A8A29E] hover:text-[#F5F5F4] cursor-pointer"
          >
            <Sparkles class="w-3.5 h-3.5 text-[#F9C86D]" />
            <span>整理</span>
          </button>

          <button
            type="button"
            class="h-7 px-2.5 rounded-[7px] border border-[#F9C86D]/20 bg-[#44403C]/80 hover:border-[#F9C86D]/50 active:scale-95 transition-all flex items-center gap-1.5 text-xs text-[#A8A29E] hover:text-[#F5F5F4] cursor-pointer"
          >
            <Database class="w-3.5 h-3.5 text-[#A8A29E]" />
            <span>备份与恢复</span>
          </button>
        </div>

      </header>

      <!-- 2. 6 大 Tab 选项卡导航栏 (从左到右: 👤状态 / 🎒背包 / ⚔️技能 / 👥社交 / 📜任务 / 📖历史) -->
      <nav class="h-11 px-2 py-1.5 flex items-center gap-1 border-b border-[#44403C] bg-[#292524] shrink-0 overflow-x-auto [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        <button
          v-for="t in tabs"
          :key="t.id"
          type="button"
          @click="activeTab = t.id"
          :class="[
            'px-2.5 h-8 rounded-lg flex items-center gap-1.5 transition-all shrink-0 cursor-pointer text-xs font-medium',
            activeTab === t.id
              ? 'border border-[#F9C86D] bg-gradient-to-br from-[#F9C86D]/25 to-[#F9C86D]/15 text-[#F9C86D] shadow-[0_0_12px_rgba(249,200,109,0.15)]'
              : 'border border-[#44403C] bg-transparent text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-white/5'
          ]"
        >
          <component :is="t.icon" class="w-3.5 h-3.5" />
          <span>{{ t.name }}</span>
        </button>
      </nav>

      <!-- 3. 主体内容滚动区域 (带底边充足留白) -->
      <main class="flex-1 overflow-y-auto p-3 flex flex-col gap-3 pb-12">
        
        <!-- ==================== TAB 1: 状态 (时空背景 + 玩家状态) ==================== -->
        <template v-if="activeTab === 1">
          <!-- (1) 时空背景卡片 -->
          <section class="p-4 rounded-xl border border-[#44403C]/60 bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col">
            <div class="pb-2 flex items-center gap-2 border-b border-[#F9C86D]/20">
              <span class="text-xs">🕒</span>
              <h3 class="text-[13px] font-semibold text-[#F9C86D] tracking-tight">
                时空背景
              </h3>
            </div>

            <div class="pt-3 grid grid-cols-1 gap-2">
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-[#A8A29E]">日期</span>
                <span class="text-base font-semibold text-[#F5F5F4] tracking-tight">
                  {{ spatioTemporal.date || "第一幕 · 初始篇" }}
                </span>
              </div>

              <div class="flex flex-col gap-0.5 pt-1">
                <span class="text-xs text-[#A8A29E]">时间</span>
                <span class="text-base font-semibold text-[#F5F5F4] font-mono">
                  {{ spatioTemporal.time || "清晨" }}
                </span>
              </div>
            </div>

            <div class="mt-3 p-3.5 rounded-lg bg-[#F9C86D]/15 border border-[#F9C86D]/30 flex flex-col gap-1">
              <div class="flex items-center gap-1.5">
                <span class="text-xs text-[#A8A29E]">📍</span>
                <span class="text-sm font-semibold text-[#A8A29E]">当前地点</span>
              </div>
              <span class="text-[15px] text-[#F5F5F4] pl-5 font-medium">
                {{ spatioTemporal.location || "起始之境" }}
              </span>
            </div>

            <div class="mt-3 pt-2 border-t border-[#F9C86D]/15 flex flex-col gap-2">
              <div class="flex items-center gap-1.5">
                <span class="text-xs">👥</span>
                <span class="text-[13px] font-semibold text-[#F9C86D]">在场角色</span>
                <span class="text-xs text-[#78716C] font-mono">({{ spatioTemporal.characters.length }})</span>
              </div>

              <div class="flex flex-wrap gap-2 pt-1">
                <div
                  v-for="(char, idx) in spatioTemporal.characters"
                  :key="idx"
                  class="px-3 py-1.5 rounded-full border border-white/10 bg-black/40 text-sm font-medium text-[#F5F5F4]"
                >
                  {{ char }}
                </div>
              </div>
            </div>
          </section>

          <!-- (2) 玩家状态卡片列表 (5项) -->
          <section class="p-3.5 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.15)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <span class="text-xs">📊</span>
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                玩家状态
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ playerStates.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="state in playerStates"
                :key="state.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2 hover:border-[#F9C86D]/40 transition-colors"
              >
                <div class="flex items-center justify-between">
                  <span class="text-[15px] font-semibold text-[#F5F5F4]">
                    {{ state.name }}
                  </span>
                  <span class="text-base font-bold text-[#F9C86D] font-mono">
                    {{ state.currentVal }} / {{ state.maxVal }}
                  </span>
                </div>

                <div class="pt-2 border-t border-[#F9C86D]/15 text-[13px] text-[#A8A29E] leading-relaxed">
                  {{ state.desc }}
                </div>
              </div>
            </div>
          </section>
        </template>

        <!-- ==================== TAB 2: 背包 (1:1 原型 Frame 85:7316) ==================== -->
        <template v-else-if="activeTab === 2">
          
          <!-- (1) 🎒 消耗品/道具 (1) -->
          <section class="p-3.5 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <Backpack class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                消耗品/道具
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ consumables.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="item in consumables"
                :key="item.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2 hover:border-[#F9C86D]/40 transition-colors"
              >
                <div class="flex items-center justify-between">
                  <span class="text-[15px] font-semibold text-[#F5F5F4]">
                    {{ item.name }}
                  </span>
                  <span class="px-2 py-0.5 rounded-full bg-[#F9C86D] text-[#0C0A09] text-xs font-bold font-mono">
                    x{{ item.count }}
                  </span>
                </div>

                <div class="flex flex-col gap-1 text-[13px] pt-1">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#78716C] font-medium">效果:</span>
                    <span class="text-[#F5F5F4]">{{ item.effect }}</span>
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#78716C] font-medium">来源:</span>
                    <span class="text-[#F5F5F4]">{{ item.source }}</span>
                  </div>
                </div>

                <div class="pt-2 border-t border-[#F9C86D]/15 text-[13px] text-[#A8A29E]">
                  {{ item.desc }}
                </div>
              </div>
            </div>
          </section>

          <!-- (2) ◇ 重要物品 (1) (带红色左边框指示条) -->
          <section class="p-3.5 rounded-xl border border-[#44403C] bg-red-500/10 shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <span class="text-xs text-[#F9C86D]">◇</span>
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                重要物品
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ importantItems.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="item in importantItems"
                :key="item.id"
                class="p-3 rounded-lg border-l-4 border-l-[#EF4444] border-t border-r border-b border-[#44403C] bg-[#292524] flex flex-col gap-2"
              >
                <div class="flex items-baseline gap-1.5">
                  <span class="text-base font-bold text-[#F5F5F4]">
                    {{ item.name }}
                  </span>
                  <span class="text-[13px] text-[#A8A29E]">
                    ({{ item.owner }})
                  </span>
                </div>

                <p class="text-sm text-[#A8A29E] leading-relaxed">
                  {{ item.desc }}
                </p>

                <div class="text-[13px] leading-relaxed">
                  <span class="font-medium text-[#EF4444]">重要性: </span>
                  <span class="text-[#EF4444]">{{ item.importance }}</span>
                </div>
              </div>
            </div>
          </section>

        </template>

        <!-- ==================== TAB 3: 技能 (1:1 原型 Frame 88:2) ==================== -->
        <template v-else-if="activeTab === 3">
          
          <!-- (1) 未装备技能 (1) -->
          <section class="p-4 rounded-xl border border-[#44403C] bg-[#44403C] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                未装备技能
              </h3>
              <span class="text-xs text-[#78716C] font-mono">(1)</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="skill in skills"
                :key="skill.id"
                class="p-3.5 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2.5"
              >
                <div class="flex items-center gap-2">
                  <span class="text-[15px] font-bold text-[#F5F5F4]">
                    {{ skill.name }}
                  </span>
                  <span class="px-1.5 py-0.5 rounded bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold font-mono">
                    Lv.1
                  </span>
                </div>

                <p class="text-[13px] text-[#A8A29E] leading-relaxed">
                  {{ skill.effect }}
                </p>

                <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-4 text-xs">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">消耗</span>
                    <span class="font-semibold text-[#F5F5F4]">{{ skill.cost }}</span>
                  </div>
                  <span class="text-[#44403C]">|</span>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">冷却</span>
                    <span class="font-semibold text-[#F5F5F4]">{{ skill.cooldown }}</span>
                  </div>
                </div>

                <div class="flex flex-col gap-1.5 pt-0.5">
                  <div class="flex items-center justify-between text-[11px] text-[#A8A29E]">
                    <span>熟练度 {{ skill.proficiencyCurrent }}/{{ skill.proficiencyMax }}</span>
                    <span class="font-mono">{{ skill.proficiency }}</span>
                  </div>
                  <div class="w-full h-1.5 rounded-full bg-[#44403C] overflow-hidden">
                    <div
                      class="h-full rounded-full bg-[#F9C86D]"
                      :style="{ width: `${skill.proficiencyCurrent}%` }"
                    />
                  </div>
                </div>

                <div class="p-2 rounded-md bg-[#F9C86D]/15 text-xs text-[#A8A29E]">
                  {{ skill.source }}
                </div>
              </div>
            </div>
          </section>

          <!-- (2) 所有技能 (1) -->
          <section class="p-4 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                所有技能
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ skills.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="skill in skills"
                :key="skill.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2"
              >
                <div class="flex items-center justify-between">
                  <span class="text-[15px] font-semibold text-[#F5F5F4]">
                    {{ skill.name }}
                  </span>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[11px] font-semibold text-[#3B82F6]">
                      {{ skill.type }}
                    </span>
                    <span class="px-1.5 py-0.2 rounded bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold font-mono">
                      Lv.{{ skill.level }}
                    </span>
                    <span class="text-[11px] font-semibold text-[#F9C86D]">
                      {{ skill.status }}
                    </span>
                  </div>
                </div>

                <div class="pt-1 text-[13px] leading-relaxed flex items-start gap-1">
                  <span class="text-[#A8A29E] shrink-0">效果:</span>
                  <span class="text-[#F5F5F4]">{{ skill.effect }}</span>
                </div>

                <div class="flex items-center gap-1.5 text-[13px]">
                  <span class="text-[#A8A29E]">熟练度:</span>
                  <span class="text-[#F5F5F4] font-mono">{{ skill.proficiency }}</span>
                </div>

                <div class="flex items-center gap-4 text-[13px]">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">消耗:</span>
                    <span class="text-[#F5F5F4]">{{ skill.cost }}</span>
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">冷却:</span>
                    <span class="text-[#F5F5F4]">{{ skill.cooldown }}</span>
                  </div>
                </div>

                <div class="flex items-center gap-1.5 text-[13px]">
                  <span class="text-[#A8A29E] shrink-0">来源:</span>
                  <span class="text-[#F5F5F4]">{{ skill.source }}</span>
                </div>
              </div>
            </div>
          </section>

        </template>

        <!-- ==================== TAB 4: 社交 (1:1 原型 Frame 91:1327) ==================== -->
        <template v-else-if="activeTab === 4">
          
          <!-- (1) 社交关系总览 四宫格状态矩阵 -->
          <section class="p-3.5 rounded-xl border border-[#F9C86D]/20 bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <Users class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                社交关系总览
              </h3>
            </div>

            <div class="grid grid-cols-2 gap-2 pt-1">
              <div class="p-2.5 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">亲密</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">{{ intimateCount }}</span>
              </div>

              <div class="p-2.5 rounded-lg bg-[#EAB308]/10 border border-[#EAB308]/20 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">友好</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">{{ friendlyCount }}</span>
              </div>

              <div class="p-2.5 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/20 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">敌对</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">{{ hostileCount }}</span>
              </div>

              <div class="p-2.5 rounded-lg bg-[#F9C86D]/15 border border-[#F9C86D]/30 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">总计</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">{{ totalSocialCount }}</span>
              </div>
            </div>
          </section>

          <!-- (2) 角色关系卡片列表 -->
          <div class="flex flex-col gap-2.5">
            <div
              v-if="socialCharacters.length === 0"
              class="p-4 rounded-xl border border-dashed border-[#44403C] text-center text-xs text-[#A8A29E] flex flex-col items-center gap-2"
            >
              <span>暂无结识的 NPC，点击下方【新增】或随剧情推进自动记录</span>
              <button
                type="button"
                @click="addSocialRelation"
                class="px-2.5 py-1 rounded bg-[#F9C86D] text-[#1C1917] font-bold text-xs cursor-pointer"
              >
                + 新增 NPC
              </button>
            </div>

            <div
              v-for="char in socialCharacters"
              :key="char.id"
              class="p-3 rounded-xl border border-[#44403C] bg-[#292524] flex flex-col gap-2.5 hover:border-[#F9C86D]/40 transition-colors shadow-md"
            >
              <div class="flex items-center justify-between">
                <h4 class="text-[15px] font-bold text-[#F5F5F4]">
                  {{ char.name }}
                </h4>
                <span
                  :class="[
                    'px-2 py-0.5 rounded-full text-xs font-semibold text-[#0C0A09]',
                    char.tagColor
                  ]"
                >
                  {{ char.relationTag }}
                </span>
              </div>

              <div class="flex items-center gap-2">
                <div class="flex-1 h-1.5 rounded-full bg-[#44403C] overflow-hidden">
                  <div
                    :class="['h-full rounded-full transition-all', char.favorBarColor]"
                    :style="{ width: `${char.favorability}%` }"
                  />
                </div>
                <span class="text-xs font-bold text-[#F5F5F4] font-mono w-6 text-right">
                  {{ char.favorability }}
                </span>
              </div>

              <div class="flex flex-col gap-1 text-xs">
                <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-2">
                  <span class="text-[#A8A29E] shrink-0">关系</span>
                  <span class="font-semibold text-[#F5F5F4]">{{ char.relation }}</span>
                </div>
                <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-2">
                  <span class="text-[#A8A29E] shrink-0">位置</span>
                  <span class="text-[#F5F5F4]">{{ char.location }}</span>
                </div>
              </div>
            </div>
          </div>

        </template>

        <!-- ==================== TAB 5: 任务 (1:1 原型 Frame 92:2745) ==================== -->
        <template v-else-if="activeTab === 5">
          
          <!-- (1) 进行中的任务 (1) -->
          <section class="p-4 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <Scroll class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                进行中的任务
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ ongoingTasks.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="task in ongoingTasks"
                :key="task.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2.5"
              >
                <!-- 顶行: 角色名 + 状态胶囊 -->
                <div class="flex items-center justify-between">
                  <span class="text-[13px] font-bold text-[#F5F5F4]">
                    {{ task.role }}
                  </span>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[11px] font-semibold text-[#EAB308]">
                      {{ task.typeTag }}
                    </span>
                    <span class="px-2 py-0.5 rounded bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold">
                      {{ task.statusTag }}
                    </span>
                  </div>
                </div>

                <!-- 任务描述 -->
                <p class="text-[13px] text-[#A8A29E] leading-relaxed">
                  {{ task.task }}
                </p>

                <!-- 任务详情三联栏 -->
                <div class="grid grid-cols-3 gap-1.5 text-xs">
                  <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-1">
                    <span class="text-[#A8A29E] shrink-0">角色:</span>
                    <span class="font-semibold text-[#F5F5F4] truncate">{{ task.role }}</span>
                  </div>
                  <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-1">
                    <span class="text-[#A8A29E] shrink-0">地点:</span>
                    <span class="font-semibold text-[#F5F5F4] truncate">{{ task.location }}</span>
                  </div>
                  <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-1">
                    <span class="text-[#A8A29E] shrink-0">持续时间:</span>
                    <span class="font-semibold text-[#F5F5F4] truncate">{{ task.duration }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

        </template>

        <!-- ==================== TAB 6: 历史 (1:1 原型 Frame 94:4096) ==================== -->
        <template v-else-if="activeTab === 6">
          
          <!-- (1) 重要事件历史总览与角色筛选卡片 -->
          <section class="p-3.5 rounded-xl border border-[#F9C86D]/20 bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <BookOpen class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                重要事件历史
              </h3>
            </div>

            <!-- 总事件与时间跨度 -->
            <div class="flex items-center gap-4 text-sm font-bold text-[#F5F5F4] pt-0.5">
              <span>总事件: {{ allHistoryFlat.length }}</span>
              <span>时间跨度: {{ historyDateGroups.length }} 幕/天</span>
            </div>

            <!-- 角色筛选标签网格 -->
            <div class="flex flex-col gap-1.5 pt-1">
              <span class="text-xs text-[#A8A29E]">角色筛选:</span>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="filter in characterFilters"
                  :key="filter.id"
                  type="button"
                  @click="activeFilter = filter.id"
                  :class="[
                    'px-2.5 py-1 rounded-md text-xs font-medium transition-all cursor-pointer border',
                    activeFilter === filter.id
                      ? 'border-[#F9C86D] bg-[#292524] text-[#F9C86D] font-bold shadow-[0_0_8px_rgba(249,200,109,0.2)]'
                      : 'border-transparent bg-[#F9C86D]/15 text-[#F5F5F4] hover:bg-[#F9C86D]/25'
                  ]"
                >
                  {{ filter.name }} ({{ filter.count }})
                </button>
              </div>
            </div>
          </section>

          <!-- (2) 时间轴事件流列表 (按日期分组) -->
          <div class="flex flex-col gap-4 pt-1">
            <div
              v-if="historyDateGroups.length === 0"
              class="p-4 rounded-xl border border-dashed border-[#44403C] text-center text-xs text-[#A8A29E] flex flex-col items-center gap-2"
            >
              <span>暂无历史事件，随剧情推进将自动记录关键节点</span>
              <button
                type="button"
                @click="addHistoryEvent"
                class="px-2.5 py-1 rounded bg-[#F9C86D] text-[#1C1917] font-bold text-xs cursor-pointer"
              >
                + 记录初遇事件
              </button>
            </div>
            <div
              v-for="group in historyDateGroups"
              :key="group.id"
              class="flex flex-col gap-2"
            >
              <!-- 日期标题行 -->
              <div class="px-3 py-1.5 rounded-lg bg-[#292524] border border-[#44403C]/60 flex items-center justify-between">
                <span class="text-[13px] font-bold text-[#F5F5F4]">
                  {{ group.dateText }}
                </span>
                <span class="px-2 py-0.5 rounded-full bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold">
                  {{ group.eventCount }}
                </span>
              </div>

              <!-- 时间轴卡片群 (左侧纵线) -->
              <div class="pl-4 ml-3 border-l-2 border-[#44403C] flex flex-col gap-2.5 relative">
                <div
                  v-for="ev in group.events"
                  :key="ev.id"
                  class="p-3 rounded-xl border border-[#44403C] bg-[#292524] flex flex-col gap-2 relative hover:border-[#F9C86D]/40 transition-colors shadow-sm"
                >
                  <!-- 节点小圆点 -->
                  <div class="w-2.5 h-2.5 rounded-full bg-[#78716C] border-2 border-[#292524] absolute -left-[22px] top-4.5" />

                  <!-- 顶行: 角色 + 地点 + 氛围/情绪标签 -->
                  <div class="flex items-center justify-between gap-1 flex-wrap">
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-semibold text-[#F9C86D]">
                        {{ ev.characters }}
                      </span>
                      <span class="text-xs text-[#A8A29E]">
                        {{ ev.location }}
                      </span>
                    </div>

                    <span class="px-2 py-0.5 rounded-md bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold">
                      {{ ev.mood }}
                    </span>
                  </div>

                  <!-- 事件描述段落 -->
                  <p class="text-[13px] text-[#F5F5F4] leading-relaxed pt-0.5">
                    {{ ev.desc }}
                  </p>
                </div>
              </div>
            </div>
          </div>

        </template>

        <!-- (3) 查看原始表格数据手风琴折叠卡片 -->
        <section class="flex flex-col gap-3">
          <!-- 折叠切换条 -->
          <button
            type="button"
            @click="isRawTablesExpanded = !isRawTablesExpanded"
            class="w-full px-3.5 py-2.5 rounded-lg border border-[#44403C] bg-[#292524] hover:bg-[#332D28] active:scale-[0.99] transition-all flex items-center justify-between cursor-pointer"
          >
            <div class="flex items-center gap-2">
              <component
                :is="isRawTablesExpanded ? ChevronUp : ChevronDown"
                class="w-4 h-4 text-[#F9C86D]"
              />
              <span class="text-xs font-semibold text-[#F9C86D]">
                查看原始表格数据
              </span>
            </div>

            <span class="text-[11px] font-semibold text-[#A8A29E]">
              ({{ activeTab === 1 || activeTab === 2 || activeTab === 4 ? '2' : '1' }}个相关表格)
            </span>
          </button>

          <!-- 展开后的表格列表 -->
          <div v-if="isRawTablesExpanded" class="flex flex-col gap-4 pt-1">
            
            <!-- 历史专属表格: 历史事件表格 (Tab 6) -->
            <div v-if="activeTab === 6" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  历史事件表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    @click="addHistoryEvent"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">发生日期</th>
                      <th class="py-2 px-2 font-medium">参与角色</th>
                      <th class="py-2 px-2 font-medium">地点</th>
                      <th class="py-2 px-2 font-medium">情绪/氛围</th>
                      <th class="py-2 px-2 font-medium">事件经过</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="ev in allHistoryFlat"
                      :key="ev.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ ev.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ ev.dateText }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#F9C86D]">{{ ev.characters }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ ev.location }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#EAB308]">{{ ev.mood }}</td>
                      <td class="py-2 px-2 max-w-[200px] truncate" :title="ev.desc">{{ ev.desc }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 任务专属表格: 任务/命令/约定表格 (Tab 5) -->
            <div v-if="activeTab === 5" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  任务/命令/约定表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    @click="addTask"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">角色</th>
                      <th class="py-2 px-2 font-medium">任务</th>
                      <th class="py-2 px-2 font-medium">地点</th>
                      <th class="py-2 px-2 font-medium">持续时间</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="t in ongoingTasks"
                      :key="t.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ t.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ t.role }}</td>
                      <td class="py-2 px-2 max-w-[180px] truncate" :title="t.task">{{ t.task }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ t.location }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ t.duration }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 社交专属表格 1: 角色特征表格 (Tab 4) -->
            <div v-if="activeTab === 4" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  角色特征表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    @click="addSocialRelation"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">角色名</th>
                      <th class="py-2 px-2 font-medium">身体特征</th>
                      <th class="py-2 px-2 font-medium">性格</th>
                      <th class="py-2 px-2 font-medium">职业</th>
                      <th class="py-2 px-2 font-medium">爱好</th>
                      <th class="py-2 px-2 font-medium">喜爱的事物</th>
                      <th class="py-2 px-2 font-medium">住所</th>
                      <th class="py-2 px-2 font-medium">其他重要信息</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="c in socialCharacters"
                      :key="c.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ c.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ c.name }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate" :title="c.bodyFeature">{{ c.bodyFeature }}</td>
                      <td class="py-2 px-2 max-w-[120px] truncate" :title="c.personality">{{ c.personality }}</td>
                      <td class="py-2 px-2 max-w-[100px] truncate">{{ c.job }}</td>
                      <td class="py-2 px-2 max-w-[90px] truncate">{{ c.hobby }}</td>
                      <td class="py-2 px-2 max-w-[100px] truncate">{{ c.favorite }}</td>
                      <td class="py-2 px-2 max-w-[100px] truncate">{{ c.residence }}</td>
                      <td class="py-2 px-2 max-w-[160px] truncate text-[#A8A29E]" :title="c.otherInfo">{{ c.otherInfo }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 社交专属表格 2: 角色与<user>社交表格 (Tab 4) -->
            <div v-if="activeTab === 4" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  角色与&lt;user&gt;社交表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">角色名</th>
                      <th class="py-2 px-2 font-medium">对&lt;user&gt;关系</th>
                      <th class="py-2 px-2 font-medium">对&lt;user&gt;态度</th>
                      <th class="py-2 px-2 font-medium">对&lt;user&gt;好感</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="c in socialCharacters"
                      :key="c.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ c.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ c.name }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#F9C86D]">{{ c.relation }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate" :title="c.attitude">{{ c.attitude }}</td>
                      <td class="py-2 px-2 font-mono font-semibold">{{ c.favorability }} ({{ c.relationTag }})</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 技能专属表格: 技能表 (Tab 3) -->
            <div v-if="activeTab === 3" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  技能表
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    @click="addSkill"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">技能名</th>
                      <th class="py-2 px-2 font-medium">技能类型</th>
                      <th class="py-2 px-2 font-medium">等级</th>
                      <th class="py-2 px-2 font-medium">熟练度</th>
                      <th class="py-2 px-2 font-medium">消耗</th>
                      <th class="py-2 px-2 font-medium">冷却时间</th>
                      <th class="py-2 px-2 font-medium">效果描述</th>
                      <th class="py-2 px-2 font-medium">学习来源</th>
                      <th class="py-2 px-2 font-medium">状态</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="s in skills"
                      :key="s.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ s.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ s.name }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#3B82F6]">{{ s.type }}</td>
                      <td class="py-2 px-2 font-mono">{{ s.level }}</td>
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ s.proficiency }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ s.cost }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ s.cooldown }}</td>
                      <td class="py-2 px-2 max-w-[200px] truncate" :title="s.effect">{{ s.effect }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate text-[#A8A29E]" :title="s.source">{{ s.source }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#F9C86D]">{{ s.status }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 背包专属表格 1: 重要物品表格 (Tab 2) -->
            <div v-if="activeTab === 2" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  重要物品表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    @click="addImportantItem"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">拥有人</th>
                      <th class="py-2 px-2 font-medium">物品描述</th>
                      <th class="py-2 px-2 font-medium">物品名</th>
                      <th class="py-2 px-2 font-medium">重要原因</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in importantItems"
                      :key="item.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ item.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ item.owner }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate" :title="item.desc">{{ item.desc }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ item.name }}</td>
                      <td class="py-2 px-2 max-w-[160px] truncate text-[#EF4444]" :title="item.importance">{{ item.importance }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 背包专属表格 2: 消耗品/道具表格 (Tab 2) -->
            <div v-if="activeTab === 2" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  消耗品/道具表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    @click="addConsumable"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">物品名</th>
                      <th class="py-2 px-2 font-medium">数量</th>
                      <th class="py-2 px-2 font-medium">类型</th>
                      <th class="py-2 px-2 font-medium">效果/属性</th>
                      <th class="py-2 px-2 font-medium">获得方式</th>
                      <th class="py-2 px-2 font-medium">备注</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in consumables"
                      :key="item.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ item.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ item.name }}</td>
                      <td class="py-2 px-2 font-mono font-bold text-[#F9C86D]">{{ item.count }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#A8A29E]">{{ item.type }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ item.effect }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#A8A29E]">{{ item.source }}</td>
                      <td class="py-2 px-2 text-[#A8A29E] max-w-[140px] truncate" :title="item.desc">
                        {{ item.desc }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 状态专属表格 1: 时空表格 (Tab 1) -->
            <div v-if="activeTab === 1" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  时空表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">日期</th>
                      <th class="py-2 px-2 font-medium">时间</th>
                      <th class="py-2 px-2 font-medium">地点（当前描写）</th>
                      <th class="py-2 px-2 font-medium">此地角色</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">1</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ spatioTemporal.date || "第一幕 · 初始篇" }}</td>
                      <td class="py-2 px-2 font-mono">{{ spatioTemporal.time || "清晨" }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ spatioTemporal.location || "起始之境" }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ spatioTemporal.characters.join("、") || "无在场角色" }}</td>
                      <td class="py-2 px-2 text-center">
                        <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]" title="编辑">
                          <Edit2 class="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 状态专属表格 2: 玩家状态表 (Tab 1) -->
            <div v-if="activeTab === 1" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  玩家状态表
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    @click="addPlayerState"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">属性类型</th>
                      <th class="py-2 px-2 font-medium">属性名</th>
                      <th class="py-2 px-2 font-medium">当前值</th>
                      <th class="py-2 px-2 font-medium">最大值</th>
                      <th class="py-2 px-2 font-medium">备注</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="state in playerStates"
                      :key="state.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ state.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#A8A29E]">{{ state.type }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ state.name }}</td>
                      <td class="py-2 px-2 font-mono text-[#F9C86D] font-bold">{{ state.currentVal }}</td>
                      <td class="py-2 px-2 font-mono text-[#A8A29E]">{{ state.maxVal }}</td>
                      <td class="py-2 px-2 max-w-[200px] truncate text-[#A8A29E]" :title="state.desc">
                        {{ state.desc }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </section>

      </main>

    </aside>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}
</style>
