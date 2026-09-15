import { createPinia } from 'pinia';
// 引入持久化插件
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

const pinia = createPinia();
//pinia使用
pinia.use(piniaPluginPersistedstate);

export default pinia;
