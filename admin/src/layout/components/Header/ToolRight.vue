<template>
  <div class="m-tool-right">
    <GlobalComSize class="item-children" />
    <HeaderSearch class="item-children" />
    <Remind class="item-children" />
    <ScreenFull class="item-children" />
    <Setting class="item-children" />
    <Avatar />
  </div>
</template>

<script lang="ts" setup>
import Avatar from './components/Avatar.vue';
import HeaderSearch from './components/HeaderSearch.vue';
import Remind from './components/Remind.vue';
import ScreenFull from './components/ScreenFull.vue';
import Setting from './components/Setting.vue';
import GlobalComSize from './components/globalComSize.vue';
</script>

<style lang="scss" scoped>
  .m-tool-right {
    display: flex;
    align-items: center;

    .item-children {
      margin-right: 22px;
    }
  }
</style>
