/** 后台组织架构与 RBAC 权限管理 API 强类型封装 */
import request from '@/utils/request';

export interface IAdminUserQuery {
  page?: number;
  size?: number;
  keyword?: string;
  department_id?: string;
  status?: string;
}

export interface IAdminUserItem {
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
  roles: IRoleItem[];
  role_names?: string;
  created_at: string;
  last_login_at?: string | null;
  last_login_ip?: string | null;
}

export interface IAdminUserPageResult {
  total: number;
  page: number;
  size: number;
  list: IAdminUserItem[];
}

export interface IAdminUserFormData {
  username?: string;
  email?: string;
  real_name?: string;
  password?: string;
  phone?: string | null;
  job_number?: string | null;
  department_id?: string | null;
  role_ids?: string[];
  status?: string;
}

export interface IRoleItem {
  id: string;
  role_key: string;
  name: string;
  description?: string | null;
  sort: number;
  status: string;
  created_at: string;
  permission_ids: string[];
}

export interface IRoleFormData {
  role_key?: string;
  name?: string;
  description?: string | null;
  sort?: number;
  status?: string;
  permission_ids?: string[];
}

export interface IDepartmentNode {
  id: string;
  parent_id?: string | null;
  name: string;
  leader?: string | null;
  phone?: string | null;
  sort: number;
  status: string;
  created_at: string;
  children: IDepartmentNode[];
}

export interface IDepartmentFormData {
  parent_id?: string | null;
  name?: string;
  leader?: string | null;
  phone?: string | null;
  sort?: number;
  status?: string;
}

export interface IPermissionTreeNode {
  id: string;
  parent_id?: string | null;
  type: 'directory' | 'menu' | 'button';
  title: string;
  code: string;
  path?: string | null;
  icon?: string | null;
  sort: number;
  status: string;
  children: IPermissionTreeNode[];
}

// ---------------- 用户管理 ----------------
export function getAdminUserList(params: IAdminUserQuery): Promise<IAdminUserPageResult> {
  return request({
    url: '/admin/rbac/users',
    method: 'get',
    params,
  });
}

export function createAdminUser(
  data: IAdminUserFormData,
): Promise<{ message: string; id: string }> {
  return request({
    url: '/admin/rbac/users',
    method: 'post',
    data,
  });
}

export function updateAdminUser(
  userId: string,
  data: IAdminUserFormData,
): Promise<{ message: string }> {
  return request({
    url: `/admin/rbac/users/${userId}`,
    method: 'put',
    data,
  });
}

export function resetAdminUserPassword(
  userId: string,
  new_password: string,
): Promise<{ message: string }> {
  return request({
    url: `/admin/rbac/users/${userId}/reset-password`,
    method: 'put',
    data: { new_password },
  });
}

export function deleteAdminUser(userId: string): Promise<{ message: string }> {
  return request({
    url: `/admin/rbac/users/${userId}`,
    method: 'delete',
  });
}

// ---------------- 角色管理 ----------------
export function getAdminRoleList(): Promise<IRoleItem[]> {
  return request({
    url: '/admin/rbac/roles',
    method: 'get',
  });
}

export function createAdminRole(data: IRoleFormData): Promise<{ message: string; id: string }> {
  return request({
    url: '/admin/rbac/roles',
    method: 'post',
    data,
  });
}

export function updateAdminRole(roleId: string, data: IRoleFormData): Promise<{ message: string }> {
  return request({
    url: `/admin/rbac/roles/${roleId}`,
    method: 'put',
    data,
  });
}

export function deleteAdminRole(roleId: string): Promise<{ message: string }> {
  return request({
    url: `/admin/rbac/roles/${roleId}`,
    method: 'delete',
  });
}

// ---------------- 部门架构 ----------------
export function getDepartmentTree(): Promise<IDepartmentNode[]> {
  return request({
    url: '/admin/rbac/departments',
    method: 'get',
  });
}

export function createDepartment(
  data: IDepartmentFormData,
): Promise<{ message: string; id: string }> {
  return request({
    url: '/admin/rbac/departments',
    method: 'post',
    data,
  });
}

export function updateDepartment(
  deptId: string,
  data: IDepartmentFormData,
): Promise<{ message: string }> {
  return request({
    url: `/admin/rbac/departments/${deptId}`,
    method: 'put',
    data,
  });
}

export function deleteDepartment(deptId: string): Promise<{ message: string }> {
  return request({
    url: `/admin/rbac/departments/${deptId}`,
    method: 'delete',
  });
}

// ---------------- 权限树 ----------------
export function getPermissionsTree(): Promise<IPermissionTreeNode[]> {
  return request({
    url: '/admin/rbac/permissions/tree',
    method: 'get',
  });
}
