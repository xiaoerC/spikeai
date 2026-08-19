<script setup lang="ts">
/**
 * 个人中心 - 使用记录流水卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { USAGE_RECORDS, type UsageRecordItem } from "@/views/profile/constants/profileMock";
import { ChevronLeft, ChevronRight, History } from "lucide-vue-next";
import { computed, ref } from "vue";

const activeFilter = ref<"all" | "income" | "expense">("all");
const currentPage = ref(1);
const totalRecords = 3963;

const filteredRecords = computed<UsageRecordItem[]>(() => {
  if (activeFilter.value === "income") {
    return USAGE_RECORDS.filter((r) => r.amount > 0);
  }
  if (activeFilter.value === "expense") {
    return USAGE_RECORDS.filter((r) => r.amount < 0);
  }
  return USAGE_RECORDS;
});
</script>

<template>
  <div class="w-full rounded-lg border border-[#C0A480]/15 bg-gradient-to-br from-[#F4E8C1]/[0.04] to-[#F4E8C1]/[0.02] flex flex-col overflow-hidden">
    
    <!-- 1. 卡片头部 (标题 + 筛选 Tab + 下拉) -->
    <div class="p-4 border-b border-[#44403C]/30 flex flex-col gap-3">
      <div class="flex items-center justify-between">
        <!-- 标题 + 渐隐装饰下划线 -->
        <div class="flex flex-col">
          <div class="flex items-center gap-2">
            <History class="w-4 h-4 text-[#F9C86D]" />
            <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[0.9px] leading-6">
              使用记录
            </h2>
          </div>
          <div class="w-12 h-[2px] bg-gradient-to-r from-[#A8A29E]/60 to-transparent mt-1" />
        </div>

        <!-- 全部 / 收入 / 支出 药丸 Tab -->
        <div class="flex items-center gap-1">
          <button
            type="button"
            @click="activeFilter = 'all'"
            :class="[
              'px-2.5 py-1 rounded-lg text-xs transition-all cursor-pointer select-none',
              activeFilter === 'all'
                ? 'text-[#F9C86D] bg-[#A8A29E]/10 border border-[#A8A29E]/30'
                : 'text-[#78716C] border border-[#44403C]/60 hover:text-white'
            ]"
          >
            全部
          </button>
          <button
            type="button"
            @click="activeFilter = 'income'"
            :class="[
              'px-2.5 py-1 rounded-lg text-xs transition-all cursor-pointer select-none',
              activeFilter === 'income'
                ? 'text-[#F9C86D] bg-[#A8A29E]/10 border border-[#A8A29E]/30'
                : 'text-[#78716C] border border-[#44403C]/60 hover:text-white'
            ]"
          >
            收入
          </button>
          <button
            type="button"
            @click="activeFilter = 'expense'"
            :class="[
              'px-2.5 py-1 rounded-lg text-xs transition-all cursor-pointer select-none',
              activeFilter === 'expense'
                ? 'text-[#F9C86D] bg-[#A8A29E]/10 border border-[#A8A29E]/30'
                : 'text-[#78716C] border border-[#44403C]/60 hover:text-white'
            ]"
          >
            支出
          </button>
        </div>
      </div>
    </div>

    <!-- 2. 流水记录列表 (1:1 原型条目) -->
    <div class="p-3 flex flex-col gap-3">
      <div
        v-for="record in filteredRecords"
        :key="record.id"
        class="p-3 rounded-lg bg-[#44403C]/20 border border-[#44403C]/30 flex flex-col gap-1.5 hover:border-[#F9C86D]/30 transition-colors"
      >
        <!-- 第一行: 类型 + 变动金额 -->
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-[#F5F5F4]">
            {{ record.type }}
          </span>
          <span
            :class="[
              'text-sm font-semibold font-mono',
              record.amount < 0 ? 'text-[#EF4444]' : 'text-[#22C55E]'
            ]"
          >
            {{ record.amount > 0 ? `+${record.amount}` : record.amount }}
          </span>
        </div>

        <!-- 第二行: 模型消耗详情 -->
        <p class="text-xs text-[#F5F5F4] leading-4">
          {{ record.description }}
        </p>

        <!-- 第三行: 关联角色卡 -->
        <p class="text-xs text-[#78716C] leading-4 truncate">
          用于《{{ record.targetCharacter }}》
        </p>

        <!-- 第四行: 时间 + 结余 -->
        <div class="flex items-center justify-between text-xs text-[#78716C] font-mono pt-0.5">
          <span>{{ record.time }}</span>
          <div class="flex items-center gap-1">
            <span>余额:</span>
            <span class="text-[#A8A29E] font-medium">{{ record.balance }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 底部完整分页控制栏 -->
    <div class="p-4 border-t border-[#44403C]/20 flex flex-col items-center gap-3 text-xs">
      <p class="text-[#78716C]">
        显示 1 - 10 条，共 <strong class="text-[#A8A29E]">{{ totalRecords }}</strong> 条记录
      </p>

      <div class="flex items-center gap-1">
        <button
          type="button"
          :disabled="currentPage === 1"
          @click="currentPage--"
          class="px-3 py-1.5 rounded-lg border border-[#44403C]/60 text-[#78716C] disabled:opacity-50 disabled:cursor-not-allowed hover:text-white transition-colors cursor-pointer"
        >
          <ChevronLeft class="w-3.5 h-3.5" />
        </button>

        <button
          v-for="page in [1, 2, 3, 4, 5]"
          :key="page"
          type="button"
          @click="currentPage = page"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-mono transition-colors cursor-pointer',
            currentPage === page
              ? 'bg-[#A8A29E]/10 border border-[#A8A29E]/30 text-[#F9C86D] font-bold'
              : 'border border-[#44403C]/60 text-[#78716C] hover:text-white'
          ]"
        >
          {{ page }}
        </button>

        <button
          type="button"
          @click="currentPage++"
          class="px-3 py-1.5 rounded-lg border border-[#44403C]/60 text-[#78716C] hover:text-white transition-colors cursor-pointer"
        >
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

  </div>
</template>
