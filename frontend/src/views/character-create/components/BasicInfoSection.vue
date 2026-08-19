<script setup lang="ts">
/**
 * 模块 3: 基本信息组件 (1:1 原型高保真)
 *
 * 包含详细描述、性格特征与背景场景。
 *
 * @packageDocumentation
 */

defineProps<{
  /** 详细描述 */
  description: string;
  /** 性格特征 */
  personality: string;
  /** 背景场景 */
  scenario: string;
}>();

const emit = defineEmits<{
  (e: "update:description", val: string): void;
  (e: "update:personality", val: string): void;
  (e: "update:scenario", val: string): void;
}>();
</script>

<template>
  <div class="w-full px-3 pb-3">
    <!-- 模块外层容器 -->
    <div class="w-full p-5 rounded-xl border border-[rgba(83,71,65,0.20)] bg-[rgba(26,25,21,0.60)] backdrop-blur-md flex flex-col gap-4 shadow-xl">
      
      <!-- 1. 模块主标题 (蓝色圆柱指示条 + 基本信息) -->
      <div class="flex items-center gap-3">
        <div class="w-1 h-6 rounded-full bg-[#3B82F6] shadow-[0_0_10px_rgba(59,130,246,0.5)]" />
        <h2 class="text-[18px] font-semibold text-[#F5F5F4] tracking-[0.9px] leading-tight select-none">
          基本信息
        </h2>
      </div>

      <!-- 2. ① 详细描述 -->
      <div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-[#F5F5F4]">
          详细描述
        </label>
        <textarea
          :value="description"
          @input="emit('update:description', ($event.target as HTMLTextAreaElement).value)"
          rows="3"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-sm text-gray-100 placeholder-[#78716C] focus:border-[#3B82F6] transition-colors resize-none leading-relaxed"
          placeholder="关于故事或者角色最核心的描述"
        />
      </div>

      <!-- 3. ② 性格特征 -->
      <div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-[#F5F5F4]">
          性格特征
        </label>
        <textarea
          :value="personality"
          @input="emit('update:personality', ($event.target as HTMLTextAreaElement).value)"
          rows="3"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-sm text-gray-100 placeholder-[#78716C] focus:border-[#3B82F6] transition-colors resize-none leading-relaxed"
          placeholder="描述角色的性格特点、行为方式、说话风格等...（如果是故事卡，也许并不需要哦）"
        />
      </div>

      <!-- 4. ③ 背景场景 -->
      <div class="flex flex-col gap-2">
        <label class="text-sm font-medium text-[#F5F5F4]">
          背景场景
        </label>
        <textarea
          :value="scenario"
          @input="emit('update:scenario', ($event.target as HTMLTextAreaElement).value)"
          rows="3"
          class="w-full p-3 rounded-lg border border-[rgba(83,71,65,0.40)] bg-[rgba(42,37,32,0.50)] text-sm text-gray-100 placeholder-[#78716C] focus:border-[#3B82F6] transition-colors resize-none leading-relaxed"
          placeholder="描述故事的整体背景或者角色所处环境哦."
        />
      </div>

    </div>
  </div>
</template>
