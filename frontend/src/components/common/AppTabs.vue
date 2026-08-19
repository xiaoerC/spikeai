<script setup lang="ts">
/**
 * 黑金暗黑玻璃拟物风格通用标签页 (Tabs) 组件。
 *
 * 基于 Reka UI (原 Radix Vue) 封装，具备原生键盘左右光标切换、
 * 无障碍焦点与平滑状态过渡。
 *
 * Usage:
 *   <AppTabs
 *     v-model="activeTab"
 *     :items="[
 *       { value: 'all', label: '全部推荐' },
 *       { value: 'story', label: '剧情深度卡' },
 *       { value: 'gentleman', label: '绅士/秘境' }
 *     ]"
 *     variant="pills"
 *   />
 */

import { TabsList, TabsRoot, TabsTrigger } from "reka-ui";

export interface TabItem {
  value: string;
  label: string;
  badge?: string | number;
  disabled?: boolean;
}

export type TabsVariant = "pills" | "line";

interface Props {
  /** 当前选中的 Tab 值 (支持 v-model) */
  modelValue: string;
  /** 选项列表数据 */
  items: TabItem[];
  /** 视觉风格 (pills 胶囊态 / line 底部下划线态) */
  variant?: TabsVariant;
  /** 自定义容器类名 */
  customClass?: string;
}

withDefaults(defineProps<Props>(), {
  variant: "pills",
  customClass: "",
});

const emit = defineEmits<(e: "update:modelValue", value: string) => void>();
</script>

<template>
  <TabsRoot
    :model-value="modelValue"
    @update:model-value="(val: string) => emit('update:modelValue', val)"
    class="w-full flex flex-col"
  >
    <TabsList
      :class="[
        'flex items-center gap-2 overflow-x-auto no-scrollbar py-1 shrink-0',
        variant === 'line' ? 'border-b border-obsidian-border/60' : '',
        customClass
      ]"
    >
      <TabsTrigger
        v-for="item in items"
        :key="item.value"
        :value="item.value"
        :disabled="item.disabled"
        :class="[
          'cursor-pointer transition-all duration-150 select-none flex items-center gap-1.5 whitespace-nowrap',
          variant === 'pills'
            ? [
                'px-3.5 py-1.5 rounded-xl text-xs font-medium',
                modelValue === item.value
                  ? 'bg-naro-gold text-[#0C0A09] font-bold shadow-gold'
                  : 'bg-obsidian-surface text-naro-muted hover:text-gray-200 border border-obsidian-border'
              ]
            : [
                'px-3 py-2 text-xs font-medium relative -mb-px',
                modelValue === item.value
                  ? 'text-naro-gold font-bold border-b-2 border-naro-gold'
                  : 'text-naro-muted hover:text-gray-200'
              ]
        ]"
      >
        <span>{{ item.label }}</span>
        <span
          v-if="item.badge !== undefined"
          :class="[
            'text-[10px] px-1.5 py-0.2 rounded-full font-bold',
            modelValue === item.value ? 'bg-black/20 text-black' : 'bg-obsidian-card text-naro-muted'
          ]"
        >
          {{ item.badge }}
        </span>
      </TabsTrigger>
    </TabsList>
  </TabsRoot>
</template>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>
