<template>
  <div class="sidebar-logo-container">
    <transition name="sidebarLogoFadeCl">
      <router-link v-if="isCollapse" key="collapse" class="sidebar-logo-link" to="/">
        <img src="@/assets/image/logo.svg" class="sidebar-logo" alt="SpikeAI" />
      </router-link>
      <router-link v-else key="expand" class="sidebar-logo-link" to="/">
        <img src="@/assets/image/logo.svg" class="sidebar-logo" alt="SpikeAI" />
        <h1 class="sidebar-title">SpikeAI Admin</h1>
      </router-link>
    </transition>
  </div>
</template>

<script lang="ts" setup>
defineProps<{ isCollapse: boolean }>();
</script>

<style lang="scss" scoped>
  .sidebarLogoFadeCl-enter-active {
    transition: opacity 2s;
  }

  .sidebarLogoFadeCl-enter-from,
  .sidebarLogoFadeCl-leave-to {
    opacity: 0;
  }

  .sidebar-logo-container {
    position: relative;
    width: 100%;
    height: 50px;
    overflow: hidden;
    background-color: var(--sidebar-bg-color);
    border-bottom: 1px solid var(--sidebar-border-color);
    box-sizing: border-box;
    line-height: 50px;
    text-align: center;
    transition: background-color 0.28s, border-color 0.28s;

    .sidebar-logo-link {
      width: 100%;
      height: 100%;

      .sidebar-logo {
        width: 32px;
        height: 32px;
        vertical-align: middle;
      }

      .sidebar-title {
        display: inline-block;
        margin: 0;
        margin-left: 12px;
        color: var(--el-text-color-primary);
        font-size: 15px;
        font-weight: 600;
        line-height: 50px;
        vertical-align: middle;
      }
    }
  }
</style>
