<script setup lang="ts">
/**
 * AI 聊天界面 - 主控面板抽屉 (1:1 Figma 原型高保真)
 *
 * 严格按照 Figma FrameId 80:2307 与真实原型截图构建：
 * 包含用户名设置、User人设、指令区、38 个角色变量网格矩阵、记忆区块、文本替换以及底部保存栏。
 *
 * @packageDocumentation
 */

import { CheckCircle2, Plus, X } from "lucide-vue-next";
import { reactive, ref } from "vue";

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<{
  (e: "update:open", val: boolean): void;
  (e: "save"): void;
}>();

// 1. 用户名设置
const userName = ref("spikeTom");

// 2. User 人设
const userPersona = ref("");

// 3. 指令区
const customPrompt = ref("");

// 4. 38 个角色变量 (variable_1 ~ variable_38)
const initialVars: Record<string, number> = {};
for (let i = 1; i <= 38; i++) {
  initialVars[`variable_${i}`] = 0;
}
const variables = reactive<Record<string, number>>(initialVars);

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

// 保存成功通知弹窗
const showSuccessNotification = ref(false);

function handleClose(): void {
  emit("update:open", false);
}

function handleResetUserName(): void {
  userName.value = "spikeTom";
}

function handleSaveUserName(): void {
  triggerSuccessNotice();
}

function handleSaveVariables(): void {
  triggerSuccessNotice();
}

function handleAddMemoryBlock(): void {
  memoryBlocks.value.push({
    id: `mem_${Date.now()}`,
    title: `记忆区块 ${memoryBlocks.value.length + 1}`,
    content: "",
    enabled: true,
  });
  triggerSuccessNotice();
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
      <!-- 1. 顶栏: 标题「主控面板」+ 关闭按钮 -->
      <header class="px-4 py-3.5 flex items-center justify-between border-b border-[#44403C] bg-[#292524] shrink-0 pt-safe">
        <h2 class="text-xl font-semibold text-[#F9C86D] tracking-tight">
          主控面板
        </h2>

        <button
          type="button"
          @click="handleClose"
          class="w-10 h-10 rounded-full flex items-center justify-center text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-white/5 active:scale-95 transition-all cursor-pointer"
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

        <!-- (4) 角色变量 (38 个双列网格矩阵) -->
        <section class="p-4 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col">
          <div class="flex items-center justify-between pb-3">
            <h3 class="text-base font-semibold text-[#F9C86D]">
              角色变量
            </h3>
            <button
              type="button"
              @click="handleSaveVariables"
              class="px-4 py-1.5 rounded-lg bg-[#F9C86D] text-sm font-bold text-[#1C1917] hover:bg-[#F9C86D]/90 active:scale-95 transition-all cursor-pointer"
            >
              保存
            </button>
          </div>

          <!-- 双列 38 个变量卡片 -->
          <div class="grid grid-cols-2 gap-3 pt-1">
            <div
              v-for="i in 38"
              :key="`variable_${i}`"
              class="p-2.5 rounded-lg border border-[#44403C] bg-[#1C1917] flex flex-col gap-1.5"
            >
              <span class="text-xs text-[#A8A29E] font-mono">
                variable_{{ i }}
              </span>
              <input
                v-model.number="variables[`variable_${i}`]"
                type="number"
                class="w-full h-9 px-2 text-center rounded-md border border-[#534741]/40 bg-[#2A2520]/50 text-[#F4E8C1] text-sm font-mono outline-none focus:border-[#F9C86D]/60"
              />
            </div>
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
                @click="triggerSuccessNotice"
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
