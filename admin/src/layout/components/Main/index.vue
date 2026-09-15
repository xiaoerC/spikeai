<template>
  <div class="app-main">
    <router-view v-slot="{ Component, route }">
      <transition name="fade-slide" mode="out-in" appear>
        <keep-alive v-if="isReload" :include="cacheRoutes">
          <component :is="useWrapComponents(Component, route)" :key="route.path" />
        </keep-alive>
      </transition>
    </router-view>
  </div>
</template>

<script lang="ts" setup>
import { useWrapComponents } from '@/hooks/useWrapComponents';
import { usePermissionStore } from '@/store/modules/permission';
import { useSettingStore } from '@/store/modules/setting';
const SettingStore = useSettingStore();
const PermissionStore = usePermissionStore();
const cacheRoutes = computed(() => {
  return PermissionStore.keepAliveRoutes
    .filter((name) => name !== undefined) // 过滤掉undefined
    .map((name) => name.toString()); // 确保转换为字符串
});
const isReload = computed(() => SettingStore.isReload);
</script>

<style lang="scss" scoped>
  .app-main {
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
    width: 100%;
    flex: 1;
    min-height: calc(100% - 90px);
    padding: 16px;
    overflow-x: hidden;

    > * {
      box-sizing: border-box;
      width: 100% !important;
      max-width: 100% !important;
    }

    .app-main-inner {
      display: flex;
      box-sizing: border-box;
      flex: 1;
      width: 100%;
      height: 100%;
      overflow-x: hidden;
      border: unset !important;
      border-radius: 12px !important;
      background-color: var(--el-bg-color) !important;
      box-shadow: 0 0 15px 2px rgb(0 0 0 / 3%);
    }
  }

</style>
