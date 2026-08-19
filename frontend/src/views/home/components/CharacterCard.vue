<script setup lang="ts">
/**
 * 叙梦 Naro 角色市场卡片组件 (Home 页面私有)
 *
 * @packageDocumentation
 */

import type { MarketCard } from "@/types";

/** 组件 Props 参数接口 */
interface Props {
  /** 角色卡片元数据 */
  card: MarketCard;
}

const props = defineProps<Props>();

/** 组件 Emits 事件 */
const emit = defineEmits<(e: "select", card: MarketCard) => void>();

/**
 * 卡片点击事件处理
 */
function handleCardClick(): void {
  emit("select", props.card);
}
</script>

<template>
  <!-- 外层卡片: 双重黑金渐变高光边框 + 内嵌发光阴影 -->
  <div
    @click="handleCardClick"
    class="flex flex-col items-start self-start h-[291.55px] w-full rounded-[12px] p-[1px] relative overflow-hidden cursor-pointer select-none transition-transform duration-200 active:scale-[0.98] group"
    style="background-image: linear-gradient(180deg, rgba(26, 21, 16, 0.90) 0%, rgba(26, 21, 16, 0.90) 100%), linear-gradient(135deg, #D4AF37 0%, #F9C86D 25%, #FFD700 50%, #F9C86D 75%, #B8860B 100%); box-shadow: 0 1px 1px 0 rgba(255, 215, 0, 0.10) inset, 0 0 8px 0 rgba(249, 198, 109, 0.15), 0 2px 4px 0 rgba(0, 0, 0, 0.10);"
  >
    <!-- 内层暗黑曜石基座容器: background: #292524 -->
    <div class="flex flex-col items-start self-stretch h-[286.22px] w-full rounded-[8px] bg-[#292524] overflow-hidden relative justify-between pb-2">
      
      <!-- 1. 顶部区域 (带左上角作者胶囊) -->
      <div class="relative w-full h-[96px] flex-shrink-0 bg-[#292524] overflow-hidden">
        <!-- 左上角作者胶囊 -->
        <div class="absolute left-2 top-2 z-10 flex items-center px-2 py-[2px] rounded-full border-[0.667px] border-[rgba(249,200,109,0.30)] bg-[rgba(0,0,0,0.70)] backdrop-blur-sm">
          <span class="text-[12px] font-medium text-[#F9C86D] leading-4 tracking-[-0.176px] truncate max-w-[90px]">
            {{ card.author }}
          </span>
        </div>
      </div>

      <!-- 2. 信息详情容器 -->
      <div class="flex flex-col items-start self-stretch px-2 pb-1 flex-1 justify-between gap-1 w-full">
        
        <!-- 热度指示器: 🔥 5799.8k -->
        <div class="flex items-center gap-1">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" class="flex-shrink-0">
            <path d="M11.7713 12.438C10.7711 13.4382 9.41453 14.0001 8.00001 14.0001C6.58548 14.0001 5.22889 13.4382 4.22867 12.438C3.22845 11.4378 2.66653 10.0812 2.66653 8.66667C2.66653 7.25214 3.22845 5.89555 4.22867 4.89533C4.22867 4.89533 4.66667 6 6.00001 6.66667C6.00001 5.33333 6.33334 3.33333 7.99067 2C9.33334 3.33333 10.7267 3.85133 11.7707 4.89533C12.2668 5.39 12.6602 5.97783 12.9284 6.62504C13.1966 7.27226 13.3342 7.96609 13.3333 8.66667C13.3343 9.36719 13.1968 10.061 12.9287 10.7082C12.6606 11.3554 12.2673 11.9433 11.7713 12.438Z" stroke="#EAB308" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6.586 10.7473C6.81826 10.9797 7.10417 11.1512 7.41846 11.2468C7.73276 11.3424 8.06576 11.3591 8.38803 11.2954C8.71031 11.2317 9.01194 11.0896 9.26628 10.8817C9.52061 10.6738 9.71981 10.4064 9.84627 10.1032C9.97273 9.80004 10.0226 9.47037 9.99136 9.14335C9.96016 8.81633 9.84888 8.50203 9.66737 8.22822C9.48585 7.95441 9.23969 7.72954 8.95062 7.57346C8.66156 7.41738 8.3385 7.33491 8.01 7.33334L7.33333 9.33334H6C6 9.84534 6.19533 10.3573 6.586 10.7473Z" stroke="#EAB308" stroke-width="1.33333" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span class="text-[14px] font-bold text-[#EAB308] leading-5 tracking-[-0.176px] font-sans">
            {{ card.heat }}
          </span>
        </div>

        <!-- 标题 -->
        <div class="flex flex-col items-start self-stretch overflow-hidden">
          <h3 class="text-[14px] font-semibold text-white/95 leading-[17px] tracking-[-0.28px] line-clamp-2 group-hover:text-[#F9C86D] transition-colors w-full">
            {{ card.title }}
          </h3>
        </div>

        <!-- 三合一指标栏 -->
        <div class="flex items-center gap-2 pt-0.5 self-stretch">
          <!-- 趋势分 -->
          <div class="flex items-center gap-[2px]">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="flex-shrink-0">
              <path d="M10.5 7.5V3.5H6.5M10.5 3.5L6.5 7.5L4.5 5.5L1.5 8.5" stroke="#FF9F43" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="text-[10px] font-semibold text-[#FF9F43] leading-none">
              {{ card.trendScore }}
            </span>
          </div>

          <!-- 对话消息数 -->
          <div class="flex items-center gap-[2px]">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="flex-shrink-0">
              <path d="M4 6H4.005M6 6H6.005M8 6H8.005M10.5 6C10.5 8.209 8.485 10 6 10C5.26432 10.0025 4.5374 9.84038 3.8725 9.5255L1.5 10L2.1975 8.14C1.756 7.521 1.5 6.787 1.5 6C1.5 3.791 3.515 2 6 2C8.485 2 10.5 3.791 10.5 6Z" stroke="#FF9F43" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="text-[10px] font-semibold text-[#FF9F43] leading-none">
              {{ card.chatCount }}
            </span>
          </div>

          <!-- 评分 -->
          <div class="flex items-center gap-[2px] ml-auto">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none" xmlns="http://www.w3.org/2000/svg" class="flex-shrink-0">
              <path d="M5.74 1.7495C5.76115 1.69792 5.79716 1.65379 5.84346 1.62273C5.88976 1.59167 5.94425 1.57509 6 1.57509C6.05575 1.57509 6.11024 1.59167 6.15654 1.62273C6.20284 1.65379 6.23885 1.69792 6.26 1.7495L7.3225 4.305C7.34239 4.35282 7.37508 4.39422 7.41698 4.42466C7.45889 4.45509 7.50837 4.47338 7.56 4.4775L10.319 4.6985C10.5685 4.7185 10.6695 5.03 10.4795 5.1925L8.3775 6.9935C8.33823 7.0271 8.30896 7.07085 8.29291 7.11998C8.27686 7.1691 8.27464 7.2217 8.2865 7.272L8.929 9.9645C8.94191 10.0185 8.93853 10.0752 8.91927 10.1273C8.90002 10.1793 8.86576 10.2246 8.82081 10.2572C8.77587 10.2898 8.72227 10.3084 8.66677 10.3106C8.61127 10.3128 8.55637 10.2985 8.509 10.2695L6.1465 8.827C6.10239 8.80005 6.05169 8.78579 6 8.78579C5.9483 8.78579 5.89761 8.80005 5.8535 8.827L3.491 10.27C3.44363 10.299 3.38872 10.3133 3.33323 10.3111C3.27773 10.3089 3.22412 10.2903 3.17918 10.2577C3.13424 10.2251 3.09998 10.1798 3.08072 10.1278C3.06147 10.0757 3.05808 10.019 3.071 9.965L3.7135 7.272C3.72541 7.2217 3.72322 7.16909 3.70717 7.11995C3.69111 7.07082 3.66182 7.02706 3.6225 6.9935L1.5205 5.1925C1.47817 5.15642 1.4475 5.10858 1.43238 5.05506C1.41725 5.00153 1.41836 4.94472 1.43554 4.89183C1.45273 4.83893 1.48523 4.79232 1.52892 4.7579C1.57262 4.72349 1.62554 4.70281 1.681 4.6985L4.44 4.4775C4.49162 4.47338 4.54111 4.45509 4.58301 4.42466C4.62491 4.39422 4.65761 4.35282 4.6775 4.305L5.74 1.7495Z" fill="#F9C86D"/>
            </svg>
            <span class="text-[10px] font-semibold text-[#F9C86D] leading-none">
              {{ card.rating }}
            </span>
          </div>
        </div>

        <!-- 简介文案 -->
        <div class="flex flex-col items-start self-stretch overflow-hidden">
          <p class="text-[10px] text-white/70 leading-[16px] tracking-[-0.176px] line-clamp-2 w-full">
            {{ card.description }}
          </p>
        </div>

        <!-- 底部标签行 -->
        <div class="flex items-start gap-1 py-[2px] self-stretch overflow-hidden">
          <span
            v-for="(tag, idx) in card.tags.slice(0, 2)"
            :key="idx"
            class="px-2 py-[2px] rounded-full border-[0.667px] border-white/20 bg-white/10 text-white/80 text-[10px] font-medium leading-none tracking-tight truncate max-w-[65px]"
          >
            {{ tag }}
          </span>

          <span
            v-if="card.extraTags || card.tags.length > 2"
            class="px-2 py-[2px] rounded-full border-[0.667px] border-dashed border-white/15 bg-white/5 text-white/60 text-[10px] font-normal leading-none whitespace-nowrap"
          >
            {{ card.extraTags || `+${card.tags.length - 2}` }}
          </span>
        </div>

      </div>

    </div>
  </div>
</template>
