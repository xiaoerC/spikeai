import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetUno,
  transformerDirectives,
} from "unocss";

export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons({
      scale: 1.2,
      warn: true,
    }),
  ],
  transformers: [transformerDirectives()],
  theme: {
    colors: {
      obsidian: {
        bg: "#0F0D0C", // 最深邃黑底
        surface: "#1A1714", // 复合面板底色
        card: "#292524", // 卡片底色
        border: "#44403C", // 幽暗分割线
        glass: "rgba(26, 23, 20, 0.95)", // 磨砂玻璃色
      },
      naro: {
        gold: "#F9C86D", // 叙梦经典高亮香槟金
        amber: "#D4AF37", // 琥珀金
        goldDark: "#B8860B", // 暗金
        orange: "#FF9F43", // 指标橙色
        fire: "#EAB308", // 热度火苗金
        search: "#A18D6F", // 搜索提示文字
        muted: "#A8A29E", // 次级浅灰文字
        dim: "#78716C", // 幽暗灰文本
      },
      gold: {
        50: "#FFFDF0",
        100: "#FFF9C2",
        200: "#FEF08A",
        300: "#FDE047",
        400: "#EAB308",
        500: "#F9C86D", // 叙梦经典香槟金
        600: "#D4AF37",
        700: "#B8860B",
        glow: "rgba(249, 200, 109, 0.35)", // 金色微光
      },
      accent: {
        purple: "#8A2BE2", // 绅士/高贵紫
        pink: "#FF69B4", // 吉祥物粉鸟红
        cyan: "#00F0FF", // 科技霓虹蓝
      },
    },
    boxShadow: {
      gold: "0 0 12px 0 rgba(249, 198, 109, 0.25)",
      "gold-lg": "0 0 24px 2px rgba(249, 198, 109, 0.35)",
      "gold-card":
        "0 0 8px 0 rgba(249, 198, 109, 0.15), 0 2px 4px 0 rgba(0, 0, 0, 0.10)",
      glass:
        "0 10px 20px 0 rgba(0, 0, 0, 0.60), 0 6px 10px 0 rgba(0, 0, 0, 0.50)",
    },
  },
  shortcuts: [
    // 叙梦豪华黑金双层渐变卡片外框
    [
      "naro-card-frame",
      "rounded-xl border-[0.67px] border-transparent bg-gradient-to-b from-[#1a1510] to-[#1a1510] shadow-gold-card relative overflow-hidden transition-transform duration-150 active:scale-[0.98]",
    ],
    // 黑金磨砂玻璃卡片
    [
      "glass-panel",
      "bg-obsidian-glass backdrop-blur-xl border border-obsidian-border/60 rounded-lg shadow-glass",
    ],
    // 金色高光按钮
    [
      "btn-gold",
      "bg-naro-gold text-[#0C0A09] font-bold px-4 py-2 rounded-lg shadow-gold active:scale-95 transition-all duration-150 cursor-pointer select-none disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100",
    ],
    // 幽暗微光次级按钮
    [
      "btn-ghost",
      "bg-obsidian-surface/80 hover:bg-obsidian-card text-naro-muted border border-obsidian-border px-4 py-2 rounded-lg transition-all duration-150 active:scale-95 cursor-pointer select-none disabled:opacity-50 disabled:cursor-not-allowed disabled:active:scale-100",
    ],
    // 标签微胶囊
    [
      "tag-pill",
      "px-2.5 py-1 rounded-full border border-[rgba(249,200,109,0.15)] bg-[rgba(249,200,109,0.08)] text-naro-muted text-xs font-medium flex items-center justify-center cursor-pointer transition-all duration-150 active:scale-95 whitespace-nowrap",
    ],
    // 标签微胶囊激活态
    [
      "tag-pill-active",
      "px-2.5 py-1 rounded-full border border-naro-gold bg-naro-gold text-[#0C0A09] text-xs font-bold flex items-center justify-center cursor-pointer shadow-gold active:scale-95 whitespace-nowrap",
    ],
    // 抽屉遮罩与容器 (轻量通透蒙版 + 150ms 顺滑过渡)
    [
      "drawer-overlay",
      "fixed inset-0 z-50 bg-black/55 backdrop-blur-sm transition-opacity duration-150",
    ],
    [
      "drawer-content",
      "fixed bottom-0 left-0 right-0 z-50 max-w-[460px] mx-auto bg-obsidian-surface border-t border-[rgba(249,200,109,0.2)] rounded-t-[24px] shadow-2xl flex flex-col focus:outline-none overflow-hidden max-h-[90vh]",
    ],
    [
      "drawer-handle",
      "w-10 h-1 rounded-full bg-[#44403C] mx-auto my-3 shrink-0 cursor-grab active:cursor-grabbing",
    ],
    // 模态弹窗遮罩与容器 (轻透蒙版 + 150ms 快速响应)
    [
      "modal-overlay",
      "fixed inset-0 z-50 bg-black/55 backdrop-blur-sm flex items-center justify-center p-4 transition-opacity duration-150",
    ],
    [
      "modal-content",
      "relative z-50 w-full max-w-[400px] bg-obsidian-surface border border-[rgba(249,200,109,0.25)] rounded-2xl p-5 shadow-gold-card shadow-glass focus:outline-none flex flex-col space-y-4 transition-transform duration-150",
    ],
  ],
  rules: [
    // iOS/Android 安全区工具类
    ["pt-safe", { "padding-top": "env(safe-area-inset-top, 0px)" }],
    ["pb-safe", { "padding-bottom": "env(safe-area-inset-bottom, 0px)" }],
    ["pl-safe", { "padding-left": "env(safe-area-inset-left, 0px)" }],
    ["pr-safe", { "padding-right": "env(safe-area-inset-right, 0px)" }],
  ],
});
