/**
 * 客户端全局自适应断点与外壳布局管理 Composable (useResponsiveLayout)
 *
 * 借鉴与对齐 admin 后台工程自适应设计标准 (useResizeHandler)，
 * 统一管理移动端 (<768px)、平板 (768px~1200px) 与宽屏桌面端 (>1200px) 视口状态，
 * 提供桌面端侧边栏收起 (68px) / 展开 (220px) 状态机与窗口缩放防抖过渡。
 *
 * Usage:
 * ```ts
 * import { useResponsiveLayout } from "@/composables/useResponsiveLayout";
 *
 * const { isMobile, isDesktop, isSidebarCollapsed, toggleSidebar } = useResponsiveLayout();
 * ```
 *
 * @packageDocumentation
 */

import { computed, onMounted, onUnmounted, ref } from "vue";

/** 移动端与桌面端分水岭断点 (像素) */
export const MOBILE_BREAKPOINT = 768;

/** 桌面端侧边栏自动收缩断点 (像素) */
export const COLLAPSE_BREAKPOINT = 1200;

/** LocalStorage 侧边栏折叠偏好存储键名 */
const STORAGE_KEY_SIDEBAR_COLLAPSED = "naro_desktop_sidebar_collapsed";

// 全局单例状态（确保多组件消费时状态一致且共享同一套监听器）
const viewportWidth = ref<number>(typeof window !== "undefined" ? window.innerWidth : 1440);
const viewportHeight = ref<number>(typeof window !== "undefined" ? window.innerHeight : 900);
const isSidebarCollapsed = ref<boolean>(
  typeof window !== "undefined" ? window.innerWidth < COLLAPSE_BREAKPOINT : false,
);
const withoutAnimation = ref<boolean>(false);
let listenerCount = 0;
let resizeTimer: ReturnType<typeof setTimeout> | null = null;

export function useResponsiveLayout() {
  const isMobile = computed(() => viewportWidth.value < MOBILE_BREAKPOINT);
  const isTablet = computed(
    () => viewportWidth.value >= MOBILE_BREAKPOINT && viewportWidth.value < COLLAPSE_BREAKPOINT,
  );
  const isDesktop = computed(() => viewportWidth.value >= MOBILE_BREAKPOINT);
  const device = computed<"mobile" | "desktop">(() => (isMobile.value ? "mobile" : "desktop"));

  /**
   * 切换侧边栏展开/收起态
   */
  function toggleSidebar(): void {
    isSidebarCollapsed.value = !isSidebarCollapsed.value;
    try {
      localStorage.setItem(STORAGE_KEY_SIDEBAR_COLLAPSED, JSON.stringify(isSidebarCollapsed.value));
    } catch {
      // 忽略存储受限异常
    }
  }

  /**
   * 显式设置侧边栏折叠状态
   */
  function setSidebarCollapsed(collapsed: boolean): void {
    isSidebarCollapsed.value = collapsed;
    try {
      localStorage.setItem(STORAGE_KEY_SIDEBAR_COLLAPSED, JSON.stringify(collapsed));
    } catch {
      // 忽略存储受限异常
    }
  }

  function handleResize(): void {
    if (typeof window === "undefined" || document.hidden) return;

    // 缩放期间激活无动画，避免重排抖动
    withoutAnimation.value = true;
    viewportWidth.value = window.innerWidth;
    viewportHeight.value = window.innerHeight;

    if (resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      withoutAnimation.value = false;
    }, 200);
  }

  onMounted(() => {
    if (listenerCount === 0 && typeof window !== "undefined") {
      // 初始化读取持久化配置
      try {
        const saved = localStorage.getItem(STORAGE_KEY_SIDEBAR_COLLAPSED);
        if (saved !== null) {
          isSidebarCollapsed.value = JSON.parse(saved);
        } else {
          isSidebarCollapsed.value = window.innerWidth < COLLAPSE_BREAKPOINT;
        }
      } catch {
        isSidebarCollapsed.value = window.innerWidth < COLLAPSE_BREAKPOINT;
      }

      window.addEventListener("resize", handleResize, { passive: true });
    }
    listenerCount++;
  });

  onUnmounted(() => {
    listenerCount--;
    if (listenerCount <= 0 && typeof window !== "undefined") {
      window.removeEventListener("resize", handleResize);
      listenerCount = 0;
      if (resizeTimer) clearTimeout(resizeTimer);
    }
  });

  return {
    viewportWidth,
    viewportHeight,
    device,
    isMobile,
    isTablet,
    isDesktop,
    isSidebarCollapsed,
    withoutAnimation,
    toggleSidebar,
    setSidebarCollapsed,
  };
}
