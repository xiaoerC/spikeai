<script setup lang="ts">
/**
 * 叙梦 Naro - 更多模型全量市场页面 (1:1 Figma 原型高保真)
 *
 * 遵循 Vue 3.5 + UnoCSS + Reka UI 规范架构，
 * 包含会员额度状态、实时搜索、分类过滤标签、家族手风琴折叠及模型卡片明细。
 *
 * @packageDocumentation
 */

import {
  MOCK_MODEL_FAMILIES,
  type ModelChannelItem,
  type ModelFamilyItem,
} from "@/views/chat-models/constants/mockModelFamilies";
import {
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Moon,
  Search,
  Star,
} from "lucide-vue-next";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

// 搜索关键词
const searchKeyword = ref("");
// 当前分类选中 Filter ("all" | "normal" | "advanced" | "infinite")
const currentCategory = ref<"all" | "normal" | "advanced" | "infinite">("all");
// 展开的手风琴家族 ID 集合（默认展开 GPT）
const expandedFamilyIds = ref<Set<string>>(new Set(["gpt"]));

// 本地模型家族数据（支持收藏响应）
const families = ref<ModelFamilyItem[]>([...MOCK_MODEL_FAMILIES]);

/**
 * 切换手风琴展开/折叠
 */
function toggleFamily(familyId: string): void {
  if (expandedFamilyIds.value.has(familyId)) {
    expandedFamilyIds.value.delete(familyId);
  } else {
    expandedFamilyIds.value.add(familyId);
  }
}

/**
 * 切换模型收藏状态
 */
function handleToggleFavorite(model: ModelChannelItem, event: Event): void {
  event.stopPropagation();
  model.isFavorite = !model.isFavorite;
}

/**
 * 选择具体模型并返回
 */
function handleSelectModel(_model: ModelChannelItem): void {
  router.back();
}

/**
 * 过滤后的模型家族列表
 */
const filteredFamilies = computed(() => {
  const kw = searchKeyword.value.trim().toLowerCase();
  return families.value.filter((f) => {
    if (!kw) return true;
    const matchFamilyName = f.name.toLowerCase().includes(kw);
    const matchModelName = f.models.some((m) => m.name.toLowerCase().includes(kw));
    return matchFamilyName || matchModelName;
  });
});
</script>

