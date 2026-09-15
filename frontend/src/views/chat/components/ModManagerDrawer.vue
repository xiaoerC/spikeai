<script setup lang="ts">
/**
 * Mod 模组生态与优先级加载流水线黑金管理抽屉 (ModManagerDrawer)
 *
 * 遵循 Obsidian Gold Glassmorphism 高奢黑金拟物视觉与 Mobile-First 规范。
 * 支持 Mod 广场检索、官方预设一键激活、优先级拖拽/上下调序、实时生效统计与自定义 Mod 创建。
 *
 * @packageDocumentation
 */

import AppButton from "@/components/common/AppButton.vue";
import AppModal from "@/components/common/AppModal.vue";
import {
  type ModItem,
  type ModPrioritySummary,
  type UserActiveModItem,
  modService,
} from "@/services/mod";
import { computed, onMounted, ref, watch } from "vue";

interface Props {
  open: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<(e: "update:open", val: boolean) => void>();

// ================= 核心状态 =================
const currentTab = ref<"active" | "square">("active");
const isLoading = ref(false);
const toastMessage = ref("");

// 已激活 Mod 列表与统计
const activeMods = ref<UserActiveModItem[]>([]);
const summary = ref<ModPrioritySummary>({
  active_count: 0,
  worldbook_entries_count: 0,
  worldbook_words_count: 0,
  system_prompt_entries_count: 0,
  system_prompt_words_count: 0,
  has_performance_warning: false,
});

// Mod 广场列表与搜索过滤
const squareMods = ref<ModItem[]>([]);
const squareCategory = ref<string>("all");
const squareKeyword = ref<string>("");
const squareSort = ref<string>("heat");

// 自定义 Mod 创建/编辑弹窗
const isCreateModalOpen = ref(false);
const isEditingMod = ref(false);
const editingModId = ref<string | null>(null);

const modForm = ref({
  title: "",
  description: "",
  category_tag: "system",
  anchor: "bottom_an",
  content: "",
});

function showToast(msg: string) {
  toastMessage.value = msg;
  setTimeout(() => {
    toastMessage.value = "";
  }, 2500);
}

// ================= 数据加载 =================
async function loadActiveMods() {
  try {
    isLoading.value = true;
    const [mods, sum] = await Promise.all([
      modService.fetchActiveMods(),
      modService.fetchModSummary(),
    ]);
    activeMods.value = mods;
    summary.value = sum;
  } catch (err: any) {
    showToast("加载已激活 Mod 列表失败");
  } finally {
    isLoading.value = false;
  }
}

async function loadSquareMods() {
  try {
    isLoading.value = true;
    const res = await modService.fetchModSquare({
      category: squareCategory.value === "all" ? undefined : squareCategory.value,
      keyword: squareKeyword.value.trim() || undefined,
      sort: squareSort.value,
      page: 1,
      page_size: 30,
    });
    squareMods.value = res.items;
  } catch (err: any) {
    showToast("加载 Mod 广场失败");
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      loadActiveMods();
      if (currentTab.value === "square") {
        loadSquareMods();
      }
    }
  },
);

watch(currentTab, (newTab) => {
  if (newTab === "square") {
    loadSquareMods();
  } else {
    loadActiveMods();
  }
});

// ================= 优先级调整与启停 =================
async function handleMovePriority(index: number, direction: "up" | "down") {
  const targetIndex = direction === "up" ? index - 1 : index + 1;
  if (targetIndex < 0 || targetIndex >= activeMods.value.length) return;

  const list = [...activeMods.value];
  const temp = list[index];
  list[index] = list[targetIndex];
  list[targetIndex] = temp;

  // 重新分配 priority_order (从上往下降序，排在最上面的为最大值)
  const total = list.length;
  const payload = list.map((item, idx) => ({
    mod_id: item.mod_id,
    priority_order: (total - idx) * 10,
    is_active: item.is_active,
  }));

  try {
    const updated = await modService.updateModPriorities(payload);
    activeMods.value = updated;
    summary.value = await modService.fetchModSummary();
    showToast(direction === "up" ? "已提升优先级 ↑" : "已降低优先级 ↓");
  } catch (err) {
    showToast("调整优先级失败");
  }
}

