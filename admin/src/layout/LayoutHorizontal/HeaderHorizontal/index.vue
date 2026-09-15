<template>
  <!--纵向布局-->
  <Height />
  <div
    class="m-layout-header"
    :class="{
      'fixed-header': themeConfig.fixedHeader
    }"
  >
    <div class="header-inner">
      <el-menu
        mode="horizontal"
        :default-active="activeMenu"
        background-color="#304156"
        text-color="#bfcbd9"
        :unique-opened="SettingStore.themeConfig.uniqueOpened"
        :collapse-transition="false"
        class="menu-horizontal"
      >
        <SubItem v-for="route in permission_routes" :key="route.path" :item="route" />
      </el-menu>
      <HeaderToolRight />
    </div>
    <TagsView v-if="themeConfig.showTag" />
  </div>
</template>

<script lang="ts" setup>
import { usePermissionStore } from '@/store/modules/permission';
import { useRoute } from 'vue-router';
import HeaderToolRight from '../../components/Header/ToolRight.vue';
// 引入组件
import Height from '../../components/Header/components/Height.vue';
import SubItem from '../../components/SubMenu/SubItem.vue';
import TagsView from '../../components/TagsView/index.vue';
const PermissionStore = usePermissionStore();

const route = useRoute();

// 获取路由
const permission_routes = computed(() => PermissionStore.permission_routes);
import { useSettingStore } from '@/store/modules/setting';
import { computed } from 'vue';
const SettingStore = useSettingStore();

const activeMenu = computed(() => {
  const { meta, path } = route;
  return String(meta.activeMenu || path); // 强制转换为字符串
});

// 主题配置
const themeConfig = computed(() => SettingStore.themeConfig);
const isCollapse = computed(() => !SettingStore.isCollapse);
</script>

<style lang="scss" scoped>
  @use './index' as *;
</style>
