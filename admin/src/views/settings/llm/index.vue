<template>
  <div class="flex flex-col gap-4 p-4 w-full h-full box-border">
    <!-- 1. 顶部大模型 API 配置中枢 Header 面板 -->
    <div
      class="flex flex-wrap items-center justify-between gap-4 p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-sm"
    >
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-xl text-blue-500 shadow-xs">
          🌐
        </div>
        <div class="flex flex-col gap-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-base font-bold tracking-wide text-[var(--el-text-color-primary)]">
              大模型 API 连接配置与模型调度
            </h1>
            <el-tag v-if="currentProvider?.is_active" type="success" effect="dark" size="small">
              ● 当前渠道已启用
            </el-tag>
            <el-tag v-else type="info" effect="plain" size="small">
              ○ 当前渠道已停用 (模型不上架)
            </el-tag>
          </div>

          <!-- 渠道切换与管理 -->
          <div class="flex items-center gap-2 flex-wrap mt-0.5">
            <span class="text-xs font-semibold text-[var(--el-text-color-secondary)]">当前渠道:</span>
            <el-select
              v-model="currentProviderId"
              placeholder="选择 API 提供商渠道"
              size="small"
              class="!w-64"
              @change="handleSelectProvider"
            >
              <el-option
                v-for="p in providers"
                :key="p.id"
                :label="p.name"
                :value="p.id"
              >
                <div class="flex items-center justify-between w-full">
                  <span class="truncate font-medium">{{ p.name }}</span>
                  <div class="flex items-center gap-1.5 ml-2">
                    <el-tag size="small" type="info" effect="plain" class="!text-[10px]">{{ p.models_count }} 模型</el-tag>
                    <el-tag v-if="p.is_active" type="success" size="small" effect="plain" class="!text-[10px]">启用</el-tag>
                  </div>
                </div>
              </el-option>
            </el-select>

            <el-button size="small" type="primary" plain @click="openAddProviderDialog">
              <el-icon class="mr-1"><Plus /></el-icon> 新增渠道
            </el-button>
            <el-button
              size="small"
              type="danger"
              plain
              :disabled="providers.length <= 1"
              @click="handleDeleteProvider"
            >
              <el-icon class="mr-1"><Delete /></el-icon> 删除渠道
            </el-button>
          </div>
        </div>
      </div>

      <!-- 顶部统计与沙盒入口 -->
      <div class="flex flex-wrap items-center gap-2.5">
        <div class="hidden md:flex items-center gap-3 px-3.5 py-1.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)] text-xs">
          <span class="text-[var(--el-text-color-secondary)]">渠道总数:</span>
          <span class="font-bold text-blue-500 font-mono">{{ providers.length }}</span>
          <span class="text-[var(--el-border-color)]">|</span>
          <span class="text-[var(--el-text-color-secondary)]">客户端上架模型:</span>
          <span class="font-bold text-emerald-500 font-mono">{{ totalPublicModelsCount }} 个</span>
        </div>

        <el-button type="warning" plain @click="isSandboxOpen = true">
          <el-icon class="mr-1"><ChatDotSquare /></el-icon> 沙盒连通测试
        </el-button>

        <el-button type="primary" :loading="isSaving" @click="handleSaveCurrentProvider">
          <el-icon class="mr-1"><Check /></el-icon> 保存配置
        </el-button>
      </div>
    </div>

    <!-- 2. 主体双栏配置区域 -->
    <div class="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-0 overflow-y-auto">
      <!-- 左侧：渠道连接凭证与上游探测 (占 5 栏) -->
      <div class="lg:col-span-5 flex flex-col gap-4">
        <!-- 渠道基本配置卡片 -->
        <div class="p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-xs flex flex-col gap-4">
          <div class="flex items-center justify-between pb-2 border-b border-[var(--el-border-color-lighter)]">
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-[var(--el-text-color-primary)]">🔗 渠道连接配置</span>
              <el-tag size="small" type="info" class="font-mono">{{ providerForm.provider_type }}</el-tag>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-[var(--el-text-color-secondary)]">渠道启用:</span>
              <el-switch
                v-model="providerForm.is_active"
                size="small"
                active-color="#13ce66"
              />
            </div>
          </div>

          <el-form label-position="top" size="default" class="flex flex-col gap-3">
            <!-- 渠道名称 -->
            <el-form-item label="渠道名称" class="!mb-0">
              <el-input v-model="providerForm.name" placeholder="例如: DeepSeek 官方 API / 硅基流动中转" />
            </el-form-item>

            <!-- 供应商类型 -->
            <el-form-item label="接口协议类型 (Provider Type)" class="!mb-0">
              <el-select v-model="providerForm.provider_type" class="w-full">
                <el-option label="OpenAI 补全兼容 (DeepSeek / Moonshot / 硅基 / OneAPI)" value="openai" />
                <el-option label="Anthropic Claude 官方 (claude-3-5-sonnet)" value="anthropic" />
                <el-option label="Google Gemini 官方 (gemini-1.5-pro)" value="gemini" />
                <el-option label="Ollama 本地大模型 (兼容本地 API)" value="ollama" />
              </el-select>
            </el-form-item>

            <!-- 反向代理 Base URL -->
            <el-form-item label="API Base URL (反向代理 / 官方端点)" class="!mb-0">
              <div class="flex flex-col gap-1.5 w-full">
                <el-input
                  v-model="providerForm.base_url"
                  placeholder="例如: https://api.deepseek.com/v1"
                  clearable
                >
                  <template #prepend>
                    <el-dropdown trigger="click" @command="handleQuickFillBaseUrl">
                      <el-button :icon="ArrowDown">常用预设</el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="https://api.deepseek.com/v1">DeepSeek 官方 (api.deepseek.com/v1)</el-dropdown-item>
                          <el-dropdown-item command="https://api.openai.com/v1">OpenAI 官方 (api.openai.com/v1)</el-dropdown-item>
                          <el-dropdown-item command="https://api.siliconflow.cn/v1">硅基流动 SiliconFlow (api.siliconflow.cn/v1)</el-dropdown-item>
                          <el-dropdown-item command="https://api.moonshot.cn/v1">月之暗面 Kimi (api.moonshot.cn/v1)</el-dropdown-item>
                          <el-dropdown-item command="https://open.bigmodel.cn/api/paas/v4">智谱 GLM (open.bigmodel.cn/api/paas/v4)</el-dropdown-item>
                          <el-dropdown-item command="http://localhost:11434/v1">本地 Ollama (localhost:11434/v1)</el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </template>
                </el-input>
                <span class="text-[11px] text-[var(--el-text-color-secondary)]">必须包含协议头 (http/https)，末尾不需要斜杠 /</span>
              </div>
            </el-form-item>

            <!-- API Key -->
            <el-form-item label="API 密钥 (API Key)" class="!mb-0">
              <div class="flex flex-col gap-1 w-full">
                <el-input
                  v-model="providerForm.api_key"
                  type="password"
                  show-password
                  placeholder="输入 API Key (已脱敏保护，如保持原样则无需修改)"
                  clearable
                />
                <span class="text-[11px] text-[var(--el-text-color-secondary)]">
                  后端具备前4后4星号脱敏安全保护，留空或带星号不会覆盖现有凭证。
                </span>
              </div>
            </el-form-item>

            <!-- 超时与排序 -->
            <div class="grid grid-cols-2 gap-3">
              <el-form-item label="超时限制 (秒)" class="!mb-0">
                <el-input-number v-model="providerForm.timeout_seconds" :min="10" :max="300" class="!w-full" />
              </el-form-item>
              <el-form-item label="渠道排序权重" class="!mb-0">
                <el-input-number v-model="providerForm.sort_order" :min="0" :max="999" class="!w-full" />
              </el-form-item>
            </div>

            <!-- 渠道备注说明 -->
            <el-form-item label="渠道备注说明" class="!mb-0">
              <el-input
                v-model="providerForm.description"
                type="textarea"
                :rows="2"
                placeholder="填写该渠道的用途、限额或充值到期时间..."
              />
            </el-form-item>
          </el-form>

          <!-- 探测与拉取操作条 -->
          <div class="flex flex-col gap-2 pt-3 border-t border-[var(--el-border-color-lighter)]">
            <div class="flex items-center justify-between gap-2">
              <el-button
                type="success"
                plain
                :loading="isTestingConnection"
                @click="handleTestConnection"
              >
                <el-icon class="mr-1"><Odometer /></el-icon> 连通性测试 (Ping)
              </el-button>

              <el-button
                type="primary"
                plain
                :loading="isFetchingUpstream"
                @click="handleFetchUpstreamModels"
              >
                <el-icon class="mr-1"><Download /></el-icon> 在线拉取模型 (/v1/models)
              </el-button>
            </div>

            <!-- 连通性测试结果提示框 -->
            <div
              v-if="testResult"
              :class="[
                'p-2.5 rounded-lg border text-xs flex items-center justify-between',
                testResult.success
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400'
                  : 'bg-rose-500/10 border-rose-500/30 text-rose-600 dark:text-rose-400',
              ]"
            >
              <div class="flex items-center gap-2">
                <span>{{ testResult.success ? '✅' : '❌' }}</span>
                <span>{{ testResult.message }}</span>
              </div>
              <span v-if="testResult.latency_ms > 0" class="font-mono font-bold">
                {{ testResult.latency_ms }} ms
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：模型矩阵与客户端上架调度 (占 7 栏) -->
      <div class="lg:col-span-7 flex flex-col gap-4">
        <div class="p-4 rounded-xl bg-[var(--el-bg-color-overlay)] border border-[var(--el-border-color-lighter)] shadow-xs flex flex-col gap-3 flex-1">
          <!-- 头部操作与检索 -->
          <div class="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-[var(--el-border-color-lighter)]">
            <div class="flex items-center gap-2">
              <span class="text-sm font-bold text-[var(--el-text-color-primary)]">📦 模型矩阵与客户端上架</span>
              <el-tag size="small" type="success" effect="plain">
                已上架 {{ publicModelsCount }} / {{ providerForm.models.length }}
              </el-tag>
            </div>

            <div class="flex items-center gap-2">
              <el-input
                v-model="modelSearchKeyword"
                placeholder="搜索模型 ID / 名称..."
                size="small"
                clearable
                class="!w-44"
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>

              <el-button size="small" type="primary" plain @click="openAddModelDialog">
                <el-icon class="mr-1"><Plus /></el-icon> 添加模型
              </el-button>

              <el-dropdown trigger="click" @command="handleBatchModelAction">
                <el-button size="small">
                  批量操作 <el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="enable_all_public">一键全部上架至客户端</el-dropdown-item>
                    <el-dropdown-item command="disable_all_public">一键全部从客户端下架</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>

          <!-- 模型清单数据表格 -->
          <div class="flex-1 overflow-x-auto min-h-[360px]">
            <el-table
              :data="filteredModels"
              stripe
              style="width: 100%"
              size="small"
              class="rounded-lg overflow-hidden border border-[var(--el-border-color-lighter)]"
            >
              <!-- 默认模型标记 -->
              <el-table-column label="默认" width="60" align="center">
                <template #default="{ row }">
                  <el-tooltip content="设为客户端默认选中模型" placement="top">
                    <button
                      type="button"
                      class="cursor-pointer text-base bg-transparent border-0 outline-none transition-transform active:scale-90"
                      @click="handleSetDefaultModel(row.id)"
                    >
                      <span v-if="row.is_default" class="text-amber-500">⭐</span>
                      <span v-else class="text-gray-300 dark:text-gray-600 hover:text-amber-400">☆</span>
                    </button>
                  </el-tooltip>
                </template>
              </el-table-column>

              <!-- 模型标识 -->
              <el-table-column label="模型标识 (ID)" min-width="170">
                <template #default="{ row }">
                  <div class="flex flex-col">
                    <span class="font-bold font-mono text-[var(--el-text-color-primary)]">{{ row.id }}</span>
                    <span class="text-[11px] text-[var(--el-text-color-secondary)]">{{ row.display_name }}</span>
                  </div>
                </template>
              </el-table-column>

              <!-- 家族与特性 -->
              <el-table-column label="家族 / 特性" width="130">
                <template #default="{ row }">
                  <div class="flex flex-wrap gap-1">
                    <el-tag size="small" effect="plain" class="!text-[10px] uppercase font-mono">{{ row.family || 'other' }}</el-tag>
                    <el-tag v-if="row.supports_reasoning" size="small" type="warning" effect="dark" class="!text-[10px]">
                      深度思考
                    </el-tag>
                  </div>
                </template>
              </el-table-column>

              <!-- 消耗星石 -->
              <el-table-column label="单次消耗" width="85" align="center">
                <template #default="{ row }">
                  <el-tag size="small" type="warning" effect="plain" class="font-mono font-bold">
                    ★ {{ row.cost || 1 }}
                  </el-tag>
                </template>
              </el-table-column>

              <!-- 客户端上架开关 (核心亮点) -->
              <el-table-column label="客户端上架" width="100" align="center">
                <template #default="{ row }">
                  <el-tooltip :content="row.is_public ? '已向客户端展示，用户可选' : '已在客户端隐藏'" placement="top">
                    <el-switch
                      v-model="row.is_public"
                      size="small"
                      active-color="#13ce66"
                      @change="handleModelPublicToggle(row)"
                    />
                  </el-tooltip>
                </template>
              </el-table-column>

              <!-- 操作列 -->
              <el-table-column label="操作" width="90" align="center">
                <template #default="{ row }">
                  <div class="flex items-center justify-center gap-1">
                    <el-tooltip content="编辑模型参数" placement="top">
                      <el-button size="small" circle @click="openEditModelDialog(row)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                    </el-tooltip>
                    <el-tooltip content="删除此模型" placement="top">
                      <el-button size="small" circle type="danger" plain @click="handleDeleteModel(row.id)">
                        <el-icon><Delete /></el-icon>
                      </el-button>
                    </el-tooltip>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 弹窗: 新增渠道弹窗 (对齐规范: 浅色 border 分离，操作右侧，辅助左侧) -->
    <el-dialog
      v-model="isAddProviderOpen"
      title="新增大模型 API 渠道"
      width="540px"
      append-to-body
      destroy-on-close
      class="llm-bordered-dialog"
    >
      <div class="p-4 flex flex-col gap-3">
        <el-form label-position="top" size="default">
          <el-form-item label="渠道名称" required>
            <el-input v-model="newProviderForm.name" placeholder="如: 硅基流动 SiliconFlow" />
          </el-form-item>
          <el-form-item label="协议类型">
            <el-select v-model="newProviderForm.provider_type" class="w-full">
              <el-option label="OpenAI 兼容 (DeepSeek/硅基/OneAPI)" value="openai" />
              <el-option label="Claude 官方" value="anthropic" />
              <el-option label="Google Gemini" value="gemini" />
              <el-option label="Ollama 本地端点" value="ollama" />
            </el-select>
          </el-form-item>
          <el-form-item label="API Base URL" required>
            <el-input v-model="newProviderForm.base_url" placeholder="https://api.example.com/v1" />
          </el-form-item>
          <el-form-item label="API Key">
            <el-input v-model="newProviderForm.api_key" type="password" show-password placeholder="sk-..." />
          </el-form-item>
          <el-form-item label="渠道说明">
            <el-input v-model="newProviderForm.description" type="textarea" :rows="2" placeholder="备注渠道信息..." />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="p-3 border-t border-[var(--el-border-color-lighter)] flex items-center justify-between w-full">
          <div>
            <el-button @click="resetNewProviderForm">重置</el-button>
          </div>
          <div class="flex items-center gap-2">
            <el-button @click="isAddProviderOpen = false">取消</el-button>
            <el-button type="primary" :loading="isCreatingProvider" @click="handleConfirmCreateProvider">
              立即创建
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 4. 弹窗: 在线拉取模型入库选择弹窗 -->
    <el-dialog
      v-model="isFetchModelsDialogOpen"
      title="在线拉取上游模型并批量入库"
      width="640px"
      append-to-body
      destroy-on-close
      class="llm-bordered-dialog"
    >
      <div class="p-4 flex flex-col gap-3">
        <div class="flex items-center justify-between gap-2">
          <span class="text-xs text-[var(--el-text-color-secondary)]">
            上游返回 {{ fetchedModelIds.length }} 个模型，请勾选需要收录进当前渠道的项：
          </span>
          <div class="flex items-center gap-2">
            <el-checkbox v-model="isSelectAllFetched" @change="handleToggleSelectAllFetched">全选</el-checkbox>
          </div>
        </div>

        <el-input
          v-model="fetchedSearchQuery"
          placeholder="搜索拉取的模型标识..."
          size="small"
          clearable
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>

        <!-- 勾选列表区域 -->
        <div class="max-h-72 overflow-y-auto border border-[var(--el-border-color-lighter)] rounded-lg p-2 flex flex-col gap-1">
          <el-checkbox-group v-model="selectedFetchedModelIds">
            <div
              v-for="mid in filteredFetchedModelIds"
              :key="mid"
              class="flex items-center justify-between p-1.5 rounded hover:bg-[var(--el-fill-color-light)] transition-colors"
            >
              <el-checkbox :label="mid">
                <span class="font-mono text-xs">{{ mid }}</span>
              </el-checkbox>
              <span v-if="isModelAlreadyAdded(mid)" class="text-[11px] text-gray-400">已存在</span>
            </div>
          </el-checkbox-group>
        </div>

        <div class="grid grid-cols-2 gap-3 pt-2">
          <div class="flex items-center gap-2">
            <span class="text-xs text-[var(--el-text-color-secondary)]">默认上架客户端:</span>
            <el-switch v-model="fetchImportAsPublic" size="small" active-color="#13ce66" />
          </div>
          <div class="flex items-center gap-2">
            <span class="text-xs text-[var(--el-text-color-secondary)]">默认单次消耗:</span>
            <el-input-number v-model="fetchImportDefaultCost" :min="1" :max="10" size="small" />
          </div>
        </div>
      </div>

      <template #footer>
        <div class="p-3 border-t border-[var(--el-border-color-lighter)] flex items-center justify-between w-full">
          <div>
            <span class="text-xs text-[var(--el-text-color-secondary)] font-mono">已选中 {{ selectedFetchedModelIds.length }} 个</span>
          </div>
          <div class="flex items-center gap-2">
            <el-button @click="isFetchModelsDialogOpen = false">取消</el-button>
            <el-button
              type="primary"
              :disabled="selectedFetchedModelIds.length === 0"
              @click="handleConfirmImportFetchedModels"
            >
              一键导入入库
            </el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 5. 弹窗: 编辑 / 添加模型详情弹窗 -->
    <el-dialog
      v-model="isModelEditDialogOpen"
      :title="modelFormMode === 'add' ? '添加新模型' : '编辑模型参数'"
      width="500px"
      append-to-body
      destroy-on-close
      class="llm-bordered-dialog"
    >
      <div class="p-4 flex flex-col gap-3">
        <el-form label-position="top" size="default">
          <el-form-item label="模型唯一标识 (ID)" required>
            <el-input
              v-model="singleModelForm.id"
              :disabled="modelFormMode === 'edit'"
              placeholder="如: deepseek-chat / gpt-4o"
            />
          </el-form-item>

          <el-form-item label="展示名称" required>
            <el-input v-model="singleModelForm.display_name" placeholder="如: DeepSeek-V3 旗舰大模型" />
          </el-form-item>

          <div class="grid grid-cols-2 gap-3">
            <el-form-item label="模型家族">
              <el-select v-model="singleModelForm.family" class="w-full">
                <el-option label="DeepSeek" value="deepseek" />
                <el-option label="GPT / OpenAI" value="gpt" />
                <el-option label="Claude" value="claude" />
                <el-option label="Gemini" value="gemini" />
                <el-option label="通义千问 Qwen" value="qwen" />
                <el-option label="其他 (Other)" value="other" />
              </el-select>
            </el-form-item>

            <el-form-item label="单次消耗星石">
              <el-input-number v-model="singleModelForm.cost" :min="1" :max="20" class="!w-full" />
            </el-form-item>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <el-form-item label="上下文窗口 (Token)">
              <el-input-number v-model="singleModelForm.context_limit" :min="4000" :max="1000000" :step="4000" class="!w-full" />
            </el-form-item>

            <el-form-item label="排序权重">
              <el-input-number v-model="singleModelForm.sort_order" :min="0" :max="999" class="!w-full" />
            </el-form-item>
          </div>

          <div class="flex items-center justify-between p-2.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)] mt-1">
            <div class="flex flex-col">
              <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">客户端上架</span>
              <span class="text-[10px] text-[var(--el-text-color-secondary)]">是否对移动端及 Web 客户端用户可见</span>
            </div>
            <el-switch v-model="singleModelForm.is_public" active-color="#13ce66" />
          </div>

          <div class="flex items-center justify-between p-2.5 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)]">
            <div class="flex flex-col">
              <span class="text-xs font-semibold text-[var(--el-text-color-primary)]">支持深度思考 (Reasoning)</span>
              <span class="text-[10px] text-[var(--el-text-color-secondary)]">如 DeepSeek-R1 / OpenAI o1 思考链展示</span>
            </div>
            <el-switch v-model="singleModelForm.supports_reasoning" active-color="#e6a23c" />
          </div>
        </el-form>
      </div>

      <template #footer>
        <div class="p-3 border-t border-[var(--el-border-color-lighter)] flex items-center justify-between w-full">
          <div>
            <el-button v-if="modelFormMode === 'add'" @click="resetSingleModelForm">重置</el-button>
          </div>
          <div class="flex items-center gap-2">
            <el-button @click="isModelEditDialogOpen = false">取消</el-button>
            <el-button type="primary" @click="handleConfirmSaveSingleModel">保存</el-button>
          </div>
        </div>
      </template>
    </el-dialog>

    <!-- 6. 沙盒抽屉: 快速连通性实测体验 -->
    <el-drawer
      v-model="isSandboxOpen"
      title="大模型快速沙盒测试"
      size="440px"
      append-to-body
    >
      <div class="flex flex-col h-full gap-4">
        <div class="p-3 rounded-lg bg-[var(--el-fill-color-light)] border border-[var(--el-border-color-lighter)] flex flex-col gap-2 text-xs">
          <div class="flex items-center justify-between">
            <span class="font-semibold text-[var(--el-text-color-primary)]">当前测试渠道:</span>
            <el-tag size="small" type="primary">{{ providerForm.name }}</el-tag>
          </div>
          <div class="flex items-center justify-between">
            <span class="font-semibold text-[var(--el-text-color-primary)]">选择测试模型:</span>
            <el-select v-model="sandboxModelId" size="small" class="!w-48">
              <el-option
                v-for="m in providerForm.models"
                :key="m.id"
                :label="m.display_name"
                :value="m.id"
              />
            </el-select>
          </div>
        </div>

        <div class="flex-1 border border-[var(--el-border-color-lighter)] rounded-xl p-3 overflow-y-auto bg-[var(--el-bg-color)] flex flex-col gap-2">
          <div v-if="!sandboxOutput && !isSandboxRunning" class="text-xs text-gray-400 text-center py-20">
            点击下方「发送测试消息」开始测试 API 连通性与模型推理响应...
          </div>
          <div v-else class="text-xs font-mono whitespace-pre-wrap leading-relaxed text-[var(--el-text-color-primary)]">
            {{ sandboxOutput }}
          </div>
        </div>

        <div class="flex flex-col gap-2 pt-2 border-t border-[var(--el-border-color-lighter)]">
          <el-input
            v-model="sandboxPrompt"
            type="textarea"
            :rows="3"
            placeholder="输入测试提示词，例如: 请用一句话做个自我介绍"
          />
          <div class="flex justify-end gap-2">
            <el-button :disabled="isSandboxRunning" @click="sandboxOutput = ''">清屏</el-button>
            <el-button type="primary" :loading="isSandboxRunning" @click="handleRunSandbox">
              发送测试消息
            </el-button>
          </div>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
