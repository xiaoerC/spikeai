import { useToast } from "@/composables/useToast";
import router from "@/router";
import { useUserStore } from "@/stores/user";
import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from "axios";

export interface ApiResponse<T = any> {
  code: number;
  message: string;
  show_message?: boolean;
  data: T;
}

const api: AxiosInstance = axios.create({
  baseURL: "/api/v1",
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截器：自动注入 JWT Bearer Token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("naro_access_token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// 响应拦截器：解包统一业务响应，根据 show_message 自动弹出 Toast，捕获 401 自动清理凭证并退回主页
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    if (response.data?.show_message && response.data?.message) {
      const { showToast } = useToast();
      showToast({ type: "success", message: response.data.message });
    }
    return response;
  },
  async (error) => {
    const resData = error.response?.data;
    const errorMsg = resData?.message || resData?.detail;
    if (errorMsg && typeof errorMsg === "string") {
      const { showToast } = useToast();
      showToast({ type: "error", message: errorMsg });
    }

    if (error.response?.status === 401 || resData?.code === 40100 || resData?.code === 401) {
      try {
        const userStore = useUserStore();
        userStore.resetState();
      } catch (_) {
        localStorage.removeItem("naro_access_token");
      }

      // 如果当前在需要登录权限的页面 (如个人中心)，自动回退至主页
      const currentPath = router.currentRoute.value?.path || "";
      const protectedPrefixes = ["/profile", "/creator"];
      if (
        protectedPrefixes.some((p) => currentPath.startsWith(p)) ||
        router.currentRoute.value?.meta?.requiresAuth
      ) {
        await router.push("/");
      }
    }
    return Promise.reject(error);
  },
);

export default api;
