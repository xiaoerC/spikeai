import requestAnimationFrameThrottle from '@/utils/requestAnimationFrameThrottle';
import { onBeforeUnmount } from 'vue';

/**
 * 监听图表容器尺寸变化并自动调用 resize 的 Composable
 *
 * @param chart ECharts 实例
 * @param chartsRef 图表 DOM 元素
 *
 * Usage:
 *   const { addObserver } = useResizeElement(myChart, chartDom);
 *   addObserver();
 */
export const useResizeElement = (chart: any, chartsRef: HTMLElement) => {
  let observer: ResizeObserver | null = null;
  let widthW = 0;
  let heightW = 0;

  const handleResize = (entries: ResizeObserverEntry[]) => {
    const { contentRect } = entries[0];
    let { width, height } = contentRect;
    width = Math.floor(width);
    height = Math.floor(height);
    if (widthW !== width || heightW !== height) {
      widthW = width;
      heightW = height;
      chart?.resize();
    }
  };

  const addObserver = () => {
    if (typeof ResizeObserver !== 'undefined' && chartsRef) {
      observer = new ResizeObserver(requestAnimationFrameThrottle(handleResize));
      observer.observe(chartsRef);
    }
  };

  const removeObserver = () => {
    if (observer) {
      observer.disconnect();
      observer = null;
    }
    chart?.dispose();
  };

  onBeforeUnmount(() => {
    removeObserver();
  });

  return {
    addObserver,
  };
};
