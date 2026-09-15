<template>
  <div class="main-container">
    <UHeader />
    <Main />
    <Footer />
  </div>
</template>

<script lang="ts" setup>
import Footer from '../components/Footer/index.vue';
import Main from '../components/Main/index.vue';
import Sidebar from '../components/Sidebar/index.vue';
import UHeader from './HeaderHorizontal/index.vue';
</script>

<style lang="scss" scoped>
  .main-container {
    display: flex;
    box-sizing: border-box;
    flex: 1;
    flex-direction: column;
    min-height: 100%;
  }
</style>