async function handleToggleMod(item: UserActiveModItem) {
  try {
    const updated = await modService.toggleModActivate(item.mod_id, !item.is_active);
    item.is_active = updated.is_active;
    summary.value = await modService.fetchModSummary();
    showToast(item.is_active ? "Mod 已启用" : "Mod 已停用");
  } catch (err) {
    showToast("切换 Mod 状态失败");
  }
}

async function handleAddFromSquare(mod: ModItem) {
  try {
    await modService.toggleModActivate(mod.id, true);
    showToast(`已成功添加并激活「${mod.title}」！`);
    await loadActiveMods();
  } catch (err) {
    showToast("添加 Mod 失败");
  }
}

// 检查某个 Mod 是否已在激活列表中
function isModInActiveList(modId: string): boolean {
  return activeMods.value.some((m) => m.mod_id === modId && m.is_active);
}

// ================= 自定义 Mod 创建 =================
function handleOpenCreateModal() {
  isEditingMod.value = false;
  editingModId.value = null;
  modForm.value = {
    title: "",
    description: "",
    category_tag: "system",
    anchor: "bottom_an",
    content: "",
  };
  isCreateModalOpen.value = true;
}

async function handleSaveCustomMod() {
  if (!modForm.value.title.trim()) {
    showToast("请输入 Mod 标题");
    return;
  }
  if (!modForm.value.content.trim()) {
    showToast("请输入提示词设定内容");
    return;
  }

  try {
    const newMod = await modService.createMod({
      title: modForm.value.title.trim(),
      description: modForm.value.description.trim() || "用户自定义扩展模组",
      category_tag: modForm.value.category_tag,
      price: 0,
      status: "published",
      entries: [
        {
          anchor: modForm.value.anchor,
          title: modForm.value.title.trim(),
          content: modForm.value.content.trim(),
          enabled: true,
          order: 10,
        },
      ],
    });

    // 自动为当前用户激活该 Mod
    await modService.toggleModActivate(newMod.id, true);
    isCreateModalOpen.value = false;
    showToast("自定义 Mod 创建并激活成功！");
    await loadActiveMods();
  } catch (err) {
    showToast("保存 Mod 失败");
  }
}

function getCategoryBadge(tag: string): { label: string; color: string } {
  switch (tag) {
    case "artist":
      return { label: "🎨 画师分镜", color: "bg-[#F9C86D]/15 text-[#F9C86D] border-[#F9C86D]/40" };
    case "system":
      return { label: "🎭 深度描写", color: "bg-[#A855F7]/15 text-[#A855F7] border-[#A855F7]/40" };
    case "command":
      return { label: "⚔️ 战斗指令", color: "bg-[#3B82F6]/15 text-[#3B82F6] border-[#3B82F6]/40" };
    case "worldbook":
      return { label: "📖 世界书", color: "bg-[#10B981]/15 text-[#10B981] border-[#10B981]/40" };
    case "regex":
      return { label: "⚡ 正则规则", color: "bg-[#EC4899]/15 text-[#EC4899] border-[#EC4899]/40" };
    default:
      return { label: "🧩 扩展模组", color: "bg-white/10 text-white/80 border-white/20" };
  }
}
</script>

