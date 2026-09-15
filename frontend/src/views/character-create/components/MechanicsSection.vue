<script setup lang="ts">
/**
 * 分节 4: 【机制】组件 (引擎执行的脚本与变量)
 *
 * 涵盖酒馆正则替换脚本流水线与 RPG 初始变量定义。
 *
 * @packageDocumentation
 */

import { useToast } from "@/composables/useToast";
import { Code, Download, Plus, Settings, Trash2, Upload, Variable } from "lucide-vue-next";
import { ref } from "vue";
import type { RegexScriptItem } from "../types";

const props = defineProps<{
  /** 正则脚本列表 */
  regexScripts: RegexScriptItem[];
  /** 初始变量字典 */
  initialVariables: Record<string, any>;
}>();

const emit = defineEmits<{
  (e: "update:regexScripts", val: RegexScriptItem[]): void;
  (e: "update:initialVariables", val: Record<string, any>): void;
}>();

const toast = useToast();
const regexFileInputRef = ref<HTMLInputElement | null>(null);

// 变量临时编辑项列表 (方便与 Record<string, any> 双向映射)
interface VarEditItem {
  id: string;
  key: string;
  type: "string" | "number" | "boolean";
  value: string;
}

const varList = ref<VarEditItem[]>(
  Object.entries(props.initialVariables || {}).map(([k, v], idx) => ({
    id: `var-${idx}-${k}`,
    key: k,
    type: typeof v === "number" ? "number" : typeof v === "boolean" ? "boolean" : "string",
    value: String(v),
  })),
);

function syncVariables(): void {
  const result: Record<string, any> = {};
  for (const item of varList.value) {
    const k = item.key.trim();
    if (!k) continue;
    if (item.type === "number") {
      result[k] = Number(item.value) || 0;
    } else if (item.type === "boolean") {
      result[k] = item.value === "true";
    } else {
      result[k] = item.value;
    }
  }
  emit("update:initialVariables", result);
}

function handleAddVariable(): void {
  varList.value.push({
    id: `var-${Date.now()}`,
    key: `var_${varList.value.length + 1}`,
    type: "number",
    value: "0",
  });
  syncVariables();
}

function handleRemoveVariable(idx: number): void {
  varList.value.splice(idx, 1);
  syncVariables();
}

function handleAddRegexScript(): void {
  const nextList = [...props.regexScripts];
  nextList.push({
    id: `regex-${Date.now()}`,
    scriptName: `规则 ${nextList.length + 1}`,
    findRegex: "",
    replaceString: "",
    placement: [2], // 默认 AI 输出阶段
    disabled: false,
  });
  emit("update:regexScripts", nextList);
}

function handleRemoveRegexScript(idx: number): void {
  const nextList = props.regexScripts.filter((_, i) => i !== idx);
  emit("update:regexScripts", nextList);
}

function handleUpdateScript(idx: number, patch: Partial<RegexScriptItem>): void {
  const nextList = [...props.regexScripts];
  if (nextList[idx]) {
    nextList[idx] = { ...nextList[idx], ...patch };
    emit("update:regexScripts", nextList);
  }
}

function triggerImportRegex(): void {
  regexFileInputRef.value?.click();
}

function handleRegexFileChange(event: Event): void {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const text = e.target?.result as string;
      const parsed = JSON.parse(text);
      const scripts = Array.isArray(parsed) ? parsed : parsed.scripts || [];
      const imported: RegexScriptItem[] = scripts.map((s: any, idx: number) => ({
        id: `regex-${Date.now()}-${idx}`,
        scriptName: s.scriptName || `导入规则 ${idx + 1}`,
        findRegex: s.findRegex || "",
        replaceString: s.replaceString || "",
        placement: Array.isArray(s.placement) ? s.placement : [2],
        disabled: s.disabled ?? false,
      }));
      emit("update:regexScripts", [...props.regexScripts, ...imported]);
      toast.success(`成功导入 ${imported.length} 条正则脚本！`);
    } catch (err) {
      console.error("解析正则脚本失败:", err);
      toast.error("导入正则脚本失败，请检查 JSON 格式");
    } finally {
      target.value = "";
    }
  };
  reader.readAsText(file);
}

