/**
 * 角色卡详情 1:1 Figma 原型 Mock 数据常量与类型定义
 *
 * @packageDocumentation
 */

export interface CharacterDetailData {
  id: string;
  name: string;
  avatarUrl: string;
  bannerUrl: string;
  status: "published" | "draft";
  isOriginal: boolean;

  // 10 项数据指标
  metrics: {
    hotness: string; // 20.5k
    likes: number; // 32
    favorites: number; // 6
    imports: number; // 105
    uses: number; // 16235
    uniquePlayers: number; // 21
    totalChats: number; // 425
    deepPlays: number; // 4
    avgCost: number; // 773.1
    totalTokens: string; // 10.0M
  };

  // 核心资产
  settingsWordCount: string; // 15,003
  worldBookCount: number; // 5

  // 序幕
  prologue: {
    title: string;
    description: string;
    html?: string;
    worldInfo: string;
    charactersInfo: string;
  };

  // 作者信息
  author: {
    id: string;
    name: string;
    avatarUrl: string;
    followersCount: number;
    isFollowed: boolean;
  };

  // 标签
  tags: string[];

  // 描述
  description: string;

  // 详细元数据
  meta: {
    createdAt: string;
    updatedAt: string;
    version: string;
    visibility: string;
  };
}

export const MOCK_CHARACTER_DETAIL: CharacterDetailData = {
  id: "c1",
  name: "深夜甜品店｜知性前辈×慌张店员",
  avatarUrl:
    "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=400&auto=format&fit=crop&q=80",
  bannerUrl:
    "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80",
  status: "published",
  isOriginal: true,
  metrics: {
    hotness: "20.5k",
    likes: 32,
    favorites: 6,
    imports: 105,
    uses: 16235,
    uniquePlayers: 21,
    totalChats: 425,
    deepPlays: 4,
    avgCost: 773.1,
    totalTokens: "10.0M",
  },
  settingsWordCount: "15,003",
  worldBookCount: 5,
  prologue: {
    title: "Dolce Notte",
    description: "藏在老街区深处的一间不太好找的店。",
    worldInfo:
      "一间只在深夜营业的手工甜品工坊。店内弥漫着焦糖与香草的微暖气息，雨夜的街道格外安静。",
    charactersInfo: "知性温柔的店长前辈与刚刚入职还略显慌乱的兼职店员，两人的命运在深夜悄然交织。",
  },
  author: {
    id: "author_xxyy",
    name: "XXYY",
    avatarUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=XXYY",
    followersCount: 178,
    isFollowed: false,
  },
  tags: ["#都市", "#纯爱", "#御姐", "#校园", "#NTR"],
  description:
    "【双女主/可纯爱可涩涩】深夜不打烊的甜品店，温柔知性的经理与明亮活泼的兼职学妹。当街角的雨声响起，推开挂着风铃的木门，浓郁的甜香与未完的故事正在等待你的选择。",
  meta: {
    createdAt: "2026/5/5",
    updatedAt: "2026/8/19",
    version: "1.0",
    visibility: "公开",
  },
};
