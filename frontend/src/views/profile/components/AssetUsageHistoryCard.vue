<script setup lang="ts">
/**
 * 个人中心 - 真实资产使用记录流水卡片 (对接真实分页与资金明细)
 *
 * @packageDocumentation
 */

import type { WalletTransactionItem } from "@/services/auth";
import { ChevronLeft, ChevronRight, History, Inbox } from "lucide-vue-next";
import { computed, ref } from "vue";

interface Props {
  transactions: {
    items: WalletTransactionItem[];
    total: number;
    page: number;
    pageSize: number;
    totalPages: number;
    isLoading: boolean;
  };
}

const props = defineProps<Props>();
const emit = defineEmits<(e: "changePage", page: number) => void>();

const activeFilter = ref<"all" | "income" | "expense">("all");

const filteredRecords = computed<WalletTransactionItem[]>(() => {
  if (activeFilter.value === "income") {
    return props.transactions.items.filter((r) => r.amount > 0);
  }
  if (activeFilter.value === "expense") {
    return props.transactions.items.filter((r) => r.amount < 0);
  }
  return props.transactions.items;
});

function formatTime(isoStr: string): string {
  try {
    const d = new Date(isoStr);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
  } catch {
    return isoStr;
  }
}

function getTypeName(type: string, currency: string): string {
  const currencyName = currency === "star" ? "星元" : "月华";
  switch (type) {
    case "daily_reward":
      return "每日签到奖励";
    case "recharge":
      return `充值${currencyName}`;
    case "chat_deduct":
      return `对话消耗${currencyName}`;
    case "tip_reward":
      return `创作者打赏${currencyName}`;
    default:
      return `${currencyName}变动`;
  }
}
</script>

<template>
  <div class="w-full rounded-lg border border-[#C0A480]/15 bg-gradient-to-br from-[#F4E8C1]/[0.04] to-[#F4E8C1]/[0.02] flex flex-col overflow-hidden">
    
    <!-- 1. 卡片头部 (标题 + 筛选 Tab) -->
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

    <!-- 2. 流水记录列表 (真实数据) -->
    <div v-if="transactions.isLoading" class="p-8 flex justify-center items-center text-xs text-[#78716C]">
      加载记录中...
    </div>

    <div v-else-if="filteredRecords.length > 0" class="p-3 flex flex-col gap-3">
      <div
        v-for="record in filteredRecords"
        :key="record.id"
        class="p-3 rounded-lg bg-[#44403C]/20 border border-[#44403C]/30 flex flex-col gap-1.5 hover:border-[#F9C86D]/30 transition-colors"
      >
        <!-- 第一行: 类型 + 变动金额 -->
        <div class="flex items-center justify-between">
          <span class="text-xs font-medium text-[#F5F5F4]">
            {{ getTypeName(record.type, record.currency) }}
          </span>
          <span
            :class="[
              'text-sm font-semibold font-mono',
              record.amount < 0 ? 'text-[#EF4444]' : 'text-[#22C55E]'
            ]"
          >
            {{ record.amount > 0 ? `+${record.amount}` : record.amount }} {{ record.currency === 'star' ? '★' : '🌙' }}
          </span>
        </div>

        <!-- 第二行: 描述详情 -->
        <p class="text-xs text-[#F5F5F4] leading-4">
          {{ record.description || "日常资产流水结算" }}
        </p>

        <!-- 第三行: 关联角色卡 (如果有) -->
        <p v-if="record.target_character_id" class="text-xs text-[#78716C] leading-4 truncate">
          用于角色卡 (ID: {{ record.target_character_id }})
        </p>

        <!-- 第四行: 时间 + 结余 -->
        <div class="flex items-center justify-between text-xs text-[#78716C] font-mono pt-0.5">
          <span>{{ formatTime(record.created_at) }}</span>
          <div class="flex items-center gap-1">
            <span>余额:</span>
            <span class="text-[#A8A29E] font-medium">{{ record.balance_after }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 真实空状态 -->
    <div v-else class="py-12 flex flex-col items-center justify-center gap-2 text-center text-[#78716C]">
      <Inbox class="w-8 h-8 opacity-40 text-[#A8A29E]" />
      <p class="text-xs">暂无资产使用记录</p>
    </div>

    <!-- 3. 底部完整分页控制栏 (仅在总数 > 0 时显示) -->
    <div v-if="transactions.total > 0" class="p-4 border-t border-[#44403C]/20 flex flex-col items-center gap-3 text-xs">
      <p class="text-[#78716C]">
        第 {{ transactions.page }} 页，共 <strong class="text-[#A8A29E] font-mono">{{ transactions.total }}</strong> 条记录
      </p>

      <div v-if="transactions.totalPages > 1" class="flex items-center gap-1">
        <button
          type="button"
          :disabled="transactions.page <= 1"
          @click="emit('changePage', transactions.page - 1)"
          class="px-3 py-1.5 rounded-lg border border-[#44403C]/60 text-[#78716C] disabled:opacity-50 disabled:cursor-not-allowed hover:text-white transition-colors cursor-pointer"
        >
          <ChevronLeft class="w-3.5 h-3.5" />
        </button>

        <button
          v-for="page in transactions.totalPages"
          :key="page"
          type="button"
          @click="emit('changePage', page)"
          :class="[
            'px-3 py-1.5 rounded-lg text-xs font-mono transition-colors cursor-pointer',
            transactions.page === page
              ? 'bg-[#A8A29E]/10 border border-[#A8A29E]/30 text-[#F9C86D] font-bold'
              : 'border border-[#44403C]/60 text-[#78716C] hover:text-white'
          ]"
        >
          {{ page }}
        </button>

        <button
          type="button"
          :disabled="transactions.page >= transactions.totalPages"
          @click="emit('changePage', transactions.page + 1)"
          class="px-3 py-1.5 rounded-lg border border-[#44403C]/60 text-[#78716C] disabled:opacity-50 disabled:cursor-not-allowed hover:text-white transition-colors cursor-pointer"
        >
          <ChevronRight class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>

  </div>
</template>
