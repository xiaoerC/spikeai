<script setup lang="ts">
/**
 * AI 聊天界面 - 主控面板抽屉 (1:1 Figma 原型高保真)
 *
 * 严格按照 Figma FrameId 80:2307 与真实原型截图构建：
 * 包含用户名设置、User人设、指令区、38 个角色变量网格矩阵、记忆区块、文本替换以及底部保存栏。
 *
 * @packageDocumentation
 */

import type { ControlPanelDTO } from "@/services/chat";
import { useUserStore } from "@/stores/user";
import { CheckCircle2, Plus, Trash2, Variable, X } from "lucide-vue-next";
import { ref, watch } from "vue";

const props = defineProps<{
  open: boolean;
  controlPanel?: ControlPanelDTO;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "save", payload: ControlPanelDTO): void;
}>();

const userStore = useUserStore();

// 1. 用户名设置 (默认读取当前登录用户真实昵称，支持针对本会话自定义修改)
const userName = ref(userStore.profile?.username || "{{user}}");

// 2. User 人设
const userPersona = ref("");

// 3. 指令区
const customPrompt = ref("");

// 4. 角色变量列表 (动态 MVU 状态机变量)
interface VarEditItem {
  id: string;
  key: string;
  type: "number" | "string" | "boolean";
  value: string;
}

const varList = ref<VarEditItem[]>([]);

function handleAddVariable(): void {
  varList.value.push({
    id: `var-${Date.now()}`,
    key: `var_${varList.value.length + 1}`,
    type: "number",
    value: "0",
  });
}

function handleRemoveVariable(idx: number): void {
  varList.value.splice(idx, 1);
}

// 5. 记忆区块列表
interface MemoryBlock {
  id: string;
  title: string;
  content: string;
  enabled: boolean;
}
const memoryBlocks = ref<MemoryBlock[]>([]);

// 6. 文本替换规则
interface ReplacementRule {
  id: string;
  fromText: string;
  toText: string;
}
const replacementRules = ref<ReplacementRule[]>([]);
const newReplaceFrom = ref("");
const newReplaceTo = ref("");

// 监听外部传入的真实 ControlPanelDTO 数据
watch(
  () => props.controlPanel,
  (newVal) => {
    if (!newVal) return;
    const incoming = (newVal.user_name || "").trim();
    userName.value = incoming && incoming !== "{{user}}"
      ? incoming
      : (userStore.profile?.username || "{{user}}");
    userPersona.value = newVal.user_persona || "";
    customPrompt.value = newVal.custom_prompt || "";

    // 赋值动态角色变量
    if (newVal.variables && typeof newVal.variables === "object") {
      varList.value = Object.entries(newVal.variables).map(([k, v], idx) => ({
        id: `var-${idx}-${k}`,
        key: k,
        type: typeof v === "number" ? "number" : typeof v === "boolean" ? "boolean" : "string",
        value: String(v ?? ""),
      }));
    } else {
      varList.value = [];
    }

    // 记忆区块
    if (Array.isArray(newVal.memory_blocks)) {
      memoryBlocks.value = newVal.memory_blocks.map((m: any, idx: number) => ({
        id: m.id || `mem_${idx}_${Date.now()}`,
        title: m.title || `记忆区块 ${idx + 1}`,
        content: m.content || "",
        enabled: m.enabled ?? true,
      }));
    }

    // 文本替换
    if (Array.isArray(newVal.text_replacements)) {
      replacementRules.value = newVal.text_replacements.map((r: any, idx: number) => ({
        id: r.id || `rep_${idx}_${Date.now()}`,
        fromText: r.fromText || r.from || "",
        toText: r.toText || r.to || "",
      }));
    }
  },
  { immediate: true, deep: true },
);

// 保存成功通知弹窗
const showSuccessNotification = ref(false);

function handleClose(): void {
  emit("update:open", false);
}

function handleResetUserName(): void {
  userName.value = userStore.profile?.username || "{{user}}";
}

