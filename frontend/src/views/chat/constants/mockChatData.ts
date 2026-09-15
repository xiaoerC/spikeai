/**
 * AI 聊天界面 1:1 Figma 原型 Mock 数据常量与类型定义
 *
 * @packageDocumentation
 */

export interface ChatMessage {
  id: string;
  sender: "ai" | "user" | "system";
  characterName?: string;
  avatarUrl?: string;
  content: string;
  thinkingContent?: string;
  timestamp: string;
  status?: "pending" | "streaming" | "success" | "error";
  errorMessage?: string;
  metrics?: {
    inputTokens: number;
    outputTokens: number;
    isSuccess: boolean;
    cost?: number;
    currency?: "star" | "moon";
  };
}

export interface AiModelItem {
  id: string;
  name: string;
  health: number; // e.g. 97
  billingType: "fixed" | "metered"; // 固定点数 或 按量计费
  starCost?: number; // 金星消耗
  moonCost?: number; // 橙月消耗
  inputRate?: string; // e.g. "入×0.6000"
  outputRate?: string; // e.g. "出×1.2000/千token"
  cost: number;
  freeCountText: string;
  isStreaming: boolean;
  isFavorite: boolean;
}

export const INITIAL_CHAT_MESSAGES: ChatMessage[] = [
  {
    id: "msg-1",
    sender: "ai",
    characterName: "灶门炭治郎",
    avatarUrl:
      "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=300&auto=format&fit=crop&q=80",
    content:
      "夜色渐浓，深山中的寒风呼啸而过。我能闻到空气中那一丝极淡却危险的血腥味……请小心跟紧我，无论发生什么，都不要离开日轮刀的防护范围！",
    timestamp: "20:00",
    metrics: {
      inputTokens: 72502,
      outputTokens: 65536,
      isSuccess: true,
    },
  },
  {
    id: "msg-2",
    sender: "user",
    content: "我请她们吃了饭 她们和我一起躺在沙发上 逗我 聊起她们每日怎么和男朋友做爱的",
    timestamp: "20:01",
  },
];

export const MOCK_CHAT_CHARACTER = {
  id: "c1",
  name: "灶门炭治郎 - 鬼杀队刃之篇",
  avatarUrl:
    "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=300&auto=format&fit=crop&q=80",
  backgroundUrl:
    "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&auto=format&fit=crop&q=80",
  backgroundImageUrl:
    "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=1200&auto=format&fit=crop&q=80",
  greeting:
    "夜色渐浓，深山中的寒风呼啸而过。我能闻到空气中那一丝极淡却危险的血腥味……请小心跟紧我，无论发生什么，都不要离开日轮刀的防护范围！",
  authorNote:
    "大正年间。\n白日里的日本正在一点点变得现代。\n蒸汽列车穿过山野，电灯照亮浅草的街道，商铺在夜里依旧有人进出。赶路的人抱怨天气，孩子追着糖果摊跑，远方的寺院钟声一声接着一声。\n没有多少人知道——\n当太阳完全落下以后，另一个世界才真正睁开眼睛。\n山路上忽然消失的旅人，深夜紧闭却仍渗出血腥味的屋门，几日之间死去整户人家的村落，还有那些明明已经被砍断手脚，却依旧能够重新站起来的东西……\n人们把它们称作怪谈、野兽、山神发怒。\n而真正见过那些东西的人，通常已经来不及告诉别人。\n鬼，以人类为食。\n它们藏在人群、山林、废宅与繁华街巷之中。有些只剩下饥饿，有些仍保存着曾经作为人的记忆，也有一些已经在漫长岁月增强大到足以令整座城镇陷入噩梦。\n在无人知晓的地方，一群同样没有被国家承认的人，已经与它们厮杀了数百年。\n他们穿着背后写有“灭”字的队服。\n腰间佩着能够斩鬼的日轮刀。\n他们可能只有十四五岁，也可能已经满身旧伤。\n他们会害怕，会流血，会骨折，会死。\n即便如此，每当鎹鸦从夜空掠过，一封新的任务传来，仍然会有人重新绑紧刀鞘，朝那个据说“最近总有人失踪”的地方走去。\n因为总得有人在天亮以前赶到。\n而今夜，你也站在这片夜色之中。\n也许你只是一个尚未见过鬼的普通人。\n也许你刚刚从藤袭山活着回来，掌心还留着握刀留下的伤口。\n也许你已经斩过许多鬼，知道真正可怕的从来不只是獠牙和利爪。\n也许你本身，就是那个不能见到阳光的存在。\n又或者——",
  prologueTitle: "序幕",
  prologueContent:
    "夜色渐浓，深山中的寒风呼啸而过。远处隐约传来枯枝被踩断的清脆声响，空气中弥漫着淡淡的紫藤花与铁锈般的微腥气息……",
  tags: ["鬼灭之刃", "热血", "奇幻", "RPG", "大正风"],
  characterBookTokens: 15003,
  prologueTokens: 5,
};
