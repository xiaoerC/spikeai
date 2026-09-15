import { ElLoading } from 'element-plus';
import type { LoadingOptions } from 'element-plus/es/components/loading/src/types';

let loading: ReturnType<typeof ElLoading.service>;

export const openLoading = (options: LoadingOptions = { text: '加载中' }) => {
  loading = ElLoading.service({
    lock: true,
    text: options.text,
  });
};

export const closeLoading = () => {
  loading?.close();
};
