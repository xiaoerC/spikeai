/**
 * 个人中心 1:1 Figma 原型 Mock 数据常量
 *
 * @packageDocumentation
 */

export interface BadgeItem {
  id: string;
  name: string;
  color: string;
  bgColor?: string;
}

export interface UsageRecordItem {
  id: string;
  type: "月华消耗" | "星元消耗" | "充值获得" | "活动奖励";
  amount: number;
  description: string;
  targetCharacter: string;
  time: string;
  balance: number;
}

export const PROFILE_USER_DATA = {
  id: "691f250529d14f3b8e7",
  shortId: "ID: 691f2505...",
  username: "spikeTom",
  email: "1103560524@qq.com",
  avatarUrl: "https://api.dicebear.com/7.x/bottts/svg?seed=spikeTom",
  isOnline: true,
  vipLevel: "普通 naro",
  starCoins: 9,
  moonGems: 826,
  inviteCode: "NAR-5CWSPD",
  unreadNotices: 2,
};

export const PROFILE_BADGES: BadgeItem[] = [
  { id: "1", name: "星元萌动", color: "#FDE68A" },
  { id: "2", name: "超级Naro", color: "#FACC15" },
  { id: "3", name: "梦的点灯人", color: "#FACC15" },
  { id: "4", name: "月华初触", color: "#60A5FA" },
  { id: "5", name: "星梦闪耀", color: "#38BDF8" },
  { id: "6", name: "星尘旅人", color: "#FCD34D" },
  { id: "7", name: "星辉流动者", color: "#FBBF24" },
  { id: "8", name: "星河筑梦者", color: "#3B82F6" },
  { id: "9", name: "星海掌控者", color: "#F59E0B" },
  { id: "10", name: "星域之主", color: "#2563EB" },
  { id: "11", name: "星梦赞助者", color: "#FBBF24" },
];

export const PLAYER_LEVEL_DATA = {
  title: "梦境常客",
  level: 10,
  currentXp: 3363,
  nextLevelXp: 34359,
  progressPercentage: 9.8,
  totalXp: "59,792",
  moonGemsUsed: "11,935",
  starCoinsUsed: "26,001",
  vipUsage: "21,856",
  totalRecharged: "***",
};

export const CREATOR_LEVEL_DATA = {
  title: "叙事见习者",
  level: 1,
  currentXp: 0,
  nextLevelXp: 50,
  progressPercentage: 0.0,
  totalXp: "0",
  originalWorks: "0",
  worksUsage: "0",
  rewardStars: "0",
  rewardMoons: "0",
};

export const USAGE_RECORDS: UsageRecordItem[] = [
  {
    id: "rec_001",
    type: "月华消耗",
    amount: -25,
    description: "使用ds4p-o1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:56:43",
    balance: 826,
  },
  {
    id: "rec_002",
    type: "月华消耗",
    amount: -25,
    description: "使用ds4p-o1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:54:22",
    balance: 851,
  },
  {
    id: "rec_003",
    type: "月华消耗",
    amount: -25,
    description: "使用ds4p-o1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:52:18",
    balance: 876,
  },
  {
    id: "rec_004",
    type: "月华消耗",
    amount: -25,
    description: "使用ds4p-o1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:50:45",
    balance: 901,
  },
  {
    id: "rec_005",
    type: "月华消耗",
    amount: -25,
    description: "使用ds4p-o1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:49:02",
    balance: 926,
  },
  {
    id: "rec_006",
    type: "月华消耗",
    amount: -25,
    description: "使用ds4p-o1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:45:30",
    balance: 951,
  },
  {
    id: "rec_007",
    type: "月华消耗",
    amount: -25,
    description: "使用ds4p-o1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:41:25",
    balance: 976,
  },
  {
    id: "rec_008",
    type: "月华消耗",
    amount: -20,
    description: "使用快双3.7-F1模型消耗月华",
    targetCharacter: "当年白月光的雌小鬼女儿找你做爸爸活",
    time: "2026/08/17 23:40:05",
    balance: 1001,
  },
];