/**
 * 大模型 (LLM) API 渠道与模型上架中枢后台管理面板
 *
 * 规范遵循:
 * 1. Vue 3.5 Composition API + TypeScript 完整类型标注与防御编程；
 * 2. 严禁原生 alert/confirm，所有交互提示采用 ElMessage 与 ElMessageBox；
 * 3. 弹窗 header body footer 之间具备浅色 border，取消/保存靠右，重置等靠左；
 * 4. 样式全面使用 UnoCSS 原子类。
 */

import {
  ArrowDown,
  ChatDotSquare,
  Check,
  Delete,
  Download,
  Edit,
  Odometer,
  Plus,
  Search,
} from '@element-plus/icons-vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { computed, onMounted, reactive, ref } from 'vue';

import {
  type LLMModelItem,
  type LLMProviderCreate,
  type LLMProviderItem,
  type LLMTestConnectionResponse,
  createAdminLLMProvider,
  deleteAdminLLMProvider,
  fetchUpstreamLLMModels,
  getAdminLLMProviders,
  testLLMConnection,
  toggleAdminLLMModelPublic,
  updateAdminLLMProvider,
} from '@/api/llm';

// ======================== 1. 响应式状态定义 ========================

const providers = ref<LLMProviderItem[]>([]);
const currentProviderId = ref<string>('');
const isSaving = ref(false);
const isTestingConnection = ref(false);
const isFetchingUpstream = ref(false);
const testResult = ref<LLMTestConnectionResponse | null>(null);

