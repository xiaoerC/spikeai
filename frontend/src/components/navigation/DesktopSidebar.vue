<script setup lang="ts">
/**
 * 桌面端高奢常驻侧边栏组件 (DesktopSidebar.vue)
 *
 * 1:1 像素级还原参考截图 1 (展开态 220px) 与截图 2 (收起态 68px)。
 * 具备黑金磨砂玻璃底色、黄金独角兽 Logo、折叠动画与子菜单展开。
 *
 * @packageDocumentation
 */

import { useResponsiveLayout } from "@/composables/useResponsiveLayout";
import { useAppStore } from "@/stores/app";
import { useUserStore } from "@/stores/user";
import {
  Bell,
  ChevronLeft,
  ChevronRight,
  ClipboardList,
  Clock,
  HelpCircle,
  LayoutGrid,
  LogIn,
  MessageSquare,
  Wand2,
  Zap,
} from "lucide-vue-next";
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const { isSidebarCollapsed, toggleSidebar, withoutAnimation } = useResponsiveLayout();
const appStore = useAppStore();
const userStore = useUserStore();
const router = useRouter();
const route = useRoute();

/** 当前路由是否在角色社区家族内 */
const isCommunityActive = computed(() => {
  return (
    route.path === "/" ||
    route.path === "/creator" ||
    route.path === "/ranking" ||
    route.path === "/activity"
  );
});

/** 导航点击分发 */
function handleNavigate(path: string): void {
  if (route.path !== path) {
    router.push(path);
  }
}

/** 触发选购 / 充值对话框或提示 */
function handleShopClick(): void {
  if (!userStore.isLoggedIn) {
    appStore.openLoginModal();
  } else {
    router.push("/profile");
  }
}

/** 用户头像点击跳转个人中心或唤起登录 */
function handleUserClick(): void {
  if (userStore.isLoggedIn) {
    router.push("/profile");
  } else {
    appStore.openLoginModal();
  }
}
</script>

