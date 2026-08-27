<script setup lang="ts">
/**
 * 新建/编辑 Mod 合集模态弹窗 (Figma 109:11681 1:1 像素级高保真)
 *
 * 包含头部预选说明、合集名称、描述、已选 Mod 列表 (⠿拖拽手柄 + 移除)、已移除 Mod 列表 (虚线卡片 + 加回)、清空与保存。
 *
 * @packageDocumentation
 */

import type {
  CollectionModEntry,
  ModCollectionItem,
  PurchasedModItem,
} from "@/views/history/types";
import { ChevronDown, ChevronUp, GripVertical, X } from "lucide-vue-next";
import { computed, ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  collection: ModCollectionItem | null;
  allPurchasedMods: PurchasedModItem[];
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (
    e: "save",
    payload: {
      id?: string;
      title: string;
      description: string;
      mods: CollectionModEntry[];
    },
  ): void;
}>();

const localTitle = ref("");
const localDescription = ref("");
const selectedMods = ref<CollectionModEntry[]>([]);
const removedMods = ref<CollectionModEntry[]>([]);
const isRemovedExpanded = ref(true);

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      if (props.collection) {
        localTitle.value = props.collection.title || "";
        localDescription.value = props.collection.description || "";
        selectedMods.value = [...props.collection.mods];
        // 计算未选中的 mod
        const selectedIdSet = new Set(selectedMods.value.map((m) => m.id));
        removedMods.value = props.allPurchasedMods
          .filter((p) => !selectedIdSet.has(p.id))
          .map((p) => ({
            id: p.id,
            title: p.title,
            description: p.description,
          }));
      } else {
        localTitle.value = "";
        localDescription.value = "";
        // 默认预选前 4 个或全部已购 Mod
        selectedMods.value = props.allPurchasedMods.slice(0, 4).map((p) => ({
          id: p.id,
          title: p.title,
          description: p.description,
        }));
        removedMods.value = props.allPurchasedMods.slice(4).map((p) => ({
          id: p.id,
          title: p.title,
          description: p.description,
        }));
      }
      isRemovedExpanded.value = true;
    }
  },
  { immediate: true },
);

const totalModsCount = computed(() => selectedMods.value.length + removedMods.value.length);
const isFormValid = computed(() => Boolean(localTitle.value.trim()));

function handleRemoveMod(index: number) {
  const mod = selectedMods.value.splice(index, 1)[0];
  if (mod) {
    removedMods.value.unshift(mod);
  }
}

function handleAddBackMod(index: number) {
  const mod = removedMods.value.splice(index, 1)[0];
  if (mod) {
    selectedMods.value.push(mod);
  }
}

function handleClearAll() {
  removedMods.value.push(...selectedMods.value);
  selectedMods.value = [];
}

function handleSave() {
  if (!isFormValid.value) return;
  emit("save", {
    id: props.collection?.id,
    title: localTitle.value,
    description: localDescription.value,
    mods: selectedMods.value,
  });
}

