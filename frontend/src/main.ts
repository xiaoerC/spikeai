import { createPinia } from "pinia";
import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

// 引入 Tailwind CSS 强力重置库 (彻底去除 button, input, border, background 浏览器系统原生丑陋样式)
import "@unocss/reset/tailwind.css";
// 引入 UnoCSS 虚拟样式
import "virtual:uno.css";

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");
