<template>
  <div class="m-setting" @click="changeSwitch('showSetting', true)">
    <el-tooltip effect="dark" content="主题设置" placement="bottom">
      <el-icon style="font-size: 20px" class="bell header-icon">
        <Setting />
      </el-icon>
    </el-tooltip>
  </div>
</template>

<script lang="ts" setup>
import { useSettingStore } from '@/store/modules/setting';
const SettingStore = useSettingStore();
const changeSwitch = (key, val) => {
  SettingStore.setThemeConfig({ key, val });
};
</script>

<style lang="scss" scoped>
  .m-setting {
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
  }

  .transverseMenu {
    .bell {
      color: white;
    }
  }
</style>