function constructPayload(): ControlPanelDTO {
  const vars: Record<string, any> = {};
  for (const item of varList.value) {
    const k = item.key.trim();
    if (!k) continue;
    if (item.type === "number") {
      vars[k] = Number(item.value) || 0;
    } else if (item.type === "boolean") {
      vars[k] = item.value === "true";
    } else {
      vars[k] = item.value;
    }
  }
  return {
    user_name: userName.value,
    user_persona: userPersona.value,
    custom_prompt: customPrompt.value,
    variables: vars,
    memory_blocks: memoryBlocks.value.map((b) => ({
      id: b.id,
      title: b.title,
      content: b.content,
      enabled: b.enabled,
    })),
    text_replacements: replacementRules.value.map((r) => ({
      id: r.id,
      fromText: r.fromText,
      toText: r.toText,
    })),
  };
}

function handleSaveUserName(): void {
  emit("save", constructPayload());
  triggerSuccessNotice();
}

function handleSaveVariables(): void {
  emit("save", constructPayload());
  triggerSuccessNotice();
}

function handleSaveMemoryBlocks(): void {
  emit("save", constructPayload());
  triggerSuccessNotice();
}

function handleAddMemoryBlock(): void {
  memoryBlocks.value.push({
    id: `mem_${Date.now()}`,
    title: `记忆区块 ${memoryBlocks.value.length + 1}`,
    content: "",
    enabled: true,
  });
}

function handleAddReplacement(): void {
  if (!newReplaceFrom.value.trim()) return;
  replacementRules.value.push({
    id: `rep_${Date.now()}`,
    fromText: newReplaceFrom.value.trim(),
    toText: newReplaceTo.value.trim(),
  });
  newReplaceFrom.value = "";
  newReplaceTo.value = "";
}

function handleSaveAll(): void {
  emit("save", constructPayload());
  triggerSuccessNotice();
}

function triggerSuccessNotice(): void {
  showSuccessNotification.value = true;
  setTimeout(() => {
    showSuccessNotification.value = false;
  }, 2500);
}
</script>

