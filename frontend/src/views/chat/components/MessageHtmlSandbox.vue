<script setup lang="ts">
/**
 * AI 聊天界面 - HTML/JavaScript 沙箱隔离挂件容器
 *
 * 用于安全隔离渲染角色卡生态中的酒馆插件 (Tavern Helper / MVU) 动态挂件、小游戏与状态栏。
 * - 采用 <iframe sandbox="allow-scripts allow-forms">，杜绝 allow-same-origin，主站 Token/Cookie 绝对安全
 * - 样式完全隔离，挂件自带的全局 CSS/图片不会污染主站黑金界面
 * - 注入双向自适应 ResizeObserver 脚本，动态伸缩高度，消灭内嵌滚动条
 * - 支持折叠/展开、查看源码与一键重载
 *
 * @packageDocumentation
 */

import { ChevronDown, Code2, RotateCcw, Sparkles } from "lucide-vue-next";
import { computed, onMounted, onUnmounted, ref } from "vue";

const props = withDefaults(
  defineProps<{
    html: string;
    title?: string;
    defaultExpanded?: boolean;
  }>(),
  {
    title: "交互式剧情挂件",
    defaultExpanded: true,
  },
);

const sandboxId = `sandbox-${Math.random().toString(36).slice(2, 9)}`;
const isExpanded = ref(props.defaultExpanded);
const isSourceVisible = ref(false);
const iframeHeight = ref(120);
const reloadKey = ref(0);
const iframeRef = ref<HTMLIFrameElement | null>(null);

/**
 * 提取并清理原始 HTML 代码（去除包裹的 ```html 标记）
 */
const rawHtml = computed(() => {
  if (!props.html) return "";
  let content = props.html.trim();
  if (content.startsWith("```html")) {
    content = content.replace(/^```html\s*/i, "");
    if (content.endsWith("```")) {
      content = content.replace(/\s*```$/, "");
    }
  } else if (content.startsWith("```")) {
    content = content.replace(/^```\s*/i, "");
    if (content.endsWith("```")) {
      content = content.replace(/\s*```$/, "");
    }
  }
  return content.trim();
});

/**
 * 注入高度汇报自适应通信代码与基础暗色背景默认样式的 srcdoc
 */
const injectedSrcdoc = computed(() => {
  if (!rawHtml.value) return "";

  const resizeScript = `
<script>
  (function() {
    function reportHeight() {
      try {
        var h = Math.max(
          document.body ? document.body.scrollHeight : 0,
          document.documentElement ? document.documentElement.scrollHeight : 0,
          document.body ? document.body.offsetHeight : 0
        );
        if (h > 0) {
          window.parent.postMessage({
            type: 'spikeai-sandbox-resize',
            sandboxId: '${sandboxId}',
            height: h
          }, '*');
        }
      } catch (e) {}
    }
    window.addEventListener('DOMContentLoaded', reportHeight);
    window.addEventListener('load', reportHeight);
    if (window.ResizeObserver && document.body) {
      new ResizeObserver(reportHeight).observe(document.body);
    }
    setTimeout(reportHeight, 150);
    setTimeout(reportHeight, 600);
    setTimeout(reportHeight, 1500);
  })();
<\/script>
`;

  const content = rawHtml.value;
  if (content.includes("</body>")) {
    return content.replace("</body>", `${resizeScript}</body>`);
  }
  return `${content}${resizeScript}`;
});

/**
 * 监听子 iframe 高度汇报消息
 */
function handleWindowMessage(event: MessageEvent): void {
  if (!event.data || typeof event.data !== "object") return;
  if (event.data.type === "spikeai-sandbox-resize" && event.data.sandboxId === sandboxId) {
    const receivedHeight = Number(event.data.height);
    if (receivedHeight && receivedHeight > 30) {
      // 限制最小 60px，最大 1200px
      iframeHeight.value = Math.min(Math.max(receivedHeight, 60), 1200);
    }
  }
}

function handleReload(): void {
  reloadKey.value++;
}

onMounted(() => {
  window.addEventListener("message", handleWindowMessage);
});

onUnmounted(() => {
  window.removeEventListener("message", handleWindowMessage);
});
</script>

<template>
  <div
    class="w-full my-2.5 rounded-xl bg-[#1C1917]/90 border border-[#F9C86D]/30 shadow-lg overflow-hidden flex flex-col transition-all"
  >
    <!-- 1. 顶部控制栏 (黑金磨砂玻璃态) -->
    <div
      class="px-3 py-2 flex items-center justify-between bg-[#292524]/80 border-b border-[#F9C86D]/20 select-none text-xs"
    >
      <div class="flex items-center gap-2 text-[#F9C86D] font-medium">
        <Sparkles class="w-3.5 h-3.5 text-[#F9C86D] animate-pulse" />
        <span class="tracking-wide">{{ title }}</span>
        <span class="px-1.5 py-0.2 rounded bg-[#F9C86D]/15 text-[10px] text-[#F9C86D] border border-[#F9C86D]/30 font-mono">
          SANDBOX
        </span>
      </div>

      <div class="flex items-center gap-1">
        <!-- 重新载入 -->
        <button
          type="button"
          @click="handleReload"
          class="p-1 rounded hover:bg-white/10 text-white/70 hover:text-[#F9C86D] transition-colors cursor-pointer"
          title="重新运行挂件脚本"
        >
          <RotateCcw class="w-3.5 h-3.5" />
        </button>

        <!-- 查看源码 -->
        <button
          type="button"
          @click="isSourceVisible = !isSourceVisible"
          :class="[
            'p-1 rounded transition-colors cursor-pointer',
            isSourceVisible ? 'text-[#F9C86D] bg-[#F9C86D]/20' : 'text-white/70 hover:text-white hover:bg-white/10'
          ]"
          title="查看挂件 HTML/JS 源码"
        >
          <Code2 class="w-3.5 h-3.5" />
        </button>

        <!-- 折叠 / 展开 -->
        <button
          type="button"
          @click="isExpanded = !isExpanded"
          class="p-1 rounded hover:bg-white/10 text-white/70 hover:text-[#F9C86D] transition-colors cursor-pointer flex items-center gap-0.5"
          :title="isExpanded ? '折叠挂件' : '展开挂件'"
        >
          <ChevronDown
            :class="[
              'w-3.5 h-3.5 transition-transform duration-200',
              isExpanded ? '' : '-rotate-90'
            ]"
          />
        </button>
      </div>
    </div>

    <!-- 2. 源码预览面板 -->
    <div
      v-if="isSourceVisible"
      class="p-2.5 bg-[#141211] border-b border-[#44403C] max-h-48 overflow-y-auto text-[11px] font-mono text-gray-300 leading-relaxed whitespace-pre-wrap select-all"
    >
      {{ rawHtml }}
    </div>

    <!-- 3. Iframe 安全沙箱视口 -->
    <div v-show="isExpanded" class="w-full bg-[#181615] overflow-x-hidden relative flex flex-col">
      <iframe
        :key="reloadKey"
        ref="iframeRef"
        :srcdoc="injectedSrcdoc"
        sandbox="allow-scripts allow-forms"
        class="w-full border-none block bg-transparent"
        :style="{ height: `${iframeHeight}px` }"
        scrolling="no"
        loading="lazy"
      />
    </div>
  </div>
</template>
