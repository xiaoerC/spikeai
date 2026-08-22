<script setup lang="ts">
/**
 * AI 聊天界面 - 选择对话大模型抽屉 (1:1 Figma 原型高保真)
 *
 * 遵循 Vue 3.5 + UnoCSS + Reka UI 架构规范，
 * 严格按照 Figma Frame 56:1057 与原型视觉还原「流式切换」、「我的最爱」、「最近模型」及「更多模型」入口。
 *
 * @packageDocumentation
 */

import { type AiModelItem, MOCK_AI_MODELS } from "@/views/chat/constants/mockChatData";
import { Check, ChevronRight, Moon, RefreshCw, Star, Zap } from "lucide-vue-next";
import { computed, ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const props = defineProps<{
  open: boolean;
  currentModelId: string;
}>();

const emit = defineEmits<{
  (e: "update:open", value: boolean): void;
  (e: "selectModel", model: AiModelItem): void;
}>();

// 流式开关状态
const isStreamingGlobal = ref(true);
// 刷新旋转动画状态
const isRefreshing = ref(false);

// 模型列表本地响应式状态（支持收藏切换）
const modelList = ref<AiModelItem[]>([...MOCK_AI_MODELS]);

// 我的最爱模型列表
const favoriteModels = computed(() => modelList.value.filter((m) => m.isFavorite));

/**
 * 切换模型选择
 */
function handleSelect(model: AiModelItem): void {
  emit("selectModel", model);
  emit("update:open", false);
}

/**
 * 切换收藏状态
 */
function handleToggleFavorite(modelId: string, event: Event): void {
  event.stopPropagation();
  const target = modelList.value.find((m) => m.id === modelId);
  if (target) {
    target.isFavorite = !target.isFavorite;
  }
}

/**
 * 刷新模型状态动画
 */
function handleRefresh(): void {
  if (isRefreshing.value) return;
  isRefreshing.value = true;
  setTimeout(() => {
    isRefreshing.value = false;
  }, 700);
}

function handleClose(): void {
  emit("update:open", false);
}
</script>

<template>
  <!-- 遮罩蒙层 -->
  <Transition name="fade">
    <div
      v-if="open"
      @click="handleClose"
      class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm transition-opacity"
    />
  </Transition>

  <!-- 底部滑出抽屉容器 (1:1 原型) -->
  <Transition name="slide-bottom">
    <div
      v-if="open"
      class="fixed left-0 right-0 bottom-0 z-50 w-full max-w-[440px] mx-auto rounded-t-2xl border-t border-[#44403C]/80 bg-[#0C0A09] shadow-2xl overflow-hidden flex flex-col select-none max-h-[85vh]"
    >
      <!-- 内部底色容器 -->
      <div class="flex flex-col w-full bg-[#292524]">
        
        <!-- 1. 顶部拖拽条 Handle -->
        <div class="flex justify-center items-center pt-2.5 pb-1 w-full">
          <div class="w-9 h-1 rounded-full bg-[#44403C]" />
        </div>

        <!-- 2. 顶栏: 标题 + 流式开关 + 刷新按钮 -->
        <div class="px-4 py-2 flex items-center justify-between w-full">
          <h3 class="text-[15px] font-semibold text-[#F5F5F4] tracking-tight">
            选择模型
          </h3>

          <div class="flex items-center gap-2">
            <!-- 流式切换开关胶囊 (border: 0.667px solid #F9C86D, background: rgba(249, 200, 109, 0.08)) -->
            <button
              type="button"
              @click="isStreamingGlobal = !isStreamingGlobal"
              class="flex items-center gap-1.5 px-2 py-1 rounded-full border border-[#F9C86D] bg-[#F9C86D]/8 text-[#F9C86D] cursor-pointer hover:bg-[#F9C86D]/15 active:scale-95 transition-all"
              title="切换流式传输"
            >
              <Zap class="w-3 h-3 text-[#F9C86D] fill-[#F9C86D]" />
              <span class="text-[10px] font-medium leading-none">流式</span>
              
              <!-- Mini Switch 滑块 -->
              <div class="w-6 h-3 rounded-full bg-[#0C0A09] p-0.5 relative flex items-center">
                <div
                  :class="[
                    'w-2 h-2 rounded-full transition-all duration-200',
                    isStreamingGlobal ? 'bg-[#F9C86D] translate-x-3' : 'bg-[#44403C] translate-x-0'
                  ]"
                />
              </div>
            </button>

            <!-- 刷新按钮 -->
            <button
              type="button"
              @click="handleRefresh"
              class="w-7 h-7 rounded-full flex items-center justify-center text-[#78716C] hover:text-[#F5F5F4] hover:bg-white/5 active:scale-90 transition-all cursor-pointer"
              title="刷新模型状态"
            >
              <RefreshCw
                class="w-3.5 h-3.5 transition-transform duration-700"
                :class="{ 'animate-spin': isRefreshing }"
              />
            </button>
          </div>
        </div>

        <!-- 3. 「我的最爱」分组 -->
        <div class="px-4 pt-3 pb-1.5 flex flex-col w-full">
          <span class="text-[11px] font-semibold text-[#F9C86D] tracking-wider uppercase">
            我的最爱
          </span>
        </div>

        <!-- 我的最爱内容区 -->
        <div v-if="favoriteModels.length === 0" class="px-4 pb-2 text-[12px] text-[#78716C] leading-snug">
          还没有收藏。到「更多模型」里点星标，把常用渠道收进来。
        </div>

        <!-- 已收藏模型列表 -->
        <div v-else class="px-1 flex flex-col w-full">
          <div
            v-for="model in favoriteModels"
            :key="`fav-${model.id}`"
            @click="handleSelect(model)"
            class="relative w-full px-4 py-2.5 flex items-center justify-between border-b border-[#292524] bg-[#0C0A09] hover:bg-[#1A1714] transition-colors cursor-pointer"
          >
            <!-- 激活高光黄条 -->
            <div
              v-if="model.id === currentModelId"
              class="absolute left-0 top-0 bottom-0 w-1 rounded-r bg-[#F9C86D]"
            />

            <!-- 模型名称与勾选 -->
            <div class="flex items-center gap-2 min-w-0">
              <span class="text-sm font-semibold text-[#F5F5F4] truncate">
                {{ model.name }}
              </span>
              <Check v-if="model.id === currentModelId" class="w-4 h-4 text-[#F9C86D] shrink-0" />
            </div>

            <!-- 右侧指标与操作 -->
            <div class="flex items-center gap-3">
              <!-- 健康度 -->
              <div class="flex flex-col items-end gap-1">
                <span class="text-xs font-semibold text-[#F5F5F4] font-mono">{{ model.health }}%</span>
                <div class="flex items-center gap-0.5">
                  <div v-for="i in 5" :key="i" class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                </div>
              </div>

              <!-- 计费 -->
              <div v-if="model.billingType === 'fixed'" class="flex flex-col items-end gap-0.5">
                <div class="flex items-center gap-1 text-[13px] font-semibold text-[#EAB308]">
                  <Star class="w-2.5 h-2.5 fill-[#EAB308]" />
                  <span>{{ model.starCost }}</span>
                </div>
                <div class="flex items-center gap-1 text-[13px] font-semibold text-[#FF9F43]">
                  <Moon class="w-2.5 h-2.5 fill-[#FF9F43]" />
                  <span>{{ model.moonCost }}</span>
                </div>
              </div>

              <ChevronRight class="w-4 h-4 text-[#78716C]" />

              <!-- 收藏星标 -->
              <button
                type="button"
                @click="handleToggleFavorite(model.id, $event)"
                class="w-10 h-10 rounded-full flex items-center justify-center text-[#F9C86D] hover:scale-110 active:scale-95 transition-transform cursor-pointer"
              >
                <Star class="w-5 h-5 fill-[#F9C86D] text-[#F9C86D]" />
              </button>
            </div>
          </div>
        </div>

        <!-- 4. 「最近」分组 -->
        <div class="px-4 pt-3 pb-1.5 flex flex-col w-full">
          <span class="text-[11px] font-semibold text-[#78716C] tracking-wider uppercase">
            最近
          </span>
        </div>

        <!-- 最近模型列表项 (1:1 复刻) -->
        <div class="px-1 flex flex-col w-full">
          
          <!-- (1) glm-5.2-o1 -->
          <div
            @click="handleSelect(modelList[0])"
            class="relative w-full pl-4 pr-1 py-2 flex items-center justify-between border-b border-[#292524] bg-[#0C0A09] hover:bg-[#171412] transition-colors cursor-pointer group"
          >
            <!-- 激活黄色垂直指示条 (贴在最左侧) -->
            <div
              v-if="modelList[0].id === currentModelId"
              class="absolute left-0 top-0 bottom-0 w-1 rounded-r bg-[#F9C86D]"
            />

            <!-- 模型名称 + 勾选 -->
            <div class="flex items-center gap-2 min-w-0">
              <span class="text-sm font-semibold text-[#F5F5F4] tracking-tight">
                {{ modelList[0].name }}
              </span>
              <Check v-if="modelList[0].id === currentModelId" class="w-4 h-4 text-[#F9C86D] shrink-0" />
            </div>

            <!-- 中右部: 健康度 + 价格 + 箭头 + 收藏 -->
            <div class="flex items-center gap-2">
              
              <!-- 可用率 97% + 5 根小绿条 -->
              <div class="flex flex-col items-end gap-1">
                <span class="text-xs font-semibold text-[#F5F5F4] font-mono leading-none">
                  {{ modelList[0].health }}%
                </span>
                <div class="flex items-end gap-[2px]">
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                </div>
              </div>

              <!-- 消耗点数: ★ 30 与 🌙 30 -->
              <div class="flex flex-col items-end gap-1 min-w-[36px]">
                <div class="flex items-center gap-1 text-[13px] font-semibold text-[#EAB308] leading-none">
                  <Star class="w-3 h-3 fill-[#EAB308] text-[#EAB308]" />
                  <span>30</span>
                </div>
                <div class="flex items-center gap-1 text-[13px] font-semibold text-[#FF9F43] leading-none">
                  <Moon class="w-3 h-3 fill-[#FF9F43] text-[#FF9F43]" />
                  <span>30</span>
                </div>
              </div>

              <!-- 右箭头 -->
              <ChevronRight class="w-4 h-4 text-[#78716C]" />

              <!-- 加入最爱星标按钮 (44x44) -->
              <button
                type="button"
                @click="handleToggleFavorite(modelList[0].id, $event)"
                class="w-10 h-10 rounded-full flex items-center justify-center text-[#78716C] hover:text-[#F9C86D] hover:scale-110 active:scale-95 transition-all cursor-pointer shrink-0"
                title="加入最爱"
              >
                <Star
                  class="w-5 h-5 transition-colors"
                  :class="modelList[0].isFavorite ? 'fill-[#F9C86D] text-[#F9C86D]' : 'text-[#78716C]'"
                />
              </button>
            </div>
          </div>

          <!-- (2) ds4f-官 -->
          <div
            @click="handleSelect(modelList[1])"
            class="relative w-full pl-4 pr-1 py-2 flex items-center justify-between border-b border-[#292524] bg-[#0C0A09] hover:bg-[#171412] transition-colors cursor-pointer group"
          >
            <!-- 激活黄色垂直指示条 -->
            <div
              v-if="modelList[1].id === currentModelId"
              class="absolute left-0 top-0 bottom-0 w-1 rounded-r bg-[#F9C86D]"
            />

            <!-- 模型名称 + 勾选 -->
            <div class="flex items-center gap-2 min-w-0">
              <span class="text-sm font-semibold text-[#F5F5F4] tracking-tight">
                {{ modelList[1].name }}
              </span>
              <Check v-if="modelList[1].id === currentModelId" class="w-4 h-4 text-[#F9C86D] shrink-0" />
            </div>

            <!-- 中右部: 健康度 + 按量计费 + 箭头 + 收藏 -->
            <div class="flex items-center gap-2">
              
              <!-- 可用率 97% + 5 根小绿条 -->
              <div class="flex flex-col items-end gap-1">
                <span class="text-xs font-semibold text-[#F5F5F4] font-mono leading-none">
                  {{ modelList[1].health }}%
                </span>
                <div class="flex items-end gap-[2px]">
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                  <div class="w-[3px] h-2 rounded-[1px] bg-[#22C55E]" />
                </div>
              </div>

              <!-- 按量计费详情 -->
              <div class="flex flex-col items-end gap-0.5">
                <span class="text-[13px] font-semibold text-[#EAB308] leading-tight">按量</span>
                <span class="text-[9.5px] text-[#78716C] leading-none">入×0.6000</span>
                <span class="text-[9.5px] text-[#78716C] leading-none">出×1.2000/千token</span>
              </div>

              <!-- 右箭头 -->
              <ChevronRight class="w-4 h-4 text-[#78716C]" />

              <!-- 加入最爱星标按钮 (44x44) -->
              <button
                type="button"
                @click="handleToggleFavorite(modelList[1].id, $event)"
                class="w-10 h-10 rounded-full flex items-center justify-center text-[#78716C] hover:text-[#F9C86D] hover:scale-110 active:scale-95 transition-all cursor-pointer shrink-0"
                title="加入最爱"
              >
                <Star
                  class="w-5 h-5 transition-colors"
                  :class="modelList[1].isFavorite ? 'fill-[#F9C86D] text-[#F9C86D]' : 'text-[#78716C]'"
                />
              </button>
            </div>
          </div>

        </div>

        <!-- 5. 底部「更多模型」入口 (1:1 复刻) -->
        <button
          type="button"
          @click="emit('update:open', false); router.push('/models')"
          class="w-full px-4 py-3.5 flex items-center justify-between border-t border-[#292524] bg-transparent hover:bg-white/5 transition-colors cursor-pointer mt-1"
        >
          <div class="flex items-center gap-2">
            <span class="text-sm font-semibold text-[#F9C86D]">更多模型</span>
            <span class="text-[12px] text-[#78716C]">14 个家族 · 78 个渠道</span>
          </div>

          <ChevronRight class="w-4 h-4 text-[#78716C]" />
        </button>


      </div>
    </div>
  </Transition>
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

.slide-bottom-enter-active,
.slide-bottom-leave-active {
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-bottom-enter-from,
.slide-bottom-leave-to {
  transform: translateY(100%);
}
</style>
