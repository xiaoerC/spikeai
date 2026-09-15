// 创建 axios 实例
import type { AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import axios from 'axios';

// 添加节流请求
const service = axios.create({
  baseURL: import.meta.env.VITE_APP_BASE_API,
  timeout: 50000,
  headers: { 'Content-Type': 'application/json;charset=utf-8' },
});

// 请求拦截器
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (!config.headers) {
      throw new Error(`Expected 'config' and 'config.headers' not to be undefined`);
    }
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      config.headers.token = token;
    }
    return config;
  },
  (error: any) => {
    return Promise.reject(error);
  },
);

// 响应拦截器
service.interceptors.response.use(
  (response: AxiosResponse) => {
    // 兼容 Blob 二进制文件
    if (Object.prototype.toString.call(response.data) === '[object Blob]') {
      return response.data;
    }
    // 标准后端响应包装 (例如 { code: 200 / 0, data: ... })
    if (response.data && typeof response.data === 'object') {
      if (
        response.data.code !== undefined &&
        response.data.code !== 0 &&
        response.data.code !== 200 &&
        response.data.code !== 20000
      ) {
        const errorMsg = response.data.message || '请求处理失败';
        ElMessage.error(errorMsg);
        return Promise.reject(new Error(errorMsg));
      }
    }
    return response.data;
  },
  (error: any) => {
    const status = error.response?.status;
    const errorData = error.response?.data;
    const errorMsg =
      (typeof errorData === 'object' && (errorData.message || errorData.detail)) ||
      error.message ||
      '网络请求异常';

    if (status === 401) {
      ElMessage.error('登录状态已失效，请重新登录');
      localStorage.removeItem('token');
      if (window.location.hash !== '#/login' && window.location.pathname !== '/login') {
        window.location.href = '#/login';
      }
    } else if (status === 403) {
      ElMessage.error(errorMsg || '操作被拒绝：暂无权限访问该资源');
    } else if (error.code === 'ERR_NETWORK') {
      ElMessage.error('无法连接到后台服务器，请检查后端服务是否已启动');
    } else {
      ElMessage.error(errorMsg);
    }
    return Promise.reject(error);
  },
);

const type = (level: string): any => {
  if (level === 'fail') {
    return 'error';
  }
  if (level === 'info') {
    return 'info';
  }
  if (level === 'warn') {
    return 'warning';
  }
};
// 导出 axios 实例
export default service;
