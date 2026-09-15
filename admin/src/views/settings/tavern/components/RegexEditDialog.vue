<template>
  <el-dialog
    :model-value="modelValue"
    width="680px"
    append-to-body
    destroy-on-close
    :close-on-click-modal="false"
    class="st-regex-edit-dialog"
    @update:model-value="(val: boolean) => emit('update:modelValue', val)"
  >
    <!-- 头部自定义插槽: 标题 + 问号Tooltip + 测试模式按钮 -->
    <template #header>
      <div class="flex items-center justify-between w-full pr-8">
        <div class="flex items-center gap-1.5">
          <span class="font-bold text-base text-[var(--el-text-color-primary)]">正则表达式编辑器</span>
          <el-tooltip
            content="“正则”是一个使用“正则表达式”来查找/替换字符串的工具。支持 ECMAScript 规范及 JS 风格 /pattern/flags。"
            placement="top"
          >
            <el-icon class="text-amber-500 cursor-pointer text-sm"><QuestionFilled /></el-icon>
          </el-tooltip>
        </div>

        <el-button
          size="small"
          :type="isTestMode ? 'warning' : 'default'"
          plain
          @click="isTestMode = !isTestMode"
          class="!px-3"
        >
          <el-icon class="mr-1"><MagicStick /></el-icon>
          {{ isTestMode ? '退出测试' : '测试模式' }}
        </el-button>
      </div>
    </template>

    <div v-if="form" class="flex flex-col gap-4 text-xs select-none">
      <!-- 简介说明行 -->
      <span class="text-xs text-[var(--el-text-color-secondary)] leading-relaxed">
        “正则”是一个使用“正则表达式”来查找/替换字符串的工具。如果您想了解更多信息，请点击标题旁边的“？”。
      </span>

      <!-- 动态提示横幅 (1:1 原生酒馆风格蓝色渐变背景与信息标识) -->
      <div class="flex items-center justify-between p-2.5 rounded-lg border border-sky-500/30 bg-sky-500/10 text-sky-600 dark:text-sky-400">
        <div class="flex items-center gap-2 font-medium text-xs">
          <el-icon><InfoFilled /></el-icon>
          <span>{{ regexMatchNotice }}</span>
        </div>
        <span class="text-[11px] font-mono opacity-80">{{ form.findRegex ? '已解析表达式' : '等待输入' }}</span>
      </div>

      <!-- 1. 脚本名称 -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">脚本名称</label>
        <el-input
          v-model="form.scriptName"
          placeholder="例如：【云瑾】包裹最新指示"
          clearable
        />
      </div>

      <!-- 2. 查找正则表达式 -->
      <div class="flex flex-col gap-1.5">
        <div class="flex items-center justify-between">
          <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">查找正则表达式</label>
          <span class="text-[11px] text-[var(--el-text-color-secondary)]">支持纯正则如 ^([\s\S]*)$ 或 /pattern/flags</span>
        </div>
        <el-input
          v-model="form.findRegex"
          placeholder="输入正则表达式..."
          clearable
          font-mono
        />
      </div>

      <!-- 3. 替换为 -->
      <div class="flex flex-col gap-1.5">
        <div class="flex items-center justify-between">
          <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">替换为</label>
          <span class="text-[11px] text-[var(--el-text-color-secondary)]">支持 $1, $2 等反向分组引用</span>
        </div>
        <el-input
          v-model="form.replaceString"
          type="textarea"
          :rows="3"
          placeholder="输入替换内容，留空表示删除匹配内容..."
          font-mono
        />
      </div>

      <!-- 4. 修剪掉 (trimStrings) -->
      <div class="flex flex-col gap-1.5">
        <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">修剪掉</label>
        <el-input
          v-model="trimStringsText"
          type="textarea"
          :rows="2"
          placeholder="在替换之前全局修剪正则表达式匹配中任何不需要的部分。用回车键分隔每个元素。"
        />
      </div>

      <!-- 5. 作用范围与选项双列网格 -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 p-3 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)]/40">
        <!-- 左列: 作用范围 -->
        <div class="flex flex-col gap-2">
          <span class="text-xs font-bold text-[var(--el-text-color-primary)]">作用范围</span>
          <div class="flex flex-col gap-1.5 pt-1">
            <el-checkbox
              v-for="opt in placementOptions"
              :key="opt.value"
              :model-value="form.placement.includes(opt.value)"
              @change="(val: boolean) => togglePlacement(opt.value, val)"
              class="!m-0 !h-6"
            >
              <span class="text-xs text-[var(--el-text-color-regular)]">{{ opt.label }}</span>
            </el-checkbox>
          </div>
        </div>

        <!-- 右列: 其他选项 -->
        <div class="flex flex-col gap-2">
          <span class="text-xs font-bold text-[var(--el-text-color-primary)]">其他选项</span>
          <div class="flex flex-col gap-2 pt-1">
            <el-checkbox v-model="form.disabled" class="!m-0 !h-6">
              <span class="text-xs text-[var(--el-text-color-regular)]">已禁用 (不执行)</span>
            </el-checkbox>

            <el-checkbox v-model="form.runOnEdit" class="!m-0 !h-6">
              <span class="text-xs text-[var(--el-text-color-regular)]">在编辑时运行</span>
            </el-checkbox>

            <!-- 查找时的宏 -->
            <div class="flex flex-col gap-1 pt-1">
              <div class="flex items-center gap-1">
                <span class="text-xs text-[var(--el-text-color-primary)] font-medium">正则表达式查找时的宏</span>
                <el-tooltip content="替换查找表达式中包含的 {{macro}} 动态宏变量" placement="top">
                  <el-icon class="text-gray-400 text-xs"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <el-select v-model="form.substituteRegex" size="small" class="w-full">
                <el-option label="不替换" :value="0" />
                <el-option label="预处理宏" :value="1" />
              </el-select>
            </div>

            <!-- 表层替换 -->
            <div class="flex flex-col gap-1 pt-1">
              <div class="flex items-center gap-1">
                <span class="text-xs text-[var(--el-text-color-primary)] font-medium">表层替换</span>
                <el-tooltip content="控制正则替换是仅用于界面 Markdown 渲染，还是直接注入后端提示词管线" placement="top">
                  <el-icon class="text-gray-400 text-xs"><QuestionFilled /></el-icon>
                </el-tooltip>
              </div>
              <div class="flex items-center gap-3">
                <el-checkbox v-model="form.markdownOnly" class="!m-0">
                  <span class="text-xs text-[var(--el-text-color-regular)]">仅影响显示</span>
                </el-checkbox>
                <el-checkbox v-model="form.promptOnly" class="!m-0">
                  <span class="text-xs text-[var(--el-text-color-regular)]">仅影响后端提示词</span>
                </el-checkbox>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 6. 深度区间配置 -->
      <div class="grid grid-cols-2 gap-4">
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-1">
            <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">最小深度</label>
            <el-tooltip content="不填或留空表示无限深度生效" placement="top">
              <el-icon class="text-gray-400 text-xs"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-input-number
            v-model="form.minDepth"
            :min="0"
            :max="999"
            class="!w-full"
            placeholder="无限"
          />
        </div>

        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-1">
            <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">最大深度</label>
            <el-tooltip content="消息深度上限。例如设为 1 表示仅对最新一轮消息生效" placement="top">
              <el-icon class="text-gray-400 text-xs"><QuestionFilled /></el-icon>
            </el-tooltip>
          </div>
          <el-input-number
            v-model="form.maxDepth"
            :min="0"
            :max="999"
            class="!w-full"
            placeholder="无限"
          />
        </div>
      </div>

      <!-- 7. 测试模式实时演练沙盒 (可折叠切换) -->
      <div
        v-if="isTestMode"
        class="flex flex-col gap-2 p-3 rounded-xl border border-amber-500/40 bg-amber-500/5 animate-fade-in"
      >
        <div class="flex items-center justify-between pb-1 border-b border-amber-500/20">
          <span class="font-bold text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
            <el-icon><MagicStick /></el-icon>
            实时测试沙盒
          </span>
          <span class="text-[11px] text-amber-700/70 dark:text-amber-400/70">
            在下方输入测试文本，实时预览该正则替换效果
          </span>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <div class="flex flex-col gap-1">
            <span class="text-[11px] font-semibold text-[var(--el-text-color-regular)]">测试原始文本：</span>
            <el-input
              v-model="testSampleText"
              type="textarea"
              :rows="4"
              placeholder="在此输入待匹配文本..."
              font-mono
            />
          </div>

          <div class="flex flex-col gap-1">
            <span class="text-[11px] font-semibold text-[var(--el-text-color-regular)]">正则替换结果：</span>
            <div class="w-full h-21 p-2 rounded border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] overflow-y-auto font-mono text-xs text-[var(--el-text-color-primary)] whitespace-pre-wrap select-text">
              {{ testResultText }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部按钮插槽: 左侧还原默认，右侧取消与确定保存 (严格符合全局弹窗规范) -->
    <template #footer>
      <div class="flex items-center justify-between w-full">
        <!-- 左侧: 还原出厂配置 -->
        <div class="flex items-center gap-2">
          <el-tooltip
            v-if="matchedDefaultScript"
            content="将当前正则恢复为官方出厂初始表达式与配置"
            placement="top"
          >
            <el-button type="warning" plain @click="resetToDefault" class="!px-4">
              <el-icon class="mr-1"><RefreshLeft /></el-icon>
              还原条目默认
            </el-button>
          </el-tooltip>
          <div v-else class="text-[11px] text-gray-400">
            (自定义新增正则)
          </div>
        </div>

        <!-- 右侧: 取消与保存 -->
        <div class="flex items-center gap-3">
          <el-button @click="emit('update:modelValue', false)" class="!px-4">
            <el-icon class="mr-1"><Close /></el-icon>
            取消
          </el-button>

          <el-button type="primary" @click="handleSave" class="!px-5">
            <el-icon class="mr-1"><Check /></el-icon>
            保存正则
          </el-button>
        </div>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
/**
 * SillyTavern 正则表达式编辑器模态框 (1:1 像素级复刻酒馆原生)
 *
 * 遵循规范:
 * 1. 采用 Vue 3.5 Composition API + TypeScript 完整类型标注；
 * 2. 严格对齐全局弹窗 Header/Body/Footer 浅色分割线规范与 Footer 左右排布；
 * 3. 完美适配 JS 风格 /pattern/flags 与 $1, $2 分组反向引用；
 * 4. 内置即时测试沙盒。
 */

import type { TavernRegexScript } from '@/api/tavern';
import {
  Check,
  Close,
  InfoFilled,
  MagicStick,
  QuestionFilled,
  RefreshLeft,
} from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';
import { computed, ref, watch } from 'vue';

interface Props {
  modelValue: boolean;
  script: TavernRegexScript | null;
  factoryScripts?: TavernRegexScript[];
}

const props = withDefaults(defineProps<Props>(), {
  factoryScripts: () => [],
});

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void;
  (e: 'save', value: TavernRegexScript): void;
}>();

