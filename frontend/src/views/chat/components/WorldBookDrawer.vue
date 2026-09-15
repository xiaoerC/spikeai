<script setup lang="ts">
/**
 * 世界书 (World Book) 沉浸式黑金抽屉与条目管理
 *
 * 遵循 黑金 Obsidian Gold 视觉设计与移动端防遮挡规范，
 * 支持词条增删改查、常驻/关键词切换、次级条件逻辑与 SillyTavern 导入导出。
 */

import AppButton from "@/components/common/AppButton.vue";
import AppModal from "@/components/common/AppModal.vue";
import {
  type WorldBookDetail,
  type WorldBookEntryItem,
  type WorldBookItem,
  worldBookService,
} from "@/services/worldBook";
import { computed, onMounted, ref, watch } from "vue";

interface Props {
  open: boolean;
  characterId?: string;
  characterName?: string;
}

const props = defineProps<Props>();
const emit = defineEmits<(e: "update:open", val: boolean) => void>();

// ================= 状态定义 =================
const isLoading = ref(false);
const worldBooks = ref<WorldBookItem[]>([]);
const currentBook = ref<WorldBookDetail | null>(null);
const selectedBookId = ref<string>("");
const toastMessage = ref("");

// 词条编辑弹窗状态
const isEntryModalOpen = ref(false);
const isEditing = ref(false);
const editingEntryId = ref<string | null>(null);

const entryForm = ref({
  keysInput: "",
  secondaryKeysInput: "",
  selectiveLogic: 0,
  content: "",
  comment: "",
  constant: false,
  enabled: true,
  insertionOrder: 100,
});

// JSON 导入弹窗
const isImportModalOpen = ref(false);
const importJsonText = ref("");

function showToast(msg: string) {
  toastMessage.value = msg;
  setTimeout(() => {
    toastMessage.value = "";
  }, 2000);
}

// ================= 数据加载与联动 =================
async function loadWorldBooks() {
  try {
    isLoading.value = true;
    const list = await worldBookService.listWorldBooks(props.characterId);
    worldBooks.value = list;
    if (list.length > 0) {
      if (!selectedBookId.value || !list.some((b) => b.id === selectedBookId.value)) {
        selectedBookId.value = list[0].id;
      }
      await loadCurrentBookDetail(selectedBookId.value);
    } else {
      currentBook.value = null;
    }
  } catch (err: any) {
    console.error("加载世界书失败:", err);
  } finally {
    isLoading.value = false;
  }
}

async function loadCurrentBookDetail(bookId: string) {
  if (!bookId) return;
  try {
    isLoading.value = true;
    const detail = await worldBookService.getWorldBookDetail(bookId);
    currentBook.value = detail;
  } catch (err: any) {
    showToast("拉取世界书条目失败");
  } finally {
    isLoading.value = false;
  }
}

watch(
  () => props.open,
  (val) => {
    if (val) {
      loadWorldBooks();
    }
  },
);

watch(selectedBookId, (newId) => {
  if (newId) {
    loadCurrentBookDetail(newId);
  }
});

// ================= 词条操作 =================
function handleOpenCreateEntry() {
  if (!currentBook.value) {
    handleCreateDefaultBook();
    return;
  }
  isEditing.value = false;
  editingEntryId.value = null;
  entryForm.value = {
    keysInput: "",
    secondaryKeysInput: "",
    selectiveLogic: 0,
    content: "",
    comment: "",
    constant: false,
    enabled: true,
    insertionOrder: (currentBook.value.entries.length + 1) * 10,
  };
  isEntryModalOpen.value = true;
}

function handleOpenEditEntry(entry: WorldBookEntryItem) {
  isEditing.value = true;
  editingEntryId.value = entry.id;
  entryForm.value = {
    keysInput: (entry.keys || []).join(", "),
    secondaryKeysInput: (entry.secondary_keys || []).join(", "),
    selectiveLogic: entry.selective_logic ?? 0,
    content: entry.content,
    comment: entry.comment,
    constant: entry.constant,
    enabled: entry.enabled,
    insertionOrder: entry.insertion_order,
  };
  isEntryModalOpen.value = true;
}