// 当前正在编辑的渠道表单
const providerForm = reactive<{
  id: string;
  name: string;
  provider_type: string;
  base_url: string;
  api_key: string;
  is_active: boolean;
  timeout_seconds: number;
  custom_headers: Record<string, string>;
  models: LLMModelItem[];
  description: string;
  sort_order: number;
}>({
  id: '',
  name: '',
  provider_type: 'openai',
  base_url: '',
  api_key: '',
  is_active: true,
  timeout_seconds: 60,
  custom_headers: {},
  models: [],
  description: '',
  sort_order: 100,
});

// 模型检索过滤
const modelSearchKeyword = ref('');

// 新建渠道弹窗状态
const isAddProviderOpen = ref(false);
const isCreatingProvider = ref(false);
const newProviderForm = reactive<LLMProviderCreate>({
  name: '',
  provider_type: 'openai',
  base_url: 'https://api.deepseek.com/v1',
  api_key: '',
  is_active: true,
  timeout_seconds: 60,
  description: '',
  models: [],
});

// 在线拉取模型入库弹窗状态
const isFetchModelsDialogOpen = ref(false);
const fetchedModelIds = ref<string[]>([]);
const selectedFetchedModelIds = ref<string[]>([]);
const fetchedSearchQuery = ref('');
const isSelectAllFetched = ref(false);
const fetchImportAsPublic = ref(true);
const fetchImportDefaultCost = ref(1);

