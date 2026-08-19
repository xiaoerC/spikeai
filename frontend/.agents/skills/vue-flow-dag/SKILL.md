---
name: vue-flow-dag
description: Vue Flow (@vue-flow/core) 剧情分支树拓扑与自适应排版规范。用于沉浸式对话剧场的分支可视化、节点分叉切换与手势交互。
license: MIT
file_patterns:
  - "frontend/**/*flow*"
  - "frontend/**/*tree*"
  - "frontend/**/*dag*"
triggers:
  - "Vue Flow"
  - "Story branch DAG"
  - "Dagre layout"
  - "Branch node"
---

# Vue Flow 剧情分支拓扑与自适应排版规范

在 Narratium 沉浸剧场中，对话历史并非简单的线性列表，而是支持多结局回滚与分叉的 **DAG 剧情树**。使用 `@vue-flow/core` 构建可视化画布时需严格遵循以下规范。

---

## 一、 核心架构与状态优化 (`shallowRef`)

由于剧情树可能包含上百个对话节点与连线，严禁使用全量深层 `reactive`，必须使用 `shallowRef` 并通过 `markRaw` 包装自定义组件：

```vue
<script setup lang="ts">
import { shallowRef, ref, onMounted, markRaw } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import type { Node, Edge } from '@vue-flow/core'
import StoryNode from '@/components/chat/flow/StoryNode.vue'

// 注册自定义剧情节点组件 (使用 markRaw 避免重复响应式包装)
const nodeTypes = {
  storyNode: markRaw(StoryNode)
}

// 节点与边数据
const nodes = shallowRef<Node[]>([])
const edges = shallowRef<Edge[]>([])

const { fitView, zoomTo, onNodeClick } = useVueFlow()

onNodeClick(({ node }) => {
  // 切换到对应分支的上下文
  console.log('选择剧情节点:', node.id)
})
</script>

<template>
  <div class="w-full h-full bg-black/60 relative">
    <VueFlow
      v-model:nodes="nodes"
      v-model:edges="edges"
      :node-types="nodeTypes"
      :default-viewport="{ zoom: 0.85 }"
      :min-zoom="0.2"
      :max-zoom="2"
      :pan-on-drag="true"
      :prevent-scrolling="false"
      class="gold-flow-canvas"
    />
  </div>
</template>
```

---

## 二、 Dagre 自动排版算法 (Auto-Layout)

当新增分支或重 Roll 生成新版本（Swipe）时，通过 `@dagrejs/dagre` 自动计算节点的 `(x, y)` 空间坐标：

```ts
import dagre from '@dagrejs/dagre'
import type { Node, Edge } from '@vue-flow/core'

/**
 * 剧情分支 DAG 树自适应排版 (自顶向下 Top-to-Bottom)
 */
export function layoutStoryTree(
  nodes: Node[],
  edges: Edge[],
  direction: 'TB' | 'LR' = 'TB'
): { nodes: Node[]; edges: Edge[] } {
  const dagreGraph = new dagre.graphlib.Graph()
  dagreGraph.setDefaultEdgeLabel(() => ({}))

  // 配置节点间距与对齐方式
  dagreGraph.setGraph({
    rankdir: direction,
    nodesep: 40,  // 同层节点间距
    ranksep: 60,  // 层与层间距
  })

  // 1. 设置节点尺寸 (固定卡片尺寸: 宽 220px, 高 100px)
  nodes.forEach((node) => {
    dagreGraph.setNode(node.id, { width: 220, height: 100 })
  })

  // 2. 设置连线
  edges.forEach((edge) => {
    dagreGraph.setEdge(edge.source, edge.target)
  })

  // 3. 执行排版计算
  dagre.layout(dagreGraph)

  // 4. 返回计算好的坐标
  const layoutedNodes = nodes.map((node) => {
    const nodeWithPosition = dagreGraph.node(node.id)
    return {
      ...node,
      position: {
        x: nodeWithPosition.x - 110,
        y: nodeWithPosition.y - 50,
      },
    }
  })

  return { nodes: layoutedNodes, edges }
}
```

---

## 三、 黑金拟物连线与移动端防穿透

1. **连线样式 (Edge Styling)**：
   * 采用发光暗金贝塞尔曲线（`type="smoothstep"` 或 `type="default"`），激活路径使用亮金色脉冲高光。
2. **移动端 Touch 处理**：
   * 在 BottomSheet 抽屉内嵌画布时，将画布容器设置 `touch-action: pan-x pan-y`，禁止双指缩放触发移动端整个网页的默认拉伸缩放行为。
