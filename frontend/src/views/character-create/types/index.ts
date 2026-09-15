/**
 * 角色卡编辑器 / 创建角色业务领域类型定义
 *
 * 遵循 SillyTavern V2 / V3 角色卡规范与叙梦 Naro 1:1 复刻设计体系。
 *
 * @packageDocumentation
 */

/**
 * 视图显示模式：简洁模式 (核心字段) vs 完整模式 (酒馆高阶全部字段)
 */
export type DisplayMode = "simple" | "full";

/**
 * 顶部 5 大锚点分节 Tab
 */
export type CreateSectionTab = "cover" | "character" | "stage" | "mechanics" | "preview";

/**
 * 备选开场白项
 */
export interface AlternateGreetingItem {
  id: string;
  title: string;
  greetingText: string;
  responsePreview?: string;
}

/**
 * 世界书条目配置 (对齐 V2/V3 角色书规范)
 */
export interface WorldbookEntryItem {
  id: string;
  name: string;
  keys: string[];
  secondaryKeys?: string[];
  content: string;
  isEnabled: boolean;
  position?: "before_char" | "after_char" | "top_an" | "bottom_an" | "at_depth" | "system_top" | string;
  order?: number;
}

/**
 * 酒馆正则替换脚本项
 */
export interface RegexScriptItem {
  id: string;
  scriptName: string;
  findRegex: string;
  replaceString: string;
  trimStrings?: string[];
  placement: number[]; // 1: User input, 2: AI output, 3: Slash commands
  disabled: boolean;
}

/**
 * 舞台沉浸式扩展挂件
 */
export interface StageExtensions {
  bgmUrl?: string;
  customCss?: string;
  sidebarPanelHtml?: string;
  assistantNote?: string;
}

/**
 * 角色创建全量表单数据实体 (4 大分节手风琴 + 发布矩阵)
 */
export interface CharacterFormData {
  // 1. 视图与导航状态
  displayMode: DisplayMode;
  activeTab: CreateSectionTab;

  // 2. 分节 1: 卡面 (Cover - 玩家在市场看到的信息)
  name: string;
  avatarUrl: string;
  tags: string[];
  marketDescription: string;
  category: "story" | "nsfw";
  isOriginal: boolean;
  isNsfw: boolean;
  visibility: "public" | "private";
  creatorName: string;
  version: string;
  creatorNotes: string;

  // 3. 分节 2: 角色 (Character - AI 模型看到的设定)
  description: string;
  personality: string;
  scenario: string;
  beforeChar: string;
  worldbookVersion: "v2" | "v3";
  worldbookEntries: WorldbookEntryItem[];
  systemPrompt: string;
  postHistoryInstructions: string;

  // 4. 分节 3: 舞台 (Stage - 玩家在对话中看到的内容)
  firstMes: string;
  alternateGreetings: AlternateGreetingItem[];
  openingReplies: string[];
  prologueHtml: string;
  stageExtensions: StageExtensions;

  // 5. 分节 4: 机制 (Mechanics - 引擎执行的脚本与变量)
  regexScripts: RegexScriptItem[];
  initialVariables: Record<string, any>;
}

/**
 * 表单校验错误项
 */
export interface FormValidationError {
  field: keyof CharacterFormData;
  message: string;
}

/**
 * 规范化酒馆/叙梦世界书插入位置
 * 将 SillyTavern 数字枚举 (0, 1, 2, 3, 4) 或任意异常类型转化为规范字符串
 *
 * @param pos - 原始位置值 (整型、数字字符串或位置名称)
 * @returns 标准化位置标识 ("before_char" | "after_char" | "top_an" | "bottom_an" | "at_depth" | string)
 *
 * @example
 * ```ts
 * normalizePosition(0) // "before_char"
 * normalizePosition(1) // "after_char"
 * normalizePosition("after_char") // "after_char"
 * ```
 */
export function normalizePosition(pos: unknown): string {
  if (pos === 0 || pos === "0" || pos === "before_char") return "before_char";
  if (pos === 1 || pos === "1" || pos === "after_char") return "after_char";
  if (pos === 2 || pos === "2" || pos === "top_an") return "top_an";
  if (pos === 3 || pos === "3" || pos === "bottom_an") return "bottom_an";
  if (pos === 4 || pos === "4" || pos === "at_depth") return "at_depth";
  if (typeof pos === "string" && pos.trim()) return pos.trim();
  return "after_char";
}
