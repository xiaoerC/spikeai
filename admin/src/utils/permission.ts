/** 细粒度按钮/操作权限校验辅助工具 */
import { useUserStore } from '@/store/modules/user';

/**
 * 校验当前登录管理员是否持有指定的一个或多个权限代码
 * @param value 权限代码 (如 'system:user:create' 或 ['system:user:create', 'system:user:update'])
 * @returns boolean 是否具有权限
 */
export function hasPerm(value: string | string[]): boolean {
  if (!value) return true;

  const userStore = useUserStore();
  // 超级管理员拥有最高全权限放行
  if (userStore.userInfo?.is_super_admin) {
    return true;
  }

  const userPerms = userStore.permissions || [];
  if (Array.isArray(value)) {
    return value.some((perm) => userPerms.includes(perm));
  }
  return userPerms.includes(value);
}