<template>
  <div class="flex flex-col min-h-screen w-full max-w-[440px] mx-auto bg-[#1C1917] text-[#F5F5F4] relative select-none">
    
    <!-- 1. 顶部控制栏 (背景 #292524 / #44403C 磨砂黑金) -->
    <header class="w-full bg-[#292524] border-b border-[#292524] pt-safe flex flex-col z-30 sticky top-0 shadow-md">
      
      <!-- 第一行: 返回按钮 + 页面标题 + 会员额度信息 -->
      <div class="px-4 py-3 flex items-center justify-between">
        <!-- 左侧: 返回 + 更多模型 -->
        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="router.back()"
            class="w-8 h-8 rounded-full flex items-center justify-center text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-white/5 active:scale-95 transition-all cursor-pointer"
            title="返回"
          >
            <ChevronLeft class="w-5 h-5 text-[#C0A480]" />
          </button>
          <h1 class="text-[15px] font-semibold text-[#F5F5F4] tracking-tight">
            更多模型
          </h1>
        </div>

        <!-- 右侧: 会员额度与次卡状态 -->
        <div class="flex items-center gap-2 text-[11px] font-sans">
          <div class="flex items-center gap-1">
            <span class="text-[#78716C]">会员免费次数</span>
            <span class="text-[#FF9F43] font-medium">今日剩余 30/30</span>
          </div>
          <div class="flex items-center gap-1">
            <span class="text-[#78716C]">包月次卡</span>
            <span class="text-[#78716C] font-medium">未持有</span>
          </div>
        </div>
      </div>

      <!-- 第二行: 搜索框 -->
      <div class="px-4 pb-2.5 w-full">
        <div class="w-full h-10 px-3 rounded-xl border border-[#44403C] bg-[#1C1917] flex items-center gap-2 focus-within:border-[#F9C86D]/60 transition-colors">
          <Search class="w-4 h-4 text-[#78716C] shrink-0" />
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索 78 个渠道"
            class="w-full bg-transparent text-xs text-[#F5F5F4] placeholder-[#78716C] outline-none"
          />
        </div>
      </div>

      <!-- 第三行: 分类筛选 Tab 药丸组 (全部 / 普通 / 高级 / 无限) -->
      <div class="px-4 pb-3 flex items-center gap-2 overflow-x-auto no-scrollbar">
        <!-- 全部 78 -->
        <button
          type="button"
          @click="currentCategory = 'all'"
          :class="[
            'px-3.5 py-1.5 rounded-full text-xs font-medium cursor-pointer transition-all shrink-0',
            currentCategory === 'all'
              ? 'bg-[#F9C86D] text-[#0C0A09] font-semibold shadow-gold'
              : 'bg-[#44403C]/80 text-[#A8A29E] hover:text-white'
          ]"
        >
          全部 78
        </button>

        <!-- 普通 12 (带蓝色圆点) -->
        <button
          type="button"
          @click="currentCategory = 'normal'"
          :class="[
            'px-3.5 py-1.5 rounded-full text-xs flex items-center gap-1.5 cursor-pointer transition-all shrink-0',
            currentCategory === 'normal'
              ? 'bg-[#F9C86D] text-[#0C0A09] font-semibold shadow-gold'
              : 'bg-[#44403C]/80 text-[#A8A29E] hover:text-white'
          ]"
        >
          <span class="w-2 h-2 rounded-full bg-[#3B82F6]" />
          <span>普通 12</span>
        </button>

        <!-- 高级 63 (带金色圆点) -->
        <button
          type="button"
          @click="currentCategory = 'advanced'"
          :class="[
            'px-3.5 py-1.5 rounded-full text-xs flex items-center gap-1.5 cursor-pointer transition-all shrink-0',
            currentCategory === 'advanced'
              ? 'bg-[#F9C86D] text-[#0C0A09] font-semibold shadow-gold'
              : 'bg-[#44403C]/80 text-[#A8A29E] hover:text-white'
          ]"
        >
          <span class="w-2 h-2 rounded-full bg-[#EAB308]" />
          <span>高级 63</span>
        </button>

        <!-- 无限 3 (带绿色圆点) -->
        <button
          type="button"
          @click="currentCategory = 'infinite'"
          :class="[
            'px-3.5 py-1.5 rounded-full text-xs flex items-center gap-1.5 cursor-pointer transition-all shrink-0',
            currentCategory === 'infinite'
              ? 'bg-[#F9C86D] text-[#0C0A09] font-semibold shadow-gold'
              : 'bg-[#44403C]/80 text-[#A8A29E] hover:text-white'
          ]"
        >
          <span class="w-2 h-2 rounded-full bg-[#22C55E]" />
          <span>无限 3</span>
        </button>
      </div>

    </header>

    <!-- 2. 模型家族手风琴列表 -->
    <main class="flex-1 w-full flex flex-col pb-12 overflow-y-auto">
      <div
        v-for="family in filteredFamilies"
        :key="family.id"
        class="w-full flex flex-col border-b border-[#292524]"
      >
        <!-- 家族标题栏 (点击折叠/展开) -->
        <button
          type="button"
          @click="toggleFamily(family.id)"
          class="w-full h-[50px] px-4 flex items-center justify-between bg-[#292524]/60 hover:bg-[#292524] transition-colors cursor-pointer"
        >
          <!-- 左侧: 折叠箭头 + 家族名 -->
          <div class="flex items-center gap-2.5">
            <component
              :is="expandedFamilyIds.has(family.id) ? ChevronDown : ChevronRight"
              class="w-4 h-4 text-[#A8A29E]"
            />
            <span class="text-[13.5px] font-semibold text-[#F5F5F4] tracking-tight">
              {{ family.name }}
            </span>
          </div>

          <!-- 右侧: 竖线指示器 + 数量 -->
          <div class="flex items-center gap-1.5">
            <div
              class="w-1 h-3 rounded-full"
              :style="{ backgroundColor: family.indicatorColor }"
            />
            <span class="text-xs font-mono text-[#78716C]">
              {{ family.channelCount }}
            </span>
          </div>
        </button>

        <!-- 展开后的模型卡片明细列表 (1:1 原型) -->
        <div
          v-if="expandedFamilyIds.has(family.id) && family.models.length > 0"
          class="flex flex-col w-full bg-[#0C0A09]"
        >
          <div
            v-for="model in family.models"
            :key="model.id"
            @click="handleSelectModel(model)"
            class="relative w-full pl-4 pr-2 min-h-[56px] py-2 flex items-center justify-between border-b border-[#292524] bg-[#0C0A09] hover:bg-[#171412] transition-colors cursor-pointer group"
          >
            <!-- 模型名称 -->
            <div class="flex items-center gap-2 min-w-0">
              <span class="text-sm font-semibold text-[#F5F5F4] tracking-tight">
                {{ model.name }}
              </span>
            </div>

            <!-- 右侧: 健康度 + 点数 + 箭头 + 收藏 -->
            <div class="flex items-center gap-2.5">
              
              <!-- 可用率与能量柱 (如 90% 或 73%) -->
              <div class="flex flex-col items-end gap-1">
                <span class="text-xs font-semibold text-[#F5F5F4] font-mono leading-none">
                  {{ model.health }}%
                </span>
                <div class="flex items-end gap-[2px]">
                  <div
                    v-for="i in 5"
                    :key="i"
                    class="w-[3px] h-2 rounded-[1px]"
                    :class="i <= Math.ceil(model.health / 20) ? 'bg-[#22C55E]' : 'bg-[#44403C]'"
                  />
                </div>
              </div>

              <!-- 消耗点数: ★ 30 与 🌙 30 -->
              <div class="flex flex-col items-end gap-1 min-w-[36px]">
                <div class="flex items-center gap-1 text-[13px] font-semibold text-[#EAB308] leading-none">
                  <Star class="w-3 h-3 fill-[#EAB308] text-[#EAB308]" />
                  <span>{{ model.starCost }}</span>
                </div>
                <div class="flex items-center gap-1 text-[13px] font-semibold text-[#FF9F43] leading-none">
                  <Moon class="w-3 h-3 fill-[#FF9F43] text-[#FF9F43]" />
                  <span>{{ model.moonCost }}</span>
                </div>
              </div>

              <!-- 进入右箭头 -->
              <ChevronRight class="w-4 h-4 text-[#78716C]" />

              <!-- 加入最爱星标按钮 (44x44) -->
              <button
                type="button"
                @click="handleToggleFavorite(model, $event)"
                class="w-10 h-10 rounded-full flex items-center justify-center text-[#78716C] hover:text-[#F9C86D] hover:scale-110 active:scale-95 transition-all cursor-pointer shrink-0"
                title="加入最爱"
              >
                <Star
                  class="w-5 h-5 transition-colors"
                  :class="model.isFavorite ? 'fill-[#F9C86D] text-[#F9C86D]' : 'text-[#78716C]'"
                />
              </button>
            </div>
          </div>
        </div>

      </div>
    </main>

  </div>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
