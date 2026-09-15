<template>
  <div class="flex flex-col gap-4 p-4 w-full h-full box-border">
    <!-- 1. 顶部全平台全局调音中枢 Header 面板 -->
    <div
      class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm"
    >
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-xl text-amber-500 shadow-xs">
          🎛️
        </div>
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-base font-bold tracking-wide text-[var(--el-text-color-primary)]">
              SillyTavern 全局调音中枢
            </h1>
            <el-tag v-if="preset.is_active" type="success" effect="dark" size="small">
              ● 当前预设全平台生效中
            </el-tag>
            <el-tag v-else type="info" effect="plain" size="small">
              ○ 未发布至全平台 (当前草稿/备选)
            </el-tag>
          </div>

          <!-- 预设选择器与快捷管理 -->
          <div class="flex items-center gap-2 flex-wrap mt-0.5">
            <span class="text-xs font-semibold text-[var(--el-text-color-secondary)]">预设库切换:</span>
            <el-select
              v-model="currentPresetId"
              placeholder="选择预设"
              size="small"
              class="!w-60"
              @change="handleSwitchPreset"
            >
              <el-option
                v-for="p in presetLibrary"
                :key="p.id"
                :label="p.preset_name"
                :value="p.id"
              >
                <div class="flex items-center justify-between w-full">
                  <span class="truncate font-medium">{{ p.preset_name }}</span>
                  <el-tag v-if="p.is_active" type="success" size="small" effect="plain" class="ml-2 !text-[10px]">生效中</el-tag>
                </div>
              </el-option>
            </el-select>

            <!-- 快捷管理小按钮组 -->
            <el-tooltip content="重命名当前预设" placement="top">
              <el-button size="small" circle @click="openRenameDialog">
                <el-icon><Edit /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="另存为新副本" placement="top">
              <el-button size="small" circle @click="handleDuplicatePreset">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip :content="preset.is_active ? '当前预设正在全平台生效中，不可删除' : '删除当前预设'" placement="top">
              <el-button
                size="small"
                circle
                type="danger"
                plain
                :disabled="preset.is_active || presetLibrary.length <= 1"
                @click="handleDeleteCurrentPreset"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </div>

      <!-- 顶部全局操作栏 -->
      <div class="flex flex-wrap items-center gap-2.5">
        <!-- 统计指标胶囊 -->
        <div class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)] text-xs">
          <span class="text-[var(--el-text-color-secondary)]">流水线:</span>
          <span class="font-bold text-amber-500 font-mono">{{ activeCount }} / {{ totalCount }}</span>
          <span class="text-[var(--el-border-color)]">|</span>
          <span class="text-[var(--el-text-color-secondary)]">正则:</span>
          <span class="font-bold text-blue-500 font-mono">{{ (preset.regex_scripts || []).length }} 项</span>
          <span class="text-[var(--el-border-color)]">|</span>
          <span class="text-[var(--el-text-color-secondary)]">预估 Token:</span>
          <span class="font-bold text-emerald-500 font-mono">{{ totalTokensEstimate }}</span>
        </div>

        <el-upload
          :show-file-list="false"
          :auto-upload="false"
          accept=".json"
          :on-change="handleImportPresetJsonFile"
        >
          <el-button type="warning" plain>
            <el-icon class="mr-1"><Upload /></el-icon> 导入预设 JSON
          </el-button>
        </el-upload>

        <el-button @click="handleExportJson">
          <el-icon class="mr-1"><Download /></el-icon> 导出当前 JSON
        </el-button>

        <el-button type="info" plain @click="router.push('/settings/llm')">
          <el-icon class="mr-1"><Connection /></el-icon> 大模型 API 配置
        </el-button>

        <el-button @click="handleSaveCurrentPreset" :loading="isSaving">
          <el-icon class="mr-1"><Check /></el-icon> 保存修改
        </el-button>

        <el-button
          type="primary"
          :disabled="preset.is_active"
          :loading="isActivating"
          @click="handleActivateCurrentPreset"
        >
          <el-icon class="mr-1"><Promotion /></el-icon>
          {{ preset.is_active ? '当前已全平台生效' : '设为全平台生效' }}
        </el-button>
      </div>
    </div>

    <!-- 2. 主体工作区 (Tabs 布局) -->
    <div class="flex-1 min-h-0 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm p-4 flex flex-col gap-4 overflow-hidden">
      <el-tabs v-model="activeMainTab" class="h-full flex flex-col flex-1 overflow-hidden tavern-tabs">
        <!-- Tab 1: 78 项提示词流水线编排器 -->
        <el-tab-pane name="pipeline" class="h-full flex flex-col gap-3 overflow-hidden">
          <template #label>
            <span class="flex items-center gap-1.5 font-medium">
              <el-icon><Operation /></el-icon>
              提示词排版流水线 ({{ totalCount }} 项)
            </span>
          </template>

          <!-- 过滤器与搜索栏 -->
          <div class="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-[var(--el-border-color-lighter)]">
            <div class="flex flex-wrap items-center gap-2.5">
              <el-radio-group v-model="filterType" size="small">
                <el-radio-button value="all">全部 ({{ totalCount }})</el-radio-button>
                <el-radio-button value="active">已启用 ({{ activeCount }})</el-radio-button>
                <el-radio-button value="marker">插桩锚点 ({{ markerCount }})</el-radio-button>
                <el-radio-button value="inactive">未启用备选 ({{ totalCount - activeCount }})</el-radio-button>
              </el-radio-group>

              <el-input
                v-model="searchKeyword"
                placeholder="搜索条目名称或正文内容..."
                clearable
                class="!w-64"
                size="small"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>

          <!-- 流水线卡片列表 (虚拟滚动/高自由度管理) -->
          <div class="flex-1 overflow-y-auto pr-1 flex flex-col gap-2">
            <div
              v-for="item in filteredPromptList"
              :key="item.identifier"
              class="group flex items-center justify-between gap-3 px-3.5 py-2.5 rounded-lg border transition-all"
              :class="[
                item.enabled
                  ? 'bg-[var(--el-fill-color-blank)] border-[var(--el-border-color)] hover:border-amber-500/50 hover:shadow-xs'
                  : 'bg-[var(--el-fill-color-light)] border-[var(--el-border-color-lighter)] opacity-60 hover:opacity-90'
              ]"
            >
              <!-- 序号与基本标识 -->
              <div class="flex items-center gap-2.5 min-w-0 flex-1">
                <span class="text-xs font-mono font-semibold w-7 text-[var(--el-text-color-secondary)] text-right flex-shrink-0">
                  {{ item.index + 1 }}.
                </span>

                <!-- 类型与插桩指示器 -->
                <div class="flex items-center gap-1.5 flex-shrink-0">
                  <el-tag
                    v-if="item.isMarker"
                    type="warning"
                    size="small"
                    effect="dark"
                    class="font-mono !px-1.5"
                  >
                    📌 锚点
                  </el-tag>
                  <el-tag
                    v-else
                    :type="item.role === 'user' ? 'danger' : (item.role === 'assistant' ? 'success' : 'info')"
                    size="small"
                    effect="plain"
                    class="font-mono !px-1.5"
                  >
                    {{ item.role }}
                  </el-tag>
                </div>

                <!-- 条目名称与标识 -->
                <div class="flex flex-col min-w-0 flex-1">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-semibold text-[var(--el-text-color-primary)] truncate">
                      {{ item.name }}
                    </span>
                    <el-tag
                      v-if="item.isUnorderedBackup"
                      size="small"
                      type="info"
                      effect="plain"
                      class="!text-[10px] !h-5 !px-1.5"
                    >
                      未编排备选
                    </el-tag>
                    <span class="text-[11px] font-mono text-[var(--el-text-color-secondary)] hidden md:inline truncate">
                      ({{ item.identifier }})
                    </span>
                  </div>
                  <p v-if="item.content" class="text-xs text-[var(--el-text-color-secondary)] truncate !m-0 max-w-[680px]">
                    {{ item.content }}
                  </p>
                  <p v-else-if="item.isMarker" class="text-xs text-amber-500/80 italic !m-0">
                    [系统核心插桩锚点：由上下文与角色设定动态渲染注入]
                  </p>
                </div>
              </div>

              <!-- 右侧控制区: Token、排序、编辑、开关 -->
              <div class="flex items-center gap-2 flex-shrink-0">
                <span class="text-xs font-mono text-[var(--el-text-color-secondary)] w-14 text-right">
                  {{ item.content ? Math.round(item.content.length * 0.7) : '-' }} tok
                </span>

                <!-- 上移 / 下移按钮 -->
                <div class="flex items-center gap-0.5">
                  <el-button
                    size="small"
                    circle
                    :disabled="item.index === 0"
                    @click="movePrompt(item.index, 'up')"
                  >
                    <el-icon><Top /></el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    :disabled="item.index === orderedPromptList.length - 1"
                    @click="movePrompt(item.index, 'down')"
                  >
                    <el-icon><Bottom /></el-icon>
                  </el-button>
                </div>

                <!-- 编辑详情按钮 -->
                <el-button
                  size="small"
                  circle
                  type="primary"
                  plain
                  @click="openEditDialog(item)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>

                <!-- 启用开关 -->
                <el-switch
                  :model-value="item.enabled"
                  size="small"
                  active-color="#e6a23c"
                  @change="toggleItemEnabled(item.identifier)"
                />
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 2: 大模型生成与物理采样超参数设置 -->
        <el-tab-pane name="generation" class="h-full flex flex-col gap-4 overflow-y-auto pr-1">
          <template #label>
            <span class="flex items-center gap-1.5 font-medium">
              <el-icon><Cpu /></el-icon>
              大模型物理采样设置
            </span>
          </template>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <!-- 概率分布与采样惩罚 -->
            <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] flex flex-col gap-4">
              <div class="flex items-center gap-2 pb-2 border-b border-[var(--el-border-color-lighter)]">
                <el-icon class="text-amber-500"><Compass /></el-icon>
                <h3 class="text-sm font-bold text-[var(--el-text-color-primary)]">概率分布与核采样</h3>
              </div>

              <el-form label-position="top" size="default">
                <el-form-item label="Temperature (采样温度 / 随机性)">
                  <div class="flex items-center gap-4 w-full">
                    <el-slider v-model="preset.temperature" :min="0" :max="2.0" :step="0.01" class="flex-1" />
                    <el-input-number v-model="preset.temperature" :min="0" :max="2.0" :step="0.01" class="!w-28" />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">较低更具确定性和逻辑自洽，较高更有创意与文笔发散度。推荐值: 0.7 ~ 1.1</span>
                </el-form-item>

                <el-form-item label="Top P (核采样概率累积阈值)">
                  <div class="flex items-center gap-4 w-full">
                    <el-slider v-model="preset.top_p" :min="0" :max="1.0" :step="0.01" class="flex-1" />
                    <el-input-number v-model="preset.top_p" :min="0" :max="1.0" :step="0.01" class="!w-28" />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">动态只在累积概率排名前 P 的高概率词元中采样。推荐值: 0.9 ~ 1.0</span>
                </el-form-item>

                <el-form-item label="Frequency Penalty (词频惩罚)">
                  <div class="flex items-center gap-4 w-full">
                    <el-slider v-model="preset.frequency_penalty" :min="-2.0" :max="2.0" :step="0.05" class="flex-1" />
                    <el-input-number v-model="preset.frequency_penalty" :min="-2.0" :max="2.0" :step="0.05" class="!w-28" />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">正值基于已出现词元的频率降低重复率，遏制反复使用相同短语。推荐值: 0.0 ~ 0.5</span>
                </el-form-item>

                <el-form-item label="Presence Penalty (存在惩罚)">
                  <div class="flex items-center gap-4 w-full">
                    <el-slider v-model="preset.presence_penalty" :min="-2.0" :max="2.0" :step="0.05" class="flex-1" />
                    <el-input-number v-model="preset.presence_penalty" :min="-2.0" :max="2.0" :step="0.05" class="!w-28" />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">正值鼓励模型在多轮对话中引入全新主题与话题拓展。推荐值: 0.0 ~ 0.4</span>
                </el-form-item>
              </el-form>
            </div>

            <!-- 上下文容量与思维链模式 -->
            <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] flex flex-col gap-4">
              <div class="flex items-center gap-2 pb-2 border-b border-[var(--el-border-color-lighter)]">
                <el-icon class="text-blue-500"><Setting /></el-icon>
                <h3 class="text-sm font-bold text-[var(--el-text-color-primary)]">Token 容量与模型控制</h3>
              </div>

              <el-form label-position="top" size="default">
                <el-form-item label="Max Output Tokens (单次最大生成限制)">
                  <div class="flex items-center gap-4 w-full">
                    <el-slider v-model="preset.openai_max_tokens" :min="100" :max="32000" :step="100" class="flex-1" />
                    <el-input-number v-model="preset.openai_max_tokens" :min="100" :max="32000" :step="100" class="!w-28" />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">限制大模型单次交互允许输出的最长 Token 上限。</span>
                </el-form-item>

                <el-form-item label="Max Context Window (上下文总预算)">
                  <div class="flex items-center gap-4 w-full">
                    <el-slider v-model="preset.openai_max_context" :min="2000" :max="2000000" :step="1000" class="flex-1" />
                    <el-input-number v-model="preset.openai_max_context" :min="2000" :max="2000000" :step="1000" class="!w-32" />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">滑动窗口保留的上下文历史总 Token 预算。</span>
                </el-form-item>

                <el-form-item label="Reasoning Effort (思维链推理强度 / 思考时间)">
                  <el-radio-group v-model="preset.reasoning_effort" class="w-full">
                    <el-radio-button value="low">低强度 (快速响应)</el-radio-button>
                    <el-radio-button value="medium">中等强度 (平衡)</el-radio-button>
                    <el-radio-button value="high">高强度 (深度规划)</el-radio-button>
                    <el-radio-button value="auto">自动适配 (Auto)</el-radio-button>
                  </el-radio-group>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)] mt-1">控制 o1 / DeepSeek-R1 / QwQ 等具备 Thinking 机制模型的推理字数。</span>
                </el-form-item>

                <el-form-item label="Seed (随机数发生器种子)">
                  <el-input-number v-model="preset.seed" :min="-1" :max="99999999" class="!w-44" />
                  <span class="text-[11px] text-[var(--el-text-color-secondary)] ml-3">设为 -1 表示完全随机，固定正整数用于复现特定生成轨迹。</span>
                </el-form-item>

                <div class="flex items-center justify-between p-3 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)] mt-2">
                  <div class="flex flex-col">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">SSE 流式打字机加速输出</span>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">开启 60fps 实时渐进式流式上屏体验</span>
                  </div>
                  <el-switch v-model="preset.stream_openai" active-color="#67c23a" />
                </div>
              </el-form>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 3: 自主导入预设库大盘管理 -->
        <el-tab-pane name="history" class="h-full flex flex-col gap-3 overflow-hidden">
          <template #label>
            <span class="flex items-center gap-1.5 font-medium">
              <el-icon><FolderOpened /></el-icon>
              预设库管理 ({{ presetLibrary.length }} 套)
            </span>
          </template>

          <el-table :data="presetLibrary" v-loading="isLoadingVersions" stripe border class="w-full flex-1">
            <el-table-column prop="preset_name" label="预设名称" min-width="180">
              <template #default="{ row }">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="font-bold text-xs text-[var(--el-text-color-primary)]">{{ row.preset_name }}</span>
                  <el-tag v-if="row.id === currentPresetId" type="warning" size="small" effect="plain">当前查看中</el-tag>
                  <el-tag v-if="row.is_active" type="success" size="small" effect="dark">全平台生效中</el-tag>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="prompts_count" label="流水线提示词" width="130" align="center">
              <template #default="{ row }">
                <span class="font-mono font-bold text-amber-500">{{ row.active_prompts_count }}</span>
                <span class="text-xs text-gray-400"> / {{ row.prompts_count }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="regex_count" label="正则脚本" width="100" align="center">
              <template #default="{ row }">
                <span class="font-mono text-blue-500">{{ row.regex_count || 0 }} 项</span>
              </template>
            </el-table-column>
            <el-table-column prop="temperature" label="采样温度" width="90" align="center" />
            <el-table-column prop="top_p" label="Top-P" width="90" align="center" />
            <el-table-column prop="updated_by" label="最后修改人" width="110" />
            <el-table-column prop="updated_at" label="最后更新时间" min-width="160">
              <template #default="{ row }">
                {{ row.updated_at || '出厂初始预置' }}
              </template>
            </el-table-column>
            <el-table-column label="快捷操作" min-width="260" fixed="right">
              <template #default="{ row }">
                <div class="flex items-center gap-1.5">
                  <el-button
                    size="small"
                    :type="row.id === currentPresetId ? 'warning' : 'default'"
                    plain
                    @click="handleSwitchPreset(row.id)"
                  >
                    {{ row.id === currentPresetId ? '查看中' : '载入编辑' }}
                  </el-button>
                  <el-button
                    size="small"
                    type="success"
                    plain
                    :disabled="row.is_active"
                    @click="handleActivateRowPreset(row as any)"
                  >
                    设为生效
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    @click="handleExportPresetById(row.id)"
                    title="导出此预设 JSON"
                  >
                    <el-icon><Download /></el-icon>
                  </el-button>
                  <el-button
                    size="small"
                    circle
                    type="danger"
                    plain
                    :disabled="row.is_active || presetLibrary.length <= 1"
                    @click="handleDeleteRowPreset(row as any)"
                    title="删除预设"
                  >
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- Tab 4: 预设正则脚本引擎 (1:1 对齐酒馆预设正则) -->
        <el-tab-pane name="regex" class="h-full flex flex-col gap-3 overflow-hidden">
          <template #label>
            <span class="flex items-center gap-1.5 font-medium">
              <el-icon><Filter /></el-icon>
              预设正则脚本 ({{ (preset.regex_scripts || []).length }} 项)
            </span>
          </template>

          <!-- 工具栏 -->
          <div class="flex flex-wrap items-center justify-between gap-3 pb-2 border-b border-[var(--el-border-color-lighter)]">
            <div class="flex flex-wrap items-center gap-2">
              <el-button type="primary" size="small" @click="openCreateRegexDialog">
                <el-icon class="mr-1"><Plus /></el-icon> 新建预设正则
              </el-button>

              <el-upload
                :show-file-list="false"
                :auto-upload="false"
                accept=".json"
                :on-change="handleImportRegexOnlyFile"
              >
                <el-button size="small">
                  <el-icon class="mr-1"><Upload /></el-icon> 导入正则
                </el-button>
              </el-upload>

              <el-button size="small" @click="handleExportRegexOnly">
                <el-icon class="mr-1"><Download /></el-icon> 导出正则
              </el-button>

              <el-button
                size="small"
                :type="isRegexSandboxOpen ? 'warning' : 'default'"
                plain
                @click="isRegexSandboxOpen = !isRegexSandboxOpen"
              >
                <el-icon class="mr-1"><MagicStick /></el-icon>
                {{ isRegexSandboxOpen ? '收起调试沙盒' : '全流程调试沙盒' }}
              </el-button>
            </div>

            <div class="flex items-center gap-2">
              <el-input
                v-model="regexSearchKeyword"
                placeholder="搜索正则名称或匹配模式..."
                clearable
                class="!w-64"
                size="small"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>

          <!-- 全流程实时调试沙盒 -->
          <div
            v-if="isRegexSandboxOpen"
            class="flex flex-col gap-2 p-3 rounded-xl border border-amber-500/30 bg-amber-500/5 transition-all animate-fade-in"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-bold text-amber-600 dark:text-amber-400 flex items-center gap-1.5">
                <el-icon><MagicStick /></el-icon>
                多重正则串联执行沙盒 (实时模拟 LLM 流水线清洗)
              </span>
              <div class="flex items-center gap-2">
                <span class="text-xs text-[var(--el-text-color-secondary)]">模拟时机:</span>
                <el-radio-group v-model="sandboxPlacement" size="small">
                  <el-radio-button :value="1">Placement 1 (用户输入/Prompt)</el-radio-button>
                  <el-radio-button :value="2">Placement 2 (AI 输出清洗)</el-radio-button>
                </el-radio-group>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
              <div class="flex flex-col gap-1">
                <span class="text-[11px] text-[var(--el-text-color-regular)]">原始待测文本：</span>
                <el-input
                  v-model="sandboxInputText"
                  type="textarea"
                  :rows="3"
                  placeholder="在此输入包含八股词汇、特殊标签或破折号的文本..."
                  font-mono
                />
              </div>
              <div class="flex flex-col gap-1">
                <span class="text-[11px] text-[var(--el-text-color-regular)]">清洗后输出效果：</span>
                <div class="w-full h-18 p-2 rounded border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] overflow-y-auto font-mono text-xs text-[var(--el-text-color-primary)] whitespace-pre-wrap select-text">
                  {{ sandboxOutputText }}
                </div>
              </div>
            </div>
          </div>

          <!-- 正则脚本卡片列表 -->
          <div class="flex-1 overflow-y-auto pr-1 flex flex-col gap-2">
            <div
              v-if="filteredRegexScripts.length === 0"
              class="flex flex-col items-center justify-center py-16 text-gray-400 gap-2"
            >
              <el-icon class="text-4xl opacity-50"><Filter /></el-icon>
              <span>暂无匹配的正则脚本，可点击上方「新建预设正则」或「导入预设 JSON」</span>
            </div>

            <div
              v-for="(script, idx) in filteredRegexScripts"
              :key="script.id"
              class="flex items-center justify-between p-3 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] hover:border-amber-500/40 hover:shadow-sm transition-all"
            >
              <!-- 左侧: 顺序调整 + 启用开关 + 脚本信息 -->
              <div class="flex items-center gap-3 flex-1 min-w-0 pr-4">
                <!-- 上下移动按钮 -->
                <div class="flex flex-col gap-0.5">
                  <button
                    type="button"
                    @click="moveRegex(idx, 'up')"
                    :disabled="idx === 0"
                    class="p-0.5 text-xs text-gray-400 hover:text-amber-500 disabled:opacity-20 cursor-pointer"
                    title="上移"
                  >
                    <el-icon><ArrowUp /></el-icon>
                  </button>
                  <button
                    type="button"
                    @click="moveRegex(idx, 'down')"
                    :disabled="idx === (preset.regex_scripts?.length || 0) - 1"
                    class="p-0.5 text-xs text-gray-400 hover:text-amber-500 disabled:opacity-20 cursor-pointer"
                    title="下移"
                  >
                    <el-icon><ArrowDown /></el-icon>
                  </button>
                </div>

                <!-- 启用/禁用 Switch -->
                <el-switch
                  :model-value="!script.disabled"
                  size="small"
                  active-color="#e6a23c"
                  @change="(val: boolean) => toggleRegexDisabled(script.id, !val)"
                />

                <!-- 脚本名称与元信息 -->
                <div class="flex flex-col min-w-0 flex-1">
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="font-bold text-xs text-[var(--el-text-color-primary)]">
                      {{ script.scriptName }}
                    </span>

                    <!-- 作用域标签 -->
                    <el-tag
                      v-if="script.placement.includes(1)"
                      size="small"
                      type="success"
                      effect="light"
                      class="!text-[10px]"
                    >
                      用户输入
                    </el-tag>
                    <el-tag
                      v-if="script.placement.includes(2)"
                      size="small"
                      type="primary"
                      effect="light"
                      class="!text-[10px]"
                    >
                      AI 输出清洗
                    </el-tag>
                    <el-tag
                      v-if="script.placement.includes(3)"
                      size="small"
                      type="info"
                      effect="plain"
                      class="!text-[10px]"
                    >
                      快捷命令
                    </el-tag>
                    <el-tag
                      v-if="script.placement.includes(4)"
                      size="small"
                      type="warning"
                      effect="plain"
                      class="!text-[10px]"
                    >
                      世界书
                    </el-tag>
                    <el-tag
                      v-if="script.placement.includes(5)"
                      size="small"
                      type="danger"
                      effect="plain"
                      class="!text-[10px]"
                    >
                      推理
                    </el-tag>

                    <!-- 深度范围 -->
                    <el-tag
                      v-if="script.maxDepth !== null && script.maxDepth !== undefined"
                      size="small"
                      type="warning"
                      effect="plain"
                      class="!text-[10px] font-mono"
                    >
                      深度 ≤ {{ script.maxDepth }}
                    </el-tag>
                    <el-tag
                      v-if="script.minDepth !== null && script.minDepth !== undefined"
                      size="small"
                      type="warning"
                      effect="plain"
                      class="!text-[10px] font-mono"
                    >
                      深度 ≥ {{ script.minDepth }}
                    </el-tag>
                  </div>

                  <!-- 表达式与替换预览 -->
                  <div class="flex items-center gap-2 text-xs font-mono text-[var(--el-text-color-secondary)] truncate mt-1">
                    <span class="bg-[var(--el-fill-color-light)] px-1.5 py-0.5 rounded truncate max-w-md">
                      {{ script.findRegex }}
                    </span>
                    <span>➔</span>
                    <span class="bg-[var(--el-fill-color-light)] px-1.5 py-0.5 rounded truncate max-w-xs text-amber-600 dark:text-amber-400">
                      {{ script.replaceString ? script.replaceString : '(抹除匹配内容)' }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 右侧动作: 编辑、删除 -->
              <div class="flex items-center gap-2">
                <el-button size="small" circle @click="openEditRegexDialog(script)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" circle type="danger" plain @click="deleteRegexScript(script.id)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>

        <!-- Tab 5: 高级格式化调优 (1:1 借鉴酒馆高级格式化体系) -->
        <el-tab-pane name="advanced" class="h-full flex flex-col gap-4 overflow-y-auto pr-1">
          <template #label>
            <span class="flex items-center gap-1.5 font-medium">
              <el-icon><Tools /></el-icon>
              高级格式化调优
            </span>
          </template>

          <div v-if="preset.advanced_formatting" class="grid grid-cols-1 lg:grid-cols-2 gap-4 pb-4">
            <!-- 1. 深度思考链 (Reasoning & CoT) 治理卡片 -->
            <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] flex flex-col gap-4">
              <div class="flex items-center justify-between pb-2 border-b border-[var(--el-border-color-lighter)]">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-500">
                    🧠
                  </div>
                  <div class="flex flex-col">
                    <h3 class="text-sm font-bold text-[var(--el-text-color-primary)]">
                      推理与思维链 (Reasoning & CoT) 治理
                    </h3>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      DeepSeek-R1 / OpenAI o1 / QwQ 等思考模型的流式解耦与上下文节省
                    </span>
                  </div>
                </div>
                <el-tag size="small" type="success" effect="plain" class="!text-[10px]">
                  P0 核心必备
                </el-tag>
              </div>

              <div class="flex flex-col gap-4">
                <!-- 自动解析 <think> -->
                <div class="flex items-center justify-between p-3 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                  <div class="flex flex-col">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      自动解析 & 剥离 &lt;think&gt; 思考标签
                    </span>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      流式生成时实时分离思考过程与正文回复，消息正文只保留纯粹角色台词
                    </span>
                  </div>
                  <el-switch
                    v-model="preset.advanced_formatting.parse_think_tags"
                    active-color="#67c23a"
                  />
                </div>

                <!-- 回传历史思考链轮数限制 -->
                <div class="flex flex-col gap-1 p-3 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      回传给后续提示词的思维链条数 (Reasoning History Depth)
                    </span>
                    <el-tag
                      size="small"
                      :type="preset.advanced_formatting.reasoning_history_depth === 0 ? 'success' : 'warning'"
                      effect="plain"
                      class="!text-[10px] font-mono"
                    >
                      {{ preset.advanced_formatting.reasoning_history_depth === 0 ? '完全不回传 (推荐)' : `保留最近 ${preset.advanced_formatting.reasoning_history_depth} 条` }}
                    </el-tag>
                  </div>
                  <div class="flex items-center gap-4 w-full mt-1">
                    <el-slider
                      v-model="preset.advanced_formatting.reasoning_history_depth"
                      :min="0"
                      :max="10"
                      :step="1"
                      class="flex-1"
                    />
                    <el-input-number
                      v-model="preset.advanced_formatting.reasoning_history_depth"
                      :min="0"
                      :max="10"
                      class="!w-24"
                      size="small"
                    />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)] mt-1">
                    💡 设为 0 可在多轮对话中自动剔除往期数千 Token 的巨大思考链，节省 80%+ 提示词费用并防止 AI 产生逻辑自锁。
                  </span>
                </div>

                <!-- 前端默认展开思维链 -->
                <div class="flex items-center justify-between p-3 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                  <div class="flex flex-col">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      前端气泡默认自动展开思维链 (Auto Expand)
                    </span>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      关闭时气泡将收拢为优雅折叠手风琴，并显示深度思考耗时
                    </span>
                  </div>
                  <el-switch
                    v-model="preset.advanced_formatting.auto_expand_reasoning"
                    active-color="#e6a23c"
                  />
                </div>
              </div>
            </div>

            <!-- 2. 历史后置强化指令 (Post-History Instruction) 卡片 -->
            <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] flex flex-col gap-4">
              <div class="flex items-center justify-between pb-2 border-b border-[var(--el-border-color-lighter)]">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-500">
                    📌
                  </div>
                  <div class="flex flex-col">
                    <h3 class="text-sm font-bold text-[var(--el-text-color-primary)]">
                      长文本历史后置指令 (Post-History Instruction)
                    </h3>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      利用注意力机制近因效应 (Recency Bias)，在会话末端再次强化角色语气与人设规则
                    </span>
                  </div>
                </div>
                <el-switch
                  v-model="preset.advanced_formatting.enable_post_history_instruction"
                  active-color="#67c23a"
                />
              </div>

              <div
                class="flex flex-col gap-3 transition-opacity"
                :class="{ 'opacity-50 pointer-events-none': !preset.advanced_formatting.enable_post_history_instruction }"
              >
                <!-- 注入深度 -->
                <div class="flex flex-col gap-1">
                  <div class="flex items-center justify-between">
                    <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      指令注入深度 (Injection Depth)
                    </label>
                    <span class="text-[11px] font-mono text-amber-500">
                      {{ preset.advanced_formatting.post_history_depth === 0 ? '绝对底部 (最后一条消息之后)' : `倒数第 ${preset.advanced_formatting.post_history_depth} 条消息之前` }}
                    </span>
                  </div>
                  <div class="flex items-center gap-4 w-full">
                    <el-slider
                      v-model="preset.advanced_formatting.post_history_depth"
                      :min="0"
                      :max="10"
                      :step="1"
                      class="flex-1"
                    />
                    <el-input-number
                      v-model="preset.advanced_formatting.post_history_depth"
                      :min="0"
                      :max="10"
                      class="!w-24"
                      size="small"
                    />
                  </div>
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                    深度 0 会作为最后一条 System 消息追加至 Prompt 末尾，对模型后续回答具有最强烈的直接约束力。
                  </span>
                </div>

                <!-- 后置指令模板内容 -->
                <div class="flex flex-col gap-1.5">
                  <div class="flex items-center justify-between">
                    <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      后置强化提示词正文
                    </label>
                    <span class="text-[11px] font-mono text-[var(--el-text-color-secondary)]">
                      {{ preset.advanced_formatting.post_history_instruction?.length || 0 }} 字符
                    </span>
                  </div>
                  <el-input
                    v-model="preset.advanced_formatting.post_history_instruction"
                    type="textarea"
                    :rows="4"
                    font-mono
                    placeholder="例如: [System: 请始终保持 {{char}} 的独特语气与人设性格，严禁代替玩家做出决定或发言，以沉浸式描写推进剧情]"
                  />
                  <!-- 快捷宏按钮 -->
                  <div class="flex items-center gap-1.5 flex-wrap pt-0.5">
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">快捷宏变量:</span>
                    <button
                      v-for="macro in ['{{char}}', '{{user}}', '{{scenario}}', '{{location}}']"
                      :key="macro"
                      type="button"
                      @click="insertMacroIntoPostHistory(macro)"
                      class="text-[11px] font-mono px-1.5 py-0.5 rounded border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)] hover:border-amber-500 hover:text-amber-500 cursor-pointer transition-colors"
                    >
                      {{ macro }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 3. 自定义终止词安全防护 (Stop Sequences) 卡片 -->
            <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] flex flex-col gap-4">
              <div class="flex items-center justify-between pb-2 border-b border-[var(--el-border-color-lighter)]">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-500">
                    🛑
                  </div>
                  <div class="flex flex-col">
                    <h3 class="text-sm font-bold text-[var(--el-text-color-primary)]">
                      自定义终止词防护 (Stop Sequences 安全兜底)
                    </h3>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      透传至底层的 stop 数组，模型输出目标字符串时立即强制截断，彻底防止自问自答
                    </span>
                  </div>
                </div>
                <el-tag size="small" type="danger" effect="plain" class="!text-[10px]">
                  防自言自语
                </el-tag>
              </div>

              <div class="flex flex-col gap-3">
                <!-- 快捷角色名/用户名作为终止词 -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  <div class="flex items-center justify-between p-2.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                    <div class="flex flex-col">
                      <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">角色名作终止词</span>
                      <span class="text-[10px] text-[var(--el-text-color-secondary)]">防模型自我重复发言</span>
                    </div>
                    <el-switch v-model="preset.advanced_formatting.char_name_as_stop" size="small" active-color="#67c23a" />
                  </div>

                  <div class="flex items-center justify-between p-2.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                    <div class="flex flex-col">
                      <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">用户名作终止词</span>
                      <span class="text-[10px] text-[var(--el-text-color-secondary)]">防伪造玩家发言自问自答</span>
                    </div>
                    <el-switch v-model="preset.advanced_formatting.user_name_as_stop" size="small" active-color="#67c23a" />
                  </div>
                </div>

                <!-- 自定义终止词标签展示与添加 -->
                <div class="flex flex-col gap-2">
                  <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                    自定义终止字符串列表 (Stop Tokens)
                  </label>

                  <div class="flex flex-wrap items-center gap-1.5 min-h-8 p-2 rounded-lg border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)]/50">
                    <span v-if="(preset.advanced_formatting.stop_sequences || []).length === 0" class="text-xs text-gray-400">
                      暂无自定义终止词，可在下方输入添加（如 \nUser: 或 &lt;|eot_id|&gt;）
                    </span>
                    <el-tag
                      v-for="(seq, sIdx) in preset.advanced_formatting.stop_sequences"
                      :key="seq"
                      closable
                      size="small"
                      effect="dark"
                      type="danger"
                      class="font-mono !text-xs"
                      @close="removeStopSequence(sIdx)"
                    >
                      {{ seq }}
                    </el-tag>
                  </div>

                  <!-- 添加输入框 -->
                  <div class="flex items-center gap-2">
                    <el-input
                      v-model="newStopSequenceInput"
                      placeholder="输入终止字符串 (支持转义字符如 \nUser:) 并按回车添加..."
                      size="small"
                      font-mono
                      clearable
                      @keyup.enter="addStopSequence"
                    />
                    <el-button size="small" type="primary" plain @click="addStopSequence">
                      <el-icon class="mr-1"><Plus /></el-icon> 添加
                    </el-button>
                  </div>

                  <!-- 常用推荐快捷按钮 -->
                  <div class="flex items-center gap-1.5 flex-wrap pt-0.5">
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">推荐常用词:</span>
                    <button
                      v-for="rec in ['\\nUser:', '\\n[用户]:', '\\n[玩家]:', '<|eot_id|>', '<|im_end|>', '### Instruction']"
                      :key="rec"
                      type="button"
                      @click="() => { newStopSequenceInput = rec; addStopSequence(); }"
                      class="text-[10px] font-mono px-1.5 py-0.5 rounded border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] hover:border-red-500 hover:text-red-500 cursor-pointer transition-colors"
                    >
                      {{ rec }}
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 4. 文本清洗流水线 (Text Cleaning) 与回复引导卡片 -->
            <div class="p-4 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] flex flex-col gap-4">
              <div class="flex items-center justify-between pb-2 border-b border-[var(--el-border-color-lighter)]">
                <div class="flex items-center gap-2">
                  <div class="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-500">
                    🧹
                  </div>
                  <div class="flex flex-col">
                    <h3 class="text-sm font-bold text-[var(--el-text-color-primary)]">
                      输出文本清洗流水线与回复前缀引导
                    </h3>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      排版美化、断句修剪与 Assistant Prefill 强制文风引导
                    </span>
                  </div>
                </div>
                <el-tag size="small" type="success" effect="plain" class="!text-[10px]">
                  观感增强
                </el-tag>
              </div>

              <div class="flex flex-col gap-3">
                <!-- 折叠连续换行符 -->
                <div class="flex items-center justify-between p-2.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                  <div class="flex flex-col">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      折叠连续多余换行符 (Collapse Newlines)
                    </span>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      将 3 个及以上连续空行自动收敛为标准双换行，杜绝大段空白跳行
                    </span>
                  </div>
                  <el-switch v-model="preset.advanced_formatting.collapse_newlines" size="small" active-color="#67c23a" />
                </div>

                <!-- 修剪未闭合的不完整句子 -->
                <div class="flex items-center justify-between p-2.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                  <div class="flex flex-col">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      修剪不完整断句 (Trim Incomplete Sentences)
                    </span>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      因 max_tokens 物理截断断在半截话时，自动修剪回退至末尾最后一个完整标点
                    </span>
                  </div>
                  <el-switch v-model="preset.advanced_formatting.trim_incomplete_sentences" size="small" active-color="#67c23a" />
                </div>

                <!-- 修剪首尾空白 -->
                <div class="flex items-center justify-between p-2.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                  <div class="flex flex-col">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      修剪首尾多余空白 (Trim Whitespace)
                    </span>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                      自动剔除生成结果前后的多余空格与空行
                    </span>
                  </div>
                  <el-switch v-model="preset.advanced_formatting.trim_whitespace" size="small" active-color="#67c23a" />
                </div>

                <!-- Assistant Prefill 回复前缀引导 -->
                <div class="flex flex-col gap-1.5 p-3 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">
                      以...开始回复 (Assistant Prefill 引导词)
                    </span>
                    <div class="flex items-center gap-1.5">
                      <span class="text-[11px] text-[var(--el-text-color-secondary)]">在气泡中显示:</span>
                      <el-switch v-model="preset.advanced_formatting.show_reply_prefix" size="small" active-color="#67c23a" />
                    </div>
                  </div>
                  <el-input
                    v-model="preset.advanced_formatting.reply_prefix"
                    placeholder="例如: * 或 【动作】： 或特定口头禅"
                    size="small"
                    font-mono
                    clearable
                  />
                  <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                    预填助手首个字符（如输入星号 * 引导 AI 强制进入动作神态旁白描写，极大增强小说沉浸感）。
                  </span>
                </div>
              </div>
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 3. 条目编辑详情模态框 -->
    <!-- 3. 条目编辑详情模态框 (1:1 像素级对齐 SillyTavern 原生条目编辑器) -->
    <el-dialog
      v-model="isEditOpen"
      title="编辑"
      width="820px"
      append-to-body
      destroy-on-close
      class="st-item-edit-dialog"
    >
      <div v-if="editingItem" class="flex flex-col gap-4 text-xs select-none">
        <!-- 上部网格：左侧(姓名、身份、位置、深度) + 右侧(触发器) -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
          <!-- 左侧两列：姓名、身份、位置 -->
          <div class="md:col-span-2 flex flex-col gap-3">
            <!-- 1. 姓名 -->
            <div class="flex flex-col gap-1">
              <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">姓名</label>
              <el-input
                v-model="editingItem.name"
                placeholder="输入提示词名称..."
                clearable
              />
              <span class="text-[11px] text-[var(--el-text-color-secondary)]">此提示词的名称。</span>
            </div>

            <!-- 2. 身份 -->
            <div class="flex flex-col gap-1">
              <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">身份</label>
              <el-select v-model="editingItem.role" class="w-full">
                <el-option label="系统" value="system" />
                <el-option label="用户" value="user" />
                <el-option label="助手" value="assistant" />
              </el-select>
              <span class="text-[11px] text-[var(--el-text-color-secondary)]">此消息应归于谁。</span>
            </div>

            <!-- 3. 位置 -->
            <div class="flex flex-col gap-1">
              <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">位置</label>
              <el-select v-model="editingItem.injection_position" class="w-full">
                <el-option label="相对" :value="0" />
                <el-option label="聊天中" :value="1" />
              </el-select>
              <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                相对（相对于提示词管理器中的其他提示词）或在聊天中的指定深度。
              </span>
            </div>

            <!-- 4. 深度 (仅在位置为“聊天中”时动态展开) -->
            <div
              v-if="editingItem.injection_position === 1"
              class="flex flex-col gap-1 p-2.5 rounded-lg border border-amber-500/40 bg-amber-500/5 transition-all animate-fade-in"
            >
              <label class="text-xs font-semibold text-amber-500 flex items-center justify-between">
                <span>深度 (Depth)</span>
                <span class="text-[11px] font-mono text-amber-600">当前: {{ editingItem.injection_depth }}</span>
              </label>
              <el-input-number
                v-model="editingItem.injection_depth"
                :min="0"
                :max="99"
                class="!w-full"
              />
              <span class="text-[11px] text-[var(--el-text-color-secondary)]">相对于最后一条消息的深度。</span>
            </div>
          </div>

          <!-- 右侧专区：触发器 (Triggers) -->
          <div class="flex flex-col gap-2 p-3 rounded-xl border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-light)]/40">
            <div class="flex flex-col gap-0.5 pb-2 border-b border-[var(--el-border-color-lighter)]">
              <div class="flex items-center justify-between">
                <label class="text-xs font-bold text-[var(--el-text-color-primary)]">触发器</label>
                <el-tag size="small" :type="isAllTriggers ? 'info' : 'warning'" effect="plain" class="!text-[10px]">
                  {{ isAllTriggers ? '所有类型（默认）' : `已选 ${editingItem.injection_trigger?.length || 0} 项` }}
                </el-tag>
              </div>
              <span class="text-[11px] text-[var(--el-text-color-secondary)]">筛选到特定的生成类型。</span>
            </div>

            <!-- 6 大触发类型复选框 -->
            <div class="flex flex-col gap-1 pt-1">
              <el-checkbox
                v-for="trig in triggerOptions"
                :key="trig.key"
                :model-value="hasTrigger(trig.key)"
                @change="(val: boolean) => toggleTrigger(trig.key, val)"
                class="!m-0 !h-6"
              >
                <span class="text-xs text-[var(--el-text-color-regular)]">{{ trig.label }}</span>
              </el-checkbox>
            </div>
          </div>
        </div>

        <!-- 提示词大文本区 -->
        <div class="flex flex-col gap-1.5 pt-2">
          <div class="flex items-center justify-between">
            <label class="text-xs font-semibold text-[var(--el-text-color-primary)]">提示词</label>
            <span class="text-[11px] font-mono text-[var(--el-text-color-secondary)]">
              预估 {{ Math.round((editingItem.content?.length || 0) * 0.7) }} tokens ({{ editingItem.content?.length || 0 }} 字符)
            </span>
          </div>
          <el-input
            v-model="editingItem.content"
            type="textarea"
            :rows="13"
            font-mono
            placeholder="输入提示词正文..."
          />
          <!-- 快捷宏变量工具行 -->
          <div class="flex items-center justify-between pt-1">
            <div class="flex items-center gap-1.5 flex-wrap">
              <span class="text-[11px] text-[var(--el-text-color-secondary)]">快捷宏变量:</span>
              <button
                v-for="macro in ['{{char}}', '{{user}}', '{{scenario}}', '{{location}}', '{{time}}', '{{trim}}']"
                :key="macro"
                type="button"
                @click="insertMacro(macro)"
                class="text-[11px] font-mono px-1.5 py-0.5 rounded border border-[var(--el-border-color-lighter)] bg-[var(--el-fill-color-blank)] hover:border-amber-500 hover:text-amber-500 cursor-pointer transition-colors"
              >
                {{ macro }}
              </button>
            </div>
            <span v-if="editingItem.identifier" class="text-[11px] font-mono text-[var(--el-text-color-secondary)]">
              ID: {{ editingItem.identifier }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-between w-full">
          <!-- 左侧: 功能按钮 (还原默认) -->
          <div class="flex items-center gap-2">
            <el-tooltip content="仅将当前条目恢复为官方出厂「仓鼠之神V2」初始设置与正文" placement="top">
              <el-button
                type="warning"
                plain
                @click="resetCurrentItemToDefault"
                class="!px-4"
                :disabled="!factoryDefaultPreset"
              >
                <el-icon class="mr-1"><RefreshLeft /></el-icon>
                还原条目默认
              </el-button>
            </el-tooltip>
          </div>

          <!-- 右侧: 主要动作按钮 (取消 / 保存) -->
          <div class="flex items-center gap-3">
            <el-button @click="isEditOpen = false" class="!px-4">
              <el-icon class="mr-1"><Close /></el-icon>
              取消
            </el-button>

            <el-button type="primary" @click="saveEditDialog" class="!px-5">
              <el-icon class="mr-1"><Check /></el-icon>
              保存条目
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 4. 正则表达式编辑模态框 (1:1 SillyTavern 原生) -->
    <RegexEditDialog
      v-model="isRegexEditOpen"
      :script="editingRegexScript"
      :factory-scripts="factoryDefaultPreset?.regex_scripts || []"
      @save="saveRegexDialog"
    />
  </div>
</template>

<script setup lang="ts">
/**
 * SillyTavern 全局调音中枢后台管理面板
 *
 * 规范遵循:
 * 1. 采用 Vue 3.5 Composition API + TypeScript 完整类型标注；
 * 2. 严格杜绝原生 alert/confirm，所有交互提示与确认统一采用 ElMessage 与 ElMessageBox；
 * 3. 样式全面使用 UnoCSS 原子类；
 * 4. 彻底解决全平台统一大模型生成设置与 78 项提示词排版流水线中枢化管控。
 */

import {
  type TavernPresetConfig,
  type TavernPresetListItem,
  type TavernPromptItem,
  type TavernRegexScript,
  activateAdminTavernPreset,
  createAdminTavernPreset,
  deleteAdminTavernPreset,
  getAdminTavernDefaultPreset,
  getAdminTavernPreset,
  getAdminTavernPresetById,
  listAdminTavernPresets,
  renameAdminTavernPreset,
  resetAdminTavernPreset,
  updateAdminTavernPreset,
  updateAdminTavernPresetById,
} from '@/api/tavern';
import {
  ArrowDown,
  ArrowUp,
  Bottom,
  Check,
  Clock,
  Close,
  Compass,
  Connection,
  CopyDocument,
  Cpu,
  Delete,
  Download,
  Edit,
  Filter,
  FolderOpened,
  MagicStick,
  Operation,
  Plus,
  Promotion,
  RefreshLeft,
  RefreshRight,
  Search,
  Setting,
  Tools,
  Top,
  Upload,
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import RegexEditDialog from './components/RegexEditDialog.vue';

const router = useRouter();

// 1. 当前活动 Tab
const activeMainTab = ref<'pipeline' | 'generation' | 'history' | 'regex' | 'advanced'>('pipeline');

// 2. 状态变量
const isSaving = ref(false);
const isActivating = ref(false);
const isResetting = ref(false);
const isLoadingVersions = ref(false);
const searchKeyword = ref('');
const filterType = ref<'all' | 'active' | 'marker' | 'inactive'>('all');

// 3. 预设核心数据与预设库状态
const presetLibrary = ref<TavernPresetListItem[]>([]);
const currentPresetId = ref<string>('');

const preset = ref<TavernPresetConfig>({
  preset_name: '仓鼠之神V2',
  is_active: true,
  temperature: 1.0,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
  top_p: 1.0,
  max_context_unlocked: true,
  openai_max_context: 2000000,
  openai_max_tokens: 32000,
  stream_openai: true,
  seed: -1,
  reasoning_effort: 'high',
  prompts: [],
  prompt_order: [],
  regex_scripts: [],
  advanced_formatting: {
    parse_think_tags: true,
    reasoning_history_depth: 0,
    auto_expand_reasoning: false,
    enable_post_history_instruction: false,
    post_history_instruction: '',
    post_history_depth: 0,
    stop_sequences: [],
    char_name_as_stop: false,
    user_name_as_stop: false,
    collapse_newlines: true,
    trim_incomplete_sentences: false,
    trim_whitespace: true,
    reply_prefix: '',
    show_reply_prefix: true,
  },
});

const versionList = ref<TavernPresetListItem[]>([]);

// 4. 编辑条目弹窗状态
const isEditOpen = ref(false);
const editingItem = ref<(TavernPromptItem & { index: number; isMarker: boolean }) | null>(null);

// 5. 正则脚本管理状态
const isRegexEditOpen = ref(false);
const editingRegexScript = ref<TavernRegexScript | null>(null);
const regexSearchKeyword = ref('');
const isRegexSandboxOpen = ref(false);
const sandboxPlacement = ref<1 | 2>(2);
const sandboxInputText = ref(
  '这是一个包含 <-begin-response->我将进行符合需求的创作： 标签与“难以察觉”八股词的测试。——破折号',
);

// 建立全量提示词查找表
const promptMap = computed(() => {
  const map = new Map<string, TavernPromptItem>();
  for (const p of preset.value.prompts) {
    map.set(p.identifier, p);
  }
  return map;
});

// 计算排序后的完整流水线列表
const orderedPromptList = computed(() => {
  const map = promptMap.value;
  const result: (TavernPromptItem & {
    index: number;
    enabled: boolean;
    isMarker: boolean;
    isUnorderedBackup?: boolean;
  })[] = [];

  const sourceOrder = preset.value.prompt_order || [];
  const orderedIdentifiers = new Set<string>();

  sourceOrder.forEach((orderItem, idx) => {
    orderedIdentifiers.add(orderItem.identifier);
    const p = map.get(orderItem.identifier);
    const rawName = p?.name?.trim();
    const name = rawName && rawName.length > 0 ? rawName : getFallbackName(orderItem.identifier);
    const role = p?.role || 'system';
    const isMarker = Boolean(p?.marker || isKnownMarker(orderItem.identifier));

    result.push({
      identifier: orderItem.identifier,
      index: idx,
      enabled: orderItem.enabled,
      name,
      role,
      content: p?.content || '',
      isMarker,
      system_prompt: p?.system_prompt ?? true,
      injection_position: p?.injection_position ?? 0,
      injection_depth: p?.injection_depth ?? 4,
      forbid_overrides: p?.forbid_overrides ?? false,
      injection_trigger: p?.injection_trigger ?? [],
      isUnorderedBackup: Boolean(orderItem.is_unordered_backup),
    });
  });

  // 双重防御：若 prompts 中有条目尚未包含在 prompt_order 中（如来自未归一化的历史数据），也作为备选追加展示
  const promptList = preset.value.prompts || [];
  promptList.forEach((p) => {
    if (!orderedIdentifiers.has(p.identifier)) {
      const rawName = p.name?.trim();
      const name = rawName && rawName.length > 0 ? rawName : getFallbackName(p.identifier);
      result.push({
        identifier: p.identifier,
        index: result.length,
        enabled: false,
        name,
        role: p.role || 'system',
        content: p.content || '',
        isMarker: Boolean(p.marker || isKnownMarker(p.identifier)),
        system_prompt: p.system_prompt ?? true,
        injection_position: p.injection_position ?? 0,
        injection_depth: p.injection_depth ?? 4,
        forbid_overrides: p.forbid_overrides ?? false,
        injection_trigger: p.injection_trigger ?? [],
        isUnorderedBackup: true,
      });
      orderedIdentifiers.add(p.identifier);
    }
  });

  return result;
});

// 过滤后的列表
const filteredPromptList = computed(() => {
  const list = orderedPromptList.value;
  const query = searchKeyword.value.trim().toLowerCase();

  return list.filter((item) => {
    if (filterType.value === 'active' && !item.enabled) return false;
    if (filterType.value === 'marker' && !item.isMarker) return false;
    if (filterType.value === 'inactive' && item.enabled) return false;

    if (query) {
      return item.name.toLowerCase().includes(query) || item.content?.toLowerCase().includes(query);
    }
    return true;
  });
});

// 统计量
const totalCount = computed(() => orderedPromptList.value.length);
const activeCount = computed(() => orderedPromptList.value.filter((o) => o.enabled).length);
const markerCount = computed(() => orderedPromptList.value.filter((o) => o.isMarker).length);

const totalTokensEstimate = computed(() => {
  let totalChars = 0;
  for (const o of orderedPromptList.value) {
    if (o.enabled && o.content) {
      totalChars += o.content.length;
    }
  }
  return Math.round(totalChars * 0.7);
});

// 判断已知内置插桩锚点
function isKnownMarker(ident: string): boolean {
  const idLower = ident.toLowerCase();
  return (
    idLower.includes('personadescription') ||
    idLower.includes('chardescription') ||
    idLower.includes('charpersonality') ||
    idLower.includes('worldinfobefore') ||
    idLower.includes('worldinfoafter') ||
    idLower.includes('scenario') ||
    idLower.includes('dialogueexamples') ||
    idLower.includes('chathistory')
  );
}

function getFallbackName(ident: string): string {
  if (ident === 'personaDescription') return 'Persona Description (用户人设)';
  if (ident === 'charDescription') return 'Char Description (角色基本设定)';
  if (ident === 'charPersonality') return 'Char Personality (角色性格特征)';
  if (ident === 'worldInfoBefore') return 'World Info Before (前置世界书)';
  if (ident === 'worldInfoAfter') return 'World Info After (后置世界书)';
  if (ident === 'scenario') return 'Scenario (情境开场)';
  if (ident === 'dialogueExamples') return 'Chat Examples (对话样例)';
  if (ident === 'chatHistory') return 'Chat History (上下文对话历史)';
  return '自定义提示词条目';
}

// 切换单项条目启用状态
function toggleItemEnabled(identifier: string): void {
  let orderTarget = preset.value.prompt_order.find((o) => o.identifier === identifier);
  if (!orderTarget) {
    orderTarget = {
      identifier,
      enabled: false,
      is_unordered_backup: true,
    };
    preset.value.prompt_order.push(orderTarget);
  }
  orderTarget.enabled = !orderTarget.enabled;

  const promptTarget = preset.value.prompts.find((p) => p.identifier === identifier);
  if (promptTarget) {
    promptTarget.enabled = !promptTarget.enabled;
  }
}

// 调整顺序
function movePrompt(index: number, direction: 'up' | 'down'): void {
  if (direction === 'up' && index <= 0) return;
  if (direction === 'down' && index >= preset.value.prompt_order.length - 1) return;

  const targetIndex = direction === 'up' ? index - 1 : index + 1;
  const list = [...preset.value.prompt_order];
  const temp = list[index];
  list[index] = list[targetIndex];
  list[targetIndex] = temp;
  preset.value.prompt_order = list;
}

// 触发器配置定义
const triggerOptions = [
  { key: 'normal', label: '正常' },
  { key: 'continue', label: '续写' },
  { key: 'impersonate', label: 'AI 帮答' },
  { key: 'swipe', label: '备选回复' },
  { key: 'regenerate', label: '重新生成' },
  { key: 'quiet', label: '静默' },
];

const isAllTriggers = computed(() => {
  if (!editingItem.value) return true;
  const list = editingItem.value.injection_trigger || [];
  return list.length === 0;
});

function hasTrigger(key: string): boolean {
  if (!editingItem.value) return false;
  const list = editingItem.value.injection_trigger || [];
  return list.includes(key);
}

function toggleTrigger(key: string, checked: boolean): void {
  if (!editingItem.value) return;
  if (!Array.isArray(editingItem.value.injection_trigger)) {
    editingItem.value.injection_trigger = [];
  }
  const set = new Set(editingItem.value.injection_trigger);
  if (checked) {
    set.add(key);
  } else {
    set.delete(key);
  }
  editingItem.value.injection_trigger = Array.from(set);
}

// 官方出厂默认预设基准（只读基准，用于单项快速还原）
const factoryDefaultPreset = ref<TavernPresetConfig | null>(null);

async function loadFactoryDefault(): Promise<void> {
  try {
    const res: any = await getAdminTavernDefaultPreset();
    const data = res?.data || res;
    if (data?.prompts) {
      factoryDefaultPreset.value = data;
    }
  } catch (err: any) {
    console.warn('获取出厂默认预设基准失败:', err);
  }
}

// 单项条目恢复出厂默认值
function resetCurrentItemToDefault(): void {
  if (!editingItem.value) return;
  if (!factoryDefaultPreset.value) {
    ElMessage.warning('出厂基准模板尚未加载完成，请稍候');
    return;
  }
  const defaultItem = factoryDefaultPreset.value.prompts.find(
    (p) => p.identifier === editingItem.value?.identifier,
  );
  if (!defaultItem) {
    ElMessage.warning(`条目「${editingItem.value.name}」在官方出厂库中无预置模板`);
    return;
  }

  editingItem.value.name = defaultItem.name;
  editingItem.value.role = defaultItem.role || 'system';
  editingItem.value.content = defaultItem.content || '';
  editingItem.value.injection_position = defaultItem.injection_position ?? 0;
  editingItem.value.injection_depth = defaultItem.injection_depth ?? 4;
  editingItem.value.injection_trigger = [...(defaultItem.injection_trigger || [])];
  editingItem.value.system_prompt = defaultItem.system_prompt ?? true;
  editingItem.value.forbid_overrides = defaultItem.forbid_overrides ?? false;

  ElMessage.success(`已将「${defaultItem.name}」恢复为官方出厂默认配置`);
}

// 打开编辑模态框
function openEditDialog(item: TavernPromptItem & { index: number; isMarker: boolean }): void {
  const cloned = JSON.parse(JSON.stringify(item));
  if (!Array.isArray(cloned.injection_trigger)) {
    cloned.injection_trigger = [];
  }
  editingItem.value = cloned;
  isEditOpen.value = true;
}

// 插入宏变量
function insertMacro(macro: string): void {
  if (!editingItem.value) return;
  editingItem.value.content = (editingItem.value.content || '') + ` ${macro} `;
}

// 保存单个条目修改
function saveEditDialog(): void {
  if (!editingItem.value) return;
  const targetId = editingItem.value.identifier;
  const idx = preset.value.prompts.findIndex((p) => p.identifier === targetId);
  if (idx !== -1) {
    preset.value.prompts[idx] = {
      ...preset.value.prompts[idx],
      name: editingItem.value.name,
      role: editingItem.value.role,
      content: editingItem.value.content,
      injection_depth: editingItem.value.injection_depth,
      injection_position: editingItem.value.injection_position,
      injection_trigger: editingItem.value.injection_trigger || [],
      forbid_overrides: editingItem.value.forbid_overrides,
    };
  } else {
    preset.value.prompts.push(JSON.parse(JSON.stringify(editingItem.value)));
  }
  isEditOpen.value = false;
  ElMessage.success(`条目「${editingItem.value.name}」修改已暂存`);
}

// 导出 JSON
function handleExportJson(): void {
  const exportData = {
    ...preset.value,
    extensions: {
      regex_scripts: preset.value.regex_scripts || [],
      advanced_formatting: preset.value.advanced_formatting,
      SPreset: {
        RegexBinding: {
          regexes: preset.value.regex_scripts || [],
        },
      },
    },
  };
  const jsonStr = JSON.stringify(exportData, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SillyTavern_Global_${preset.value.preset_name}.json`;
  a.click();
  URL.revokeObjectURL(url);
  ElMessage.success('已导出当前预设配置 JSON 文件 (包含提示词流水线与正则脚本)');
}

// 过滤后的正则脚本清单
const filteredRegexScripts = computed(() => {
  const list = preset.value.regex_scripts || [];
  const kw = regexSearchKeyword.value.trim().toLowerCase();
  if (!kw) return list;
  return list.filter(
    (s) =>
      s.scriptName.toLowerCase().includes(kw) ||
      s.findRegex.toLowerCase().includes(kw) ||
      (s.replaceString && s.replaceString.toLowerCase().includes(kw)),
  );
});

// 全流程实时沙盒输出
const sandboxOutputText = computed(() => {
  if (!sandboxInputText.value) return '';
  let output = sandboxInputText.value;
  const scripts = (preset.value.regex_scripts || []).filter(
    (s) => !s.disabled && s.placement.includes(sandboxPlacement.value),
  );

  for (const s of scripts) {
    try {
      let pattern = s.findRegex;
      let flags = 'g';
      if (pattern.startsWith('/')) {
        const match = pattern.match(/^\/(.*)\/([a-z]*)$/s);
        if (match) {
          pattern = match[1];
          flags = match[2] || '';
        }
      }
      const reg = new RegExp(pattern, flags);
      output = output.replace(reg, s.replaceString || '');
      for (const trimStr of s.trimStrings || []) {
        if (trimStr) {
          output = output.replaceAll(trimStr, '');
        }
      }
    } catch (err: any) {
      console.warn('沙盒正则运算异常:', s.scriptName, err);
    }
  }
  return output;
});

// 打开新建正则模态框
function openCreateRegexDialog(): void {
  editingRegexScript.value = null;
  isRegexEditOpen.value = true;
}

// 打开编辑正则模态框
function openEditRegexDialog(script: TavernRegexScript): void {
  editingRegexScript.value = JSON.parse(JSON.stringify(script));
  isRegexEditOpen.value = true;
}

// 保存单项正则修改
function saveRegexDialog(savedScript: TavernRegexScript): void {
  if (!Array.isArray(preset.value.regex_scripts)) {
    preset.value.regex_scripts = [];
  }
  const idx = preset.value.regex_scripts.findIndex((s) => s.id === savedScript.id);
  if (idx !== -1) {
    preset.value.regex_scripts[idx] = savedScript;
  } else {
    preset.value.regex_scripts.push(savedScript);
  }
}

// 删除正则项
function deleteRegexScript(id: string): void {
  if (!preset.value.regex_scripts) return;
  preset.value.regex_scripts = preset.value.regex_scripts.filter((s) => s.id !== id);
  ElMessage.success('已删除该正则脚本');
}

// 切换单项正则启用状态
function toggleRegexDisabled(id: string, disabled: boolean): void {
  const target = (preset.value.regex_scripts || []).find((s) => s.id === id);
  if (target) {
    target.disabled = disabled;
  }
}

// 调整正则顺序
function moveRegex(index: number, direction: 'up' | 'down'): void {
  if (!preset.value.regex_scripts) return;
  if (direction === 'up' && index <= 0) return;
  if (direction === 'down' && index >= preset.value.regex_scripts.length - 1) return;

  const targetIndex = direction === 'up' ? index - 1 : index + 1;
  const list = [...preset.value.regex_scripts];
  const temp = list[index];
  list[index] = list[targetIndex];
  list[targetIndex] = temp;
  preset.value.regex_scripts = list;
}

// ==================== 预设库与全局持久化管理 ====================

// 刷新预设库列表
async function refreshPresetLibrary(selectId?: string): Promise<void> {
  isLoadingVersions.value = true;
  try {
    const res: any = await listAdminTavernPresets();
    const list = res?.data || res;
    if (Array.isArray(list)) {
      presetLibrary.value = list;
      versionList.value = list;
      if (selectId) {
        currentPresetId.value = selectId;
      }
    }
  } catch (err: any) {
    ElMessage.error(err?.message || '获取预设库列表失败');
  } finally {
    isLoadingVersions.value = false;
  }
}

// 确保预设的高级格式化配置各项默认字段健全
function ensureAdvancedFormatting(cfg: TavernPresetConfig): void {
  if (!cfg.advanced_formatting) {
    cfg.advanced_formatting = {
      parse_think_tags: true,
      reasoning_history_depth: 0,
      auto_expand_reasoning: false,
      enable_post_history_instruction: false,
      post_history_instruction: '',
      post_history_depth: 0,
      stop_sequences: [],
      char_name_as_stop: false,
      user_name_as_stop: false,
      collapse_newlines: true,
      trim_incomplete_sentences: false,
      trim_whitespace: true,
      reply_prefix: '',
      show_reply_prefix: true,
    };
  } else {
    cfg.advanced_formatting.parse_think_tags = cfg.advanced_formatting.parse_think_tags ?? true;
    cfg.advanced_formatting.reasoning_history_depth =
      cfg.advanced_formatting.reasoning_history_depth ?? 0;
    cfg.advanced_formatting.auto_expand_reasoning =
      cfg.advanced_formatting.auto_expand_reasoning ?? false;
    cfg.advanced_formatting.enable_post_history_instruction =
      cfg.advanced_formatting.enable_post_history_instruction ?? false;
    cfg.advanced_formatting.post_history_instruction =
      cfg.advanced_formatting.post_history_instruction ?? '';
    cfg.advanced_formatting.post_history_depth = cfg.advanced_formatting.post_history_depth ?? 0;
    cfg.advanced_formatting.stop_sequences = cfg.advanced_formatting.stop_sequences ?? [];
    cfg.advanced_formatting.char_name_as_stop = cfg.advanced_formatting.char_name_as_stop ?? false;
    cfg.advanced_formatting.user_name_as_stop = cfg.advanced_formatting.user_name_as_stop ?? false;
    cfg.advanced_formatting.collapse_newlines = cfg.advanced_formatting.collapse_newlines ?? true;
    cfg.advanced_formatting.trim_incomplete_sentences =
      cfg.advanced_formatting.trim_incomplete_sentences ?? false;
    cfg.advanced_formatting.trim_whitespace = cfg.advanced_formatting.trim_whitespace ?? true;
    cfg.advanced_formatting.reply_prefix = cfg.advanced_formatting.reply_prefix ?? '';
    cfg.advanced_formatting.show_reply_prefix = cfg.advanced_formatting.show_reply_prefix ?? true;
  }
}

// 切换当前查看/编辑的预设
async function handleSwitchPreset(id: string): Promise<void> {
  if (!id) return;
  try {
    const res: any = await getAdminTavernPresetById(id);
    const data = res?.data || res;
    if (data?.prompts) {
      // 方案 A: 补齐未在 prompt_order 中的 prompts 条目作为备选 (enabled: false, is_unordered_backup: true)
      const parsedOrder = Array.isArray(data.prompt_order) ? [...data.prompt_order] : [];
      const orderedSet = new Set(
        parsedOrder.map((o: any) => (typeof o === 'object' ? o.identifier : o)),
      );
      for (const p of data.prompts) {
        if (p?.identifier && !orderedSet.has(p.identifier)) {
          parsedOrder.push({
            identifier: p.identifier,
            enabled: false,
            is_unordered_backup: true,
          });
          orderedSet.add(p.identifier);
        }
      }
      data.prompt_order = parsedOrder;
      ensureAdvancedFormatting(data);
      preset.value = data;
      currentPresetId.value = id;
    }
  } catch (err: any) {
    ElMessage.error(err?.message || '载入预设详情失败');
  }
}

// 导入整包酒馆预设 JSON (入库为独立实体并立即自动切换)
function handleImportPresetJsonFile(file: any): void {
  const rawFile = file.raw || file;
  if (!rawFile) return;
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      let content = (e.target?.result as string) || '';
      if (content.charCodeAt(0) === 0xfeff) {
        content = content.slice(1);
      }
      const json = JSON.parse(content);

      // 解析预设名称（优先从 JSON 取，兜底文件名）
      const fileNameFallback = rawFile.name
        ? rawFile.name.replace(/\.[^/.]+$/, '')
        : '自定义导入预设';
      const presetName = (json.preset_name || json.name || fileNameFallback).trim();

      // 解析流水线排序
      let parsedOrder: any[] = [];
      if (Array.isArray(json.prompt_order)) {
        if (json.prompt_order[0]?.order) {
          parsedOrder = json.prompt_order[0].order;
        } else {
          parsedOrder = json.prompt_order;
        }
      }

      // 方案 A: 补齐未在 prompt_order 中的 prompts 条目作为备选 (enabled: false, is_unordered_backup: true)
      const parsedPrompts = Array.isArray(json.prompts) ? json.prompts : [];
      const orderedSet = new Set(
        parsedOrder.map((o: any) => (typeof o === 'object' ? o.identifier : o)),
      );
      for (const p of parsedPrompts) {
        if (p?.identifier && !orderedSet.has(p.identifier)) {
          parsedOrder.push({
            identifier: p.identifier,
            enabled: false,
            is_unordered_backup: true,
          });
          orderedSet.add(p.identifier);
        }
      }

      // 解析正则脚本
      let regexList = json.regex_scripts;
      if (!regexList && json.extensions?.regex_scripts) {
        regexList = json.extensions.regex_scripts;
      }
      if (!regexList && json.extensions?.SPreset?.RegexBinding?.regexes) {
        regexList = json.extensions.SPreset.RegexBinding.regexes;
      }

      // 解析高级格式化配置
      const advFmt = json.advanced_formatting || json.extensions?.advanced_formatting;

      const newPresetPayload: TavernPresetConfig = {
        preset_name: presetName,
        is_active: false,
        temperature: json.temperature !== undefined ? json.temperature : 1.0,
        frequency_penalty: json.frequency_penalty !== undefined ? json.frequency_penalty : 0.0,
        presence_penalty: json.presence_penalty !== undefined ? json.presence_penalty : 0.0,
        top_p: json.top_p !== undefined ? json.top_p : 1.0,
        max_context_unlocked:
          json.max_context_unlocked !== undefined ? json.max_context_unlocked : true,
        openai_max_context:
          json.openai_max_context !== undefined ? json.openai_max_context : 2000000,
        openai_max_tokens: json.openai_max_tokens !== undefined ? json.openai_max_tokens : 32000,
        stream_openai: json.stream_openai !== undefined ? json.stream_openai : true,
        seed: json.seed !== undefined ? json.seed : -1,
        reasoning_effort: json.reasoning_effort !== undefined ? json.reasoning_effort : 'high',
        prompts: Array.isArray(json.prompts) ? json.prompts : [],
        prompt_order: parsedOrder,
        regex_scripts: Array.isArray(regexList) ? regexList : [],
        advanced_formatting: advFmt,
      };
      ensureAdvancedFormatting(newPresetPayload);

      // 1. 持久化入库
      const res: any = await createAdminTavernPreset(newPresetPayload);
      const createdItem = res?.data || res;
      const newId = createdItem?.id;

      // 2. 刷新预设库大盘
      await refreshPresetLibrary(newId);

      // 3. 立即自动切换视图至该预设
      if (newId) {
        await handleSwitchPreset(newId);
      }

      ElMessage.success(
        `成功导入并已切换至预设「${presetName}」，包含 ${newPresetPayload.prompts.length} 项提示词与 ${newPresetPayload.regex_scripts?.length || 0} 项正则脚本`,
      );
    } catch (err: any) {
      ElMessage.error(`预设 JSON 导入失败: ${err.message}`);
    }
  };
  reader.readAsText(rawFile);
}

// 单独导入正则 JSON
function handleImportRegexOnlyFile(file: any): void {
  const rawFile = file.raw || file;
  if (!rawFile) return;
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      let content = (e.target?.result as string) || '';
      if (content.charCodeAt(0) === 0xfeff) {
        content = content.slice(1);
      }
      const json = JSON.parse(content);
      const list = Array.isArray(json)
        ? json
        : json.regex_scripts ||
          json.extensions?.regex_scripts ||
          json.extensions?.SPreset?.RegexBinding?.regexes;
      if (Array.isArray(list)) {
        preset.value.regex_scripts = [...(preset.value.regex_scripts || []), ...list];
        ElMessage.success(`成功追加导入 ${list.length} 项正则脚本`);
      } else {
        ElMessage.warning('未能识别到有效的正则脚本数组');
      }
    } catch (err: any) {
      ElMessage.error(`正则文件解析失败: ${err.message}`);
    }
  };
  reader.readAsText(rawFile);
}

// 单独导出正则 JSON
function handleExportRegexOnly(): void {
  const scripts = preset.value.regex_scripts || [];
  const jsonStr = JSON.stringify(scripts, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `SillyTavern_RegexScripts_${Date.now()}.json`;
  a.click();
  URL.revokeObjectURL(url);
  ElMessage.success(`已导出 ${scripts.length} 项正则脚本配置`);
}

// 按指定 ID 导出预设 JSON
async function handleExportPresetById(id: string): Promise<void> {
  try {
    const res: any = await getAdminTavernPresetById(id);
    const data = res?.data || res;
    const exportData = {
      ...data,
      extensions: {
        regex_scripts: data.regex_scripts || [],
        advanced_formatting: data.advanced_formatting,
        SPreset: {
          RegexBinding: {
            regexes: data.regex_scripts || [],
          },
        },
      },
    };
    const jsonStr = JSON.stringify(exportData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `SillyTavern_Global_${data.preset_name || 'Preset'}.json`;
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success(`已导出预设「${data.preset_name}」JSON 配置文件`);
  } catch (err: any) {
    ElMessage.error(err?.message || '导出预设失败');
  }
}

// ==================== 高级格式化调优 Tab 5 交互逻辑 ====================
const newStopSequenceInput = ref('');

function addStopSequence(): void {
  const seq = newStopSequenceInput.value.trim();
  if (!seq) return;
  ensureAdvancedFormatting(preset.value);
  const adv = preset.value.advanced_formatting;
  if (!adv) return;
  if (!adv.stop_sequences) {
    adv.stop_sequences = [];
  }
  if (!adv.stop_sequences.includes(seq)) {
    adv.stop_sequences.push(seq);
    ElMessage.success(`已添加终止词「${seq}」`);
  } else {
    ElMessage.info(`终止词「${seq}」已存在`);
  }
  newStopSequenceInput.value = '';
}

function removeStopSequence(index: number): void {
  const adv = preset.value.advanced_formatting;
  if (adv?.stop_sequences) {
    adv.stop_sequences.splice(index, 1);
  }
}

function insertMacroIntoPostHistory(macro: string): void {
  ensureAdvancedFormatting(preset.value);
  const adv = preset.value.advanced_formatting;
  if (!adv) return;
  adv.post_history_instruction = `${adv.post_history_instruction || ''} ${macro} `;
}

// 保存当前预设修改 (落库该预设实体，不影响全平台生效标记)
async function handleSaveCurrentPreset(): Promise<void> {
  if (!currentPresetId.value) return;
  isSaving.value = true;
  try {
    ensureAdvancedFormatting(preset.value);
    const res: any = await updateAdminTavernPresetById(currentPresetId.value, preset.value);
    const data = res?.data || res;
    if (data?.prompts) {
      ensureAdvancedFormatting(data);
      preset.value = data;
    }
    ElMessage.success(`预设「${preset.value.preset_name}」修改已成功持久化落库！`);
    await refreshPresetLibrary(currentPresetId.value);
  } catch (err: any) {
    ElMessage.error(err?.message || '保存预设修改失败');
  } finally {
    isSaving.value = false;
  }
}

// 将当前预设设为全平台生效
async function handleActivateCurrentPreset(): Promise<void> {
  if (!currentPresetId.value) return;
  if (preset.value.is_active) {
    ElMessage.info('当前预设已处于全平台生效中');
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确认将「${preset.value.preset_name}」设为【全平台全局生效】？\n发布后所有用户的后续对话与模型调用将立即按此预设流水线生效！`,
      '全平台热发布确认',
      {
        confirmButtonText: '确认生效',
        cancelButtonText: '取消',
        type: 'warning',
      },
    );
  } catch {
    return;
  }

  isActivating.value = true;
  try {
    // 1. 先将当前草稿改动落库
    await updateAdminTavernPresetById(currentPresetId.value, preset.value);
    // 2. 激活为全局生效
    await activateAdminTavernPreset(currentPresetId.value);
    preset.value.is_active = true;
    ElMessage.success(`预设「${preset.value.preset_name}」已成功设为全平台热生效！`);
    await refreshPresetLibrary(currentPresetId.value);
  } catch (err: any) {
    ElMessage.error(err?.message || '激活预设失败');
  } finally {
    isActivating.value = false;
  }
}

// 重命名当前预设
async function openRenameDialog(): Promise<void> {
  if (!currentPresetId.value) return;
  try {
    const { value } = await ElMessageBox.prompt('请输入预设新名称', '重命名预设', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: preset.value.preset_name,
      inputPattern: /\S+/,
      inputErrorMessage: '预设名称不能为空',
    });
    if (value && value.trim()) {
      await renameAdminTavernPreset(currentPresetId.value, value.trim());
      preset.value.preset_name = value.trim();
      ElMessage.success('预设重命名成功');
      await refreshPresetLibrary(currentPresetId.value);
    }
  } catch {
    // 用户取消
  }
}

