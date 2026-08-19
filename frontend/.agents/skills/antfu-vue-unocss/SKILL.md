---
name: antfu-vue-unocss
description: Vue 3.5 + TypeScript + Vite 6 + UnoCSS 前端开发专家指南。包含 Script Setup 响应式解构、组件内注释功能域物理内聚、大厂级 Composable 编写 4 大铁律与 UnoCSS 原子化最佳实践。仅限在 frontend/ 作用域生效。
license: MIT
file_patterns:
  - "frontend/**/*.vue"
  - "frontend/**/*.ts"
  - "frontend/uno.config.ts"
  - "frontend/vite.config.ts"
triggers:
  - "Vue 3 component"
  - "UnoCSS styling"
  - "Composition API"
  - "Composable pattern"
  - "Pinia store"
---

# Antfu Style Vue 3.5 + UnoCSS + Composition API 大厂最佳实践

本规范基于 Anthony Fu 的工程实践、Vue 3.5 官方标准以及大厂（字节/腾讯/VueUse）组合式 API 架构准则制定。

---

## 一、 Vue 3.5+ 组件内编码与组织分级标准

### 1. Script Setup 与强类型响应式解构
- 强制使用 `<script setup lang="ts">`。
- 优先使用 Vue 3.5 响应式解构语法（Reactive Props Destructure）：
  ```vue
  <script setup lang="ts">
  interface Props {
    id: string
    name: string
    avatarUrl?: string
    isNsfw?: boolean
  }

  // Vue 3.5 官方带默认值的响应式解构 (解构后仍保持响应性)
  const { id, name, avatarUrl = '', isNsfw = false } = defineProps<Props>()

  const emit = defineEmits<{
    (e: 'select', id: string): void
  }>()
  </script>
  ```

### 2. 小型/常规组件（< 150 行）：【注释功能域】物理就近内聚
在单个组件内，**严禁**将所有 `ref` 堆顶部、所有 methods 堆中间、所有 `onMounted/watch` 堆底部（这属于 Options API 的回退思维）。
必须按**功能关注点（Feature Blocks）**划分注释块，将每个功能专属的变量、计算属性、方法及副作用在**物理位置上聚拢放置**：

```vue
<script setup lang="ts">
// ==================== 1. 外部依赖与基础设施 ====================
const route = useRoute()
const userStore = useUserStore()

// ==================== 2. 功能一：搜索过滤逻辑 ====================
const searchKeyword = ref('')
const filteredList = computed(() => {
  return list.value.filter(item => item.name.includes(searchKeyword.value))
})
const handleSearch = () => { /* 搜索处理 */ }
watch(searchKeyword, () => { /* 搜索联动 */ })

// ==================== 3. 功能二：分页与触底加载 ====================
const page = ref(1)
const isLoading = ref(false)
const loadMore = async () => { /* 异步加载 */ }
onMounted(() => { loadMore() })
</script>
```

---

## 二、 大厂级组合式函数（Composable / useXxx.ts）编写 4 大铁律

当组件逻辑超过 150 行或需要在多处复用时，必须抽离为独立的 `useXxx.ts`。编写 Composable 必须严格遵守以下 4 条铁律：

### 铁律 1: 入参灵活支持 `MaybeRefOrGetter<T>` + `toValue()`
参数既要支持普通值，也要支持 `Ref` 或 Getter 函数计算值，使用 Vue 3.3+ 内置的 `toValue` 规范解析：
```ts
import { toValue, type MaybeRefOrGetter } from 'vue'

export function useFetchData(url: MaybeRefOrGetter<string>) {
  const execute = async () => {
    // 无论是 'https://...' 还是 ref('https://...') 还是 () => props.url，均可安全解析
    const resolvedUrl = toValue(url)
    // 请求数据...
  }
}
```

### 铁律 2: 返回值必须是普通对象包裹 `ref`（支持安全解构）
❌ **严禁返回裸 `reactive` 对象**，否则调用方解构时会丢失响应性！
```ts
// ❌ 错误做法：解构后 count 失去响应性
export function useCounter() {
  const state = reactive({ count: 0 })
  return state 
}

// ✅ 大厂标准：返回包含 Ref 的普通对象，解构依然响应
export function useCounter() {
  const count = ref(0)
  const inc = () => count.value++
  return { count, inc }
}
```

### 铁律 3: 副作用与生命周期全闭环（自动销毁与清理）
Composable 内部注册的事件监听器、定时器、WebSocket 连接等，必须在自身内部通过 `onUnmounted` 或 `onScopeDispose` 销毁，杜绝内存泄漏：
```ts
import { onMounted, onUnmounted } from 'vue'

export function useWindowResize(callback: () => void) {
  onMounted(() => window.addEventListener('resize', callback))
  onUnmounted(() => window.removeEventListener('resize', callback)) // 👈 内部自动清理
}
```

### 铁律 4: 单向数据流与状态保护 (`readonly`)
如果状态只允许 Composable 内部逻辑修改，严禁外部直接赋值篡改，必须使用 `readonly` 对外暴露：
```ts
import { ref, readonly } from 'vue'

export function useAuth() {
  const user = ref<User | null>(null)

  const login = async (token: string) => { /* 内部修改 user.value */ }
  const logout = () => { user.value = null }

  return {
    user: readonly(user), // 👈 外部只能读取，不能 user.value = null
    login,
    logout
  }
}
```

---

## 三、 UnoCSS 原子化最佳实践

### 1. 组合与快捷方式 (Shortcuts)
- 保持模板干净，高频使用的黑金玻璃拟物样式必须抽象为 UnoCSS shortcuts（在 `uno.config.ts` 中定义）：
  ```ts
  export default defineConfig({
    shortcuts: {
      'gold-glass': 'bg-obsidian-surface/80 backdrop-blur-xl border border-obsidian-border rounded-xl shadow-glass',
      'btn-gold': 'bg-naro-gold text-[#0C0A09] font-bold px-4 py-2 rounded-xl shadow-gold active:scale-95 transition-all cursor-pointer',
      'pb-safe': 'pb-[env(safe-area-inset-bottom,0px)]',
    }
  })
  ```

### 2. 纯 CSS 图标方案
- 图标一律使用 `@unocss/preset-icons`（如 `i-carbon-chat`, `i-carbon-settings`），杜绝笨重的 svg 文件引入。