// 本地表单状态
const form = ref<TavernRegexScript>({
  id: '',
  scriptName: '',
  findRegex: '',
  replaceString: '',
  trimStrings: [],
  placement: [2],
  disabled: false,
  markdownOnly: false,
  promptOnly: true,
  runOnEdit: true,
  substituteRegex: 0,
  minDepth: null,
  maxDepth: null,
});

// 修剪词回车分割文本
const trimStringsText = ref('');
// 是否开启测试模式
const isTestMode = ref(false);
const testSampleText = ref('这是一段包含 12345 和 <-begin-response-> 以及——破折号的示例。');

// 作用范围选项定义 (1=用户输入, 2=AI输出, 3=快捷命令, 4=世界书, 5=推理)
const placementOptions = [
  { value: 1, label: '用户输入' },
  { value: 2, label: 'AI 输出' },
  { value: 3, label: '快捷命令' },
  { value: 4, label: '世界书' },
  { value: 5, label: '推理' },
];

// 监听打开时克隆数据
watch(
  () => props.script,
  (newVal) => {
    if (newVal) {
      form.value = JSON.parse(JSON.stringify(newVal));
      if (!Array.isArray(form.value.placement)) {
        form.value.placement = [2];
      }
      trimStringsText.value = (form.value.trimStrings || []).join('\n');
    } else {
      // 新建默认值
      form.value = {
        id: `regex-${Date.now()}`,
        scriptName: '',
        findRegex: '',
        replaceString: '',
        trimStrings: [],
        placement: [2],
        disabled: false,
        markdownOnly: false,
        promptOnly: true,
        runOnEdit: true,
        substituteRegex: 0,
        minDepth: null,
        maxDepth: null,
      };
      trimStringsText.value = '';
    }
  },
  { immediate: true },
);

