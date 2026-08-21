/**
 * 帮助中心业务领域强类型定义
 *
 * @packageDocumentation
 */

export type HelpTabType = "guide" | "faq" | "commands";

/**
 * 新手指南步骤数据项
 */
export interface HelpStep {
  id: string;
  stepNumber: string; // 如 "01", "02"
  title: string;
  description: string;
  badges?: string[];
  subsections?: {
    subtitle: string;
    detail: string;
    scenarios?: {
      name: string;
      desc: string;
      match: string;
    }[];
  }[];
  promptCommand?: string;
  stepGuideList?: string[];
}

/**
 * FAQ 常见问题项
 */
export interface FaqItem {
  id: string;
  question: string;
  answer: string;
  category?: string;
}

/**
 * 官方指令数据项
 */
export interface CommandItem {
  id: string;
  name: string;
  category: string;
  description: string;
  commandText: string;
}
