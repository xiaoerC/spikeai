<template>
  <div class="m-info">
    <el-popover width="200px" placement="bottom">
      <template #reference>
        <el-badge :value="3" class="item-info-pop">
          <el-icon class="bell header-icon" style="font-size: 20px"><Bell /></el-icon>
        </el-badge>
      </template>
      <div>
        <el-tabs v-model="activeName" class="demo-tabs" @tab-click="handleClick">
          <el-tab-pane label="通知" name="first">
            <div class="item-child">
              通知消息一：
              <el-button type="primary" link> 点我 </el-button>
            </div>
            <el-divider style="margin-bottom: 15px" />
            <div class="item-child">
              通知消息二：
              <el-button type="primary" link> 点我 </el-button>
            </div>
            <el-divider />
            <div class="item-child">
              通知消息三：
              <el-button type="primary" link> 点我 </el-button>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-popover>
  </div>
</template>

<script lang="ts" setup>
import type { TabsPaneContext } from 'element-plus';
import { ref } from 'vue';

const activeName = ref('first');
const toGitHub = (link) => {
  window.open(link);
};
const handleClick = (tab: TabsPaneContext, event: Event) => {
  console.log(tab, event);
};
</script>

<style lang="scss" scoped>
  .m-info {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
    cursor: pointer;

    .item-info-pop {
      display: flex;
      align-items: center;
    }

    .bell {
      color: var(--header-text-color);
      transition: color 0.2s;

      &:hover {
        color: var(--el-color-primary);
      }
    }

    .item-child {
      display: flex;
      align-items: center;
      font-size: 13px;
    }
  }

  ::v-deep(.el-divider--horizontal) {
    margin-top: 10px;
    margin-bottom: 10px;
  }

  .transverseMenu {
    .bell {
      color: white;
    }
  }
</style>
