/**
 * 叙梦 Naro - 历史记录模拟数据集 (1:1 像素级复刻原图数据)
 *
 * @packageDocumentation
 */

import type { HistoryCardItem } from "@/views/history/types";

export const MOCK_HISTORY_CARDS: HistoryCardItem[] = [
  {
    id: "history-1",
    characterId: "char-kimetsu",
    title: "《鬼灭之刃》",
    author: "@吾峠呼世晴",
    // 炭治郎与祢豆子日漫雪景插画
    avatarUrl: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=600&q=85",
    isPinned: true,
    lastActiveTime: "2026/08/16 14:30",
    messageCount: 42,
    category: "story",
  },
  {
    id: "history-2",
    characterId: "char-zhenfen",
    title: "超级嘴臭雌大鬼——甄芬",
    author: "@路过的hfs101",
    // 金发双马尾校服动漫少女插画
    avatarUrl: "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=600&q=85",
    isPinned: false,
    lastActiveTime: "2026/08/16 06:45",
    messageCount: 128,
    category: "story",
  },
];
