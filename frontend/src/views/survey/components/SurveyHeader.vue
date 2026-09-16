<script setup lang="ts">
/**
 * 问卷页面顶部 Header 导航与介绍组件 (1:1 原型高保真)
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
  <header class="sticky top-0 z-40 w-full max-w-[440px] md:max-w-none mx-auto pt-3 px-4 pb-2 flex flex-col bg-[rgba(26,21,16,0.92)] backdrop-blur-md">
    <div class="w-full max-w-[1000px] mx-auto">
      <!-- 顶部返回行 -->
      <div class="flex items-center justify-between">
      <button
        type="button"
        @click="handleBack"
        class="p-1 rounded-lg text-[#A8A29E] hover:text-white hover:bg-white/10 active:scale-95 transition-all cursor-pointer"
      >
        <ArrowLeft class="w-5 h-5" />
      </button>
      <div class="w-5" />
    </div>

      <!-- 标题与副标题区 -->
      <div class="flex flex-col items-center text-center mt-1">
        <h1 class="text-xl font-semibold text-[#F9C86D] tracking-tight">
          问卷调查
        </h1>
        <p class="text-xs text-[#78716C] mt-1">
          参与问卷分享你的想法，完成即可获得星元奖励
        </p>
      </div>
    </div>
  </header>
</template>
