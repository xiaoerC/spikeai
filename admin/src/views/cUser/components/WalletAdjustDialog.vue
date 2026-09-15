<template>
  <el-dialog
    v-model="visible"
    title="人工资产调账"
    width="480px"
    destroy-on-close
    :close-on-click-modal="false"
    class="rounded-xl"
  >
    <div v-if="targetUser" class="flex flex-col gap-4">
      <div class="flex items-center justify-between p-3 rounded-lg bg-[var(--el-fill-color-light)]">
        <div class="flex items-center gap-3">
          <el-avatar :size="40" :src="targetUser.avatar_url">
            {{ targetUser.username.slice(0, 1).toUpperCase() }}
          </el-avatar>
          <div class="flex flex-col">
            <span class="font-semibold text-[var(--el-text-color-primary)] text-sm">
              {{ targetUser.username }}
            </span>
            <span class="text-xs text-[var(--el-text-color-secondary)]">
              {{ targetUser.email }}
            </span>
          </div>
        </div>
        <div class="flex flex-col items-end gap-1 text-xs">
          <span>当前星元: <strong class="text-amber-500 font-bold">{{ targetUser.star_coins }} ★</strong></span>
          <span>当前月华: <strong class="text-cyan-500 font-bold">{{ targetUser.moon_gems }} 🌙</strong></span>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        class="flex flex-col gap-3"
      >
        <el-form-item label="调账币种" prop="currency">
          <el-radio-group v-model="form.currency" class="w-full">
            <el-radio-button value="star">星元 ★ (基础通用币)</el-radio-button>
            <el-radio-button value="moon">月华 🌙 (高级算力币)</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="操作方向" prop="action">
          <el-radio-group v-model="form.action" class="w-full">
            <el-radio-button value="add">
              <span class="text-emerald-500 font-semibold">+ 增加资产</span>
            </el-radio-button>
            <el-radio-button value="sub">
              <span class="text-rose-500 font-semibold">- 扣减资产</span>
            </el-radio-button>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="变动数量" prop="amount">
          <el-input-number
            v-model="form.amount"
            :min="1"
            :max="100000"
            :step="10"
            class="!w-full"
            placeholder="请输入调账数值"
          />
        </el-form-item>

        <el-form-item label="调账原因 / 审计备注" prop="reason">
          <el-input
            v-model="form.reason"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="请详细说明调账原因（如：首发充值补偿、违规作弊罚没、系统异常修复等，必填）"
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
          确认调账
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script lang="ts" setup>
import { type ICUserItem, type IWalletAdjustPayload, adjustUserWallet } from '@/api/cUser';
import { ElMessage, type FormInstance, type FormRules } from 'element-plus';
import { reactive, ref } from 'vue';

const emit =
  defineEmits<
    (e: 'success', data: { userId: string; currency: string; balanceAfter: number }) => void
  >();

const visible = ref(false);
const loading = ref(false);
const formRef = ref<FormInstance>();
const targetUser = ref<ICUserItem | null>(null);

const form = reactive<IWalletAdjustPayload>({
  currency: 'star',
  action: 'add',
  amount: 100,
  reason: '',
});

const rules: FormRules = {
  currency: [{ required: true, message: '请选择调账币种', trigger: 'change' }],
  action: [{ required: true, message: '请选择操作类型', trigger: 'change' }],
  amount: [{ required: true, message: '请输入调账数值', trigger: 'blur' }],
  reason: [
    { required: true, message: '必须填写调账原因以备审计', trigger: 'blur' },
    { min: 2, message: '调账原因不能少于 2 个字', trigger: 'blur' },
  ],
};

function open(user: ICUserItem) {
  targetUser.value = user;
  form.currency = 'star';
  form.action = 'add';
  form.amount = 100;
  form.reason = '';
  visible.value = true;
}

async function handleSubmit() {
  if (!formRef.value || !targetUser.value) return;
  await formRef.value.validate(async (valid) => {
    if (!valid || !targetUser.value) return;
    try {
      loading.value = true;
      const res = await adjustUserWallet(targetUser.value.id, form);
      ElMessage.success('人工调账成功，已写入资金审计流水');
      visible.value = false;
      emit('success', {
        userId: targetUser.value.id,
        currency: form.currency,
        balanceAfter: res.data.balance_after,
      });
    } catch (error: any) {
      ElMessage.error(error?.message || '调账失败，请检查余额是否足够');
    } finally {
      loading.value = false;
    }
  });
}

defineExpose({
  open,
});
</script>
