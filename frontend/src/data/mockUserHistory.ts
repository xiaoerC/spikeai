/**
 * 个人历史记录真实高保真 Mock 数据源
 *
 * @packageDocumentation
 */

import type { UserHistoryItem } from "@/views/history/types";

export const MOCK_USER_HISTORY: UserHistoryItem[] = [
  {
    id: "uh-001",
    characterId: "c-guimie-1",
    title: "《鬼灭之刃》",
    avatar: "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=500&q=80",
    category: "story",
    isPinned: true,
    lastChatTime: "10分钟前",
    lastChatDate: "2026/08/19 13:28",
    branchName: "《鬼灭之刃》",
    messageCount: 48,
    isCloudBacked: true,
  },
  {
    id: "uh-002",
    characterId: "c-heroine-1",
    title: "☁️英雄救美！前台大姐姐喊我乖崽，我听到咯~",
    avatar: "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&q=80",
    category: "story",
    isPinned: false,
    lastChatTime: "2小时前",
    lastChatDate: "2026/08/19 12:50",
    branchName: "☁️英雄救美！前台大姐姐喊我乖崽，我听到咯~",
    messageCount: 32,
    isCloudBacked: true,
  },
  {
    id: "uh-003",
    characterId: "c-guimie-2",
    title: "《鬼灭之刃》",
    avatar: "https://images.unsplash.com/photo-1563089145-599997674d42?w=500&q=80",
    category: "story",
    isPinned: false,
    lastChatTime: "昨天",
    lastChatDate: "2026/08/16 07:24",
    branchName: "《鬼灭之刃》",
    messageCount: 15,
    isCloudBacked: false,
  },
  {
    id: "uh-004",
    characterId: "c-zhenfen-1",
    title: "超级嘴臭雌大鬼——甄芬",
    avatar: "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500&q=80",
    category: "story",
    isPinned: false,
    lastChatTime: "3天前",
    lastChatDate: "2026/08/16 06:45",
    branchName: "超级嘴臭雌大鬼——甄芬",
    messageCount: 104,
    isCloudBacked: true,
  },
];
