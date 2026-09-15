<template>
  <div class="main-columns">
    <div class="layout-columns-aside">
      <div class="logo flex-center">
        <img src="@/assets/image/logo.svg" alt="SpikeAI" class="w-8 h-8" />
      </div>
      <el-scrollbar>
        <div class="menu-wrap">
          <div
            v-for="item in menusRoutes"
            :key="item.path"
            class="item-menu-wrap"
            :class="{
              'active-menu': activeCurrentMenu === item.path
            }"
            @click="handleChangeMenu(item)"
          >
            <el-icon :size="20">
              <component :is="item?.meta?.icon"></component>
            </el-icon>
            <span class="title">{{ item?.meta?.title }}</span>
          </div>
        </div>
      </el-scrollbar>
    </div>

    <div class="layout-columns-sub" :style="{ width: isCollapse ? '60px' : '210px' }">
      <div class="logo flex-center">
        <span v-show="subMenus.length">{{ isCollapse ? 'Spike' : 'SpikeAI Admin' }}</span>
      </div>
      <el-scrollbar>
        <el-menu
          :collapse="isCollapse"
          :router="false"
          :default-active="activeMenu"
          :unique-opened="SettingStore.themeConfig.uniqueOpened"
          :collapse-transition="false"
          class="menu-columns"
        >
          <SubMenu :menu-list="subMenus" />
        </el-menu>
      </el-scrollbar>
    </div>

    <div class="col-container">
      <div class="layout-header">
        <div class="header-tool">
          <HeaderToolLeft />
          <HeaderToolRight />
        </div>
        <TagsView v-if="themeConfig.showTag" />
      </div>
      <Main />
      <Footer />
    </div>
  </div>
</template>

<script setup lang="ts">
import { usePermissionStore } from '@/store/modules/permission';
import { useSettingStore } from '@/store/modules/setting';
import { computed, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Footer from '../components/Footer/index.vue';
import SubMenu from '../components/SubMenu/SubMenu.vue';
import TagsView from '../components/TagsView/index.vue';
const PermissionStore = usePermissionStore();
const SettingStore = useSettingStore();
const route = useRoute();
const router = useRouter();
import type { RouteRecordRaw } from 'vue-router';
import HeaderToolLeft from '../components/Header/ToolLeft.vue';
import HeaderToolRight from '../components/Header/ToolRight.vue';
import Main from '../components/Main/index.vue';

// 获取路由
const permission_routes = computed(() => PermissionStore.permission_routes);

// 获取路由
const menusRoutes = computed(() => {
  return permission_routes.value.filter((item: any) => !item.hidden);
});

// 折叠菜单
const isCollapse = computed(() => SettingStore.isCollapse);

const themeConfig = computed(() => SettingStore.themeConfig);

const subMenus = ref<RouteRecordRaw[]>([]);

const activeCurrentMenu = ref('');

// 选中的菜单
const activeMenu = computed<string>(() => {
  const { meta, path } = route;
  if (meta.activeMenu) {
    return String(meta.activeMenu);
  }
  return path;
});

const filterRoutes = () => {
  menusRoutes.value.map((item: any) => {
    if (route.path.includes(item.path)) {
      activeCurrentMenu.value = item.path;
      subMenus.value = item.children || [];
    }
  });
};

const handleChangeMenu = (item: any) => {
  router.push(item.path);
};

watch(
  () => route.path,
  () => {
    filterRoutes();
  },
  {
    immediate: true,
  },
);
</script>

<style lang="scss" scoped>
.main-columns {
  display: flex;
  width: 100%;
  height: 100%;

  .layout-columns-aside {
    display: flex;
    flex-direction: column;
    width: 70px;
    height: 100%;
    background: #1e222d;

    .logo {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 50px;
    }

    .menu-wrap {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 10px 0;

      .item-menu-wrap {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 54px;
        height: 54px;
        border-radius: 8px;
        color: #a6adb4;
        cursor: pointer;
        transition: all 0.2s;

        &:hover,
        &.active-menu {
          color: #fff;
          background: var(--el-color-primary, #409eff);
        }

        .title {
          margin-top: 4px;
          font-size: 11px;
          white-space: nowrap;
        }
      }
    }
  }

  .layout-columns-sub {
    display: flex;
    flex-direction: column;
    height: 100%;
    background: #fff;
    border-right: 1px solid var(--el-border-color-light);
    transition: width 0.3s;

    .logo {
      display: flex;
      align-items: center;
      justify-content: center;
      height: 50px;
      border-bottom: 1px solid var(--el-border-color-light);
      color: #333;
      font-weight: 600;
    }
  }

  .col-container {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-width: 0;
    height: 100%;
    overflow: hidden;

    .layout-header {
      background: #fff;
      border-bottom: 1px solid var(--el-border-color-light);

      .header-tool {
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 50px;
        padding: 0 16px;
      }
    }
  }
}
</style>

