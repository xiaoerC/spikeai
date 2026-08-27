---
name: frontend-api-sse-state
description: 前端强类型 API 客户端、SSE 流式打字机交互与 Pinia 状态流转大厂最佳实践指南。用于前后端联调、流式 Token 渲染、状态持久化与网络容灾。仅限在 frontend/ 作用域生效。
license: MIT
file_patterns:
  - "frontend/src/services/**/*"
  - "frontend/src/stores/**/*"
  - "frontend/src/composables/**/*stream*"
  - "frontend/src/views/chat/**/*"
triggers:
  - "API client"
  - "Axios interceptor"
  - "SSE streaming"
  - "Chat stream"
  - "Pinia store"
  - "State persistence"
  - "Typewriter effect"
---

# 前端 API 契约、SSE 流式交互与 Pinia 状态流转最佳实践指南

本指南为 SpikeAI / 叙梦 Naro 前端工程在进入**业务联调、SSE 流式对话与复杂状态流转**阶段时提供大厂级标准范式，确保网络请求强类型化、流式渲染丝滑（60fps）、状态单向流及网络异常防御。

---

## 一、 强类型 API 客户端规范 (`src/services/api.ts`)

### 1. 统一响应契约与泛型包装
所有网络请求必须使用强类型泛型包装，严格匹配后端 FastAPI Pydantic 返回结构：

```ts
/**
 * 后端统一业务响应外壳
 */
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
  timestamp?: number
}

/**
 * 业务分页结构
 */
export interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  pageSize: number
  hasMore: boolean
}
```

### 2. Axios 拦截器与防御性错误处理
```ts
import axios from 'axios'
import type { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios'

export const apiClient: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截：自动注入 JWT Token
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('naro_auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截：全局业务码拦截与异常分发
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const res = response.data
    // 假设 200 为业务成功
    if (res.code === 200) {
      return res.data as any
    }
    
    // 402: 余额不足，分发事件唤起充值 Drawer
    if (res.code === 402) {
      window.dispatchEvent(new CustomEvent('naro:insufficient-balance'))
    }
    
    return Promise.reject(new Error(res.message || '业务请求失败'))
  },
  (error) => {
    if (error.response?.status === 401) {
      // 401: 登录失效，唤起登录 Modal
      window.dispatchEvent(new CustomEvent('naro:unauthorized'))
    }
    return Promise.reject(error)
  }
)
```

---

## 二、 SSE (Server-Sent Events) 打字机流式消费规范

在沉浸式对话剧场中，后端通过 SSE 流式输出 LLM 生成的内容。为避免高频响应式触发导致 Vue 视图重排卡顿，必须遵循以下标准：

### 1. 流式调度 Composable (`src/composables/useChatStream.ts`)
- **使用 `fetch` + `ReadableStreamDefaultReader` + `AbortController`** 支持用户随时点击“停止生成”。
- **`requestAnimationFrame` 缓冲队列机制**：将流式接收到的文本放入队列，以 60fps 平滑消费，杜绝界面撕裂与掉帧。

