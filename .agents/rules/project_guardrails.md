---
description: NaroAI / SpikeAI 项目全局工程与 Agent 行为守则
always_on: true
---

# SpikeAI / NaroAI 全局工程守则

1. **中文交流**：使用中文与用户沟通和输出。
2. **强类型与文档注释**：编写或修改代码时，强制编写完整的类型标注（TypeScript / Python Type Hints）与详尽的文档注释（包含 Usage 示例）。
3. **防御编程**：严禁静默捕获异常（如空 `except:` 或空 `catch {}`），错误必须显式抛出或记录日志。
4. **最小侵入**：非任务相关的历史代码和注释必须完整保留，严禁无意义的大面积重构或格式化。
5. **依赖隔离**：前端使用 `pnpm`，后端使用 `uv` 虚拟环境，严禁污染全局环境。
6. **宁问勿猜**：遇到需求模糊或系统设计权衡时，先向用户提出针对性的问题澄清，达成共识后再开始编码。
7. **Karpathy Guidelines 实践**：
   - Think Before Coding（思考先行）
   - Simplicity First（极简实现，拒绝过度设计）
   - Surgical Changes（手术刀式精准修改）
   - Goal-Driven Execution（可验证的目标闭环）
