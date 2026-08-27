<script setup lang="ts">
/**
 * 我的上传记录空状态卡片面板 (1:1 原型像素级高保真)
 *
 * @packageDocumentation
 */
</script>

<template>
  <div class="px-4 pt-2">
    <div class="w-full flex flex-col items-center justify-center p-8 rounded-[12px] border border-[#44403C] bg-[#292524] text-center shadow-lg">
      <!-- 1. 64x64 暗金五角星 (Figma 64:916) -->
      <div class="w-16 h-16 flex items-center justify-center">
        <svg
          width="64"
          height="64"
          viewBox="0 0 64 64"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            d="M32 0L38 20H60L42 32L48 52L32 40L16 52L22 32L4 20H26L32 0Z"
            fill="#F9C86D"
            fill-opacity="0.45"
          />
        </svg>
      </div>

      <!-- 2. 主标题 -->
      <h3 class="text-[16px] font-normal text-[#F5F5F4] leading-[27.2px] pt-6">
        您还没有上传任何角色到社区
      </h3>

      <!-- 3. 副描述 -->
      <p class="text-[14px] font-normal text-[#A8A29E] leading-[20px] pt-6">
        点击上方的"上传到社区"按钮开始上传您的角色卡
      </p>
    </div>
  </div>
</template>
