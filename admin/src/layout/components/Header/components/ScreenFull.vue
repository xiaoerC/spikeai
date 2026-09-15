<template>
  <div class="m-screenful">
    <el-tooltip effect="dark" content="全屏" placement="bottom">
      <!--      <svg-icon-->
      <!--        :icon-class="isFullscreen ? 'exit-fullscreen' : 'fullscreen'"-->
      <!--        @click="toggle"-->
      <!--        className="header-icon"-->
      <!--      />-->
      <el-icon style="font-size: 20px" class="bell header-icon">
        <FullScreen @click="toggle" />
      </el-icon>
    </el-tooltip>
  </div>
</template>

<script lang="ts" setup>
import Setting from '@/layout/components/Header/components/Setting.vue';
import { useFullscreen } from '@vueuse/core';
const { toggle, isFullscreen } = useFullscreen();
</script>

<style lang="scss" scoped>
  .m-screenful {
    display: flex;
    align-items: center;
    justify-content: center;
    padding-right: 0;
    transition: all 0.3s;
    cursor: pointer;
  }
</style>