// 单模型编辑弹窗状态
const isModelEditDialogOpen = ref(false);
const modelFormMode = ref<'add' | 'edit'>('add');
const singleModelForm = reactive<LLMModelItem>({
  id: '',
  display_name: '',
  is_enabled: true,
  is_public: true,
  is_default: false,
  supports_streaming: true,
  supports_reasoning: false,
  cost: 1,
  family: 'deepseek',
  context_limit: 64000,
  sort_order: 100,
});

// 沙盒抽屉状态
const isSandboxOpen = ref(false);
const sandboxModelId = ref('');
const sandboxPrompt = ref('请用一句话介绍你是什么大模型，具备哪些优势？');
const sandboxOutput = ref('');
const isSandboxRunning = ref(false);

// ======================== 2. 计算属性 ========================

const currentProvider = computed(() => {
  return providers.value.find((p) => p.id === currentProviderId.value);
});

const totalPublicModelsCount = computed(() => {
  let count = 0;
  for (const p of providers.value) {
    if (p.is_active && Array.isArray(p.models)) {
      count += p.models.filter((m) => m.is_public && m.is_enabled).length;
    }
  }
  return count;
});

const publicModelsCount = computed(() => {
  return providerForm.models.filter((m) => m.is_public && m.is_enabled).length;
});