// 匹配的出厂原版正则 (用于还原默认)
const matchedDefaultScript = computed(() => {
  if (!form.value?.id) return null;
  return props.factoryScripts.find(
    (s) => s.id === form.value.id || s.scriptName === form.value.scriptName,
  );
});

// 动态提示文案 (解析 /pattern/flags)
const regexMatchNotice = computed(() => {
  const reg = form.value?.findRegex || '';
  if (!reg) return '输入正则表达式以查看匹配策略';
  const isGlobal = reg.includes('/g') || !reg.startsWith('/');
  const isCaseInsensitive = reg.includes('/i');
  return `${isGlobal ? '全局替换匹配项' : '仅应用于第一个匹配项'}. ${isCaseInsensitive ? '不区分大小写' : '区分大小写'}`;
});

// 切换作用范围复选框
function togglePlacement(val: number, checked: boolean): void {
  const set = new Set(form.value.placement);
  if (checked) {
    set.add(val);
  } else {
    set.delete(val);
  }
  form.value.placement = Array.from(set);
}

// 还原为出厂默认值
function resetToDefault(): void {
  if (!matchedDefaultScript.value) return;
  const def = matchedDefaultScript.value;
  form.value.findRegex = def.findRegex;
  form.value.replaceString = def.replaceString || '';
  form.value.placement = [...def.placement];
  form.value.disabled = def.disabled ?? false;
  form.value.minDepth = def.minDepth ?? null;
  form.value.maxDepth = def.maxDepth ?? null;
  form.value.promptOnly = def.promptOnly ?? true;
  form.value.markdownOnly = def.markdownOnly ?? false;
  form.value.runOnEdit = def.runOnEdit ?? true;
  form.value.trimStrings = [...(def.trimStrings || [])];
  trimStringsText.value = (def.trimStrings || []).join('\n');
  ElMessage.success(`已恢复「${def.scriptName}」为官方出厂配置`);
}

