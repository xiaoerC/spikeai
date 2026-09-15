<template>
  <el-dialog
    v-model="visible"
    title="角色卡状态治理与内容审核"
    width="500px"
    destroy-on-close
    :close-on-click-modal="false"
    class="rounded-xl"
  >
    <div v-if="targetChar" class="flex flex-col gap-4">
      <!-- 角色简况 -->
      <div class="flex items-center gap-3 p-3 rounded-lg bg-[var(--el-fill-color-light)]">
        <el-avatar :size="48" shape="square" :src="targetChar.avatar_url" class="rounded-lg">
          {{ targetChar.name.slice(0, 1) }}
        </el-avatar>
        <div class="flex flex-col flex-1 leading-snug">
          <div class="flex items-center justify-between">
            <span class="font-bold text-sm text-[var(--el-text-color-primary)]">
              {{ targetChar.name }}
            </span>
            <el-tag
              :type="targetChar.status === 'published' ? 'success' : targetChar.status === 'banned' ? 'danger' : 'info'"
              size="small"
            >
              {{ targetChar.status === 'published' ? '已上架' : targetChar.status === 'banned' ? '已违规下架' : '私密/未上架' }}
            </el-tag>
          </div>
          <span class="text-xs text-[var(--el-text-color-secondary)] mt-1">
            创作者: {{ targetChar.author_name }} ({{ targetChar.author_email }})
          </span>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="flex flex-col gap-3"
      >
        <el-form-item label="处置操作 / 目标状态" prop="status">
          <el-radio-group v-model="form.status" class="w-full">
            <el-radio-button value="published">
              <span class="text-emerald-500 font-semibold">✔ 审核通过 / 上架</span>
            </el-radio-button>
            <el-radio-button value="private">
              <span class="text-amber-500 font-semibold">🔒 转为私密</span>
            </el-radio-button>
            <el-radio-button value="banned">
              <span class="text-rose-500 font-semibold">⛔ 违规封禁下架</span>
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="处置说明 / 审核意见" prop="reason">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="若执行违规封禁或转为私密，请详述原因（如：涉嫌版权侵权、包含敏感违规描写、设定质量不符等，必填）"
          />
        </el-form-item>
      </el-form>
    </div>

    <template #footer>
      <div class="flex justify-end gap-3">
        <el-button @click="visible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleSubmit"
        >
          确认处置
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import {
  type IAdminCharacterItem,
  type IAdminCharacterStatusPayload,
  updateCharacterStatus,
} from '@/api/character';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { reactive, ref } from 'vue';

const emit = defineEmits<(e: 'success') => void>();

const visible = ref(false);
const loading = ref(false);
const formRef = ref<FormInstance>();
const targetChar = ref<IAdminCharacterItem | null>(null);

const form = reactive<IAdminCharacterStatusPayload>({
  status: 'published',
  reason: '',
});

const rules: FormRules = {
  status: [{ required: true, message: '请选择处置状态', trigger: 'change' }],
  reason: [
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (form.status === 'banned' && (!value || value.trim().length < 2)) {
          callback(new Error('违规下架封存必须填写处置理由（至少2字）以备安全审计'));
        } else {
          callback();
        }
      },
      trigger: 'blur',
    },
  ],
};

function open(char: IAdminCharacterItem) {
  targetChar.value = char;
  form.status = char.status === 'published' ? 'banned' : 'published';
  form.reason = '';
  visible.value = true;
}

async function handleSubmit() {
  if (!formRef.value || !targetChar.value) return;
  await formRef.value.validate(async (valid) => {
    if (!valid || !targetChar.value) return;
    try {
      loading.value = true;
      await updateCharacterStatus(targetChar.value.id, form);
      ElMessage.success('角色卡状态处置成功，审计日志已记录');
      visible.value = false;
      emit('success');
    } catch (error: any) {
      ElMessage.error(error?.message || '操作失败');
    } finally {
      loading.value = false;
    }
  });
}

defineExpose({
  open,
});
</script>
