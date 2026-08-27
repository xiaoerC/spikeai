/**
 * 全局黑金高奢 Toast 消息通知 Composable
 *
 * @packageDocumentation
 */

import { reactive } from "vue";

export type ToastType = "success" | "error" | "info" | "warning";

export interface ToastItem {
  id: number;
  type: ToastType;
  message: string;
  duration?: number;
}

const state = reactive<{
  toasts: ToastItem[];
}>({
  toasts: [],
});

let idCounter = 0;

export function useToast() {
  function showToast(options: { type?: ToastType; message: string; duration?: number }): number {
    const id = ++idCounter;
    const toast: ToastItem = {
      id,
      type: options.type || "info",
      message: options.message,
      duration: options.duration ?? 3000,
    };

    state.toasts.push(toast);

    if (typeof toast.duration === "number" && toast.duration > 0) {
      setTimeout(() => {
        removeToast(id);
      }, toast.duration);
    }

    return id;
  }

  function removeToast(id: number): void {
    const index = state.toasts.findIndex((t) => t.id === id);
    if (index !== -1) {
      state.toasts.splice(index, 1);
    }
  }

  return {
    toasts: state.toasts,
    showToast,
    removeToast,
    success: (message: string, duration?: number) => showToast({ type: "success", message, duration }),
    error: (message: string, duration?: number) => showToast({ type: "error", message, duration }),
    info: (message: string, duration?: number) => showToast({ type: "info", message, duration }),
    warning: (message: string, duration?: number) => showToast({ type: "warning", message, duration }),
  };
}