// 实时测试沙盒运算输出
const testResultText = computed(() => {
  if (!form.value.findRegex) return testSampleText.value;
  try {
    let pattern = form.value.findRegex;
    let flags = 'g';
    if (pattern.startsWith('/')) {
      const match = pattern.match(/^\/(.*)\/([a-z]*)$/s);
      if (match) {
        pattern = match[1];
        flags = match[2] || '';
      }
    }
    const regExp = new RegExp(pattern, flags);
    let output = testSampleText.value.replace(regExp, form.value.replaceString || '');
    // 应用 trimStrings
    const trimArr = trimStringsText.value
      .split('\n')
      .map((t) => t.trim())
      .filter(Boolean);
    for (const t of trimArr) {
      output = output.replaceAll(t, '');
    }
    return output;
  } catch (err: any) {
    return `[正则解析错误: ${err.message}]`;
  }
});

// 保存提交
function handleSave(): void {
  if (!form.value.scriptName.trim()) {
    ElMessage.warning('请输入正则脚本名称');
    return;
  }
  if (!form.value.findRegex.trim()) {
    ElMessage.warning('请输入查找正则表达式');
    return;
  }
  if (form.value.placement.length === 0) {
    ElMessage.warning('请至少选择一个作用范围');
    return;
  }

  // 保存修剪词列表
  form.value.trimStrings = trimStringsText.value
    .split('\n')
    .map((t) => t.trim())
    .filter(Boolean);

  emit('save', JSON.parse(JSON.stringify(form.value)));
  emit('update:modelValue', false);
  ElMessage.success(`正则脚本「${form.value.scriptName}」已保存`);
}
</script>

<style scoped>
.st-regex-edit-dialog :deep(.el-input__inner),
.st-regex-edit-dialog :deep(.el-textarea__inner) {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
}
</style>
