<template>
  <div class="flex flex-col size-full p-4 box-border overflow-y-auto gap-4">
    <!-- 顶部欢迎卡片 -->
    <div class="card-base flex items-center justify-between">
      <div class="flex items-center gap-4">
        <el-avatar :size="56" :src="AvatarLogo" />
        <div class="flex flex-col gap-1">
          <h2 class="text-xl font-bold text-gray-800 dark:text-gray-100">
            {{ getTimeStateStr() }}，管理员
          </h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">
            欢迎来到 SpikeAI / 叙梦 Naro 运营管理后台
          </p>
        </div>
      </div>
      <div class="hidden sm:flex items-center gap-3">
        <el-tag type="success" effect="dark">系统正常运行</el-tag>
        <el-tag type="warning" effect="plain">Vite 6 + Vue 3.5</el-tag>
      </div>
    </div>

    <!-- 核心指标统计网格 (Grid 优先) -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div class="card-base flex items-center justify-between">
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">累计注册用户</span>
          <div class="text-2xl font-bold text-blue-500">
            <CountTo :start-val="0" :end-val="12580" :duration="2000" />
          </div>
          <span class="text-xs text-emerald-500">较上周 +12.5%</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-50 dark:bg-blue-950/40 flex items-center justify-center text-blue-500 text-2xl">
          <el-icon><User /></el-icon>
        </div>
      </div>

      <div class="card-base flex items-center justify-between">
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">AI 角色卡总数</span>
          <div class="text-2xl font-bold text-emerald-500">
            <CountTo :start-val="0" :end-val="386" :duration="2000" />
          </div>
          <span class="text-xs text-emerald-500">已审核通过 98.2%</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-50 dark:bg-emerald-950/40 flex items-center justify-center text-emerald-500 text-2xl">
          <el-icon><Postcard /></el-icon>
        </div>
      </div>

      <div class="card-base flex items-center justify-between">
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">分支会话互动数</span>
          <div class="text-2xl font-bold text-amber-500">
            <CountTo :start-val="0" :end-val="89240" :duration="2000" />
          </div>
          <span class="text-xs text-amber-500">DAG 节点 24.6 万</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-amber-50 dark:bg-amber-950/40 flex items-center justify-center text-amber-500 text-2xl">
          <el-icon><ChatDotRound /></el-icon>
        </div>
      </div>

      <div class="card-base flex items-center justify-between">
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500 dark:text-gray-400 font-medium">Token 消耗总计</span>
          <div class="text-2xl font-bold text-purple-500">
            <CountTo :start-val="0" :end-val="468900" :duration="2000" />
          </div>
          <span class="text-xs text-purple-500">今日活跃峰值</span>
        </div>
        <div class="w-12 h-12 rounded-xl bg-purple-50 dark:bg-purple-950/40 flex items-center justify-center text-purple-500 text-2xl">
          <el-icon><Coin /></el-icon>
        </div>
      </div>
    </div>

    <!-- 中部系统状态概览 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <div class="card-base lg:col-span-2 flex flex-col gap-3">
        <div class="flex items-center justify-between pb-2 border-b border-gray-100 dark:border-gray-800">
          <span class="font-bold text-base text-gray-800 dark:text-gray-100">SpikeAI 核心架构状态</span>
          <el-tag size="small" type="primary">实时监控</el-tag>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div class="p-3 rounded-lg bg-gray-50 dark:bg-[#262727] flex items-center justify-between">
            <div class="flex flex-col">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">FastAPI 网关</span>
              <span class="text-xs text-gray-400">Python 3.12 异步网关</span>
            </div>
            <el-tag type="success" size="small">在线 200 OK</el-tag>
          </div>

          <div class="p-3 rounded-lg bg-gray-50 dark:bg-[#262727] flex items-center justify-between">
            <div class="flex flex-col">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">PostgreSQL 16</span>
              <span class="text-xs text-gray-400">pgvector 向量知识库</span>
            </div>
            <el-tag type="success" size="small">已就绪</el-tag>
          </div>

          <div class="p-3 rounded-lg bg-gray-50 dark:bg-[#262727] flex items-center justify-between">
            <div class="flex flex-col">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Redis 7 缓存</span>
              <span class="text-xs text-gray-400">会话上下文与行锁</span>
            </div>
            <el-tag type="success" size="small">运行中</el-tag>
          </div>

          <div class="p-3 rounded-lg bg-gray-50 dark:bg-[#262727] flex items-center justify-between">
            <div class="flex flex-col">
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">SSE 流式网关</span>
              <span class="text-xs text-gray-400">打字机逐字输出服务</span>
            </div>
            <el-tag type="success" size="small">低延迟</el-tag>
          </div>
        </div>
      </div>

      <div class="card-base flex flex-col gap-3">
        <div class="flex items-center justify-between pb-2 border-b border-gray-100 dark:border-gray-800">
          <span class="font-bold text-base text-gray-800 dark:text-gray-100">管理快捷入口</span>
        </div>
        <div class="flex flex-col gap-2">
          <el-button class="w-full justify-start" @click="$router.push('/om/user')">
            <template #icon><el-icon><User /></el-icon></template>
            用户与账号管理
          </el-button>
          <el-button class="w-full justify-start" @click="$router.push('/om/role')">
            <template #icon><el-icon><Lock /></el-icon></template>
            角色与权限配置
          </el-button>
          <el-button class="w-full justify-start" @click="$router.push('/om/department')">
            <template #icon><el-icon><OfficeBuilding /></el-icon></template>
            组织架构管理
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import AvatarLogo from '@/assets/image/berserk.jpg';
import CountTo from '@/components/CountTo/index.vue';
import { getTimeStateStr } from '@/utils/index';
import { ChatDotRound, Coin, Lock, OfficeBuilding, Postcard, User } from '@element-plus/icons-vue';
</script>
