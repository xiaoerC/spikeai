<script setup lang="ts">
/**
 * 叙梦 Naro - 公告中心 / 系统公告与更新日志 (Smart Container 主入口)
 *
 * 1:1 像素级还原公告页面，展示 4 大分类 Tabs 与更新/活动/系统公告列表流。
 *
 * @packageDocumentation
 */

import BottomTabBar from "@/components/navigation/BottomTabBar.vue";
import { useAppStore } from "@/stores/app";
import LoginModal from "@/views/login/components/LoginModal.vue";
import NoticeDetailModal from "@/views/notice/components/NoticeDetailModal.vue";
import NoticeHeader from "@/views/notice/components/NoticeHeader.vue";
import NoticeListItem from "@/views/notice/components/NoticeListItem.vue";
import { useNoticeList } from "@/views/notice/composables/useNoticeList";

const appStore = useAppStore();
const {
  notices,
  totalCount,
  currentCategory,
  selectedNotice,
  isModalOpen,
  setCategory,
  openNoticeDetail,
} = useNoticeList();
</script>

<template>
  <div class="flex flex-col min-h-screen w-full bg-gradient-to-br from-[#1A1511] to-[#2A221A] md:bg-none md:bg-[#15120E] text-gray-100 relative">
    
    <!-- 1. 顶部 Header 与分类 Tabs -->
    <NoticeHeader
      :current-category="currentCategory"
      :total-count="totalCount"
      @select-category="setCategory"
    />

    <!-- 2. 主内容区: 公告列表流 -->
    <main class="w-full max-w-[440px] md:max-w-[1200px] mx-auto px-3 md:px-6 pt-3 md:pt-6 pb-24 md:pb-12 flex flex-col gap-2.5">
      <NoticeListItem
        v-for="notice in notices"
        :key="notice.id"
        :notice="notice"
        @select="openNoticeDetail"
      />
    </main>

    <!-- 3. 全局底部 5-Tab Bar -->
    <BottomTabBar />

    <!-- 4. 公告详情弹窗 -->
    <NoticeDetailModal
      v-model:open="isModalOpen"
      :notice="selectedNotice"
    />

    <!-- 5. 登录弹窗 -->
    <LoginModal v-model:open="appStore.isLoginModalOpen" />

  </div>
</template>
