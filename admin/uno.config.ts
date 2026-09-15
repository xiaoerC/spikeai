import {
  defineConfig,
  presetAttributify,
  presetIcons,
  presetUno,
  transformerDirectives,
} from 'unocss';

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
      el: {
        primary: 'var(--el-color-primary)',
        'primary-light-3': 'var(--el-color-primary-light-3)',
        'primary-light-7': 'var(--el-color-primary-light-7)',
        'primary-light-9': 'var(--el-color-primary-light-9)',
        bg: 'var(--el-bg-color)',
        page: 'var(--el-bg-color-page)',
        overlay: 'var(--el-bg-color-overlay)',
        border: 'var(--el-border-color)',
        'border-light': 'var(--el-border-color-lighter)',
        text: 'var(--el-text-color-primary)',
        'text-regular': 'var(--el-text-color-regular)',
        'text-secondary': 'var(--el-text-color-secondary)',
      },
    },
  },
  shortcuts: [
    ['flex-center', 'flex items-center justify-center'],
    ['flex-between', 'flex items-center justify-between'],
    ['table-page-container', 'flex flex-col size-full p-4 box-border overflow-hidden'],
    [
      'card-base',
      'bg-[var(--el-bg-color-overlay)] rounded-lg border border-[var(--el-border-color-lighter)] p-4 transition-all shadow-[var(--shadow-1)]',
    ],
    [
      'filter-form-wrap',
      'flex flex-wrap items-center gap-3 mb-4 bg-[var(--el-bg-color-overlay)] p-4 rounded-lg border border-[var(--el-border-color-lighter)]',
    ],
  ],
});