async function handleSaveEntry() {
  if (!currentBook.value) return;
  if (!entryForm.value.content.trim()) {
    showToast("设定内容不能为空");
    return;
  }

  const keys = entryForm.value.keysInput
    .split(/[,，]/)
    .map((s) => s.trim())
    .filter(Boolean);

  const secondaryKeys = entryForm.value.secondaryKeysInput
    .split(/[,，]/)
    .map((s) => s.trim())
    .filter(Boolean);

  try {
    if (isEditing.value && editingEntryId.value) {
      await worldBookService.updateEntry(editingEntryId.value, {
        keys,
        secondary_keys: secondaryKeys,
        selective_logic: entryForm.value.selectiveLogic,
        content: entryForm.value.content.trim(),
        comment: entryForm.value.comment.trim(),
        constant: entryForm.value.constant,
        enabled: entryForm.value.enabled,
        insertion_order: Number(entryForm.value.insertionOrder),
      });
      showToast("词条修改成功");
    } else {
      await worldBookService.addEntry(currentBook.value.id, {
        keys,
        secondary_keys: secondaryKeys,
        selective_logic: entryForm.value.selectiveLogic,
        content: entryForm.value.content.trim(),
        comment: entryForm.value.comment.trim(),
        constant: entryForm.value.constant,
        enabled: entryForm.value.enabled,
        insertion_order: Number(entryForm.value.insertionOrder),
      });
      showToast("词条添加成功");
    }
    isEntryModalOpen.value = false;
    await loadCurrentBookDetail(currentBook.value.id);
  } catch (err: any) {
    showToast("保存词条失败");
  }
}

async function handleToggleEntry(entry: WorldBookEntryItem) {
  try {
    const updated = await worldBookService.updateEntry(entry.id, {
      enabled: !entry.enabled,
    });
    entry.enabled = updated.enabled;
    showToast(entry.enabled ? "已启用词条" : "已停用词条");
  } catch (err) {
    showToast("切换状态失败");
  }
}

async function handleDeleteEntry(entryId: string) {
  if (!confirm("确定要删除该条目设定吗？")) return;
  try {
    await worldBookService.deleteEntry(entryId);
    showToast("词条已删除");
    if (currentBook.value) {
      await loadCurrentBookDetail(currentBook.value.id);
    }
  } catch (err) {
    showToast("删除失败");
  }
}

// 快速创建一本默认世界书
async function handleCreateDefaultBook() {
  try {
    const newBook = await worldBookService.createWorldBook({
      name: `${props.characterName || "角色"}的世界书`,
      description: "包含专属背景设定、术式体系与地理历史",
      character_id: props.characterId,
      entries: [
        {
          keys: ["草薙剑", "佐助"],
          content: "草薙剑是师傅宇智波佐助托付给博人的佩剑，锋利无比且可注入雷遁查克拉。",
          comment: "佩剑信物",
          constant: false,
          insertion_order: 10,
        },
      ],
    });
    selectedBookId.value = newBook.id;
    await loadWorldBooks();
    showToast("已初始化专属世界书！");
  } catch (err) {
    showToast("创建世界书失败");
  }
}

// ================= SillyTavern 导入与导出 =================
async function handleExportJson() {
  if (!currentBook.value) return;
  try {
    const data = await worldBookService.exportSillyTavern(currentBook.value.id);
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${currentBook.value.name}_SillyTavern.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast("已成功导出 SillyTavern 格式 JSON！");
  } catch (err) {
    showToast("导出失败");
  }
}

