<script setup lang="ts">
/**
 * 模块 7: 创建须知与合规提醒组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { ShieldAlert } from "lucide-vue-next";
</script>

<template>
  <div class="w-full px-3 pb-3">
    <!-- 模块外层容器 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      
      <!-- 标题 -->
      <div class="flex items-center gap-2 text-sm font-semibold text-[#F5F5F4]">
        <ShieldAlert class="w-4 h-4 text-[#F9C86D]" />
        <span>创建须知</span>
      </div>

      <div class="text-xs text-[#A8A29E] leading-relaxed">
        我们不支持创建的场景：
      </div>

      <ul class="flex flex-col gap-1.5 text-xs text-[#78716C] pl-2 list-disc list-inside">
        <li>涉及 18 岁以下角色的不适场景</li>
        <li>涉及现实中真实人物 / 组织的敏感场景</li>
        <li>严重违背社会公序良俗与过分暴露的场景</li>
      </ul>

    </div>
  </div>
</template>
