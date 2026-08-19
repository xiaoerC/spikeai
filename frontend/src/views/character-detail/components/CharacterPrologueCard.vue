<script setup lang="ts">
/**
 * 角色卡详情 - 序幕剧情卡片 (1:1 原型高保真米白纸质拟物风格)
 *
 * @packageDocumentation
 */

import { ChevronDown, ChevronUp, Plus } from "lucide-vue-next";
import { ref } from "vue";

defineProps<{
  prologue: {
    title: string;
    description: string;
    worldInfo: string;
    charactersInfo: string;
  };
}>();

const isWorldOpen = ref(false);
const isCharactersOpen = ref(false);
</script>

<template>
  <div class="w-full flex flex-col gap-2 px-3 pt-4 select-none">
    
    <!-- 1. 标题: • 序幕 -->
    <div class="flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-[#F9C86D]" />
      <h2 class="text-[18px] font-semibold text-[#F9C86D] tracking-[-0.36px] leading-6 font-sans">
        序幕
      </h2>
    </div>

    <!-- 2. 米白纸质拟物卡片主体 (min-height: 480px, background: #F5F2EB, text: #443425) -->
    <div class="w-full rounded-2xl bg-[#F5F2EB] text-[#2C241E] p-6 shadow-2xl flex flex-col items-center justify-between min-h-[460px] border border-[#E6DFC8] relative overflow-hidden">
      
      <!-- 纸张暗纹与微晕边 -->
      <div class="absolute inset-0 bg-gradient-to-b from-white/30 via-transparent to-[#E8E0D0]/40 pointer-events-none" />

      <!-- (1) Dolce Notte 艺术大标题 -->
      <div class="w-full flex flex-col items-center pt-8 z-10">
        <h3 class="text-4xl font-serif font-black tracking-wider text-[#2A1E14] drop-shadow-sm text-center italic">
          {{ prologue.title || "Dolce Notte" }}
        </h3>

        <!-- 手写风副标题 / 诗意导语 -->
        <p class="text-[16px] text-[#5A4838] font-serif tracking-widest mt-6 text-center leading-relaxed">
          {{ prologue.description || "藏在老街区深处的一间不太好找的店。" }}
        </p>
      </div>

      <!-- (2) 底部两个拟物圆角微凸折叠卡片 (关于世界 / 主要角色) -->
      <div class="w-full flex flex-col gap-3 pb-4 z-10">
        
        <!-- 关于世界 -->
        <div class="w-full rounded-2xl bg-white/70 backdrop-blur-md border border-[#E2DAC8] shadow-sm overflow-hidden transition-all">
          <button
            type="button"
            @click="isWorldOpen = !isWorldOpen"
            class="w-full px-5 py-3.5 flex items-center justify-between text-left cursor-pointer hover:bg-white/90 transition-colors"
          >
            <span class="text-[15px] font-serif font-bold text-[#3D3025]">
              关于世界
            </span>
            <div class="w-6 h-6 rounded-full bg-[#EFE9DC] flex items-center justify-center text-[#9E8B77]">
              <ChevronUp v-if="isWorldOpen" class="w-4 h-4" />
              <Plus v-else class="w-4 h-4" />
            </div>
          </button>

          <!-- 展开内容 -->
          <div v-if="isWorldOpen" class="px-5 pb-4 text-xs text-[#5A4838] leading-relaxed animate-fade-in font-sans">
            {{ prologue.worldInfo }}
          </div>
        </div>

        <!-- 主要角色 -->
        <div class="w-full rounded-2xl bg-white/70 backdrop-blur-md border border-[#E2DAC8] shadow-sm overflow-hidden transition-all">
          <button
            type="button"
            @click="isCharactersOpen = !isCharactersOpen"
            class="w-full px-5 py-3.5 flex items-center justify-between text-left cursor-pointer hover:bg-white/90 transition-colors"
          >
            <span class="text-[15px] font-serif font-bold text-[#3D3025]">
              主要角色
            </span>
            <div class="w-6 h-6 rounded-full bg-[#EFE9DC] flex items-center justify-center text-[#9E8B77]">
              <ChevronUp v-if="isCharactersOpen" class="w-4 h-4" />
              <Plus v-else class="w-4 h-4" />
            </div>
          </button>

          <!-- 展开内容 -->
          <div v-if="isCharactersOpen" class="px-5 pb-4 text-xs text-[#5A4838] leading-relaxed animate-fade-in font-sans">
            {{ prologue.charactersInfo }}
          </div>
        </div>

      </div>

    </div>

  </div>
</template>
