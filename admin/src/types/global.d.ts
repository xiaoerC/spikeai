declare global {
  interface Document {
    webkitFullscreenEnabled?: boolean;
    mozFullScreenEnabled?: boolean;
    msFullscreenEnabled?: boolean;
    webkitFullscreenElement?: Element | null;
    mozFullScreenElement?: Element | null;
    msFullscreenElement?: Element | null;
    webkitRequestFullScreen?: () => Promise<void>;
    mozRequestFullScreen?: () => Promise<void>;
    msRequestFullscreen?: () => Promise<void>;
    webkitExitFullscreen?: () => Promise<void>;
    mozCancelFullScreen?: () => Promise<void>;
    msExitFullscreen?: () => Promise<void>;
    onwebkitfullscreenerror?: (this: Document, ev: Event) => any;
    onmozfullscreenerror?: (this: Document, ev: Event) => any;
    onmsfullscreenerror?: (this: Document, ev: Event) => any;
    onwebkitfullscreenchange?: (this: Document, ev: Event) => any;
    onmozfullscreenchange?: (this: Document, ev: Event) => any;
    onmsfullscreenchange?: (this: Document, ev: Event) => any;
  }
}

export {};

declare module 'vue' {
  interface ComponentCustomProperties {
    $parseTime: (val: string) => string; // 声明全局方法类型
  }
}