async function handleImportJson() {
  if (!importJsonText.value.trim()) {
    showToast("请输入有效 JSON 内容");
    return;
  }
  try {
    const parsed = JSON.parse(importJsonText.value.trim());
    const imported = await worldBookService.importSillyTavern({
      name: parsed.name || "导入的世界书",
      description: parsed.description || "从 SillyTavern 导入",
      character_id: props.characterId,
      entries: parsed.entries || parsed,
    });
    isImportModalOpen.value = false;
    importJsonText.value = "";
    selectedBookId.value = imported.id;
    await loadWorldBooks();
    showToast("成功导入 SillyTavern 世界书！");
  } catch (err: any) {
    showToast("解析或导入 JSON 失败，请检查格式");
  }
}
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 overflow-hidden flex justify-end"
    @click.self="emit('update:open', false)"
  >
    <!-- 背景遮罩 -->
    <div
      class="fixed inset-0 bg-black/70 backdrop-blur-sm transition-opacity"
      @click="emit('update:open', false)"
    />

    <!-- 抽屉主体 (黑金暗黑拟物) -->
    <aside
      class="relative z-10 w-full max-w-[540px] h-full bg-[#161311] border-l border-[#F9C86D]/20 shadow-2xl flex flex-col overflow-hidden text-[#E6E4DF]"
    >
      <!-- 1. Header (严格 56px 弹性居中) -->
      <header class="h-14 px-5 flex items-center justify-between border-b border-white/10 bg-[#1C1815] shrink-0">
        <div class="flex items-center gap-2.5">
          <div class="w-2.5 h-2.5 rounded-full bg-[#F9C86D] shadow-[0_0_8px_#F9C86D]" />
          <h2 class="text-base font-bold text-[#F9C86D] tracking-wide leading-none flex items-center gap-1.5">
            <span>📖 世界书设定集</span>
            <span class="text-xs text-[#A8A29E] font-normal">(World Book RAG)</span>
          </h2>
        </div>

        <div class="flex items-center gap-2">
          <!-- 导出按钮 -->
          <button
            v-if="currentBook"
            class="px-2.5 py-1 rounded-md text-xs bg-white/5 hover:bg-white/10 text-[#D6D3D1] border border-white/10 transition-colors"
            title="导出为 SillyTavern JSON"
            @click="handleExportJson"
          >
            导出
          </button>
          <!-- 导入按钮 -->
          <button
            class="px-2.5 py-1 rounded-md text-xs bg-white/5 hover:bg-white/10 text-[#D6D3D1] border border-white/10 transition-colors"
            title="导入 SillyTavern JSON"
            @click="isImportModalOpen = true"
          >
            导入
          </button>
          <!-- 关闭按钮 -->
          <button
            class="w-8 h-8 flex items-center justify-center rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/5 transition-colors"
            @click="emit('update:open', false)"
          >
            <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </button>
        </div>
      </header>

      <!-- 2. 世界书切换与参数条 -->
      <div class="p-4 border-b border-white/5 bg-[#1A1613] flex flex-col gap-3 shrink-0">
        <div class="flex items-center justify-between gap-3">
          <div class="flex-1 flex items-center gap-2">
            <span class="text-xs text-[#A8A29E] whitespace-nowrap">当前世界书:</span>
            <select
              v-if="worldBooks.length > 0"
              v-model="selectedBookId"
              class="flex-1 bg-[#241F1C] border border-white/10 rounded-lg px-2.5 py-1.5 text-xs text-[#F9C86D] focus:outline-none focus:border-[#F9C86D]/50 cursor-pointer"
            >
              <option v-for="b in worldBooks" :key="b.id" :value="b.id">
                {{ b.name }} ({{ b.entry_count }} 词条)
              </option>
            </select>
            <span v-else class="text-xs text-[#78716C]">暂无可用世界书</span>
          </div>

          <button
            class="px-3 py-1.5 rounded-lg bg-[#F9C86D] text-[#161311] text-xs font-bold hover:bg-[#FFE3A8] transition-colors shrink-0 flex items-center gap-1 shadow-[0_0_12px_rgba(249,200,109,0.2)]"
            @click="handleOpenCreateEntry"
          >
            <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M12 5v14M5 12h14" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
            <span>+ 新增词条</span>
          </button>
        </div>

        <div v-if="currentBook" class="flex items-center justify-between text-[11px] text-[#A8A29E] px-1">
          <div class="flex items-center gap-3">
            <span>扫描深度: <b class="text-[#D6D3D1]">{{ currentBook.scan_depth }} 轮</b></span>
            <span>Token 预算: <b class="text-[#D6D3D1]">{{ currentBook.token_budget }}</b></span>
          </div>
          <span class="text-[#78716C] italic">{{ currentBook.description || "无描述" }}</span>
        </div>
      </div>

      <!-- 3. 词条列表展示区 (滚动) -->
      <main class="flex-1 overflow-y-auto p-4 flex flex-col gap-3">
        <!-- 空状态 -->
        <div
          v-if="!currentBook || currentBook.entries.length === 0"
          class="flex-1 flex flex-col items-center justify-center py-16 text-center"
        >
          <div class="w-16 h-16 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center text-3xl mb-4 text-[#F9C86D]/60">
            📜
          </div>
          <p class="text-sm font-medium text-[#D6D3D1] mb-1">暂无世界书词条</p>
          <p class="text-xs text-[#78716C] max-w-xs mb-4">
            添加设定词条后，当聊天中提及对应关键词时，AI 将自动加载专属深度世界观。
          </p>
          <AppButton size="sm" variant="gold" @click="handleOpenCreateEntry">
            立即创建第一个词条
          </AppButton>
        </div>

        <!-- 词条卡片列表 -->
        <div
          v-for="entry in currentBook?.entries"
          :key="entry.id"
          class="group p-3.5 rounded-xl bg-[#1C1815] border border-white/10 hover:border-[#F9C86D]/40 transition-all flex flex-col gap-2.5 relative"
          :class="{ 'opacity-50': !entry.enabled }"
        >
          <!-- 卡片头部: 标题/备注 + 状态标签 + 操作 -->
          <div class="flex items-center justify-between gap-2">
            <div class="flex items-center gap-2 flex-wrap">
              <span class="text-xs font-bold text-[#F9C86D]">
                {{ entry.comment || "未命名设定" }}
              </span>
              <!-- 常驻标记 -->
              <span
                v-if="entry.constant"
                class="px-1.5 py-0.5 rounded text-[10px] font-bold bg-[#EF4444]/20 text-[#F87171] border border-[#EF4444]/30"
              >
                ★ 常驻生效
              </span>
              <!-- 优先级权重 -->
              <span class="text-[10px] text-[#78716C] font-mono">
                #{{ entry.insertion_order }}
              </span>
            </div>

            <!-- 开关与操作按钮 -->
            <div class="flex items-center gap-1.5">
              <button
                class="px-2 py-0.5 rounded text-[10px] transition-colors"
                :class="entry.enabled ? 'bg-[#22C55E]/20 text-[#4ADE80] border border-[#22C55E]/30' : 'bg-white/5 text-[#78716C]'"
                @click="handleToggleEntry(entry)"
              >
                {{ entry.enabled ? "已启用" : "已停用" }}
              </button>
              <button
                class="p-1 rounded text-[#A8A29E] hover:text-[#F9C86D] hover:bg-white/5 transition-colors"
                title="编辑"
                @click="handleOpenEditEntry(entry)"
              >
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                  <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                </svg>
              </button>
              <button
                class="p-1 rounded text-[#A8A29E] hover:text-[#EF4444] hover:bg-white/5 transition-colors"
                title="删除"
                @click="handleDeleteEntry(entry.id)"
              >
                <svg class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                </svg>
              </button>
            </div>
          </div>

          <!-- 关键词 Tags -->
          <div v-if="!entry.constant && entry.keys && entry.keys.length > 0" class="flex flex-wrap gap-1.5 items-center">
            <span class="text-[10px] text-[#78716C]">触发词:</span>
            <span
              v-for="k in entry.keys"
              :key="k"
              class="px-2 py-0.5 rounded-full text-[10px] bg-[#F9C86D]/10 text-[#F9C86D] border border-[#F9C86D]/30"
            >
              {{ k }}
            </span>
            <span v-if="entry.secondary_keys && entry.secondary_keys.length > 0" class="text-[10px] text-[#78716C] ml-1">
              + 次级: {{ entry.secondary_keys.join(", ") }}
            </span>
          </div>

          <!-- 设定内容正文 -->
          <div class="p-2.5 rounded-lg bg-[#14110F] border border-white/5 text-xs text-[#D6D3D1] leading-relaxed break-words font-sans">
            {{ entry.content }}
          </div>
        </div>
      </main>

      <!-- 4. Toast 轻提示 -->
      <div
        v-if="toastMessage"
        class="absolute bottom-5 left-1/2 -translate-x-1/2 px-4 py-2 rounded-lg bg-[#292524] text-[#F9C86D] text-xs font-bold shadow-xl border border-[#F9C86D]/40 z-50 animate-fade-in"
      >
        {{ toastMessage }}
      </div>
    </aside>

    <!-- 5. 词条编辑/新增 抽屉内滑入面板 (绝对定位高层级) -->
    <div
      v-if="isEntryModalOpen"
      class="absolute inset-0 z-30 bg-[#161311]/95 backdrop-blur-md flex flex-col p-5 animate-fade-in"
    >
      <header class="h-10 flex items-center justify-between border-b border-white/10 pb-3 mb-4">
        <h3 class="text-sm font-bold text-[#F9C86D]">
          {{ isEditing ? '编辑设定词条' : '新建设定词条' }}
        </h3>
        <button
          class="text-xs text-[#A8A29E] hover:text-white px-2 py-1"
          @click="isEntryModalOpen = false"
        >
          ✕ 取消
        </button>
      </header>

      <div class="flex-1 overflow-y-auto flex flex-col gap-4 text-xs text-[#E6E4DF] pr-1">
        <!-- 备注/标题 -->
        <div class="flex flex-col gap-1.5">
          <label class="font-bold text-[#A8A29E]">词条备注 / 标题</label>
          <input
            v-model="entryForm.comment"
            type="text"
            placeholder="例如: 草薙剑之誓 / 净眼时空秘术"
            class="bg-[#1C1815] border border-white/10 rounded-lg px-3 py-2 text-xs text-[#E6E4DF] focus:outline-none focus:border-[#F9C86D]/60"
          />
        </div>

        <!-- 常驻开关 -->
        <div class="flex items-center justify-between p-3 rounded-lg bg-[#1C1815] border border-white/10">
          <div>
            <div class="font-bold text-[#F9C86D]">常驻生效 (Constant)</div>
            <div class="text-[11px] text-[#78716C]">开启后无论是否命中关键词，每次对话均强制注入 Prompt</div>
          </div>
          <input
            v-model="entryForm.constant"
            type="checkbox"
            class="w-4 h-4 accent-[#F9C86D] cursor-pointer"
          />
        </div>

        <!-- 主关键词 -->
        <div v-if="!entryForm.constant" class="flex flex-col gap-1.5">
          <label class="font-bold text-[#A8A29E]">主触发关键词 (逗号分隔)</label>
          <input
            v-model="entryForm.keysInput"
            type="text"
            placeholder="例如: 草薙剑, 佐助, 佩剑"
            class="bg-[#1C1815] border border-white/10 rounded-lg px-3 py-2 text-xs text-[#E6E4DF] focus:outline-none focus:border-[#F9C86D]/60"
          />
        </div>

        <!-- 次级关键词 -->
        <div v-if="!entryForm.constant" class="flex flex-col gap-1.5">
          <label class="font-bold text-[#A8A29E]">次级过滤词 (Secondary Keys，可选)</label>
          <input
            v-model="entryForm.secondaryKeysInput"
            type="text"
            placeholder="例如: 木叶, 爪垢"
            class="bg-[#1C1815] border border-white/10 rounded-lg px-3 py-2 text-xs text-[#E6E4DF] focus:outline-none focus:border-[#F9C86D]/60"
          />
        </div>

        <!-- 设定内容 -->
        <div class="flex flex-col gap-1.5">
          <label class="font-bold text-[#A8A29E]">设定具体内容 (Markdown / 纯文本)</label>
          <textarea
            v-model="entryForm.content"
            rows="5"
            placeholder="输入注入大模型 System Prompt 的核心设定描写..."
            class="bg-[#1C1815] border border-white/10 rounded-lg p-3 text-xs text-[#E6E4DF] focus:outline-none focus:border-[#F9C86D]/60 resize-none font-sans"
          />
        </div>

        <!-- 优先级权重 -->
        <div class="flex items-center justify-between">
          <label class="font-bold text-[#A8A29E]">插入优先级权重</label>
          <input
            v-model.number="entryForm.insertionOrder"
            type="number"
            class="w-24 bg-[#1C1815] border border-white/10 rounded-lg px-2 py-1 text-xs text-center text-[#F9C86D]"
          />
        </div>
      </div>

      <div class="flex justify-end gap-2 pt-3 border-t border-white/10 shrink-0">
        <AppButton size="sm" variant="ghost" @click="isEntryModalOpen = false">取消</AppButton>
        <AppButton size="sm" variant="gold" @click="handleSaveEntry">保存词条</AppButton>
      </div>
    </div>

    <!-- 6. SillyTavern JSON 导入抽屉内面板 -->
    <div
      v-if="isImportModalOpen"
      class="absolute inset-0 z-30 bg-[#161311]/95 backdrop-blur-md flex flex-col p-5 animate-fade-in"
    >
      <header class="h-10 flex items-center justify-between border-b border-white/10 pb-3 mb-4">
        <h3 class="text-sm font-bold text-[#F9C86D]">导入 SillyTavern JSON 世界书</h3>
        <button
          class="text-xs text-[#A8A29E] hover:text-white px-2 py-1"
          @click="isImportModalOpen = false"
        >
          ✕ 取消
        </button>
      </header>

      <div class="flex-1 flex flex-col gap-3 text-xs text-[#E6E4DF]">
        <p class="text-[#A8A29E]">
          粘贴酒馆导出的标准世界书 JSON 内容：
        </p>
        <textarea
          v-model="importJsonText"
          rows="10"
          placeholder='{ "name": "...", "entries": { ... } }'
          class="flex-1 bg-[#1C1815] border border-white/10 rounded-lg p-3 text-xs text-[#E6E4DF] font-mono focus:outline-none focus:border-[#F9C86D]/60 resize-none"
        />
      </div>

      <div class="flex justify-end gap-2 pt-3 border-t border-white/10 shrink-0">
        <AppButton size="sm" variant="ghost" @click="isImportModalOpen = false">取消</AppButton>
        <AppButton size="sm" variant="gold" @click="handleImportJson">确认导入</AppButton>
      </div>
    </div>
  </div>
</template>
