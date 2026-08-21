/**
 * 更多模型页面 1:1 Figma 原型 Mock 数据常量与类型定义
 *
 * @packageDocumentation
 */

export interface ModelChannelItem {
  id: string;
  name: string;
  familyId: string;
  category: "normal" | "advanced" | "infinite";
  health: number; // 90, 73, etc.
  starCost: number;
  moonCost: number;
  isFavorite: boolean;
}

export interface ModelFamilyItem {
  id: string;
  name: string;
  channelCount: number;
  indicatorColor: string; // "#EAB308", "#3B82F6", "#22C55E"
  models: ModelChannelItem[];
}

export const MOCK_MODEL_FAMILIES: ModelFamilyItem[] = [
  {
    id: "gpt",
    name: "GPT",
    channelCount: 2,
    indicatorColor: "#EAB308",
    models: [
      {
        id: "gpt-5.5-m-v1",
        name: "gpt-5.5-m-v1",
        familyId: "gpt",
        category: "advanced",
        health: 90,
        starCost: 30,
        moonCost: 30,
        isFavorite: false,
      },
      {
        id: "gpt-5.5-m-v2",
        name: "gpt-5.5-m-v2",
        familyId: "gpt",
        category: "advanced",
        health: 73,
        starCost: 30,
        moonCost: 30,
        isFavorite: false,
      },
    ],
  },
  {
    id: "deep-whale-4",
    name: "深海蓝鲸4",
    channelCount: 3,
    indicatorColor: "#EAB308",
    models: [
      {
        id: "deep-whale-4-turbo",
        name: "deep-whale-4-turbo",
        familyId: "deep-whale-4",
        category: "advanced",
        health: 95,
        starCost: 25,
        moonCost: 25,
        isFavorite: false,
      },
      {
        id: "deep-whale-4-pro",
        name: "deep-whale-4-pro",
        familyId: "deep-whale-4",
        category: "advanced",
        health: 88,
        starCost: 35,
        moonCost: 35,
        isFavorite: false,
      },
    ],
  },
  {
    id: "super-gemini-2",
    name: "超级双子星2",
    channelCount: 5,
    indicatorColor: "#EAB308",
    models: [
      {
        id: "gemini-2-pro",
        name: "gemini-2.0-pro",
        familyId: "super-gemini-2",
        category: "advanced",
        health: 99,
        starCost: 20,
        moonCost: 20,
        isFavorite: false,
      },
    ],
  },
  {
    id: "domestic",
    name: "国产",
    channelCount: 4,
    indicatorColor: "#EAB308",
    models: [
      {
        id: "glm-5.2-o1",
        name: "glm-5.2-o1",
        familyId: "domestic",
        category: "advanced",
        health: 97,
        starCost: 30,
        moonCost: 30,
        isFavorite: true,
      },
      {
        id: "ds4f-official",
        name: "ds4f-官",
        familyId: "domestic",
        category: "normal",
        health: 97,
        starCost: 15,
        moonCost: 15,
        isFavorite: false,
      },
    ],
  },
  {
    id: "super-gemini-3",
    name: "超级双子星3",
    channelCount: 3,
    indicatorColor: "#EAB308",
    models: [],
  },
  {
    id: "super-gemini-3-1",
    name: "超级双子星3.1",
    channelCount: 9,
    indicatorColor: "#EAB308",
    models: [],
  },
  {
    id: "grok",
    name: "Grok",
    channelCount: 3,
    indicatorColor: "#3B82F6",
    models: [],
  },
  {
    id: "fast-gemini",
    name: "快速双子星",
    channelCount: 9,
    indicatorColor: "#3B82F6",
    models: [],
  },
  {
    id: "super-claude",
    name: "超级小克",
    channelCount: 5,
    indicatorColor: "#EAB308",
    models: [],
  },
  {
    id: "super-claude-opus-4-6",
    name: "超级小克Opus-4-6",
    channelCount: 16,
    indicatorColor: "#EAB308",
    models: [],
  },
  {
    id: "super-claude-opus-4-7",
    name: "超级小克Opus-4-7",
    channelCount: 9,
    indicatorColor: "#EAB308",
    models: [],
  },
  {
    id: "super-claude-opus-4-8",
    name: "超级小克Opus-4-8",
    channelCount: 4,
    indicatorColor: "#EAB308",
    models: [],
  },
  {
    id: "super-claude-opus-5",
    name: "超级小克Opus-5",
    channelCount: 3,
    indicatorColor: "#EAB308",
    models: [],
  },
  {
    id: "member-exclusive",
    name: "次卡专属",
    channelCount: 3,
    indicatorColor: "#22C55E",
    models: [],
  },
];