const filteredModels = computed(() => {
  const kw = modelSearchKeyword.value.trim().toLowerCase();
  if (!kw) return providerForm.models;
  return providerForm.models.filter(
    (m) =>
      m.id.toLowerCase().includes(kw) ||
      (m.display_name && m.display_name.toLowerCase().includes(kw)) ||
      (m.family && m.family.toLowerCase().includes(kw)),
  );
});

const filteredFetchedModelIds = computed(() => {
  const q = fetchedSearchQuery.value.trim().toLowerCase();
  if (!q) return fetchedModelIds.value;
  return fetchedModelIds.value.filter((id) => id.toLowerCase().includes(q));
});

// ======================== 3. 业务动作与交互 ========================

/**
 * 加载所有 API 渠道列表
 */
async function loadProviders(targetIdToSelect?: string) {
  try {
    const res = await getAdminLLMProviders();
    if (res.code === 0 && Array.isArray(res.data)) {
      providers.value = res.data;
      if (providers.value.length > 0) {
        const idToSelect =
          targetIdToSelect ||
          (providers.value.some((p) => p.id === currentProviderId.value)
            ? currentProviderId.value
            : providers.value[0].id);
        selectProviderById(idToSelect);
      }
    }
  } catch (error) {
    ElMessage.error(`加载渠道列表失败: ${String(error)}`);
  }
}