function handleExportRegex(): void {
  if (props.regexScripts.length === 0) {
    toast.info("当前暂无正则脚本可导出");
    return;
  }
  const blob = new Blob([JSON.stringify(props.regexScripts, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `regex_scripts_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  toast.success("正则脚本已成功导出为 JSON！");
}
</script>

<template>
  <section id="section-mechanics" class="w-full px-3 pb-4 flex flex-col gap-4">
    <!-- 隐藏的正则导入 input -->
    <input
      ref="regexFileInputRef"
      type="file"
      accept=".json"
      class="hidden"
      @change="handleRegexFileChange"
    />

    <!-- 分节大标题: 机制 (引擎执行的脚本与变量) -->
    <div class="flex items-center justify-between pt-1">
      <div class="flex items-center gap-2.5">
        <div class="w-1 h-5 rounded-full bg-[#EF4444] shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
        <h2 class="text-base font-bold text-gray-100 tracking-wide select-none">
          机制
        </h2>
        <span class="text-xs text-[#78716C] font-normal">
          引擎执行的脚本与变量
        </span>
      </div>
    </div>

    <!-- 1. 正则脚本流水线卡片 -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Code class="w-4 h-4 text-[#F9C86D]" />
          <h3 class="text-xs font-semibold text-gray-200">
            正则脚本流水线
          </h3>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="triggerImportRegex"
            class="flex items-center gap-1 px-2 py-0.5 rounded bg-stone-800 hover:bg-stone-700 text-[10px] text-stone-300 border border-stone-700 transition-colors cursor-pointer select-none"
          >
            <Upload class="w-3 h-3" />
            <span>导入正则</span>
          </button>
          <button
            type="button"
            @click="handleExportRegex"
            class="flex items-center gap-1 px-2 py-0.5 rounded bg-stone-800 hover:bg-stone-700 text-[10px] text-stone-300 border border-stone-700 transition-colors cursor-pointer select-none"
          >
            <Download class="w-3 h-3" />
            <span>导出正则</span>
          </button>
        </div>
      </div>

      <div class="flex items-center justify-between pt-1">
        <span class="text-[11px] text-[#78716C]">
          在用户输入或模型生成阶段动态替换或格式化特定语法。
        </span>
        <button
          type="button"
          @click="handleAddRegexScript"
          class="flex items-center gap-1 text-xs text-[#F9C86D] hover:underline cursor-pointer select-none font-medium"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>+ 添加脚本</span>
        </button>
      </div>

      <!-- 脚本卡片列表 -->
      <div v-if="regexScripts.length > 0" class="flex flex-col gap-2.5 pt-1">
        <div
          v-for="(script, idx) in regexScripts"
          :key="script.id"
          class="p-3 rounded-lg border border-[#44403C]/80 bg-[#1F1C18]/90 flex flex-col gap-2 shadow"
        >
          <div class="flex items-center justify-between">
            <input
              :value="script.scriptName"
              @input="handleUpdateScript(idx, { scriptName: ($event.target as HTMLInputElement).value })"
              type="text"
              class="bg-transparent border-b border-transparent hover:border-stone-600 focus:border-[#F9C86D] text-xs font-semibold text-gray-200 outline-none px-1"
              placeholder="规则名称"
            />
            <div class="flex items-center gap-2">
              <label class="flex items-center gap-1 text-[11px] text-[#A8A29E] cursor-pointer">
                <input
                  type="checkbox"
                  :checked="!script.disabled"
                  @change="handleUpdateScript(idx, { disabled: script.disabled ? false : true })"
                  class="rounded accent-[#F9C86D]"
                />
                <span>启用</span>
              </label>
              <button
                type="button"
                @click="handleRemoveRegexScript(idx)"
                class="text-red-400 hover:text-red-300 p-0.5 cursor-pointer"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <!-- 匹配模式与替换内容 -->
          <div class="grid grid-cols-1 gap-2 pt-1">
            <div class="flex flex-col gap-1">
              <label class="text-[10px] text-stone-400">匹配模式 (Regex Pattern & Flags)</label>
              <input
                :value="script.findRegex"
                @input="handleUpdateScript(idx, { findRegex: ($event.target as HTMLInputElement).value })"
                type="text"
                placeholder="/<think>[\s\S]*?<\/think>/g"
                class="w-full px-2.5 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs font-mono text-amber-200/90 placeholder-[#78716C] focus:border-[#F9C86D]"
              />
            </div>
            <div class="flex flex-col gap-1">
              <label class="text-[10px] text-stone-400">替换内容 (支持 $1 等捕获组)</label>
              <input
                :value="script.replaceString"
                @input="handleUpdateScript(idx, { replaceString: ($event.target as HTMLInputElement).value })"
                type="text"
                placeholder="留空则直接剔除，或输入替换文本"
                class="w-full px-2.5 py-1.5 rounded bg-black/40 border border-[#44403C] text-xs font-mono text-gray-200 placeholder-[#78716C] focus:border-[#F9C86D]"
              />
            </div>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-2 text-xs text-[#78716C]">
        暂无正则规则，可点击“+ 添加脚本”或“导入正则”。
      </div>
    </div>

    <!-- 2. RPG 初始变量定义卡片 -->
    <div class="w-full p-4.5 rounded-xl border border-[rgba(83,71,65,0.25)] bg-[rgba(26,23,20,0.70)] backdrop-blur-md flex flex-col gap-3 shadow-xl">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Variable class="w-4 h-4 text-[#F9C86D]" />
          <h3 class="text-xs font-semibold text-gray-200">
            RPG 初始变量声明 (MVU 状态机)
          </h3>
        </div>

        <button
          type="button"
          @click="handleAddVariable"
          class="flex items-center gap-1 text-xs text-[#F9C86D] hover:underline cursor-pointer select-none font-medium"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>+ 添加变量定义</span>
        </button>
      </div>

      <p class="text-[11px] text-[#78716C]">
        为角色卡设定开局初始变量矩阵（如好感度、生命值、货币或剧情状态标志）。
      </p>

      <div v-if="varList.length > 0" class="flex flex-col gap-2 pt-1">
        <div
          v-for="(item, idx) in varList"
          :key="item.id"
          class="flex items-center gap-2 p-2 rounded-lg bg-black/40 border border-stone-800"
        >
          <!-- 变量名 -->
          <input
            v-model="item.key"
            @change="syncVariables"
            type="text"
            placeholder="变量名 (如 hp)"
            class="flex-1 px-2 py-1 rounded bg-stone-900 border border-stone-700 text-xs text-gray-200 font-mono focus:border-[#F9C86D]"
          />

          <!-- 变量类型 -->
          <select
            v-model="item.type"
            @change="syncVariables"
            class="w-20 px-1 py-1 rounded bg-stone-900 border border-stone-700 text-xs text-stone-300 focus:border-[#F9C86D]"
          >
            <option value="number">数字</option>
            <option value="string">文本</option>
            <option value="boolean">布尔</option>
          </select>

          <!-- 初始值 -->
          <input
            v-model="item.value"
            @change="syncVariables"
            type="text"
            placeholder="初始值"
            class="w-24 px-2 py-1 rounded bg-stone-900 border border-stone-700 text-xs text-gray-200 font-mono focus:border-[#F9C86D]"
          />

          <!-- 删除 -->
          <button
            type="button"
            @click="handleRemoveVariable(idx)"
            class="text-red-400 hover:text-red-300 p-1 cursor-pointer"
          >
            <Trash2 class="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div v-else class="text-center py-2 text-xs text-[#78716C]">
        暂无初始变量定义，点击“+ 添加变量定义”可开启 RPG 剧情数值演算。
      </div>
    </div>
  </section>
</template>
