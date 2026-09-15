<template>
  <el-drawer
    v-model="visible"
    title="对话历史全景回溯与推理审计"
    size="720px"
    destroy-on-close
    class="custom-drawer"
  >
    <div v-if="session" v-loading="loading" class="flex flex-col h-full gap-4">
      <!-- 1. 顶部会话元数据面板 -->
      <div class="p-3 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)] flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <el-avatar :size="42" :src="session.character_avatar" class="rounded-lg border border-[var(--el-border-color-lighter)]">
            {{ session.character_name.slice(0, 1) }}
          </el-avatar>
          <div class="flex flex-col leading-snug">
            <span class="font-bold text-sm text-[var(--el-text-color-primary)]">
              {{ session.character_name }}
            </span>
            <span class="text-xs text-[var(--el-text-color-secondary)]">
              与用户 <strong>{{ session.user_name }}</strong> ({{ session.user_email }})
            </span>
          </div>
        </div>

        <div class="flex items-center gap-2 text-xs">
          <el-tag size="small" type="primary" effect="plain">{{ session.current_model_id }}</el-tag>
          <el-tag size="small" type="warning" effect="plain">共 {{ messages.length }} 条记录</el-tag>
          <el-tag size="small" type="success" effect="plain">消耗 {{ totalTokens }} Token</el-tag>
        </div>
      </div>

      <!-- 2. 消息流气泡区域 -->
      <div class="flex-1 overflow-y-auto p-3 flex flex-col gap-4 bg-[var(--el-bg-color-page)] rounded-xl border border-[var(--el-border-color-lighter)]">
        <div v-if="messages.length === 0" class="text-center py-12 text-xs text-[var(--el-text-color-placeholder)]">
          该会话尚无对话交互记录
        </div>

        <div
          v-for="msg in messages"
          :key="msg.id"
          class="flex flex-col gap-1"
        >
          <!-- 系统消息 -->
          <div v-if="msg.sender === 'system'" class="flex justify-center my-1">
            <span class="text-[11px] px-3 py-1 rounded-full bg-[var(--el-fill-color-dark)] text-[var(--el-text-color-secondary)]">
              {{ msg.content }}
            </span>
          </div>

          <!-- 用户消息 (靠右) -->
          <div v-else-if="msg.sender === 'user'" class="flex items-start justify-end gap-2.5 pl-12">
            <div class="flex flex-col items-end gap-1 max-w-[85%]">
              <div class="flex items-center gap-2 text-[11px] text-[var(--el-text-color-placeholder)]">
                <span>{{ session.user_name }}</span>
                <span>{{ msg.created_at?.slice(11, 19) }}</span>
              </div>
              <div class="p-3 rounded-2xl rounded-tr-xs bg-[var(--el-color-primary)] text-white text-xs leading-relaxed whitespace-pre-wrap shadow-xs">
                {{ msg.content }}
              </div>
            </div>
            <el-avatar :size="32" :src="session.user_avatar" class="flex-shrink-0 mt-1">
              {{ session.user_name.slice(0, 1) }}
            </el-avatar>
          </div>

          <!-- AI 发言消息 (靠左) -->
          <div v-else class="flex items-start gap-2.5 pr-12">
            <el-avatar :size="32" :src="session.character_avatar" class="flex-shrink-0 mt-1">
              {{ session.character_name.slice(0, 1) }}
            </el-avatar>
            <div class="flex flex-col items-start gap-1 max-w-[85%]">
              <div class="flex items-center gap-2 text-[11px] text-[var(--el-text-color-placeholder)]">
                <span class="font-medium text-[var(--el-text-color-regular)]">{{ session.character_name }}</span>
                <span>{{ msg.created_at?.slice(11, 19) }}</span>
              </div>

              <!-- AI 思维链折叠卡片 -->
              <el-collapse v-if="msg.thinking_content" class="w-full mb-1 border-none bg-transparent">
                <el-collapse-item name="thinking">
                  <template #title>
                    <span class="text-xs text-amber-500 font-medium flex items-center gap-1">
                      🧠 深度推理思维链 ({{ msg.thinking_content.length }} 字符)
                    </span>
                  </template>
                  <pre class="m-0 p-2.5 rounded-lg text-xs font-mono bg-zinc-900 text-zinc-300 dark:bg-black/50 overflow-x-auto whitespace-pre-wrap leading-relaxed max-h-48">
                    {{ msg.thinking_content }}
                  </pre>
                </el-collapse-item>
              </el-collapse>

              <!-- AI 正文 -->
              <div class="p-3 rounded-2xl rounded-tl-xs bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] text-xs text-[var(--el-text-color-primary)] leading-relaxed whitespace-pre-wrap shadow-xs">
                {{ msg.content }}
              </div>

              <!-- Token 审计指标小标 -->
              <div v-if="msg.input_tokens || msg.output_tokens" class="text-[10px] text-[var(--el-text-color-placeholder)] flex items-center gap-2 mt-0.5">
                <span>In: {{ msg.input_tokens }} tok</span>
                <span>Out: {{ msg.output_tokens }} tok</span>
                <span class="text-emerald-500 font-medium">Total: {{ msg.input_tokens + msg.output_tokens }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 3. 底部操作栏 -->
      <div class="flex items-center justify-between pt-2">
        <el-button type="danger" plain size="small" @click="handleDelete">
          清理/删除此违规会话
        </el-button>
        <el-button @click="visible = false">关闭</el-button>
      </div>
    </div>
  </el-drawer>
</template>

<script lang="ts" setup>
import {
  type IAdminChatMessageItem,
  type IAdminChatSessionItem,
  deleteChatSession,
  getChatTranscript,
} from '@/api/chatOps';
import { ElMessage, ElMessageBox } from 'element-plus';
import { computed, ref } from 'vue';

const emit = defineEmits<(e: 'deleted') => void>();

const visible = ref(false);
const loading = ref(false);
const session = ref<IAdminChatSessionItem | null>(null);
const messages = ref<IAdminChatMessageItem[]>([]);

const totalTokens = computed(() => {
  return messages.value.reduce((acc, m) => acc + (m.input_tokens || 0) + (m.output_tokens || 0), 0);
});

async function open(item: IAdminChatSessionItem) {
  session.value = item;
  visible.value = true;
  loading.value = true;
  try {
    const res = await getChatTranscript(item.id);
    session.value = res.session;
    messages.value = res.messages || [];
  } catch (error: any) {
    ElMessage.error(error?.message || '获取会话历史记录失败');
    visible.value = false;
  } finally {
    loading.value = false;
  }
}

async function handleDelete() {
  if (!session.value) return;
  try {
    await ElMessageBox.confirm(
      `确定要彻底删除用户 ${session.value.user_name} 与角色 ${session.value.character_name} 的此段会话记录吗？操作不可逆并记录审计日志。`,
      '清理违规会话确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    );
    loading.value = true;
    await deleteChatSession(session.value.id);
    ElMessage.success('会话已彻底清理');
    visible.value = false;
    emit('deleted');
  } catch {
    // 用户取消
  } finally {
    loading.value = false;
  }
}

defineExpose({
  open,
});
</script>
