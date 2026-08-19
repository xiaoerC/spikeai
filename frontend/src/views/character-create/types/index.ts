/**
 * 角色卡编辑器 / 创建角色业务领域类型定义
 *
 * @packageDocumentation
 */

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
 * 世界书条目配置
 */
export interface WorldbookEntryItem {
  id: string;
  name: string;
  keys: string[];
  content: string;
  isEnabled: boolean;
}

/**
 * 角色创建全量表单数据实体 (兼容 SillyTavern V2 / V3 标准规范)
 */
export interface CharacterFormData {
  // 1. 作者的话
  creatorNotes: string;

  // 2. 角色卡信息
  name: string;
  avatarUrl: string;
  tags: string[];

  // 3. 基本信息
  description: string;
  personality: string;
  scenario: string;

  // 4. 序幕 (HTML / 故事卡展示)
  prologueHtml: string;

  // 5. 对话设置
  firstMes: string;
  alternateGreetings: AlternateGreetingItem[];

  // 6. 高级补充信息
  systemPrompt: string;
  postHistoryInstructions: string;
  worldbookEntries: WorldbookEntryItem[];
}

/**
 * 表单校验错误项
 */
export interface FormValidationError {
  field: keyof CharacterFormData;
  message: string;
}
