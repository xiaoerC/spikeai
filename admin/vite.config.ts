import path, { resolve } from 'node:path';
import vue from '@vitejs/plugin-vue';
import vueJsx from '@vitejs/plugin-vue-jsx';
import { visualizer } from 'rollup-plugin-visualizer';
import UnoCSS from 'unocss/vite';
import AutoImport from 'unplugin-auto-import/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import Components from 'unplugin-vue-components/vite';
import { type ConfigEnv, type UserConfig, defineConfig, loadEnv } from 'vite';
import { VxeResolver, lazyImport } from 'vite-plugin-lazy-import';
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons';

export default defineConfig(({ mode }: ConfigEnv): UserConfig => {
  const pathSrc = path.resolve(__dirname, 'src');
  const root = process.cwd();
  const env = loadEnv(mode, root); // 环境变量对象
  return {
    root, //项目根目录（index.html 文件所在的位置） 默认： process.cwd()
    base: env.VITE_APP_BASE_PATHNAME, //  开发或生产环境服务的公共基础路径：默认'/'   1、绝对 URL 路径名： /foo/；  2、完整的 URL： https://foo.com/； 3、空字符串或 ./（用于开发环境）
    assetsInclude: resolve(__dirname, './src/assets'), // 静态资源处理
    // env配置文件变量前缀， 默认 VITE_，可自行定义
    envPrefix: 'VITE_',
    plugins: [
      vue(),
      vueJsx(),
      UnoCSS(),
      visualizer({ open: true }),
      lazyImport({
        resolvers: [
          VxeResolver({
            libraryName: 'vxe-pc-ui',
          }),
          VxeResolver({
            libraryName: 'vxe-table',
          }),
        ],
      }),
      AutoImport({
        resolvers: [ElementPlusResolver()],
        imports: ['vue', 'vue-router'],
        dts: path.resolve(pathSrc, 'types', 'auto-imports.d.ts'), // (false) 配置文件生成位置，默认是根目录 /auto-imports.d.ts
        eslintrc: {
          enabled: true, // 生成eslintrc配置文件，在项目根目录生成
          filepath: './.eslintrc-auto-import.json', // 指定eslintrc的文件路径
          globalsPropValue: true, // 配置默认的全局引入
        },
      }),
      Components({
        resolvers: [ElementPlusResolver()],
        dirs: ['src/components'],
        extensions: ['vue', 'tsx'],
        dts: path.resolve(pathSrc, 'types', 'components.d.ts'), // (false) 配置文件生成位置，默认是根目录 /components.d.ts
      }),
      createSvgIconsPlugin({
        // 指定需要缓存的图标文件夹
        iconDirs: [path.resolve(pathSrc, 'assets/icons')],
        // 指定symbolId格式
        symbolId: 'icon-[dir]-[name]',
      }),
    ],
    resolve: {
      alias: {
        '@': pathSrc,
        '@public': resolve('public'),
      },
    },
    build: {
      sourcemap: false,
      chunkSizeWarningLimit: 10240,
    },
    // 本地反向代理解决浏览器跨域限制
    server: {
      host: '0.0.0.0',
      port: Number(env.VITE_APP_PORT || 3000),
      open: false,
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:8080',
          changeOrigin: true,
          ws: true,
        },
      },
    },

    css: {
      preprocessorOptions: {
        // 导入scss全局变量
        scss: {
          additionalData: (content: string, filename: string) => {
            if (filename.includes('variables.scss') || filename.includes('index.scss')) {
              return content;
            }
            return `@use "@/styles/variables.scss" as *;\n${content}`;
          },
        },
      },
    },
  };
});
