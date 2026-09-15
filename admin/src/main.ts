import { createApp } from 'vue';
import App from './App.vue';

// 引入iconfont
import '@/assets/iconfont/iconfont.css';
import '@/assets/iconfont/iconfont.js';
// 引入remixIconFont
import '@/assets/remixIconFont/remixicon.scss';
// unocss导入
import 'virtual:uno.css';
// svg
import 'virtual:svg-icons-register';
// 引入暗黑模式 element-plus 2.2 内置暗黑模式
import 'element-plus/dist/index.css';
import 'element-plus/theme-chalk/dark/css-vars.css';
// element-plus 图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
// 导入 vxe 基础主题变量
import 'vxe-pc-ui/styles/cssvar.scss';
// 自定义暗黑模式与全局覆盖
import '@/styles/element-dark.scss';
import '@/styles/index.scss';
// 权限路由
import './permission';
// 按钮权限指令
import { setupAuthDirective } from './directives/auth';

// vxe-table
import { VxeUI } from 'vxe-pc-ui';
import { VxeColgroup, VxeColumn, VxeGrid, VxeTable, VxeToolbar } from 'vxe-table';
// 路由
import router from './routers';
// pinia
import pinia from './store';

// 导入默认的语言
import zhCN from 'vxe-pc-ui/lib/language/zh-CN';

VxeUI.setI18n('zh-CN', zhCN);
VxeUI.setLanguage('zh-CN');

function setupVxeTable(app: any) {
  app.use(VxeTable);
  app.use(VxeColumn);
  app.use(VxeColgroup);
  app.use(VxeGrid);
  app.use(VxeToolbar);
}

import { parseTime } from './utils';

const app = createApp(App);
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}
app.config.globalProperties.$parseTime = parseTime;
app.use(router);
app.use(pinia);
app.use(setupVxeTable);
setupAuthDirective(app);
app.mount('#app');