```ts
import { ref, readonly } from 'vue'

export interface StreamOptions {
  onToken?: (token: string) => void
  onComplete?: (fullText: string) => void
  onError?: (err: Error) => void
}

export function useChatStream() {
  const isStreaming = ref(false)
  const streamedContent = ref('')
  let abortController: AbortController | null = null

  const startStream = async (url: string, payload: unknown, options: StreamOptions = {}) => {
    if (isStreaming.value) return
    
    isStreaming.value = true
    streamedContent.value = ''
    abortController = new AbortController()

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('naro_auth_token') || ''}`,
        },
        body: JSON.stringify(payload),
        signal: abortController.signal,
      })

      if (!response.ok || !response.body) {
        throw new Error(`SSE 连接失败: ${response.statusText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let done = false
      let buffer = ''

      while (!done) {
        const { value, done: streamDone } = await reader.read()
        done = streamDone
        if (value) {
          const chunk = decoder.decode(value, { stream: true })
          buffer += chunk
          
          // 解析 SSE data: 行
          const lines = buffer.split('\n')
          buffer = lines.pop() || ''

          for (const line of lines) {
            const trimmed = line.trim()
            if (trimmed.startsWith('data:')) {
              const dataStr = trimmed.replace(/^data:\s*/, '')
              if (dataStr === '[DONE]') break
              
              try {
                const parsed = JSON.parse(dataStr)
                const textChunk = parsed.delta || parsed.content || ''
                streamedContent.value += textChunk
                options.onToken?.(textChunk)
              } catch {
                // 处理非 JSON 纯文本流
                streamedContent.value += dataStr
                options.onToken?.(dataStr)
              }
            }
          }
        }
      }

      options.onComplete?.(streamedContent.value)
    } catch (err: any) {
      if (err.name === 'AbortError') {
        console.log('用户手动终止了流式生成')
      } else {
        options.onError?.(err)
      }
    } finally {
      isStreaming.value = false
      abortController = null
    }
  }

  const stopStream = () => {
    if (abortController) {
      abortController.abort()
      isStreaming.value = false
    }
  }

  return {
    isStreaming: readonly(isStreaming),
    streamedContent: readonly(streamedContent),
    startStream,
    stopStream,
  }
}
```

---

## 三、 Pinia 复杂状态分层与持久化规范

### 1. 组合式语法与状态保护
所有 Store 统一采用 `defineStore(name, () => { ... })` 组合式语法，核心状态通过 `readonly` 暴露，仅允许通过 Action 变更：

```ts
// src/stores/wallet.ts
import { defineStore } from 'pinia'
import { ref, computed, readonly } from 'vue'

export const useWalletStore = defineStore('wallet', () => {
  // 1. 内部状态
  const starCoins = ref(0)       // 星元★ (付费)
  const moonEssence = ref(0)     // 月华🌙 (免费)
  const isLoading = ref(false)

  // 2. 计算属性
  const totalBalance = computed(() => starCoins.value + moonEssence.value)

  // 3. Actions 事务变更
  const fetchBalance = async () => {
    isLoading.value = true
    try {
      // 调用 API 更新
    } finally {
      isLoading.value = false
    }
  }

  const deductOptimistic = (starCost: number, moonCost: number) => {
    // 乐观扣费更新，失败时回滚
    starCoins.value = Math.max(0, starCoins.value - starCost)
    moonEssence.value = Math.max(0, moonEssence.value - moonCost)
  }

  return {
    // 导出只读状态与必要 actions
    starCoins: readonly(starCoins),
    moonEssence: readonly(moonEssence),
    isLoading: readonly(isLoading),
    totalBalance,
    fetchBalance,
    deductOptimistic,
  }
})
```

### 2. 状态持久化（IndexedDB / LocalStorage）
- 针对用户已导入的巨大 SillyTavern 角色卡库与长篇历史分支，**禁止塞入 LocalStorage**（容量仅 5MB 且同步阻塞）。
- 必须使用 `@vueuse/core` 中的 `useIDBKeyval` 或 `localforage` 存储在异步 IndexedDB 中。

---

## 四、 大厂级联调 4 大禁止反模式

1. ❌ **严禁在组件内直接写裸 `fetch` 或 `axios.get`**：所有接口必须收敛在 `src/services/` 统一导出。
2. ❌ **严禁直接修改 Pinia 导出的 Ref 状态**：调用方禁止 `walletStore.starCoins = 100`，必须走 Action 方法。
3. ❌ **严禁静默吞掉网络异常**：`catch (e) {}` 必须显式展示 Toast、设置 `error` 状态或记录日志。
4. ❌ **严禁在 SSE 渲染中无节制调用 `nextTick` 强刷滚动**：滚动到底部必须使用节流（`throttle` / `requestAnimationFrame`），避免移动端卡顿。
