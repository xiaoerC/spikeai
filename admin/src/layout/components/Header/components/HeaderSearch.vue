<template>
  <div class="m-headerSearch">
    <el-tooltip effect="dark" content="菜单搜索" placement="bottom">
      <el-icon class="bell header-icon" style="font-size: 22px" @click="handleSearch">
        <Search />
      </el-icon>
    </el-tooltip>
    <el-dialog v-model="isShowSearch" width="600px" destroy-on-close :show-close="false">
      <el-select
        ref="headerSearchSelect"
        v-model="search"
        style="width: 100%"
        :remote-method="querySearch"
        filterable
        default-first-option
        remote
        placeholder="菜单搜索 ：支持菜单名称、路径"
        class="header-search-select"
        @change="change"
      >
        <el-option
          v-for="item in options"
          :key="item.item.path"
          :value="item.item.path"
          :label="item && item.item.title && item.item.title.length && item.item.title.join(' > ')"
        ></el-option>
      </el-select>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import Fuse from 'fuse.js';
import path from 'path-browserify';
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
const router = useRouter();
const isShowSearch = ref(false);
const options = ref<any>([]);
const searchPool = ref([]);
const search = ref('');
const fuse = ref();
import { usePermissionStore } from '@/store/modules/permission';
const PermissionStore = usePermissionStore();
const routes = computed(() => PermissionStore.routes);

const handleSearch = () => {
  isShowSearch.value = true;
};
const initFuse = (list: any[]) => {
  fuse.value = new Fuse(list, {
    shouldSort: true,
    threshold: 0.4, // 匹配阈值，值越小匹配越严格
    ignoreLocation: true, // 忽略字段中的位置
    minMatchCharLength: 2, // 最小匹配字符长度改为2，减少1个字符的噪声匹配
    keys: [
      {
        name: 'title',
        weight: 0.7,
      },
      {
        name: 'path',
        weight: 0.3,
      },
    ],
  });
};

watch(searchPool, (list) => {
  initFuse(list);
});

// 筛选出可以在侧栏中显示的路线 生成标题
const generateRoutes = (routes, basePath = '/', prefixTitle = []) => {
  let res: any = [];

  for (const router of routes) {
    // 忽略隐藏的路由
    if (router.hidden) {
      continue;
    }

    const data: any = {
      path: path.resolve(basePath, router.path),
      title: [...prefixTitle],
    };
    if (router.meta && router.meta.title) {
      data.title = [...data.title, router.meta.title];

      if (router.redirect !== 'noRedirect') {
        // 仅推送带有标题的路由
        // 特殊情况：需要排除无重定向的父路由器
        res.push(data);
      }
    }
    // 递归子路由
    if (router.children) {
      const tempRoutes = generateRoutes(router.children, data.path, data.title);
      if (tempRoutes.length >= 1) {
        res = [...res, ...tempRoutes];
      }
    }
  }
  return res;
};

const change = (val) => {
  if (val) {
    router.push({
      path: val,
    });
  }
  options.value = [];
  search.value = '';
  isShowSearch.value = false;
};
onMounted(() => {
  searchPool.value = generateRoutes(JSON.parse(JSON.stringify(routes.value)));
});

const querySearch = (query) => {
  if (query !== '') {
    options.value = fuse.value.search(query);
  } else {
    options.value = [];
  }
};
</script>

<style lang="scss" scoped>
  .m-headerSearch {
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    cursor: pointer;

    .bell {
      color: var(--header-text-color);
      transition: color 0.2s;

      &:hover {
        color: var(--el-color-primary);
      }
    }

    :deep(.el-dialog) {
      .el-dialog__header {
        display: none;
      }

      .el-dialog__body {
        padding: 0;
      }
    }

    .header-search-select {
      height: 50px;

      :deep(.el-input__wrapper) {
        height: 50px;
      }
    }
  }

  .transverseMenu {
    .bell {
      color: white;
    }
  }
</style>