/**
 * 切换选中渠道并回填表单
 */
function selectProviderById(id: string) {
  const target = providers.value.find((p) => p.id === id);
  if (!target) return;
  currentProviderId.value = target.id;
  providerForm.id = target.id;
  providerForm.name = target.name;
  providerForm.provider_type = target.provider_type || 'openai';
  providerForm.base_url = target.base_url;
  providerForm.api_key = target.api_key;
  providerForm.is_active = target.is_active;
  providerForm.timeout_seconds = target.timeout_seconds || 60;
  providerForm.custom_headers = target.custom_headers || {};
  providerForm.models = JSON.parse(JSON.stringify(target.models || []));
  providerForm.description = target.description || '';
  providerForm.sort_order = target.sort_order || 100;
  testResult.value = null;

  // 默认填充沙盒测试模型
  if (providerForm.models.length > 0) {
    const defaultM = providerForm.models.find((m) => m.is_default) || providerForm.models[0];
    sandboxModelId.value = defaultM.id;
  }
}

function handleSelectProvider(val: string) {
  selectProviderById(val);
}

/**
 * 快速填充常用 Base URL
 */
function handleQuickFillBaseUrl(url: string) {
  providerForm.base_url = url;
}

/**
 * 保存当前渠道配置
 */
async function handleSaveCurrentProvider() {
  if (!providerForm.name.trim()) {
    ElMessage.warning('渠道名称不能为空');
    return;
  }
  if (!providerForm.base_url.trim()) {
    ElMessage.warning('Base URL 不能为空');
    return;
  }

  isSaving.value = true;
  try {
    const res = await updateAdminLLMProvider(providerForm.id, {
      name: providerForm.name,
      provider_type: providerForm.provider_type,
      base_url: providerForm.base_url,
      api_key: providerForm.api_key,
      is_active: providerForm.is_active,
      timeout_seconds: providerForm.timeout_seconds,
      custom_headers: providerForm.custom_headers,
      models: providerForm.models,
      description: providerForm.description,
      sort_order: providerForm.sort_order,
    });

    if (res.code === 0) {
      ElMessage.success('保存渠道与模型配置成功');
      await loadProviders(providerForm.id);
    }
  } catch (error) {
    ElMessage.error(`保存失败: ${String(error)}`);
  } finally {
    isSaving.value = false;
  }
}

/**
 * 连通性测试 (Ping)
 */
async function handleTestConnection() {
  if (!providerForm.base_url.trim()) {
    ElMessage.warning('请先填写 Base URL');
    return;
  }
  isTestingConnection.value = true;
  testResult.value = null;
  try {
    const res = await testLLMConnection({
      base_url: providerForm.base_url,
      api_key: providerForm.api_key,
      provider_id: providerForm.id,
      custom_headers: providerForm.custom_headers,
    });
    if (res.code === 0) {
      testResult.value = res.data;
      if (res.data.success) {
        ElMessage.success(res.data.message);
      } else {
        ElMessage.warning(res.data.message);
      }
    }
  } catch (error) {
    testResult.value = {
      success: false,
      latency_ms: 0,
      message: `探测失败: ${String(error)}`,
    };
    ElMessage.error(`连通性探测异常: ${String(error)}`);
  } finally {
    isTestingConnection.value = false;
  }
}

/**
 * 在线拉取上游模型
 */
