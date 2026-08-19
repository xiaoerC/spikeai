/**
 * 移动端视口与软键盘避让工具库。
 *
 * 核心机制: 利用 window.visualViewport 监听移动端软键盘弹起，
 * 动态计算输入区域抬升偏移量，彻底避免 iOS/Android 键盘遮挡输入框或顶飞布局。
 *
 * Usage:
 *   import { setupVisualViewportListener } from "@/utils/viewport";
 *   const cleanup = setupVisualViewportListener((keyboardHeight, isKeyboardOpen) => {
 *     console.log("Keyboard height:", keyboardHeight, isKeyboardOpen);
 *   });
 */

export type KeyboardChangeCallback = (keyboardHeight: number, isKeyboardOpen: boolean) => void;

/**
 * 注册移动端视觉视口动态监听器。
 *
 * @param onKeyboardChange - 软键盘状态变化回调函数
 * @returns 清理与注销监听器的函数
 */
export function setupVisualViewportListener(onKeyboardChange: KeyboardChangeCallback): () => void {
  if (typeof window === "undefined" || !window.visualViewport) {
    return () => {};
  }

  const viewport = window.visualViewport;

  const handleResize = () => {
    // 当 visualViewport 高度小于 window.innerHeight 超过 120px 时判定为软键盘弹起
    const currentHeight = viewport.height;
    const windowHeight = window.innerHeight;
    const diff = windowHeight - currentHeight;

    if (diff > 120) {
      onKeyboardChange(diff, true);
    } else {
      onKeyboardChange(0, false);
    }
  };

  viewport.addEventListener("resize", handleResize);
  viewport.addEventListener("scroll", handleResize);

  return () => {
    viewport.removeEventListener("resize", handleResize);
    viewport.removeEventListener("scroll", handleResize);
  };
}

/**
 * 判断当前是否处于移动端小屏视口 (< 768px)。
 *
 * @returns boolean
 */
export function checkIsMobileViewport(): boolean {
  if (typeof window === "undefined") return false;
  return window.innerWidth < 768;
}
