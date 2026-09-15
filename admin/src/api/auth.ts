/** 后台管理认证与个人中心 API 强类型封装 */
import request from '@/utils/request';

export interface ILoginParams {
  username: string;
  password: string;
}

export interface ILoginResult {
  token_type: string;
  access_token: string;
  expires_in: number;
}

export interface IMenuNode {
  id: string;
  parent_id?: string | null;
  type: 'directory' | 'menu' | 'button';
  title: string;
  name?: string | null;
  code: string;
  path?: string | null;
  component?: string | null;
  icon?: string | null;
  sort: number;
  is_hidden: boolean;
  children: IMenuNode[];
}

export interface IAdminUserInfo {
  id: string;
  username: string;
  email: string;
  real_name: string;
  avatar?: string | null;
  phone?: string | null;
  job_number?: string | null;
  department_id?: string | null;
  department_name?: string | null;
  is_super_admin: boolean;
  status: string;
}

export interface IAdminMeResult {
  user_info: IAdminUserInfo;
  roles: string[];
  permissions: string[];
  menus: IMenuNode[];
}

/** 管理员登录 */
export function loginApi(data: ILoginParams): Promise<ILoginResult> {
  return request({
    url: '/admin/auth/login',
    method: 'post',
    data,
  });
}

/** 获取当前管理员信息、角色、权限编码及菜单树 */
export function getAdminMeApi(): Promise<IAdminMeResult> {
  return request({
    url: '/admin/auth/me',
    method: 'get',
  });
}

/** 管理员安全注销 */
export function logoutApi(): Promise<{ message: string }> {
  return request({
    url: '/admin/auth/logout',
    method: 'post',
  });
}

export interface IChangePasswordParams {
  old_password: string;
  new_password: string;
}

/** 当前管理员自行修改登录密码 */
export function changePasswordApi(data: IChangePasswordParams): Promise<{ message: string }> {
  return request({
    url: '/admin/auth/change-password',
    method: 'put',
    data,
  });
}