<template>
  <div>
    <!-- 抽屉暗黑遮罩 -->
    <div
      v-if="open"
      @click="emit('update:open', false)"
      class="fixed inset-0 z-40 bg-black/70 backdrop-blur-sm transition-opacity"
    />

    <!-- 黑金滑出抽屉面板 (Mobile-First Safe Area 适配) -->
    <div
      :class="[
        'fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-[#121214]/95 border-l border-[#2E2C29] backdrop-blur-2xl shadow-2xl flex flex-col transition-transform duration-300 ease-out select-none',
        open ? 'translate-x-0' : 'translate-x-full'
      ]"
    >
      <!-- 1. 顶部 Header -->
      <div class="px-5 py-4 border-b border-[#2E2C29]/80 flex items-center justify-between shrink-0">
        <div>
          <div class="flex items-center gap-2">
            <span class="text-lg">🧩</span>
            <h2 class="text-base font-bold text-[#F9C86D] tracking-wide font-serif">
              Mod 优先级扩展管理器
            </h2>
          </div>
          <p class="text-[11px] text-[#A8A29E] mt-0.5">
            基于 Transformer 注意力权重矩阵，越靠顶端优先级越高
          </p>
        </div>

        <button
          type="button"
          @click="emit('update:open', false)"
          class="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/10 text-[#A8A29E] hover:text-white flex items-center justify-center transition-colors cursor-pointer"
        >
          ✕
        </button>
      </div>

      <!-- 2. 当前生效统计横幅 -->
      <div class="px-5 py-3 bg-[#1C1A17]/80 border-b border-[#2E2C29]/60 shrink-0">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center gap-3">
            <div class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full bg-[#10B981] animate-pulse" />
              <span class="text-[#E7E5E4] font-medium">生效 Mod: {{ summary.active_count }} 个</span>
            </div>
            <span class="text-[#78716C]">|</span>
            <div class="text-[#A8A29E]">
              注入条目: <span class="text-[#F9C86D] font-mono">{{ summary.system_prompt_entries_count + summary.worldbook_entries_count }}</span>
            </div>
          </div>

          <div class="text-[11px] text-[#A8A29E] font-mono">
            约 {{ summary.system_prompt_words_count + summary.worldbook_words_count }} 字
          </div>
        </div>

        <!-- 性能超限黄色警告 -->
        <div
          v-if="summary.has_performance_warning"
          class="mt-2 px-2.5 py-1.5 rounded bg-[#FEF08A]/10 border border-[#FEF08A]/30 text-[#FEF08A] text-[11px] flex items-center gap-1.5"
        >
          <span>⚠️</span>
          <span>注入字数已超 4000 字，可能占用较多上下文预算</span>
        </div>
      </div>

      <!-- 3. Tab 切换按钮组 (已激活矩阵 / Mod 广场) -->
      <div class="px-5 pt-3 pb-2 border-b border-[#2E2C29]/60 flex items-center gap-2 shrink-0">
        <button
          type="button"
          @click="currentTab = 'active'"
          :class="[
            'flex-1 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center justify-center gap-1.5',
            currentTab === 'active'
              ? 'bg-[#F9C86D]/15 text-[#F9C86D] border border-[#F9C86D]/40 font-bold shadow-sm'
              : 'bg-white/5 text-[#A8A29E] hover:text-white border border-transparent'
          ]"
        >
          <span>⚡ 已激活矩阵</span>
          <span class="text-[10px] px-1.5 py-0.2 rounded-full bg-white/10 text-white font-mono">
            {{ activeMods.filter(m => m.is_active).length }}
          </span>
        </button>

        <button
          type="button"
          @click="currentTab = 'square'"
          :class="[
            'flex-1 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center justify-center gap-1.5',
            currentTab === 'square'
              ? 'bg-[#F9C86D]/15 text-[#F9C86D] border border-[#F9C86D]/40 font-bold shadow-sm'
              : 'bg-white/5 text-[#A8A29E] hover:text-white border border-transparent'
          ]"
        >
          <span>🏛️ Mod 广场</span>
          <span class="text-[10px] px-1.5 py-0.2 rounded-full bg-white/10 text-white font-mono">
            精选
          </span>
        </button>
      </div>

      <!-- 4. Tab 1: 已激活 Mod 列表主内容 -->
      <div v-if="currentTab === 'active'" class="flex-1 overflow-y-auto px-5 py-3 space-y-2.5">
        <div v-if="activeMods.length === 0" class="py-12 text-center text-xs text-[#78716C]">
          暂未激活任何 Mod，可前往「Mod 广场」挑选添加
        </div>

        <div
          v-for="(item, idx) in activeMods"
          :key="item.id"
          :class="[
            'p-3 rounded-xl border transition-all relative overflow-hidden flex flex-col gap-2',
            item.is_highest_priority
              ? 'border-[#F9C86D] bg-[#1F1C16]/90 shadow-[0_0_15px_rgba(249,200,109,0.15)]'
              : item.is_active
                ? 'border-[#383531] bg-[#181614]/80'
                : 'border-[#262422] bg-[#121110]/50 opacity-60'
          ]"
        >
          <!-- 最高优先级金色高光标识 -->
          <div
            v-if="item.is_highest_priority"
            class="absolute top-0 right-0 px-2 py-0.5 rounded-bl-lg bg-[#F9C86D] text-[#1C1917] text-[10px] font-bold tracking-wider uppercase"
          >
            ★ 最高优先级 (Top)
          </div>

          <div class="flex items-start justify-between gap-2 pr-14">
            <div class="flex flex-col gap-1">
              <div class="flex items-center gap-2 flex-wrap">
                <!-- 分类 Badge -->
                <span
                  :class="[
                    'text-[10px] px-1.5 py-0.5 rounded border font-medium',
                    getCategoryBadge(item.category_tag).color
                  ]"
                >
                  {{ getCategoryBadge(item.category_tag).label }}
                </span>

                <h3 class="text-xs font-bold text-[#E7E5E4] truncate max-w-[200px]">
                  {{ item.mod_title }}
                </h3>
              </div>

              <div class="text-[11px] text-[#A8A29E] flex items-center gap-2">
                <span>包含 {{ item.entries_count }} 个提示词条目</span>
                <span class="text-[#57534E]">·</span>
                <span class="font-mono text-[10px] text-[#78716C]">权值 #{{ item.priority_order }}</span>
              </div>
            </div>
          </div>

          <!-- 操作条 (上下移动调序 + 启停开关) -->
          <div class="flex items-center justify-between pt-2 border-t border-white/5">
            <!-- 上移 / 下移按钮 -->
            <div class="flex items-center gap-1">
              <button
                type="button"
                @click="handleMovePriority(idx, 'up')"
                :disabled="idx === 0"
                class="px-2 py-1 rounded bg-white/5 hover:bg-white/10 disabled:opacity-30 text-[#A8A29E] hover:text-white text-[11px] flex items-center gap-1 transition-colors cursor-pointer disabled:cursor-not-allowed"
                title="提升注意力优先级"
              >
                ▲ 升序
              </button>

              <button
                type="button"
                @click="handleMovePriority(idx, 'down')"
                :disabled="idx === activeMods.length - 1"
                class="px-2 py-1 rounded bg-white/5 hover:bg-white/10 disabled:opacity-30 text-[#A8A29E] hover:text-white text-[11px] flex items-center gap-1 transition-colors cursor-pointer disabled:cursor-not-allowed"
                title="降低注意力优先级"
              >
                ▼ 降序
              </button>
            </div>

            <!-- 启停 Switch Toggle -->
            <button
              type="button"
              @click="handleToggleMod(item)"
              :class="[
                'px-3 py-1 rounded-full text-xs font-medium transition-all cursor-pointer flex items-center gap-1.5',
                item.is_active
                  ? 'bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40'
                  : 'bg-white/5 text-[#78716C] border border-white/10'
              ]"
            >
              <span :class="['w-1.5 h-1.5 rounded-full', item.is_active ? 'bg-[#10B981]' : 'bg-[#78716C]']" />
              <span>{{ item.is_active ? "已启用" : "已停用" }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 5. Tab 2: Mod 广场主内容 -->
      <div v-else class="flex-1 overflow-y-auto px-5 py-3 space-y-3">
        <!-- 搜索与分类药丸 -->
        <div class="space-y-2">
          <input
            v-model="squareKeyword"
            @keyup.enter="loadSquareMods"
            placeholder="搜索 Mod 标题或功能说明..."
            class="w-full h-8 px-3 rounded-lg bg-white/5 border border-[#383531] text-xs text-[#E7E5E4] placeholder-[#78716C] focus:outline-none focus:border-[#F9C86D]"
          />

          <!-- 分类 Pills -->
          <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] scrollbar-none">
            <button
              v-for="cat in [
                { key: 'all', label: '全部' },
                { key: 'artist', label: '画师分镜' },
                { key: 'system', label: '深度描写' },
                { key: 'command', label: '战斗指令' },
                { key: 'worldbook', label: '世界书' },
              ]"
              :key="cat.key"
              @click="squareCategory = cat.key; loadSquareMods();"
              :class="[
                'px-2.5 py-1 rounded-full whitespace-nowrap transition-all cursor-pointer',
                squareCategory === cat.key
                  ? 'bg-[#F9C86D]/20 text-[#F9C86D] border border-[#F9C86D]/50 font-bold'
                  : 'bg-white/5 text-[#A8A29E] hover:text-white border border-transparent'
              ]"
            >
              {{ cat.label }}
            </button>
          </div>
        </div>

        <!-- Mod 广场卡片列表 -->
        <div class="space-y-2.5 pt-1">
          <div
            v-for="mod in squareMods"
            :key="mod.id"
            class="p-3.5 rounded-xl border border-[#2E2C29] bg-[#181614]/80 hover:border-[#F9C86D]/40 transition-all flex flex-col gap-2"
          >
            <div class="flex items-start justify-between gap-2">
              <div>
                <div class="flex items-center gap-1.5">
                  <span
                    :class="[
                      'text-[10px] px-1.5 py-0.2 rounded border font-medium',
                      getCategoryBadge(mod.category_tag).color
                    ]"
                  >
                    {{ getCategoryBadge(mod.category_tag).label }}
                  </span>
                  <h3 class="text-xs font-bold text-[#E7E5E4]">{{ mod.title }}</h3>
                </div>
                <p class="text-[11px] text-[#A8A29E] mt-1 line-clamp-2 leading-relaxed">
                  {{ mod.description }}
                </p>
              </div>

              <!-- 评分与使用量 -->
              <div class="text-right shrink-0">
                <div class="text-xs font-bold text-[#F9C86D]">⭐ {{ mod.rating.toFixed(1) }}</div>
                <div class="text-[10px] text-[#78716C] mt-0.5">{{ mod.downloads }} 次使用</div>
              </div>
            </div>

            <div class="flex items-center justify-between pt-2 border-t border-white/5">
              <span class="text-xs text-[#E7E5E4] font-mono">
                {{ mod.price === 0 ? "免费" : `★ ${mod.price}` }}
              </span>

              <button
                type="button"
                @click="handleAddFromSquare(mod)"
                :disabled="isModInActiveList(mod.id)"
                :class="[
                  'px-3 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer flex items-center gap-1',
                  isModInActiveList(mod.id)
                    ? 'bg-white/5 text-[#78716C] border border-white/10 cursor-not-allowed'
                    : 'bg-[#F9C86D] text-[#1C1917] hover:bg-[#F9C86D]/90 font-bold shadow'
                ]"
              >
                <span>{{ isModInActiveList(mod.id) ? "✓ 已启用" : "+ 添加并激活" }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 6. 底部固定操作区 (创建自定义 Mod) -->
      <div class="p-4 border-t border-[#2E2C29] bg-[#141312] flex items-center justify-between shrink-0 pb-safe">
        <button
          type="button"
          @click="handleOpenCreateModal"
          class="w-full py-2.5 rounded-xl bg-gradient-to-r from-[#F9C86D]/20 to-[#EAB308]/10 hover:from-[#F9C86D]/30 hover:to-[#EAB308]/20 border border-[#F9C86D]/50 text-[#F9C86D] text-xs font-bold transition-all flex items-center justify-center gap-2 cursor-pointer shadow-lg"
        >
          <span>＋ 新建自定义 Prompt Mod</span>
        </button>
      </div>
    </div>

    <!-- 7. 自定义 Mod 创建弹窗 (基于 AppModal) -->
    <AppModal
      v-model:open="isCreateModalOpen"
      title="新建自定义 Prompt Mod"
      description="配置专属提示词并挂载至指定的插桩槽位"
      custom-class="w-[90vw] max-w-[500px]"
    >
      <div class="space-y-3 py-2 text-xs">
        <div>
          <label class="block text-[#A8A29E] mb-1">Mod 标题</label>
          <input
            v-model="modForm.title"
            placeholder="例如：赛博朋克霓虹光影强化"
            class="w-full h-8 px-3 rounded-lg bg-white/5 border border-[#383531] text-xs text-[#E7E5E4] focus:outline-none focus:border-[#F9C86D]"
          />
        </div>

        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-[#A8A29E] mb-1">分类标签</label>
            <select
              v-model="modForm.category_tag"
              class="w-full h-8 px-2 rounded-lg bg-[#1C1917] border border-[#383531] text-xs text-[#E7E5E4] focus:outline-none focus:border-[#F9C86D]"
            >
              <option value="system">🎭 深度描写 (system)</option>
              <option value="artist">🎨 画师分镜 (artist)</option>
              <option value="command">⚔️ 战斗指令 (command)</option>
              <option value="worldbook">📖 世界观 (worldbook)</option>
            </select>
          </div>

          <div>
            <label class="block text-[#A8A29E] mb-1">插桩锚点 (Slot)</label>
            <select
              v-model="modForm.anchor"
              class="w-full h-8 px-2 rounded-lg bg-[#1C1917] border border-[#383531] text-xs text-[#E7E5E4] focus:outline-none focus:border-[#F9C86D]"
            >
              <option value="bottom_an">底部描写增强 (bottom_an)</option>
              <option value="before_char">角色人设前置 (before_char)</option>
              <option value="system_prefix">最高系统指令 (system_prefix)</option>
              <option value="user_suffix">输入后置引导 (user_suffix)</option>
            </select>
          </div>
        </div>

        <div>
          <label class="block text-[#A8A29E] mb-1">功能简要说明</label>
          <input
            v-model="modForm.description"
            placeholder="简要说明该 Mod 的作用和特色..."
            class="w-full h-8 px-3 rounded-lg bg-white/5 border border-[#383531] text-xs text-[#E7E5E4] focus:outline-none focus:border-[#F9C86D]"
          />
        </div>

        <div>
          <label class="block text-[#A8A29E] mb-1">提示词设定内容 (Prompt Body)</label>
          <textarea
            v-model="modForm.content"
            rows="5"
            placeholder="输入具体要注入大模型的 System Prompt 或设定指令..."
            class="w-full p-2.5 rounded-lg bg-white/5 border border-[#383531] text-xs text-[#E7E5E4] leading-relaxed focus:outline-none focus:border-[#F9C86D]"
          />
        </div>
      </div>

      <template #footer>
        <AppButton variant="ghost" @click="isCreateModalOpen = false">取消</AppButton>
        <AppButton variant="gold" @click="handleSaveCustomMod">创建并激活</AppButton>
      </template>
    </AppModal>

    <!-- 轻提示 Toast -->
    <Transition name="fade">
      <div
        v-if="toastMessage"
        class="fixed bottom-20 left-1/2 -translate-x-1/2 z-50 px-4 py-2 rounded-full bg-black/90 border border-[#F9C86D]/50 text-[#F9C86D] text-xs shadow-2xl backdrop-blur-md"
      >
        {{ toastMessage }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
