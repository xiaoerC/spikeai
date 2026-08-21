/**
 * 帮助中心官方文档高保真 Mock 数据源
 *
 * @packageDocumentation
 */

import type { CommandItem, FaqItem, HelpStep } from "@/views/help/types";

export const MOCK_GUIDE_STEPS: HelpStep[] = [
  {
    id: "step-01",
    stepNumber: "01",
    title: "使用推荐浏览器进行游玩",
    description:
      "推荐使用 Chrome 或 Edge 浏览器访问叙梦，可以降低页面显示异常、功能按钮失效等兼容性问题发生的概率。",
    badges: ["推荐浏览器：Chrome", "推荐浏览器：Edge"],
  },
  {
    id: "step-02",
    stepNumber: "02",
    title: "选择模型与文风",
    description: "",
    subsections: [
      {
        subtitle: "2.1 选择模型，开始对话",
        detail:
          "不同模型适合不同的剧情节奏和表达方式。第一次使用时，可以先选择自己感兴趣的角色，再根据实际聊天体验调整模型。",
      },
      {
        subtitle: "2.2 选择文风，品尝不同风味",
        detail: "根据剧情需求选择或变更文风：",
        scenarios: [
          {
            name: "场景 01",
            desc: "使用超级小克，但剧情总在同一个场景反复转悠，节奏太慢。",
            match: "可以匹配「织梦2.0 加速」",
          },
          {
            name: "场景 02",
            desc: "正在进行恋爱剧情，不希望突然出现第三者或怪物制造冲突。",
            match: "可以匹配「梦语」，降低冲突感",
          },
        ],
      },
      {
        subtitle: "2.3 个性化文风与自由搭配",
        detail: "不想让系统自动匹配预设时，可以前往「用户中心 → 高级设置」，关闭自动切换预设。",
      },
    ],
  },
  {
    id: "step-03",
    stepNumber: "03",
    title: "不知道如何开展对话？",
    description:
      "如果很喜欢一张角色卡，却不知道该如何接话，可以使用 Naro 助手的「剧情延续」指令，让角色主动推进剧情，同时为你保留回应空间。",
    promptCommand: "(请角色主动推进剧情并给我留出反应空间)",
  },
  {
    id: "step-04",
    stepNumber: "04",
    title: "跑剧情太累？开启剧情辅助",
    description:
      "不想一直思考下一步如何推进时，可以开启剧情辅助。你只需要选择符合心意的选项，系统会帮助你继续当前剧情。",
  },
  {
    id: "step-05",
    stepNumber: "05",
    title: "让角色记住你们的故事",
    description:
      "开启记忆增强后，可以在对话过程中执行自动总结，将重要剧情、人物关系和关键约定整理成记忆区块。\n\n• 当对话出现记忆提示后，点击「自动总结」，系统会根据当前剧情形成记忆区块。\n• 总结后的记忆可以在「主控面板」中查看和管理。",
  },
  {
    id: "step-06",
    stepNumber: "06",
    title: "把叙梦添加到桌面",
    description:
      "如果觉得每次打开浏览器比较麻烦，可以将叙梦添加到桌面。之后通过快捷方式就能快速进入，获得接近 APP 的使用体验。",
    badges: ["Chrome", "Edge"],
    stepGuideList: [
      "使用 Chrome 打开叙梦。",
      "打开浏览器右上角的菜单。",
      "选择「添加到主屏幕」。",
      "确认名称后，桌面上会生成叙梦快捷方式。",
    ],
  },
];

export const MOCK_FAQS: FaqItem[] = [
  {
    id: "faq-001",
    question: "Token 消耗是如何计算的？",
    answer:
      "Token 计算基于输入提示词（包括角色设定、前置背景、历史消息）与模型生成的回复内容。不同模型费率略有不同，可在对话输入框上方查看当前模型的费率与剩余免费额度。",
  },
  {
    id: "faq-002",
    question: "如何导出角色卡为 SillyTavern 兼容格式？",
    answer:
      "在角色详情页或创建编辑页中，点击右上角菜单选择「导出 PNG 角色卡」，系统会自动将完整的 V2/V3 角色元数据以无损 tEXt/iTXt 块嵌入 PNG 头像中，可直接拖入酒馆导入。",
  },
  {
    id: "faq-003",
    question: "什么是剧情分支树（DAG）？",
    answer:
      "叙梦支持在任意对话节点创建新分支。点击消息气泡下方的「分支」按钮即可开启平行宇宙，你可以回溯探索不同的剧情走向而不会覆盖原有故事线。",
  },
];

export const MOCK_COMMANDS: CommandItem[] = [
  {
    id: "cmd-001",
    name: "主动剧情推进",
    category: "剧情把控",
    description: "当卡文或不知道如何回复时，让角色或旁白主动推进发展。",
    commandText: "(请角色主动推进剧情并给我留出反应空间)",
  },
  {
    id: "cmd-002",
    name: "深度心理与神态特写",
    category: "描写强化",
    description: "强化角色微表情、眼神流转与复杂心理独白描写。",
    commandText: "[系统指令：请深入细腻地刻画角色的微表情、肢体动作与隐秘内心活动]",
  },
  {
    id: "cmd-003",
    name: "插入环境旁白",
    category: "氛围烘托",
    description: "在对话中加入光影、声音与天气细节烘托沉浸感。",
    commandText: "[系统指令：在回复中增加对当前环境氛围、光影与背景声音的细腻描写]",
  },
];
