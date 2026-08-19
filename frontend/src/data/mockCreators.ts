/**
 * 创作者专区真实高保真 Mock 数据源
 *
 * @packageDocumentation
 */

import type { CreatorItem } from "@/views/creator/types";

export const MOCK_CREATORS: CreatorItem[] = [
  {
    id: "creator-001",
    username: "萌羽不萌",
    avatarUrl:
      "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80",
    level: 27,
    levelBadgeColor: "#A78BFA",
    followersCount: "5.2K",
    interactionsCount: "20.8M",
    isFollowed: true,
    featuredWorks: [
      {
        id: "work-101",
        title: "西幻世界模拟器（增加11个剧情mod可以购买总计30万字）",
        coverUrl:
          "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        heat: "6149.3k",
        commentsCount: "138.4k",
        tokenUsage: "18157.6M",
        rating: 4.9,
        summary:
          "新增11个剧情和战斗mod可以购买，序幕更新地图🗺️，更新【四灾】，魔女化灾害、十位魔女，序幕可以看见，不懂的问村长。...",
        tags: ["#RPG", "#世界", "+3"],
        authorName: "@萌羽不萌",
      },
      {
        id: "work-102",
        title: "傲天版真实修仙模拟器",
        coverUrl:
          "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500&auto=format&fit=crop&q=80",
        heat: "4138.8k",
        commentsCount: "112.3k",
        tokenUsage: "8061.9M",
        rating: 5.0,
        summary:
          "群号1071140492偏向爽文版的游戏修仙，也可以体验最新版本的困难难度，新版真实修仙模拟器。注意是完整世界，淫道，魔...",
        tags: ["#RPG", "#世界", "+3"],
        authorName: "@萌羽不萌",
        rankBadge: {
          cupName: "古风杯",
          rank: "#1",
        },
      },
      {
        id: "work-103",
        title: "新版真实修仙模拟器",
        coverUrl:
          "https://images.unsplash.com/photo-1563089145-599997674d42?w=500&auto=format&fit=crop&q=80",
        heat: "3433.8k",
        commentsCount: "78.4k",
        tokenUsage: "7725.1M",
        rating: 5.0,
        summary: "最新困难版真实修仙模拟器，设定翻倍更加细化，给你不一样的全新体验！",
        tags: ["#RPG", "#世界", "+3"],
        authorName: "@萌羽不萌",
      },
      {
        id: "work-104",
        title: "修仙模拟器（指令竞技对抗mod已成功）",
        coverUrl:
          "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&auto=format&fit=crop&q=80",
        heat: "2159.4k",
        commentsCount: "45.5k",
        tokenUsage: "6007.5M",
        rating: 4.9,
        summary: "包含完整竞技对战MOD，支持指令交互与宗门争霸，快来体验爽快修仙旅程！",
        tags: ["#RPG", "#修仙", "+2"],
        authorName: "@萌羽不萌",
      },
    ],
  },
  {
    id: "creator-002",
    username: "为了防止8",
    avatarUrl:
      "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?w=150&auto=format&fit=crop&q=80",
    level: 25,
    levelBadgeColor: "#F472B6",
    followersCount: "3.9M",
    interactionsCount: "151.2M",
    isFollowed: false,
    featuredWorks: [
      {
        id: "work-201",
        title: "女武神学院：执事官 (全角色图鉴)",
        coverUrl:
          "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500&auto=format&fit=crop&q=80",
        heat: "516.2M",
        commentsCount: "250.5k",
        tokenUsage: "2872.7M",
        rating: 5.0,
        summary: "身为女武神学院唯一的特级执事官，你将执掌全院调动大权与机密武装档案...",
        tags: ["#校园", "#二次元", "+3"],
        authorName: "@为了防止8",
      },
      {
        id: "work-202",
        title: "Fate 圣杯战争",
        coverUrl:
          "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=500&auto=format&fit=crop&q=80",
        heat: "485.0M",
        commentsCount: "171.4k",
        tokenUsage: "1261.7M",
        rating: 4.8,
        summary: "七骑从者，降临冬木！以令咒之名，回应圣杯的召唤，开启宿命的对决！",
        tags: ["#同人", "#玄幻", "+2"],
        authorName: "@为了防止8",
      },
    ],
  },
];
