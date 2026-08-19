<script setup lang="ts">
/**
 * 云端备份与同步配置模态弹窗 (1:1 黑金高奢拟物)
 *
 * 支持本地 JSON 数据备份导出、导入恢复以及 WebDAV 自动同步配置。
 *
 * @packageDocumentation
 */

import { AppButton, AppModal } from "@/components/common";
import { Cloud, Download, HardDrive, RefreshCw, Upload } from "lucide-vue-next";
import { ref } from "vue";

const props = defineProps<{
  /** 弹窗是否打开 (v-model:open) */
  open: boolean;
}>();

const emit = defineEmits<(e: "update:open", value: boolean) => void>();

// 自动同步状态
const isAutoSync = ref<boolean>(false);
const webdavUrl = ref<string>("https://dav.jianguoyun.com/dav/");
const webdavUser = ref<string>("");
const isSyncing = ref<boolean>(false);
const syncSuccessMessage = ref<string>("");

/**
 * 模拟触发云端即时同步
 */
function handleSyncNow(): void {
  isSyncing.value = true;
  syncSuccessMessage.value = "";
  setTimeout(() => {
    isSyncing.value = false;
    syncSuccessMessage.value = "云端同步完成！已成功备份全部历史记录。";
  }, 1200);
}

/**
 * 本地导出备份文件
 */
function handleExportLocal(): void {
  const dummyData = {
    version: "1.0.0",
    exportTime: new Date().toISOString(),
    system: "Narratium / 叙梦 Naro",
    notice: "叙梦 Naro 角色卡与对话历史备份档案",
  };
  const blob = new Blob([JSON.stringify(dummyData, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `naro_history_backup_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
}
</script>

<template>
  <AppModal
    :open="open"
    title="云端与本地数据备份"
    description="管理您的历史对话、剧情存档与个性化卡片配置"
    size="md"
    @update:open="emit('update:open', $event)"
  >
    <div class="flex flex-col gap-5 py-2">
      <!-- 1. 快捷操作卡片组 (导出 / 导入) -->
      <div class="grid grid-cols-2 gap-3">
        <!-- 本地导出 -->
        <button
          type="button"
          @click="handleExportLocal"
          class="flex flex-col items-center justify-center p-3.5 rounded-xl border border-[#44403C] bg-[rgba(26,23,20,0.60)] hover:border-[#F9C86D]/50 hover:bg-[rgba(40,35,30,0.80)] transition-all group cursor-pointer"
        >
          <div class="w-10 h-10 rounded-full bg-[#F9C86D]/10 text-[#F9C86D] flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
            <Download class="w-5 h-5" />
          </div>
          <span class="text-xs font-semibold text-gray-200">导出备份文件</span>
          <span class="text-[10px] text-[#78716C] mt-0.5">JSON 格式离线保存</span>
        </button>

        <!-- 本地导入恢复 -->
        <button
          type="button"
          class="flex flex-col items-center justify-center p-3.5 rounded-xl border border-[#44403C] bg-[rgba(26,23,20,0.60)] hover:border-[#F9C86D]/50 hover:bg-[rgba(40,35,30,0.80)] transition-all group cursor-pointer"
        >
          <div class="w-10 h-10 rounded-full bg-[#38BDF8]/10 text-[#38BDF8] flex items-center justify-center mb-2 group-hover:scale-110 transition-transform">
            <Upload class="w-5 h-5" />
          </div>
          <span class="text-xs font-semibold text-gray-200">导入恢复存档</span>
          <span class="text-[10px] text-[#78716C] mt-0.5">支持覆写与增量合并</span>
        </button>
      </div>

      <!-- 2. WebDAV 坚果云 / 自建云端同步 -->
      <div class="flex flex-col gap-3 p-3.5 rounded-xl border border-[#44403C]/80 bg-[rgba(18,16,14,0.70)]">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Cloud class="w-4 h-4 text-[#F9C86D]" />
            <span class="text-xs font-semibold text-gray-200">WebDAV 云端自动备份</span>
          </div>
          <!-- 开关 -->
          <button
            type="button"
            @click="isAutoSync = !isAutoSync"
            :class="[
              'w-9 h-5 rounded-full p-0.5 transition-colors cursor-pointer flex items-center',
              isAutoSync ? 'bg-[#F9C86D] justify-end' : 'bg-[#44403C] justify-start'
            ]"
          >
            <div class="w-4 h-4 rounded-full bg-black shadow" />
          </button>
        </div>

        <div v-if="isAutoSync" class="flex flex-col gap-2.5 pt-1 animate-fade-in">
          <div class="flex flex-col gap-1">
            <label class="text-[10px] text-[#A8A29E]">服务器地址 (Server URL)</label>
            <input
              v-model="webdavUrl"
              type="text"
              class="w-full px-3 py-1.5 rounded-lg border border-[#44403C] bg-black/40 text-xs text-gray-200 focus:border-[#F9C86D]"
              placeholder="https://..."
            />
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-[10px] text-[#A8A29E]">账号 / 邮箱 (Username)</label>
            <input
              v-model="webdavUser"
              type="text"
              class="w-full px-3 py-1.5 rounded-lg border border-[#44403C] bg-black/40 text-xs text-gray-200 focus:border-[#F9C86D]"
              placeholder="user@example.com"
            />
          </div>
        </div>
      </div>

      <!-- 成功提示 -->
      <div v-if="syncSuccessMessage" class="p-2.5 rounded-lg bg-green-950/40 border border-green-700/50 text-[11px] text-green-300 text-center animate-fade-in">
        {{ syncSuccessMessage }}
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between w-full">
        <div class="flex items-center gap-1.5 text-[11px] text-[#78716C]">
          <HardDrive class="w-3.5 h-3.5" />
          <span>本地占用: 2.4 MB</span>
        </div>
        <div class="flex items-center gap-2">
          <AppButton
            variant="ghost"
            size="sm"
            @click="emit('update:open', false)"
          >
            关闭
          </AppButton>
          <AppButton
            variant="gold"
            size="sm"
            :disabled="isSyncing"
            @click="handleSyncNow"
          >
            <RefreshCw v-if="isSyncing" class="w-3.5 h-3.5 animate-spin mr-1" />
            <span>{{ isSyncing ? "正在同步..." : "立即同步" }}</span>
          </AppButton>
        </div>
      </div>
    </template>
  </AppModal>
</template>