<template>
  <aside
    :class="[
      'h-full shrink-0 z-40 bg-[#16120E] border-r border-[#2D241C] flex flex-col justify-between select-none overflow-hidden',
      isSidebarCollapsed ? 'w-[68px]' : 'w-[220px]',
      withoutAnimation ? '' : 'transition-[width] duration-200 ease-in-out'
    ]"
  >
    <!-- 顶部 Logo 与系统主标题 -->
    <div class="flex flex-col min-h-0 flex-1">
      <div
        :class="[
          'h-16 flex items-center px-4 border-b border-[#251E17] shrink-0',
          isSidebarCollapsed ? 'justify-center px-2' : 'justify-between'
        ]"
      >
        <!-- 品牌标识 -->
        <router-link
          to="/"
          class="flex items-center gap-2.5 group cursor-pointer"
        >
          <!-- 叙梦专属独角兽/天马黄金徽章 -->
          <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-[#2D2318] to-[#1A140E] border border-[#F9C86D]/40 flex items-center justify-center shadow-[0_0_10px_rgba(249,200,109,0.25)] group-hover:scale-105 transition-transform shrink-0">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M19.5 7.05c-.35-.72-.94-1.3-1.66-1.66L15.5 4.1a3 3 0 0 0-3.32.42L10 6.3V4a1 1 0 0 0-1.7-.7L5.6 5.99A2.99 2.99 0 0 0 4.5 8.32V12c0 2.2 1.8 4 4 4h1.5a1 1 0 0 1 1 1v1.5a2.5 2.5 0 0 0 2.5 2.5h1a1 1 0 0 0 1-1v-2.1c1.2-.4 2.2-1.3 2.7-2.5l1.5-3.3a3 3 0 0 0 .3-2.05z" fill="#F9C86D"/>
            </svg>
          </div>

          <span
            v-if="!isSidebarCollapsed"
            class="text-base font-black tracking-widest text-[#F9C86D] drop-shadow-sm font-serif truncate"
          >
            NARO
          </span>
        </router-link>

        <!-- 展开态下的折叠收缩按钮 -->
        <button
          v-if="!isSidebarCollapsed"
          type="button"
          @click="toggleSidebar"
          class="p-1 rounded text-[#78716C] hover:text-[#F9C86D] hover:bg-[#2A221A] transition-colors cursor-pointer"
          title="收起侧边栏"
        >
          <ChevronLeft class="w-4 h-4" />
        </button>
      </div>

      <!-- 主功能导航菜单列表 (独立内部滚动，决不影响整体视口) -->
      <nav class="flex flex-col gap-1 p-2 overflow-y-auto min-h-0 flex-1 [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        
        <!-- 1. 角色社区 (带二级子菜单) -->
        <div class="flex flex-col">
          <button
            type="button"
            @click="handleNavigate('/')"
            :class="[
              'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
              isCommunityActive
                ? 'text-[#F9C86D] bg-[#2E251B] shadow-[inset_0_0_8px_rgba(249,200,109,0.15)] border border-[#F9C86D]/20'
                : 'text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14]'
            ]"
            :title="isSidebarCollapsed ? '角色社区' : undefined"
          >
            <LayoutGrid class="w-4 h-4 shrink-0" :class="isCommunityActive ? 'text-[#F9C86D]' : ''" />
            <span v-if="!isSidebarCollapsed" class="truncate">角色社区</span>
          </button>

          <!-- 展开态下的四级子项：角色、创作者、榜单、活动 (1:1 还原截图 1) -->
          <div
            v-if="!isSidebarCollapsed && isCommunityActive"
            class="flex flex-col ml-7 pl-2 my-1 border-l border-[#3A2E22] gap-0.5 text-xs animate-fade-in"
          >
            <button
              type="button"
              @click="handleNavigate('/')"
              :class="[
                'text-left py-1.5 px-2 rounded transition-colors cursor-pointer',
                route.path === '/' ? 'text-[#F9C86D] font-bold' : 'text-[#78716C] hover:text-[#D6D3D1]'
              ]"
            >
              角色
            </button>
            <button
              type="button"
              @click="handleNavigate('/creator')"
              :class="[
                'text-left py-1.5 px-2 rounded transition-colors cursor-pointer',
                route.path === '/creator' ? 'text-[#F9C86D] font-bold' : 'text-[#78716C] hover:text-[#D6D3D1]'
              ]"
            >
              创作者
            </button>
            <button
              type="button"
              @click="handleNavigate('/ranking')"
              :class="[
                'text-left py-1.5 px-2 rounded transition-colors cursor-pointer',
                route.path === '/ranking' ? 'text-[#F9C86D] font-bold' : 'text-[#78716C] hover:text-[#D6D3D1]'
              ]"
            >
              榜单
            </button>
            <button
              type="button"
              @click="handleNavigate('/activity')"
              :class="[
                'text-left py-1.5 px-2 rounded transition-colors cursor-pointer',
                route.path === '/activity' ? 'text-[#F9C86D] font-bold' : 'text-[#78716C] hover:text-[#D6D3D1]'
              ]"
            >
              活动
            </button>
          </div>
        </div>

        <!-- 2. 选购 / 商店 -->
        <button
          type="button"
          @click="handleShopClick"
          class="flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14] transition-all cursor-pointer"
          :title="isSidebarCollapsed ? '选购' : undefined"
        >
          <Zap class="w-4 h-4 shrink-0 text-[#EAB308]" />
          <span v-if="!isSidebarCollapsed" class="truncate">选购</span>
        </button>

        <!-- 3. 历史记录 -->
        <button
          type="button"
          @click="handleNavigate('/history')"
          :class="[
            'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
            route.path === '/history'
              ? 'text-[#F9C86D] bg-[#2E251B] border border-[#F9C86D]/20'
              : 'text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14]'
          ]"
          :title="isSidebarCollapsed ? '历史记录' : undefined"
        >
          <Clock class="w-4 h-4 shrink-0" :class="route.path === '/history' ? 'text-[#F9C86D]' : ''" />
          <span v-if="!isSidebarCollapsed" class="truncate">历史记录</span>
        </button>

        <!-- 4. 创作 -->
        <button
          type="button"
          @click="handleNavigate('/create')"
          :class="[
            'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
            route.path === '/create'
              ? 'text-[#F9C86D] bg-[#2E251B] border border-[#F9C86D]/20'
              : 'text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14]'
          ]"
          :title="isSidebarCollapsed ? '创作' : undefined"
        >
          <Wand2 class="w-4 h-4 shrink-0" :class="route.path === '/create' ? 'text-[#F9C86D]' : ''" />
          <span v-if="!isSidebarCollapsed" class="truncate">创作</span>
        </button>

        <!-- 5. 公告 -->
        <button
          type="button"
          @click="handleNavigate('/notice')"
          :class="[
            'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
            route.path === '/notice'
              ? 'text-[#F9C86D] bg-[#2E251B] border border-[#F9C86D]/20'
              : 'text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14]'
          ]"
          :title="isSidebarCollapsed ? '公告' : undefined"
        >
          <Bell class="w-4 h-4 shrink-0" :class="route.path === '/notice' ? 'text-[#F9C86D]' : ''" />
          <span v-if="!isSidebarCollapsed" class="truncate">公告</span>
        </button>

        <!-- 6. 聊天室 -->
        <button
          type="button"
          @click="handleNavigate('/character-history')"
          :class="[
            'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
            route.path.startsWith('/chat') || route.path === '/character-history'
              ? 'text-[#F9C86D] bg-[#2E251B] border border-[#F9C86D]/20'
              : 'text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14]'
          ]"
          :title="isSidebarCollapsed ? '聊天室' : undefined"
        >
          <MessageSquare class="w-4 h-4 shrink-0" :class="route.path.startsWith('/chat') ? 'text-[#F9C86D]' : ''" />
          <span v-if="!isSidebarCollapsed" class="truncate">聊天室</span>
        </button>

        <!-- 7. 问卷 -->
        <button
          type="button"
          @click="handleNavigate('/survey')"
          :class="[
            'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
            route.path === '/survey'
              ? 'text-[#F9C86D] bg-[#2E251B] border border-[#F9C86D]/20'
              : 'text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14]'
          ]"
          :title="isSidebarCollapsed ? '问卷' : undefined"
        >
          <ClipboardList class="w-4 h-4 shrink-0" :class="route.path === '/survey' ? 'text-[#F9C86D]' : ''" />
          <span v-if="!isSidebarCollapsed" class="truncate">问卷</span>
        </button>

        <!-- 8. 客服中心 -->
        <button
          type="button"
          @click="handleNavigate('/help')"
          :class="[
            'flex items-center gap-3 w-full px-3 py-2.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
            route.path === '/help'
              ? 'text-[#F9C86D] bg-[#2E251B] border border-[#F9C86D]/20'
              : 'text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-[#221B14]'
          ]"
          :title="isSidebarCollapsed ? '客服中心' : undefined"
        >
          <HelpCircle class="w-4 h-4 shrink-0" :class="route.path === '/help' ? 'text-[#F9C86D]' : ''" />
          <span v-if="!isSidebarCollapsed" class="truncate">客服中心</span>
        </button>

      </nav>
    </div>

    <!-- 底部区域 (根据展开/收起态分别对齐截图 1 与截图 2) -->
    <div class="p-3 border-t border-[#251E17] flex flex-col gap-2 shrink-0">
      
      <!-- 收起态下的展开箭头与用户入口 (截图 2 样式) -->
      <template v-if="isSidebarCollapsed">
        <button
          type="button"
          @click="toggleSidebar"
          class="flex items-center justify-center w-full py-2 text-[#78716C] hover:text-[#F9C86D] hover:bg-[#221B14] rounded-lg transition-colors cursor-pointer"
          title="展开侧边栏"
        >
          <ChevronRight class="w-4 h-4" />
        </button>

        <button
          type="button"
          @click="handleUserClick"
          class="w-10 h-10 mx-auto rounded-full bg-gradient-to-br from-[#2D2318] to-[#1A140E] border border-[#F9C86D]/40 flex items-center justify-center text-[#F9C86D] hover:scale-105 transition-transform cursor-pointer shadow-md"
          :title="userStore.isLoggedIn ? userStore.profile?.username : '登录账号'"
        >
          <img
            v-if="userStore.isLoggedIn && userStore.profile?.avatar_url"
            :src="userStore.profile.avatar_url"
            class="w-full h-full rounded-full object-cover"
          />
          <LogIn v-else class="w-4 h-4" />
        </button>
      </template>

      <!-- 展开态下的法律协议与用户登录/充值入口 (截图 1 样式) -->
      <template v-else>
        <!-- 法律合规微文本 -->
        <div class="flex flex-col gap-0.5 text-[10px] text-[#574F47] px-2 mb-1">
          <span class="text-[#78716C]">法律条款</span>
          <div class="flex items-center gap-2">
            <span class="hover:text-[#A8A29E] cursor-pointer">用户协议</span>
            <span>·</span>
            <span class="hover:text-[#A8A29E] cursor-pointer">隐私政策</span>
          </div>
          <span class="hover:text-[#A8A29E] cursor-pointer">消费须知</span>
        </div>

        <!-- 用户登录与充值卡片 -->
        <div
          v-if="userStore.isLoggedIn"
          class="flex items-center justify-between p-2 rounded-lg bg-[#221A13] border border-[#3A2E22]"
        >
          <div
            @click="router.push('/profile')"
            class="flex items-center gap-2 cursor-pointer min-w-0"
          >
            <div class="w-8 h-8 rounded-full bg-[#2D2318] border border-[#F9C86D]/50 flex items-center justify-center shrink-0 overflow-hidden">
              <img
                v-if="userStore.profile?.avatar_url"
                :src="userStore.profile.avatar_url"
                class="w-full h-full object-cover"
              />
              <span v-else class="text-xs text-[#F9C86D] font-bold">
                {{ userStore.profile?.username?.slice(0, 1) || "U" }}
              </span>
            </div>
            <div class="flex flex-col min-w-0">
              <span class="text-xs font-bold text-[#F5F5F4] truncate">
                {{ userStore.profile?.username || "旅人" }}
              </span>
              <span class="text-[10px] text-[#F9C86D]">
                {{ userStore.starCoins }} 金币
              </span>
            </div>
          </div>

          <button
            type="button"
            @click="handleShopClick"
            class="px-2 py-1 rounded text-[11px] font-bold bg-[#F9C86D] text-black hover:bg-[#F9C86D]/90 active:scale-95 transition-all cursor-pointer"
          >
            充值
          </button>
        </div>

        <div v-else class="flex items-center gap-2">
          <button
            type="button"
            @click="appStore.openLoginModal()"
            class="flex-1 py-1.5 rounded-lg text-xs font-bold bg-[#F9C86D] text-black hover:bg-[#F9C86D]/90 active:scale-95 transition-all cursor-pointer text-center"
          >
            登录
          </button>
          <button
            type="button"
            @click="appStore.openRegisterModal()"
            class="px-3 py-1.5 rounded-lg text-xs font-medium text-[#A8A29E] bg-[#221B14] hover:text-[#F5F5F4] border border-[#3A2E22] transition-colors cursor-pointer"
          >
            注册
          </button>
        </div>
      </template>

    </div>
  </aside>
</template>