function handleClose() {
  emit("update:open", false);
}
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4 overflow-y-auto"
  >
    <div class="w-full max-w-[408px] max-h-[90vh] rounded-[12px] border border-[#44403C] bg-[#292524] flex flex-col overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-200">
      <!-- 1. 头部 Header (Figma 109:11681) -->
      <div class="flex items-start justify-between p-5 border-b border-[#44403C]">
        <div class="flex flex-col">
          <h3 class="text-[16px] leading-[20px] font-semibold text-[#F5F5F4] tracking-[-0.32px]">
            {{ collection ? "编辑合集" : "新建合集" }}
          </h3>
          <p class="text-[12px] leading-[16px] text-[#78716C] pt-1">
            已预选你的全部 Mod（{{ totalModsCount }} 个），拖拽排序或移除不需要的
          </p>
        </div>

        <button
          type="button"
          @click="handleClose"
          class="p-1 rounded-[4px] text-[#78716C] hover:text-[#F5F5F4] transition-colors cursor-pointer select-none"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- 2. 可滚动表单区域 (Figma 109:11681) -->
      <div class="flex-1 overflow-y-auto p-5 flex flex-col gap-4">
        <!-- 合集名称 -->
        <div class="flex flex-col">
          <label class="text-[12px] leading-[16px] text-[#A8A29E] pb-1.5">
            合集名称
          </label>
          <input
            v-model="localTitle"
            type="text"
            placeholder="例如: 极致沉浸式角色扮演合集"
            class="w-full h-[37px] px-3 rounded-[6px] border border-[#44403C] bg-[#292524] text-[14px] text-[#F5F5F4] placeholder-[#F5F5F4]/40 focus:border-[#F9C86D] focus:outline-none transition-colors"
          />
        </div>

        <!-- 描述（可选） -->
        <div class="flex flex-col">
          <label class="text-[12px] leading-[16px] text-[#A8A29E] pb-1.5">
            描述（可选）
          </label>
          <textarea
            v-model="localDescription"
            rows="2"
            placeholder="介绍这个合集的用途..."
            class="w-full p-2.5 rounded-[6px] border border-[#44403C] bg-[#292524] text-[14px] leading-[20px] text-[#F5F5F4] placeholder-[#F5F5F4]/40 focus:border-[#F9C86D] focus:outline-none resize-none transition-colors"
          ></textarea>
        </div>

        <!-- 合集内 Mod 列表 -->
        <div class="flex flex-col">
          <div class="flex items-center justify-between pb-1.5">
            <span class="text-[12px] leading-[16px] text-[#A8A29E]">
              合集内 Mod（{{ selectedMods.length }} 个，拖拽排序）
            </span>
            <button
              v-if="selectedMods.length > 0"
              type="button"
              @click="handleClearAll"
              class="px-2 py-0.5 rounded-[4px] bg-[#292524] text-[10px] leading-[17px] text-[#78716C] hover:text-[#EF4444] cursor-pointer select-none"
            >
              清空
            </button>
          </div>

          <!-- 选中的 Mod 项列表 (Figma 109:11681) -->
          <div class="flex flex-col gap-2">
            <div
              v-for="(mod, idx) in selectedMods"
              :key="mod.id"
              class="p-2.5 rounded-[8px] border border-[#44403C] bg-[#292524] flex items-center justify-between gap-2"
            >
              <!-- 拖拽抓手 + 标题/描述 -->
              <div class="flex items-center gap-2 flex-1 min-w-0">
                <GripVertical class="w-4 h-4 text-[#78716C] flex-shrink-0 cursor-grab" />
                <div class="flex flex-col min-w-0">
                  <span class="text-[14px] leading-[20px] text-[#F5F5F4] font-normal truncate">
                    {{ mod.title }}
                  </span>
                  <span class="text-[10px] leading-[14px] text-[#78716C] truncate">
                    {{ mod.description }}
                  </span>
                </div>
              </div>

              <!-- 移除按钮 -->
              <button
                type="button"
                @click="handleRemoveMod(idx)"
                class="px-2 py-0.5 rounded-[4px] text-[12px] leading-[16px] text-[#EF4444] hover:bg-[rgba(239,68,68,0.10)] flex-shrink-0 cursor-pointer select-none"
              >
                移除
              </button>
            </div>

            <div
              v-if="selectedMods.length === 0"
              class="py-4 text-center text-xs text-[#78716C]"
            >
              暂无选中的 Mod，请在下方点击「加回」添加
            </div>
          </div>
        </div>

        <!-- 已移除 Mod 折叠面板 (Figma 109:11681) -->
        <div v-if="removedMods.length > 0" class="flex flex-col pt-1">
          <button
            type="button"
            @click="isRemovedExpanded = !isRemovedExpanded"
            class="flex items-center gap-1 text-[12px] leading-[16px] text-[#78716C] hover:text-[#A8A29E] cursor-pointer select-none pb-2"
          >
            <component :is="isRemovedExpanded ? ChevronUp : ChevronDown" class="w-3.5 h-3.5" />
            <span>已移除 {{ removedMods.length }} 个 Mod（点击重新加入）</span>
          </button>

          <div v-if="isRemovedExpanded" class="flex flex-col gap-2">
            <div
              v-for="(mod, idx) in removedMods"
              :key="mod.id"
              class="p-2.5 rounded-[8px] border border-dashed border-[#44403C] bg-[#292524] flex items-center justify-between gap-2"
            >
              <span class="text-[14px] leading-[20px] text-[#A8A29E] truncate flex-1">
                {{ mod.title }}
              </span>

              <!-- 加回按钮 -->
              <button
                type="button"
                @click="handleAddBackMod(idx)"
                class="px-2 py-0.5 rounded-[4px] bg-[rgba(249,200,109,0.15)] text-[12px] leading-[16px] text-[#F9C86D] hover:bg-[rgba(249,200,109,0.25)] flex-shrink-0 cursor-pointer select-none"
              >
                加回
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 底部 Footer 操作区 -->
      <div class="flex items-center justify-end gap-2 p-4 border-t border-[#44403C] bg-[#1A1714]">
        <button
          type="button"
          @click="handleClose"
          class="px-4 py-2 rounded-[8px] border border-[#44403C] bg-[#292524] text-[13px] text-[#A8A29E] hover:text-[#F5F5F4] cursor-pointer select-none"
        >
          取消
        </button>

        <button
          type="button"
          @click="handleSave"
          :disabled="!isFormValid"
          class="px-4 py-2 rounded-[8px] bg-[rgba(249,200,109,0.15)] border border-[rgba(249,200,109,0.30)] text-[#F9C86D] text-[13px] font-medium transition-all select-none"
          :class="isFormValid ? 'hover:bg-[rgba(249,200,109,0.25)] active:scale-95 cursor-pointer opacity-100' : 'opacity-50 cursor-not-allowed'"
        >
          保存合集
        </button>
      </div>
    </div>
  </div>
</template>
