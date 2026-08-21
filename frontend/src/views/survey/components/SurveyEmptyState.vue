<script setup lang="ts">
/**
 * 问卷空状态组件 (1:1 原型高保真)
 *
 * @packageDocumentation
 */

defineProps<{
  text?: string;
}>();
</script>

<template>
  <div class="w-full flex flex-col items-center justify-center py-16 px-4 text-center">
    <p class="text-sm text-[#78716C]">
      {{ text || "目前暂无可参与的问卷" }}
    </p>
  </div>
</template>
