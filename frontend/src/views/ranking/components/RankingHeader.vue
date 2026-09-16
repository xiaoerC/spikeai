<script setup lang="ts">
/**
 * 榜单页面顶部 Header 导航组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

import { ArrowLeft } from "lucide-vue-next";
import { useRouter } from "vue-router";

const router = useRouter();

function handleBack() {
  if (window.history.length > 1) {
    router.back();
  } else {
    router.push("/");
  }
}
</script>

<template>
  <header class="sticky top-0 z-40 w-full max-w-[440px] md:max-w-none mx-auto px-4 py-3.5 flex items-center justify-between bg-[rgba(26,21,16,0.92)] backdrop-blur-md border-b border-white/5 shadow-md">
    <div class="flex items-center justify-between w-full max-w-[1200px] mx-auto">
      <!-- 左侧返回按钮 -->
      <button
        type="button"
        @click="handleBack"
        class="p-1 rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/10 active:scale-95 transition-all cursor-pointer"
      >
        <ArrowLeft class="w-5 h-5" />
      </button>

      <!-- 中间居中标题 -->
      <h1 class="text-base font-bold text-[#F5F5F4] tracking-wide pr-6">
        等级榜
      </h1>

      <!-- 占位保持居中 -->
      <div class="w-5" />
    </div>
  </header>
</template>
