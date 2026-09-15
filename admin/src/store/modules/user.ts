import { type ILoginParams, getAdminMeApi, loginApi, logoutApi } from '@/api/auth';
import store from '@/store';
import { ElMessage } from 'element-plus';
import { defineStore } from 'pinia';
import type { PersistenceOptions } from 'pinia-plugin-persistedstate';
import type { IUserInfo, IUserStore } from './type';

export const useUserStore = defineStore('userState', {
  state: (): IUserStore => ({
    token: localStorage.getItem('token') || '',
    userInfo: null,
    roles: [],
    permissions: [],
  }),
  actions: {
    // 登录
    async login(params: ILoginParams) {
      const res = await loginApi(params);
      this.token = res.access_token;
      localStorage.setItem('token', this.token);
      // 登录后拉取权限和信息
      await this.fetchUserInfo();
    },
    // 获取用户信息、角色及权限清单
    async fetchUserInfo() {
      const res = await getAdminMeApi();
      this.userInfo = {
        ...res.user_info,
        name: res.user_info.real_name,
        photo: res.user_info.avatar || '',
      };
      this.roles = res.roles;
      this.permissions = res.permissions;
      return res;
    },
    // 兼容获取角色
    async getRoles() {
      if (this.roles && this.roles.length > 0) {
        return this.roles;
      }
      const res = await this.fetchUserInfo();
      return res.roles;
    },
    // 退出
    async logout(router?: any) {
      try {
        await logoutApi();
      } catch (error) {
        console.error('退出接口异常:', error);
      } finally {
        this.token = '';
        this.userInfo = null;
        this.roles = [];
        this.permissions = [];
        localStorage.removeItem('token');
        if (router) {
          router.replace({ name: 'login' });
        }
        ElMessage.success('已安全退出');
      }
    },
  },

  // 进行持久化存储
  persist: {
    // 本地存储的名称
    key: import.meta.env.VITE_APP_NAME + '_userState',
    //保存的位置
    storage: localStorage, //localstorage
    pick: ['token', 'roles', 'permissions'], // 只持久化 token 和 roles，userInfo 不持久化
    serializer: {
      serialize: JSON.stringify,
      deserialize: JSON.parse,
    },
  } as PersistenceOptions,
});

export function useUserStoreHook() {
  return useUserStore(store);
}
