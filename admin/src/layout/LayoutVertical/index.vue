<template>
  <!--纵向布局-->
  <Sidebar />
  <div class="main-container">
    <HeaderVertical />
    <Main />
    <!--    <Footer />-->
  </div>
</template>

<script lang="ts" setup>
import Footer from '../components/Footer/index.vue';
import Main from '../components/Main/index.vue';
import Sidebar from '../components/Sidebar/index.vue';
import HeaderVertical from './HeaderVertical/index.vue';
</script>

<style lang="scss" scoped>
  .main-container {
    display: flex;
    box-sizing: border-box;
    flex: 1;
    flex-direction: column;
    min-height: 100%;
  }

  .g-container-layout {
    width: 100%;
    height: 100%;

    .main-container {
      display: flex;
      box-sizing: border-box;
      flex-direction: column;
      height: 100%;
    }

    &.mobile.openSidebar {
      position: fixed;
      top: 0;
    }
  }

  .sidebar-container {
    display: flex;
    flex-direction: column;
  }

  .drawer-bg {
    position: absolute;
    z-index: 90;
    top: 0;
    width: 100%;
    height: 100%;
    opacity: 0.3;
    background: #000;
  }
</style>
