/** 全局按钮级权限自定义指令 v-auth */
import { hasPerm } from '@/utils/permission';
import type { App, Directive, DirectiveBinding } from 'vue';

export const authDirective: Directive = {
  mounted(el: HTMLElement, binding: DirectiveBinding) {
    const { value } = binding;
    if (value) {
      const allowed = hasPerm(value);
      if (!allowed) {
        // 无权限时直接移除该 DOM 节点，杜绝显示
        el.parentNode?.removeChild(el);
      }
    } else {
      throw new Error('使用 v-auth 指令必须指定权限代码，如 v-auth="[\'system:user:create\']"');
    }
  },
};

export function setupAuthDirective(app: App) {
  app.directive('auth', authDirective);
}
