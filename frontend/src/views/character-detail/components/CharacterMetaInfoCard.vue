<script setup lang="ts">
/**
 * 角色卡详情 - 详细信息元数据卡片 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

defineProps<{
  meta: {
    createdAt: string;
    updatedAt: string;
    version: string;
    visibility: string;
  };
}>();
</script>

<template>
  <div class="w-full px-3 pt-3 select-none">
    <div class="w-full p-4 rounded-lg border border-[#292524] bg-[#1A1714]/95 flex flex-col gap-3">
      
      <!-- 标题: 详细信息 -->
      <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[-0.36px] leading-5">
        详细信息
      </h2>

      <!-- 4 项元数据列表 -->
      <div class="flex flex-col gap-3 pt-1">
        <!-- (1) 创建时间 -->
        <div class="flex items-center justify-between py-1 border-b border-[#292524]/60">
          <span class="text-xs text-[#A8A29E]">创建时间</span>
          <span class="text-sm text-[#F5F5F4] font-mono">{{ meta.createdAt }}</span>
        </div>

        <!-- (2) 更新时间 -->
        <div class="flex items-center justify-between py-1 border-b border-[#292524]/60">
          <span class="text-xs text-[#A8A29E]">更新时间</span>
          <span class="text-sm text-[#F5F5F4] font-mono">{{ meta.updatedAt }}</span>
        </div>

        <!-- (3) 版本 -->
        <div class="flex items-center justify-between py-1 border-b border-[#292524]/60">
          <span class="text-xs text-[#A8A29E]">版本</span>
          <span class="text-sm text-[#F5F5F4] font-mono">{{ meta.version }}</span>
        </div>

        <!-- (4) 可见性 -->
        <div class="flex items-center justify-between py-1">
          <span class="text-xs text-[#A8A29E]">可见性</span>
          <span class="text-sm text-[#F5F5F4] font-sans">{{ meta.visibility }}</span>
        </div>
      </div>

    </div>
  </div>
</template>