// 另存为新副本
async function handleDuplicatePreset(): Promise<void> {
  if (!currentPresetId.value) return;
  try {
    const { value } = await ElMessageBox.prompt('请输入新副本预设名称', '另存为新副本', {
      confirmButtonText: '创建副本',
      cancelButtonText: '取消',
      inputValue: `${preset.value.preset_name} (副本)`,
      inputPattern: /\S+/,
      inputErrorMessage: '预设名称不能为空',
    });
    if (value && value.trim()) {
      const { id: _, ...rest } = JSON.parse(JSON.stringify(preset.value));
      const copyPayload: TavernPresetConfig = {
        ...rest,
        preset_name: value.trim(),
        is_active: false,
      };
      const res: any = await createAdminTavernPreset(copyPayload);
      const newId = res?.data?.id || res?.id;
      ElMessage.success(`副本「${value.trim()}」已成功创建并自动切换`);
      await refreshPresetLibrary(newId);
      if (newId) {
        await handleSwitchPreset(newId);
      }
    }
  } catch {
    // 用户取消
  }
}

// 删除当前预设
async function handleDeleteCurrentPreset(): Promise<void> {
  if (!currentPresetId.value) return;
  if (preset.value.is_active) {
    ElMessage.warning('当前预设正在全平台生效中，无法删除！请先将其他预设设为生效。');
    return;
  }
  if (presetLibrary.value.length <= 1) {
    ElMessage.warning('预设库中至少需保留一套预设，无法删除');
    return;
  }
  try {
    await ElMessageBox.confirm(
      `确定要彻底删除当前预设「${preset.value.preset_name}」吗？删除后不可恢复。`,
      '删除预设警告',
      {
        confirmButtonText: '彻底删除',
        cancelButtonText: '取消',
        type: 'error',
      },
    );
    await deleteAdminTavernPreset(currentPresetId.value);
    ElMessage.success('预设已成功删除');
    await refreshPresetLibrary();
    const fallback = presetLibrary.value.find((p) => p.is_active) || presetLibrary.value[0];
    if (fallback) {
      await handleSwitchPreset(fallback.id);
    }
  } catch {
    // 用户取消
  }
}

