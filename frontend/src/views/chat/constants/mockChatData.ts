/**
 * AI 聊天界面 1:1 Figma 原型 Mock 数据常量与类型定义
 *
 * @packageDocumentation
 */

export interface ChatMessage {
  id: string;
  sender: "ai" | "user";
  characterName?: string;
  avatarUrl?: string;
  content: string;
  timestamp: string;
  metrics?: {
    inputTokens: number;
    outputTokens: number;
    isSuccess: boolean;
  };
}

export interface AiModelItem {
  id: string;
  name: string;
  cost: number;
  freeCountText: string;
  isStreaming: boolean;
}

export const MOCK_AI_MODELS: AiModelItem[] = [
  {
    id: "gemini-flash-3",
    name: "快速双子星3（关流式）",
    cost: 15,
    freeCountText: "会员免费(30/30)",
    isStreaming: false,
  },
  {
    id: "ds4p-o1",
    name: "DeepSeek 4P (o1推理)",
    cost: 25,
    freeCountText: "会员特惠(10/10)",
    isStreaming: true,
  },
  {
    id: "claude-3-5-sonnet",
    name: "Claude 3.5 Sonnet",
    cost: 35,
    freeCountText: "按量扣除",
    isStreaming: true,
  },
];

export const MOCK_CHAT_CHARACTER = {
  id: "c1",
  name: "灶门炭治郎 - 鬼杀队刃之篇",
  avatarUrl:
    "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=300&auto=format&fit=crop&q=80",
  // 鬼灭之刃大正时代全屏立绘插画背景
  backgroundImageUrl:
    "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&auto=format&fit=crop&q=80",
  authorNoteTitle: "作者的话",
  authorNote: `大正年间。
白日里的日本正在一点点变得现代。
蒸汽列车穿过山野，电灯照亮浅草的街道，商铺在夜里依旧有人进出。赶路的人抱怨天气，孩子追着糖果摊跑，远方的寺院钟声一声接着一声。
没有多少人知道——
当太阳完全落下以后，另一个世界才真正睁开眼睛。
山路上忽然消失的旅人，深夜紧闭却仍渗出血腥味的屋门，几日之间死去整户人家的村落，还有那些明明已经被砍断手脚，却依旧能够重新站起来的东西……
人们把它们称作怪谈、野兽、山神发怒。
而真正见过那些东西的人，通常已经来不及告诉别人。
鬼，以人类为食。
它们藏在人群、山林、废宅与繁华街巷之中。有些只剩下饥饿，有些仍保存着曾经作为人的记忆，也有一些已经在漫长岁月中强大到足以令整座城镇陷入噩梦。
在无人知晓的地方，一群同样没有被国家承认的人，已经与它们厮杀了数百年。
他们穿着背后写有“灭”字的队服。
腰间佩着能够斩鬼的日轮刀。
他们可能只有十四五岁，也可能已经满身旧伤。
他们会害怕，会流血，会骨折，会死。
即便如此，每当鎹鸦从夜空掠过，一封新的任务传来，仍然会有人重新绑紧刀鞘，朝那个据说“最近总有人失踪”的地方走去。
因为总得有人在天亮以前赶到。
而今夜，你也站在了这片夜色之中。
也许你只是一个尚未见过鬼的普通人。
也许你刚刚从藤袭山活着回来，掌心还留着握刀留下的伤口。
也许你已经斩过许多鬼，知道真正可怕的从来不只是獠牙和利爪。
也许你本身，就是那个不能见到阳光的存在。
又或者——`,
  prologueTitle: "序幕",
  prologueContent:
    "夜色渐浓，深山中的寒风呼啸而过。远处隐约传来枯枝被踩断的清脆声响，空气中弥漫着淡淡的紫藤花与铁锈般的微腥气息……",
};

export const INITIAL_CHAT_MESSAGES: ChatMessage[] = [];
