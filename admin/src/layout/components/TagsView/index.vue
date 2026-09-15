<template>
  <div class="m-tags-view">
    <div class="tags-view">
      <el-tabs v-model="activeTabsValue" type="card" @tab-click="tabClick" @tab-remove="removeTab">
        <el-tab-pane
          v-for="item in visitedViews"
          :key="item.path"
          :path="item.path"
          :label="item.title"
          :name="item.path"
          :closable="!(item.meta && item.meta.affix)"
        >
          <template #label>
            <el-icon v-if="item.icon" class="tabs-icon">
              <component :is="item.icon"></component>
            </el-icon>
            {{ item.title }}
          </template>
        </el-tab-pane>
      </el-tabs>
    </div>
    <div class="right-btn">
      <MoreButton />
    </div>
  </div>
</template>
<script lang="ts" setup>
import { usePermissionStore } from '@/store/modules/permission';
import { useTagsViewStore } from '@/store/modules/tagsView';
import type { TabsPaneContext } from 'element-plus';
import path from 'path-browserify';
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import MoreButton from './components/MoreButton.vue';

const route = useRoute();
const router = useRouter();
const TagsViewStore = useTagsViewStore();
const PermissionStore = usePermissionStore();
const visitedViews = computed<any>(() => TagsViewStore.visitedViews);
const routes = computed(() => PermissionStore.routes);

const addTags = () => {
  const { name } = route;
  if (name === 'Login') {
    return;
  }
  if (name) {
    TagsViewStore.addView(route);
  }
  return false;
};
const affixTags = ref([]);
function filterAffixTags(routes, basePath = '/') {
  let tags: any = [];
  routes.forEach((route) => {
    if (route.meta && route.meta.affix) {
      const tagPath = path.resolve(basePath, route.path);
      tags.push({
        fullPath: tagPath,
        path: tagPath,
        name: route.name,
        meta: { ...route.meta },
      });
    }
    if (route.children) {
      const tempTags = filterAffixTags(route.children, route.path);
      if (tempTags.length >= 1) {
        tags = [...tags, ...tempTags];
      }
    }
  });
  return tags;
}
const initTags = () => {
  const routesNew = routes.value;
  const affixTag = (affixTags.value = filterAffixTags(routesNew));
  for (const tag of affixTag) {
    if (tag.name) {
      TagsViewStore.addVisitedView(tag);
    }
  }
};
onMounted(() => {
  initTags();
  addTags();
});
watch(route, () => {
  addTags();
});
const tabIndex = 2;
const activeTabsValue = computed({
  get: () => {
    return TagsViewStore.activeTabsValue;
  },
  set: (val) => {
    TagsViewStore.setTabsMenuValue(val);
  },
});
function toLastView(activeTabPath) {
  const index = visitedViews.value.findIndex((item) => item.path === activeTabPath);
  const nextTab = visitedViews.value[index + 1] || visitedViews.value[index - 1];
  if (!nextTab) return;
  router.push(nextTab.path);
  TagsViewStore.addVisitedView(nextTab);
}
const tabClick = (tabItem: TabsPaneContext) => {
  const path = tabItem.props.name as string;
  router.push(path);
};

const isActive = (path) => {
  return path === route.path;
};
const removeTab = async (name: string | number) => {
  const activeTabPath = name.toString(); // 确保转换为字符串
  if (isActive(activeTabPath)) {
    toLastView(activeTabPath);
  }
  await TagsViewStore.delView(activeTabPath);
};
</script>
<style lang="scss" scoped>
  .m-tags-view {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-right: 12px;
    padding-left: 12px;
    background-color: var(--tags-view-bg-color);
    border-bottom: 1px solid var(--header-border-color);
    box-sizing: border-box;
    transition: background-color 0.28s, border-color 0.28s;

    .right-btn {
      flex-shrink: 0;
      height: 100%;
    }
  }

  .tags-view {
    box-sizing: border-box;
    flex: 1;
    overflow: hidden;

    .el-tabs--card :deep(.el-tabs__header) {
      box-sizing: border-box;
      height: 38px;
      margin: 0;
      padding: 0 4px;
      border-bottom: none;
    }

    :deep(.el-tabs) {
      .el-tabs__nav {
        border: none;
        gap: 6px;
        display: flex;
        align-items: center;
      }

      .el-tabs__header .el-tabs__item {
        border: 1px solid var(--tags-view-item-border);
        border-radius: 6px;
        height: 28px;
        line-height: 26px;
        padding: 0 12px;
        margin: 0;
        font-size: 12px;
        font-weight: 500;
        color: var(--el-text-color-regular);
        background-color: var(--tags-view-item-bg);
        transition: all 0.2s ease;

        &:hover {
          color: var(--el-color-primary);
        }

        .is-icon-close {
          margin-left: 6px;
          border-radius: 50%;
          font-size: 11px;
          transition: background-color 0.15s;

          &:hover {
            background-color: var(--el-fill-color-dark);
            color: #fff;
          }
        }
      }

      .el-tabs__header .el-tabs__item.is-active {
        background-color: var(--tags-view-item-active-bg);
        color: var(--el-color-primary);
        border-color: var(--el-color-primary-light-7, #bfdbfe);
        font-weight: 600;
      }
    }
  }
</style>
