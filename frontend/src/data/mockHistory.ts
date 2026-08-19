/**
 * 历史记录真实高保真 Mock 数据源
 *
 * @packageDocumentation
 */

import type { HistoryCharacterCard, WeekOption } from "@/views/history/types";

export const MOCK_WEEK_OPTIONS: WeekOption[] = [
  { id: "all", label: "全部周次" },
  { id: "current", label: "本周回顾 (第34周)" },
  { id: "w33", label: "第33周 (08.10 - 08.16)" },
  { id: "w32", label: "第32周 (08.03 - 08.09)" },
  { id: "w31", label: "第31周 (07.27 - 08.02)" },
];

export const MOCK_HISTORY_CARDS: HistoryCharacterCard[] = [
  {
    id: "hist-001",
    title: "《在地下城寻求邂逅是否搞错了什么》",
    coverUrl:
      "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
    heat: "63.8k",
    commentsCount: "1.6k",
    tokenUsage: "146.6M",
    summary:
      "巴别塔之下，沉睡着永无尽头的地下城；欧拉丽的街道上，神明、冒险者与怪物共同等待着新的相遇。 你可以成为熟悉的英雄，...",
    tags: ["#世界", "#玄幻", "+3"],
    authorName: "@路过的hfs101",
    weekPeriod: "current",
    lastInteractedTime: "20分钟前",
  },
  {
    id: "hist-002",
    title: "《权游世界模拟器》（8.14更新正则美化）",
    coverUrl:
      "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
    heat: "47.4k",
    commentsCount: "1.6k",
    tokenUsage: "232.9M",
    rating: 5.0,
    summary: "“凛冬将至，凡人皆有一死。”为你铺开一张冰与火的棋局。一切，皆由你落子。",
    tags: ["#剧情", "#同人", "+2"],
    authorName: "@为止8",
    weekPeriod: "current",
    lastInteractedTime: "1小时前",
  },
  {
    id: "hist-003",
    title: "《无职转生》",
    coverUrl:
      "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500&auto=format&fit=crop&q=80",
    heat: "40.6k",
    commentsCount: "1.2k",
    tokenUsage: "81.6M",
    summary:
      "如果人生真的能重来一次 你还会不会走上和过去一样的路？ 《无职转生》带你真正走进那个辽阔而真实的异世界",
    tags: ["#同人", "#世界", "+3"],
    authorName: "@主",
    weekPeriod: "current",
    lastInteractedTime: "3小时前",
  },
  {
    id: "hist-004",
    title: "《斩！赤红之瞳》",
    coverUrl:
      "https://images.unsplash.com/photo-1563089145-599997674d42?w=500&auto=format&fit=crop&q=80",
    heat: "38.4k",
    commentsCount: "719",
    tokenUsage: "97.5M",
    summary:
      "帝都的夜，从来不会等人告别。 你可以改变命运，却无法要求命运一定温柔。有人会倒在任务结束以前，有些承诺永远等不到兑...",
    tags: ["#同人", "#二次元", "+3"],
    authorName: "@路过的hfs101",
    weekPeriod: "current",
    lastInteractedTime: "昨天",
  },
  {
    id: "hist-005",
    title: "《鬼灭之刃》",
    coverUrl:
      "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500&auto=format&fit=crop&q=80",
    heat: "37.6k",
    commentsCount: "929",
    tokenUsage: "69.2M",
    summary:
      "无限列车的黎明，还会有人死吗？ 游郭的灯火熄灭以后，那对兄妹还能不能一起离开？ 刀匠村会不会再次染血？ 而当无惨站...",
    tags: ["#同人", "#二次元", "+3"],
    authorName: "@主",
    weekPeriod: "w33",
    lastInteractedTime: "3天前",
  },
  {
    id: "hist-006",
    title: "岑语莞",
    coverUrl:
      "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=500&auto=format&fit=crop&q=80",
    heat: "29.3k",
    commentsCount: "710",
    tokenUsage: "42.9M",
    summary: "曾经牛过你的黄毛忘了这件事，多年后却邀请你参加他的婚礼",
    tags: ["#NTR", "#NTL", "+3"],
    authorName: "@嘉嘉",
    weekPeriod: "w33",
    lastInteractedTime: "4天前",
  },
  {
    id: "hist-007",
    title: "相亲模拟器•系统",
    coverUrl:
      "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=500&auto=format&fit=crop&q=80",
    heat: "28.9k",
    commentsCount: "1.0k",
    tokenUsage: "41.6M",
    rating: 5.0,
    summary: "寻找你的另一半但是。。系统不是只有“你”拥有其他npc也有",
    tags: ["#真实", "#都市", "+3"],
    authorName: "@博涛",
    weekPeriod: "w33",
    lastInteractedTime: "5天前",
  },
  {
    id: "hist-008",
    title: "苏糯糯",
    coverUrl:
      "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=500&auto=format&fit=crop&q=80",
    heat: "24.3k",
    commentsCount: "918",
    tokenUsage: "55.1M",
    rating: 5.0,
    summary: "笨蛋？nonono我是优雅的千金，我不笨的好叭",
    tags: ["#真假笨蛋", "#纯爱？纯爱！", "+2"],
    authorName: "@霖",
    weekPeriod: "w32",
    lastInteractedTime: "上周",
  },
  {
    id: "hist-009",
    title: "竹马回国，女友的选择",
    coverUrl:
      "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=500&auto=format&fit=crop&q=80",
    heat: "13.8k",
    commentsCount: "294",
    tokenUsage: "13.8M",
    summary: "你一开始就知道女友的竹马回国了，没有背着你，后续就看你自己发挥了",
    tags: ["#都市", "#剧情", "+1"],
    authorName: "@梦 LX",
    weekPeriod: "w32",
    lastInteractedTime: "上周",
  },
  {
    id: "hist-010",
    title: "《楚汉争霸模拟器》",
    coverUrl:
      "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=500&auto=format&fit=crop&q=80",
    heat: "11.2k",
    commentsCount: "314",
    tokenUsage: "22.7M",
    summary: "哟，是色色王来啦 楚汉争霸，你可成为千古霸王项羽，亦可成为剑斩白蛇刘邦",
    tags: ["#世界", "#剧情", "+2"],
    authorName: "@为止8",
    weekPeriod: "w31",
    lastInteractedTime: "半月前",
  },
];