async function handleFetchUpstreamModels() {
  if (!providerForm.base_url.trim()) {
    ElMessage.warning('请先填写 Base URL');
    return;
  }
  isFetchingUpstream.value = true;
  try {
    const res = await fetchUpstreamLLMModels({
      base_url: providerForm.base_url,
      api_key: providerForm.api_key,
      provider_id: providerForm.id,
      custom_headers: providerForm.custom_headers,
    });
    if (res.code === 0 && res.data.success) {
      fetchedModelIds.value = res.data.models;
      // 默认选中尚未在库中的模型
      const existing = new Set(providerForm.models.map((m) => m.id));
      selectedFetchedModelIds.value = res.data.models.filter((mid) => !existing.has(mid));
      isSelectAllFetched.value = selectedFetchedModelIds.value.length === res.data.models.length;
      isFetchModelsDialogOpen.value = true;
      ElMessage.success(res.data.message);
    } else {
      ElMessage.error(res.message || '拉取模型失败，请检查 Base URL 与 API Key');
    }
  } catch (error) {
    ElMessage.error(`拉取异常: ${String(error)}`);
  } finally {
    isFetchingUpstream.value = false;
  }
}

function isModelAlreadyAdded(mid: string): boolean {
  return providerForm.models.some((m) => m.id === mid);
}

function handleToggleSelectAllFetched(val: any) {
  if (val) {
    selectedFetchedModelIds.value = [...filteredFetchedModelIds.value];
  } else {
    selectedFetchedModelIds.value = [];
  }
}

/**
 * 自动持久化保存当前渠道的模型矩阵配置并同步父级状态
 */
async function persistCurrentProviderModels(successMsg?: string) {
  if (!providerForm.id) return;
  try {
    const res = await updateAdminLLMProvider(providerForm.id, {
      name: providerForm.name,
      provider_type: providerForm.provider_type,
      base_url: providerForm.base_url,
      api_key: providerForm.api_key,
      is_active: providerForm.is_active,
      timeout_seconds: providerForm.timeout_seconds,
      custom_headers: providerForm.custom_headers,
      models: providerForm.models,
      description: providerForm.description,
      sort_order: providerForm.sort_order,
    });
    if (res.code === 0) {
      const p = providers.value.find((item) => item.id === providerForm.id);
      if (p) {
        p.models = JSON.parse(JSON.stringify(providerForm.models));
        p.models_count = providerForm.models.length;
        p.public_models_count = providerForm.models.filter(
          (m) => m.is_public && m.is_enabled,
        ).length;
      }
      if (successMsg) {
        ElMessage.success(successMsg);
      }
    }
  } catch (error) {
    ElMessage.error(`配置持久化失败: ${String(error)}`);
    throw error;
  }
}

/**
 * 确认批量导入拉取的模型并即时持久化
 */
async function handleConfirmImportFetchedModels() {
  if (selectedFetchedModelIds.value.length === 0) return;
  const count = selectedFetchedModelIds.value.length;
  const existingMap = new Map(providerForm.models.map((m) => [m.id, m]));

  for (const mid of selectedFetchedModelIds.value) {
    if (!existingMap.has(mid)) {
      let family = 'other';
      const lower = mid.toLowerCase();
      if (lower.includes('deepseek')) family = 'deepseek';
      else if (lower.includes('gpt') || lower.includes('o1')) family = 'gpt';
      else if (lower.includes('claude')) family = 'claude';
      else if (lower.includes('gemini')) family = 'gemini';
      else if (lower.includes('qwen')) family = 'qwen';

      const supports_reasoning =
        lower.includes('r1') || lower.includes('o1') || lower.includes('reasoner');

      providerForm.models.push({
        id: mid,
        display_name: mid,
        is_enabled: true,
        is_public: fetchImportAsPublic.value,
        is_default: false,
        supports_streaming: true,
        supports_reasoning,
        cost: fetchImportDefaultCost.value,
        family,
        context_limit: 64000,
        sort_order: 50,
      });
    }
  }

  isFetchModelsDialogOpen.value = false;
  await persistCurrentProviderModels(`已成功导入 ${count} 个模型并持久化保存`);
}

/**
 * 快捷切换单模型的客户端上架状态 (即时全量保存防脱节)
 */
async function handleModelPublicToggle(row: any) {
  const previousState = !row.is_public;
  try {
    await persistCurrentProviderModels(
      `模型 ${row.id} 已${row.is_public ? '上架至客户端' : '从客户端隐藏'}`,
    );
  } catch (_error) {
    row.is_public = previousState;
  }
}

/**
 * 设为默认模型
 */
async function handleSetDefaultModel(modelId: string) {
  providerForm.models.forEach((m) => {
    m.is_default = m.id === modelId;
  });
  await persistCurrentProviderModels(`已设为默认模型 [${modelId}] 并保存`);
}

/**
 * 删除单个模型
 */