<template>
  <!-- 抽屉蒙层 -->
  <Transition name="fade">
    <div
      v-if="open"
      @click="handleClose"
      class="fixed inset-0 z-50 bg-black/85 backdrop-blur-sm transition-opacity"
    />
  </Transition>

  <!-- 右侧全高抽屉 (1:1 Figma 规格: width: 100%, max-w-[440px], background: #292524) -->
  <Transition name="slide-right">
    <aside
      v-if="open"
      class="fixed top-0 right-0 bottom-0 z-50 w-full max-w-[440px] bg-[#292524] text-[#F5F5F4] flex flex-col shadow-2xl overflow-hidden select-none"
    >
      <!-- 1. 顶栏: 标题「主控面板」+ 关闭按钮 (标准 h-14 56px 弹性完美垂直居中) -->
      <header class="h-14 px-5 flex items-center justify-between border-b border-[#44403C] bg-[#292524] shrink-0">
        <h2 class="text-lg font-bold text-[#F9C86D] tracking-tight leading-none">
          主控面板
        </h2>

        <button
          type="button"
          @click="handleClose"
          class="w-8 h-8 rounded-lg flex items-center justify-center text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-white/5 active:scale-95 transition-all cursor-pointer"
          title="关闭"
        >
          <X class="w-5 h-5" />
        </button>
      </header>

      <!-- 2. 可滚动的主体配置区域 -->
      <main class="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        
        <!-- (1) 用户名设置 -->
        <section class="p-4 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col">
          <h3 class="text-base font-semibold text-[#F9C86D]">
            用户名设置
          </h3>
          
          <div class="pt-3 flex flex-col">
            <label class="text-sm text-[#A8A29E]">
              显示用户名
            </label>
            <p class="text-xs text-[#A8A29E]/70 pt-1 pb-2">
              你在对话中的名字，替代 &#123;&#123;user&#125;&#125;
            </p>
            <input
              v-model="userName"
              type="text"
              class="w-full px-3 py-2 rounded-md border border-[#44403C] bg-[#1C1917] text-[#F4E8C1] text-base font-mono outline-none focus:border-[#F9C86D]/60 transition-colors"
            />
          </div>

          <div class="pt-4 flex items-center gap-3">
            <button
              type="button"
              @click="handleResetUserName"
              class="px-4 py-2 rounded-lg bg-[#44403C] text-sm font-medium text-[#A8A29E] hover:text-[#F5F5F4] active:scale-95 transition-all cursor-pointer"
            >
              重置
            </button>
            <button
              type="button"
              @click="handleSaveUserName"
              class="px-4 py-2 rounded-lg bg-[#F9C86D] text-sm font-medium text-[#1C1917] hover:bg-[#F9C86D]/90 active:scale-95 transition-all cursor-pointer"
            >
              保存
            </button>
          </div>
        </section>

        <!-- (2) User 人设 -->
        <section class="p-4 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col">
          <h3 class="text-base font-semibold text-[#F9C86D] pb-3">
            User人设
          </h3>
          <textarea
            v-model="userPersona"
            rows="4"
            placeholder="输入你的角色人设..."
            class="w-full p-3 rounded-md border border-[#44403C] bg-[#1C1917] text-sm text-[#F4E8C1] placeholder-[#F4E8C1]/40 outline-none focus:border-[#F9C86D]/60 transition-colors resize-none"
          />
        </section>

        <!-- (3) 指令区 -->
        <section class="p-4 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col">
          <h3 class="text-base font-semibold text-[#F9C86D] pb-3">
            指令区
          </h3>
          <textarea
            v-model="customPrompt"
            rows="4"
            placeholder="此处的指令会在每次对话时自动附加发送给 AI"
            class="w-full p-3 rounded-md border border-[#44403C] bg-[#1C1917] text-sm text-[#F4E8C1] placeholder-[#F4E8C1]/40 outline-none focus:border-[#F9C86D]/60 transition-colors resize-none"
          />
        </section>

        <!-- (4) 角色变量 (动态 MVU 状态机变量) -->
        <section class="p-4 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Variable class="w-4 h-4 text-[#F9C86D]" />
              <h3 class="text-base font-semibold text-[#F9C86D]">
                角色变量 ({{ varList.length }})
              </h3>
            </div>
            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="handleAddVariable"
                class="flex items-center gap-1 text-xs text-[#F9C86D] hover:underline cursor-pointer select-none font-medium px-2 py-1 rounded hover:bg-white/5 transition-all"
              >
                <Plus class="w-3.5 h-3.5" />
                <span>添加变量</span>
              </button>
              <button
                type="button"
                @click="handleSaveVariables"
                class="px-3.5 py-1.5 rounded-lg bg-[#F9C86D] text-xs font-bold text-[#1C1917] hover:bg-[#F9C86D]/90 active:scale-95 transition-all cursor-pointer"
              >
                保存
              </button>
            </div>
          </div>

          <p class="text-xs text-[#A8A29E]/70 leading-relaxed">
            RPG 剧情动态变量矩阵（如好感度、HP、货币或状态开关），可随对话剧情推演自动增量更新。
          </p>

          <!-- 变量列表 -->
          <div v-if="varList.length > 0" class="flex flex-col gap-2 pt-1">
            <div
              v-for="(item, idx) in varList"
              :key="item.id"
              class="flex items-center gap-2 p-2 rounded-lg bg-[#1C1917] border border-[#44403C]"
            >
              <!-- 变量名 -->
              <input
                v-model="item.key"
                type="text"
                placeholder="变量名 (如 hp)"
                class="flex-1 min-w-0 px-2.5 py-1.5 rounded bg-[#292524] border border-[#44403C] text-xs text-[#F4E8C1] font-mono outline-none focus:border-[#F9C86D]/60"
              />

              <!-- 类型切换 -->
              <select
                v-model="item.type"
                class="w-18 px-1.5 py-1.5 rounded bg-[#292524] border border-[#44403C] text-xs text-[#A8A29E] outline-none focus:border-[#F9C86D]/60 cursor-pointer"
              >
                <option value="number">数字</option>
                <option value="string">文本</option>
                <option value="boolean">布尔</option>
              </select>

              <!-- 数值输入 -->
              <template v-if="item.type === 'boolean'">
                <select
                  v-model="item.value"
                  class="w-24 px-1.5 py-1.5 rounded bg-[#292524] border border-[#44403C] text-xs text-[#F4E8C1] font-mono outline-none focus:border-[#F9C86D]/60 cursor-pointer"
                >
                  <option value="true">true</option>
                  <option value="false">false</option>
                </select>
              </template>
              <template v-else-if="item.type === 'number'">
                <input
                  v-model="item.value"
                  type="number"
                  placeholder="数值"
                  class="w-24 px-2 py-1.5 rounded bg-[#292524] border border-[#44403C] text-xs text-[#F4E8C1] font-mono outline-none focus:border-[#F9C86D]/60"
                />
              </template>
              <template v-else>
                <input
                  v-model="item.value"
                  type="text"
                  placeholder="文本值"
                  class="w-24 px-2 py-1.5 rounded bg-[#292524] border border-[#44403C] text-xs text-[#F4E8C1] font-mono outline-none focus:border-[#F9C86D]/60"
                />
              </template>

              <!-- 删除按钮 -->
              <button
                type="button"
                @click="handleRemoveVariable(idx)"
                class="text-[#78716C] hover:text-red-400 p-1 cursor-pointer transition-colors"
                title="删除变量"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div v-else class="text-center py-3 text-xs text-[#78716C]">
            暂无变量声明，点击上方“添加变量”创建角色剧情数值。
          </div>
        </section>

        <!-- (5) 记忆区块 (0) -->
        <section class="p-4 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col">
          <div class="flex items-center justify-between pb-3">
            <h3 class="text-base font-semibold text-[#F9C86D]">
              记忆区块 ({{ memoryBlocks.length }})
            </h3>
            <div class="flex items-center gap-2">
              <button
                type="button"
                @click="handleAddMemoryBlock"
                class="px-3 py-1.5 rounded-lg border border-[#F9C86D]/30 bg-[#44403C] text-xs font-medium text-[#F9C86D] hover:bg-[#44403C]/80 active:scale-95 transition-all cursor-pointer flex items-center gap-1"
              >
                <Plus class="w-3.5 h-3.5" />
                <span>新建区块</span>
              </button>
              <button
                type="button"
                @click="handleSaveMemoryBlocks"
                class="px-3.5 py-1.5 rounded-lg bg-[#F9C86D] text-xs font-medium text-[#1C1917] hover:bg-[#F9C86D]/90 active:scale-95 transition-all cursor-pointer"
              >
                保存
              </button>
            </div>
          </div>

          <!-- 说明提示 -->
          <div class="pt-2 text-xs text-[#78716C] flex flex-col gap-1 leading-relaxed">
            <p>💡 记忆区块可以手动创建，也会在自动总结时自动生成。</p>
            <p>• 启用的区块会被发送给AI作为长期记忆</p>
            <p>• 禁用的区块不会发送，但会保留在这里</p>
            <p>• 可以手动编辑标题和内容，调整顺序</p>
          </div>

          <!-- 列表区 -->
          <div v-if="memoryBlocks.length > 0" class="mt-3 flex flex-col gap-2">
            <div
              v-for="block in memoryBlocks"
              :key="block.id"
              class="p-2.5 rounded border border-[#44403C] bg-[#1C1917] flex flex-col gap-2"
            >
              <div class="flex items-center justify-between">
                <input
                  v-model="block.title"
                  type="text"
                  class="bg-transparent text-xs font-semibold text-[#F9C86D] outline-none"
                />
                <button
                  type="button"
                  @click="memoryBlocks = memoryBlocks.filter(b => b.id !== block.id)"
                  class="text-xs text-[#78716C] hover:text-red-400"
                >
                  删除
                </button>
              </div>
              <textarea
                v-model="block.content"
                rows="2"
                placeholder="区块记忆内容..."
                class="w-full p-2 bg-[#292524] text-xs text-[#F5F5F4] rounded border border-[#44403C] outline-none resize-none"
              />
            </div>
          </div>
        </section>

        <!-- (6) 文本替换 -->
        <section class="flex flex-col">
          <h3 class="text-base font-semibold text-[#F9C86D] pb-3">
            文本替换
          </h3>

          <div class="p-4 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-3">
            <div class="flex flex-col gap-2">
              <input
                v-model="newReplaceFrom"
                type="text"
                placeholder="输入要替换的文本..."
                class="w-full px-3 py-2 rounded-md border border-[#44403C] bg-[#1C1917] text-sm text-[#F4E8C1] placeholder-[#78716C] outline-none focus:border-[#F9C86D]/60"
              />
              <div class="flex items-center justify-center text-[#C0A480] text-sm">
                ↓
              </div>
              <input
                v-model="newReplaceTo"
                type="text"
                placeholder="输入替换后的文本..."
                class="w-full px-3 py-2 rounded-md border border-[#44403C] bg-[#1C1917] text-sm text-[#F4E8C1] placeholder-[#78716C] outline-none focus:border-[#F9C86D]/60"
              />
            </div>

            <div class="flex justify-start">
              <button
                type="button"
                @click="handleAddReplacement"
                :disabled="!newReplaceFrom.trim()"
                :class="[
                  'px-4 py-1.5 rounded-lg text-sm font-medium transition-all cursor-pointer',
                  newReplaceFrom.trim()
                    ? 'bg-[#F9C86D] text-[#1C1917] hover:bg-[#F9C86D]/90'
                    : 'bg-[#F9C86D]/40 text-[#1C1917]/60 cursor-not-allowed'
                ]"
              >
                添加
              </button>
            </div>

            <!-- 规则列表或空状态 -->
            <div class="pt-2 flex flex-col">
              <div
                v-if="replacementRules.length === 0"
                class="text-xs text-[#C0A480] py-2"
              >
                暂无替换规则
              </div>
              <div v-else class="flex flex-col gap-1.5">
                <div
                  v-for="rule in replacementRules"
                  :key="rule.id"
                  class="px-2.5 py-1.5 rounded border border-[#44403C] bg-[#1C1917] flex items-center justify-between text-xs"
                >
                  <span class="text-[#F4E8C1] font-mono">
                    {{ rule.fromText }} → {{ rule.toText }}
                  </span>
                  <button
                    type="button"
                    @click="replacementRules = replacementRules.filter(r => r.id !== rule.id)"
                    class="text-[#78716C] hover:text-red-400"
                  >
                    删除
                  </button>
                </div>
              </div>

              <p class="text-xs text-[#78716C] pt-2">
                规则按添加顺序生效，支持中文文本替换，实时显示效果
              </p>
            </div>
          </div>
        </section>

      </main>

      <!-- 3. 底部固定保存栏 (增加充足底部留白 pb-9 / 36px，消除紧贴感) -->
      <footer class="px-4 pt-3.5 pb-9 flex items-center justify-end border-t border-[#44403C]/80 bg-[#292524]/95 backdrop-blur-md shrink-0 shadow-lg">
        <button
          type="button"
          @click="handleSaveAll"
          class="px-6 py-2.5 rounded-lg bg-[#F9C86D] text-sm font-bold text-[#1C1917] hover:bg-[#F9C86D]/90 active:scale-95 transition-all shadow-[0_4px_16px_rgba(249,200,109,0.2)] cursor-pointer"
        >
          保存设置
        </button>
      </footer>


      <!-- 4. 成功通知弹层 (1:1 像素级还原图片中的绿色微光成功卡片) -->
      <Transition name="fade">
        <div
          v-if="showSuccessNotification"
          class="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 z-50 px-5 py-4 rounded-xl border border-[#22C55E]/60 bg-[#1A1F1C]/95 backdrop-blur-xl flex items-center gap-3 shadow-2xl animate-fade-in pointer-events-none"
        >
          <CheckCircle2 class="w-6 h-6 text-[#22C55E] shrink-0" />
          <div class="flex flex-col">
            <span class="text-sm font-bold text-white">成功</span>
            <span class="text-xs text-[#A8A29E] mt-0.5">人设和记忆区已保存</span>
          </div>
        </div>
      </Transition>

    </aside>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}
</style>