// 表格行快捷设为生效
async function handleActivateRowPreset(row: any): Promise<void> {
  try {
    await ElMessageBox.confirm(
      `确认将「${row.preset_name}」设为全平台全局生效？\n生效后所有用户后续对话将使用此预设！`,
      '设为全局生效确认',
      {
        confirmButtonText: '确认生效',
        cancelButtonText: '取消',
        type: 'warning',
      },
    );
    await activateAdminTavernPreset(row.id);
    ElMessage.success(`预设「${row.preset_name}」已设为全平台生效！`);
    await refreshPresetLibrary();
    if (row.id === currentPresetId.value) {
      preset.value.is_active = true;
    } else {
      await handleSwitchPreset(row.id);
    }
  } catch {
    // 用户取消
  }
}

// 表格行快捷删除
async function handleDeleteRowPreset(row: any): Promise<void> {
  if (row.is_active) {
    ElMessage.warning('生效中的预设不可删除');
    return;
  }
  if (presetLibrary.value.length <= 1) {
    ElMessage.warning('预设库中至少需保留一套预设，无法删除');
    return;
  }
  try {
    await ElMessageBox.confirm(`确定要删除预设「${row.preset_name}」吗？`, '删除预设确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'error',
    });
    await deleteAdminTavernPreset(row.id);
    ElMessage.success(`预设「${row.preset_name}」已删除`);
    const currentDeleted = row.id === currentPresetId.value;
    await refreshPresetLibrary();
    if (currentDeleted) {
      const fallback = presetLibrary.value.find((p) => p.is_active) || presetLibrary.value[0];
      if (fallback) {
        await handleSwitchPreset(fallback.id);
      }
    }
  } catch {
    // 用户取消
  }
}

// 初始化加载后台数据
async function loadData(): Promise<void> {
  await refreshPresetLibrary();
  if (presetLibrary.value.length > 0) {
    const activeItem = presetLibrary.value.find((p) => p.is_active) || presetLibrary.value[0];
    await handleSwitchPreset(activeItem.id);
  } else {
    try {
      const res: any = await getAdminTavernPreset();
      const data = res?.data || res;
      if (data?.prompts) {
        preset.value = data;
        currentPresetId.value = data.id || '';
      }
      await refreshPresetLibrary(currentPresetId.value);
    } catch (err: any) {
      ElMessage.error(err?.message || '读取全局酒馆配置失败');
    }
  }
}

onMounted(() => {
  loadData();
  loadFactoryDefault();
});
</script>

<style scoped>
.tavern-tabs :deep(.el-tabs__content) {
  flex: 1;
  overflow: hidden;
  height: 100%;
}
</style>