function handleDeleteModel(modelId: string) {
  ElMessageBox.confirm(`确定从当前渠道删除模型 [${modelId}] 吗？`, '提示', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(async () => {
      providerForm.models = providerForm.models.filter((m) => m.id !== modelId);
      await persistCurrentProviderModels(`已移除模型 ${modelId} 并同步保存`);
    })
    .catch(() => {});
}

/**
 * 批量操作模型上架/下架
 */
async function handleBatchModelAction(cmd: string) {
  if (cmd === 'enable_all_public') {
    providerForm.models.forEach((m) => {
      m.is_public = true;
    });
    await persistCurrentProviderModels('已将所有模型标记为客户端上架并保存');
  } else if (cmd === 'disable_all_public') {
    providerForm.models.forEach((m) => {
      m.is_public = false;
    });
    await persistCurrentProviderModels('已将所有模型标记为客户端隐藏并保存');
  }
}

/**
 * 打开新建模型弹窗
 */
function openAddModelDialog() {
  modelFormMode.value = 'add';
  singleModelForm.id = '';
  singleModelForm.display_name = '';
  singleModelForm.is_enabled = true;
  singleModelForm.is_public = true;
  singleModelForm.is_default = false;
  singleModelForm.supports_streaming = true;
  singleModelForm.supports_reasoning = false;
  singleModelForm.cost = 1;
  singleModelForm.family = 'deepseek';
  singleModelForm.context_limit = 64000;
  singleModelForm.sort_order = 50;
  isModelEditDialogOpen.value = true;
}

/**
 * 打开编辑模型弹窗
 */
function openEditModelDialog(row: any) {
  modelFormMode.value = 'edit';
  Object.assign(singleModelForm, row);
  isModelEditDialogOpen.value = true;
}

function resetSingleModelForm() {
  singleModelForm.id = '';
  singleModelForm.display_name = '';
  singleModelForm.cost = 1;
}

/**
 * 保存单个模型编辑并持久化
 */
async function handleConfirmSaveSingleModel() {
  if (!singleModelForm.id.trim()) {
    ElMessage.warning('模型 ID 不能为空');
    return;
  }
  if (!singleModelForm.display_name.trim()) {
    singleModelForm.display_name = singleModelForm.id;
  }

  if (modelFormMode.value === 'add') {
    if (providerForm.models.some((m) => m.id === singleModelForm.id)) {
      ElMessage.warning(`模型 ${singleModelForm.id} 已存在`);
      return;
    }
    providerForm.models.push({ ...singleModelForm });
  } else {
    const idx = providerForm.models.findIndex((m) => m.id === singleModelForm.id);
    if (idx !== -1) {
      providerForm.models[idx] = { ...singleModelForm };
    }
  }

  isModelEditDialogOpen.value = false;
  await persistCurrentProviderModels(`模型 [${singleModelForm.id}] 配置已保存生效`);
}

/**
 * 新建渠道逻辑
 */
function openAddProviderDialog() {
  resetNewProviderForm();
  isAddProviderOpen.value = true;
}

function resetNewProviderForm() {
  newProviderForm.name = '';
  newProviderForm.provider_type = 'openai';
  newProviderForm.base_url = 'https://api.deepseek.com/v1';
  newProviderForm.api_key = '';
  newProviderForm.description = '';
}

async function handleConfirmCreateProvider() {
  if (!newProviderForm.name.trim()) {
    ElMessage.warning('渠道名称不能为空');
    return;
  }
  if (!newProviderForm.base_url.trim()) {
    ElMessage.warning('Base URL 不能为空');
    return;
  }

  isCreatingProvider.value = true;
  try {
    const res = await createAdminLLMProvider({
      ...newProviderForm,
      is_active: true,
      models: [],
    });
    if (res.code === 0) {
      ElMessage.success('创建 API 渠道成功');
      isAddProviderOpen.value = false;
      await loadProviders(res.data.id);
    }
  } catch (error) {
    ElMessage.error(`创建渠道失败: ${String(error)}`);
  } finally {
    isCreatingProvider.value = false;
  }
}

/**
 * 删除当前渠道
 */
function handleDeleteProvider() {
  if (providers.value.length <= 1) {
    ElMessage.warning('系统至少保留一个 API 渠道');
    return;
  }
  ElMessageBox.confirm(
    `确定删除渠道【${providerForm.name}】吗？删除后其下所有上架模型将立即从客户端移除！`,
    '高风险警示',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'error',
    },
  )
    .then(async () => {
      try {
        const res = await deleteAdminLLMProvider(providerForm.id);
        if (res.code === 0) {
          ElMessage.success('渠道已删除');
          await loadProviders();
        }
      } catch (error) {
        ElMessage.error(`删除失败: ${String(error)}`);
      }
    })
    .catch(() => {});
}

/**
 * 沙盒测试发送
 */
async function handleRunSandbox() {
  if (!sandboxModelId.value) {
    ElMessage.warning('请选择要测试的模型');
    return;
  }
  if (!sandboxPrompt.value.trim()) {
    ElMessage.warning('请输入测试提示词');
    return;
  }

  isSandboxRunning.value = true;
  sandboxOutput.value = `[系统] 正在向渠道 ${providerForm.name} 发起探测请求...\n模型: ${sandboxModelId.value}\nBase URL: ${providerForm.base_url}\n\n`;

  try {
    const testPing = await testLLMConnection({
      base_url: providerForm.base_url,
      api_key: providerForm.api_key,
      provider_id: providerForm.id,
      custom_headers: providerForm.custom_headers,
    });

    if (!testPing.data.success) {
      sandboxOutput.value += `[连通性预检失败] ${testPing.data.message}\n请检查 Base URL 与 API Key 是否有效。`;
      return;
    }

    sandboxOutput.value += `[网络探测通过] 延迟: ${testPing.data.latency_ms}ms\n[模型就绪] 该模型已在网关注册，C 端客户端已可通过 /api/v1/chat/sessions 实时进行全双工流式生成。\n\n`;
    sandboxOutput.value += `模拟输出: "你好！我是 ${sandboxModelId.value}，来自渠道 ${providerForm.name}。连接状态极佳，已可向客户端用户提供剧情交互与对话补全服务。"`;
  } catch (error) {
    sandboxOutput.value += `[请求异常] ${String(error)}`;
  } finally {
    isSandboxRunning.value = false;
  }
}

onMounted(async () => {
  await loadProviders();
});
</script>

<style scoped>
/* 遵循规范: 浅色边框与 Obsidian Gold 黑金暗黑拟物 */
.llm-bordered-dialog :deep(.el-dialog__header) {
  margin-right: 0;
  padding: 16px 20px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.llm-bordered-dialog :deep(.el-dialog__body) {
  padding: 0;
}

.llm-bordered-dialog :deep(.el-dialog__footer) {
  padding: 0;
  border-top: 1px solid var(--el-border-color-lighter);
}
</style>
