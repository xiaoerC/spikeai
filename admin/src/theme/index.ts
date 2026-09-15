import { BLACK, PRE, PRE_DARK, PRE_LIGHT, WHITE } from './token';

/**
 * 预设主题颜色列表（符合现代设计规范的企业级调色板）
 */
export const THEME_PRESET_COLORS: string[] = [
  '#409EFF', // 科技蓝（默认）
  '#00B96B', // 极客绿
  '#1677FF', // 极光蓝
  '#722ED1', // 典雅紫
  '#13C2C2', // 碧青色
  '#FA8C16', // 琥珀金
  '#EB2F96', // 玫瑰粉
  '#304156', // 曜石蓝灰
  '#2F54EB', // 深海蓝
  '#52C41A', // 鲜活绿
  '#FAAD14', // 暖阳金
  '#F5222D', // 烈焰红
];

/**
 * 十六进制颜色与白/黑混合算法
 * @param color1 基准色（十六进制）
 * @param color2 混入色（十六进制）
 * @param weight 混入比例 0~1
 */
export function mixColor(color1: string, color2: string, weight: number): string {
  const clampWeight = Math.max(Math.min(Number(weight), 1), 0);
  const r1 = Number.parseInt(color1.substring(1, 3), 16);
  const g1 = Number.parseInt(color1.substring(3, 5), 16);
  const b1 = Number.parseInt(color1.substring(5, 7), 16);
  const r2 = Number.parseInt(color2.substring(1, 3), 16);
  const g2 = Number.parseInt(color2.substring(3, 5), 16);
  const b2 = Number.parseInt(color2.substring(5, 7), 16);

  const r = Math.round(r1 * (1 - clampWeight) + r2 * clampWeight);
  const g = Math.round(g1 * (1 - clampWeight) + g2 * clampWeight);
  const b = Math.round(b1 * (1 - clampWeight) + b2 * clampWeight);

  const _r = ('0' + (r || 0).toString(16)).slice(-2);
  const _g = ('0' + (g || 0).toString(16)).slice(-2);
  const _b = ('0' + (b || 0).toString(16)).slice(-2);
  return '#' + _r + _g + _b;
}

/**
 * 全局应用主题色并生成 1~9 级衍生色与 dark-2 色阶
 * @param color 选中的十六进制主色
 * @param isDark 是否处于暗黑模式
 */
export function applyThemeColor(color?: string, isDark = false): void {
  if (!color || typeof document === 'undefined') return;

  const html = document.documentElement;

  // 1. 设置主颜色
  html.style.setProperty(PRE, color);

  // 2. 循环生成 1 ~ 9 级次阶衍生色
  if (isDark) {
    // 暗黑模式下：使用深色背景进行阶梯淡化，防止产生高反差白边
    for (let i = 1; i < 9; i += 1) {
      html.style.setProperty(`${PRE_LIGHT}-${i}`, mixColor(color, '#141414', i * 0.08));
    }
    html.style.setProperty(`${PRE_LIGHT}-9`, '#1a1a1a');
    // 深阶色在暗黑下提升微光高亮
    html.style.setProperty(`${PRE_DARK}-2`, mixColor(color, WHITE, 0.2));
  } else {
    // 明亮模式下：与纯白混合生成浅阶色
    for (let i = 1; i < 10; i += 1) {
      html.style.setProperty(`${PRE_LIGHT}-${i}`, mixColor(color, WHITE, i * 0.1));
    }
    // 深阶色在明亮模式下混合黑色生成暗阶 hover 色
    html.style.setProperty(`${PRE_DARK}-2`, mixColor(color, BLACK, 0.2));
  }
}

/**
 * 切换全局字体族
 * @param typeface 字体族名称
 */
export function useChangeTypeface(typeface: string): void {
  if (typeof document === 'undefined') return;
  document.documentElement.style.setProperty('--el-font-family', typeface);
}

// 兼容旧导出
export const themeColors = THEME_PRESET_COLORS;
export function useElementPlusTheme(color?: string): void {
  applyThemeColor(color, false);
}
export function useElementPlusDarkTheme(color?: string): void {
  applyThemeColor(color, true);
}
