<template>
  <div class="relative min-h-screen w-full flex items-center justify-center overflow-hidden bg-slate-50 dark:bg-[#0A0B10] transition-colors duration-300 select-none">
    <!-- 背景流光氛围光斑 (Dark / Light 双模式自适应) -->
    <div class="absolute -top-40 -left-40 w-96 h-96 rounded-full bg-amber-400/10 dark:bg-amber-500/15 blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 rounded-full bg-indigo-400/10 dark:bg-indigo-600/15 blur-3xl pointer-events-none"></div>
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] rounded-full bg-amber-300/5 dark:bg-amber-400/5 blur-3xl pointer-events-none"></div>

    <!-- 右上角主题切换浮窗 -->
    <div class="absolute top-6 right-6 z-20 flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/70 dark:bg-zinc-800/70 backdrop-blur-md border border-slate-200/80 dark:border-zinc-700/60 shadow-sm">
      <span class="text-xs text-slate-500 dark:text-zinc-400">主题模式</span>
      <SwitchDark />
    </div>

    <!-- 核心卡片容器 -->
    <div class="relative z-10 w-full max-w-4xl mx-4 my-8 grid grid-cols-1 lg:grid-cols-12 rounded-3xl overflow-hidden bg-white/80 dark:bg-[#151722]/85 backdrop-blur-2xl border border-slate-200/80 dark:border-amber-500/20 shadow-[0_25px_60px_rgba(0,0,0,0.06)] dark:shadow-[0_25px_60px_rgba(0,0,0,0.6)] transition-all">
      
      <!-- 左侧: 品牌视觉与系统特性区 (大屏显示) -->
      <div class="hidden lg:flex lg:col-span-5 flex-col justify-between p-10 bg-gradient-to-br from-slate-100/80 to-slate-200/40 dark:from-[#1A1D2B]/90 dark:to-[#12141F]/80 border-r border-slate-200/60 dark:border-zinc-800/80">
        <div>
          <div class="flex items-center gap-3 mb-8">
            <img src="@/assets/image/logo.svg" alt="SpikeAI" class="w-10 h-10 drop-shadow" />
            <div>
              <h1 class="text-xl font-bold tracking-tight text-slate-900 dark:text-zinc-100">SpikeAI</h1>
              <span class="text-xs text-amber-600 dark:text-amber-400 font-medium">智能体全栈运营管理中枢</span>
            </div>
          </div>

          <h3 class="text-2xl font-bold text-slate-800 dark:text-zinc-100 leading-snug mb-3">
            新一代智能体角色运营<br />与互动管理服务平台
          </h3>
          <p class="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed mb-6">
            面向高并发沉浸式角色对话、知识库世界书治理、多维数据流转与平台资产结算的一站式企业级运营系统。
          </p>

          <!-- 特性矩阵小徽章 -->
          <div class="flex flex-col gap-2.5">
            <div class="flex items-center gap-2.5 px-3 py-2 rounded-xl bg-white/60 dark:bg-zinc-800/40 border border-slate-200/50 dark:border-zinc-700/50 text-xs text-slate-700 dark:text-zinc-300">
              <el-icon class="text-amber-500"><Lock /></el-icon>
              <span>企业级 RBAC 细粒度权限控制与操作审计</span>
            </div>
            <div class="flex items-center gap-2.5 px-3 py-2 rounded-xl bg-white/60 dark:bg-zinc-800/40 border border-slate-200/50 dark:border-zinc-700/50 text-xs text-slate-700 dark:text-zinc-300">
              <el-icon class="text-blue-500"><Connection /></el-icon>
              <span>全链路实时会话流式推理与智能体监控</span>
            </div>
            <div class="flex items-center gap-2.5 px-3 py-2 rounded-xl bg-white/60 dark:bg-zinc-800/40 border border-slate-200/50 dark:border-zinc-700/50 text-xs text-slate-700 dark:text-zinc-300">
              <el-icon class="text-emerald-500"><Platform /></el-icon>
              <span>智能体知识库语义检索与内容安全治理</span>
            </div>
          </div>
        </div>

        <div class="text-[11px] text-slate-400 dark:text-zinc-500 pt-6">
          © 2026 SpikeAI Systems. All Rights Reserved.
        </div>
      </div>

      <!-- 右侧: 登录表单区 -->
      <div class="lg:col-span-7 flex flex-col justify-center px-8 py-10 sm:px-12">
        <LoginForm />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import SwitchDark from '@/components/SwitchDark/index.vue';
import LoginForm from './components/LoginForm.vue';
</script>
