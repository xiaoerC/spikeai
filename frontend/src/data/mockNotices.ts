/**
 * 官方公告真实高保真 Mock 数据源
 *
 * @packageDocumentation
 */

import type { NoticeItem } from "@/views/notice/types";

export const MOCK_NOTICES: NoticeItem[] = [
  {
    id: "notice-001",
    type: "update",
    typeText: "更新",
    title: "Naro · 叙梦8月上旬更新",
    publishedAt: "2026/08/05 15:05",
    content: `
      亲爱的旅行者：
      
      叙梦 Naro 8月上旬版本现已正式发布，本次更新带来多项重要优化：
      
      1. 【剧情分支树】性能优化：提升大规模分支节点渲染流畅度，支持自适应排版与一键聚焦。
      2. 【提示词编辑器】新增实时 Markdown 预览与代码高亮插件。
      3. 【世界书语义检索】针对超长设定集混合召回准确率提升 40%。
      4. 修复了若干移动端输入法键盘遮挡问题。
      
      感谢大家的支持与陪伴！
    `,
    isImportant: true,
  },
  {
    id: "notice-002",
    type: "activity",
    typeText: "活动",
    title: "特价小克撸羊毛快猛猛蹬！",
    publishedAt: "2026/07/26 17:07",
    content: `
      🎉 限时活动开启！
      
      Claude 3.5 Sonnet 特惠通道现已限时开放，单次交互 Token 折扣低至 5 折！
      活动时间：2026/07/26 - 2026/08/02
      快来开启极速沉浸式角色互动吧！
    `,
  },
  {
    id: "notice-003",
    type: "update",
    typeText: "更新",
    title: "7.10功能更新",
    publishedAt: "2026/07/10 19:52",
    content: `
      本次更新内容：
      - 新增角色卡片一键导出为 SillyTavern V2/V3 PNG 元数据规范；
      - 创作者专区支持自定义等级徽标与个性化简介；
      - 修复了弱网环境下 SSE 流式断连自动重试逻辑。
    `,
  },
  {
    id: "notice-004",
    type: "update",
    typeText: "更新",
    title: "微信好了",
    publishedAt: "2026/07/03 21:40",
    content: `
      各位旅行者，微信登录及扫码充值通道现已全面恢复正常，若有未及时到账订单请联系客服「薯条鸽」补发。
    `,
  },
  {
    id: "notice-005",
    type: "update",
    typeText: "更新",
    title: "常规更新",
    publishedAt: "2026/07/03 12:30",
    content: `
      - 服务器后台节点性能扩容；
      - 优化移动端触控反馈与手势拖拽体验；
      - 修复部分历史记录卡片封面显示异常。
    `,
  },
  {
    id: "notice-006",
    type: "update",
    typeText: "更新",
    title: "Naro · 叙梦6月下旬更新公告",
    publishedAt: "2026/06/30 12:30",
    content: `
      年中大版本发布，推出全新黑金暗黑玻璃拟物设计语言，全面升级个人中心与等级榜领奖台！
    `,
  },
  {
    id: "notice-007",
    type: "update",
    typeText: "更新",
    title: "更新日志",
    publishedAt: "2026/06/28 21:16",
    content: `
      - 修复了部分角色前置 System Prompt 变量替换丢失的 Bug；
      - 增加卡片快捷收藏与本地历史同步。
    `,
  },
  {
    id: "notice-008",
    type: "activity",
    typeText: "活动",
    title: "大转盘开了",
    publishedAt: "2026/06/25 06:27",
    content: `
      夏日幸运大转盘活动正式上线！每日签到即可免费获得抽奖机会，月卡、星元与限定画师串等你来拿！
    `,
  },
  {
    id: "notice-009",
    type: "update",
    typeText: "更新",
    title: "2.5.6",
    publishedAt: "2026/06/22 16:16",
    content: `
      核心引擎版本升级至 2.5.6，响应延迟降低 25%。
    `,
  },
  {
    id: "notice-010",
    type: "activity",
    typeText: "活动",
    title: "Naro · 叙梦 酷暑狂欢活动",
    publishedAt: "2026/06/20 11:43",
    content: `
      酷暑狂欢盛典，全场热门世界书与模组免费体验！
    `,
  },
  {
    id: "notice-011",
    type: "system",
    typeText: "系统",
    title: "谷歌拉闸",
    publishedAt: "2026/06/19 17:46",
    content: `
      由于上游 Google Gemini API 突发临时波动，部分 Gemini 1.5 Pro 对话节点可能出现偶发延迟，已紧急切换至备用链路。
    `,
    isImportant: true,
  },
  {
    id: "notice-012",
    type: "system",
    typeText: "系统",
    title: "小克遇官方大规模风控",
    publishedAt: "2026/06/13 12:51",
    content: `
      Anthropic 官方对部分高频 API 接口进行了安全策略收紧，技术团队已完成反代混淆与智能分流适配。
    `,
  },
  {
    id: "notice-013",
    type: "update",
    typeText: "更新",
    title: "小克官方风控",
    publishedAt: "2026/06/02 06:56",
    content: `
      持续跟进风控策略优化，全面保障对话稳定性。
    `,
  },
  {
    id: "notice-014",
    type: "update",
    typeText: "更新",
    title: "新增新手攻略pdf",
    publishedAt: "2026/05/31 08:54",
    content: `
      新手指南与进阶教程 PDF 现已上传至帮助中心，欢迎下载查阅！
    `,
  },
  {
    id: "notice-015",
    type: "system",
    typeText: "系统",
    title: "剧情卡/绅士卡分区",
    publishedAt: "2026/05/27 17:39",
    content: `
      为了提供更加规范健康的内容浏览环境，角色社区已上线「剧情卡」与「绅士卡」独立专区过滤开关。
    `,
  },
  {
    id: "notice-016",
    type: "update",
    typeText: "更新",
    title: "创作者更新",
    publishedAt: "2026/05/26 15:07",
    content: `
      创作者中心上线数据统计看板与粉丝互动通知体系。
    `,
  },
  {
    id: "notice-017",
    type: "update",
    typeText: "更新",
    title: "高级设置",
    publishedAt: "2026/05/09 19:43",
    content: `
      角色创建页面高级选项全面支持 Temperature、Top-P、Repetition Penalty 自定义微调。
    `,
  },
  {
    id: "notice-018",
    type: "activity",
    typeText: "活动",
    title: "充值活动延期",
    publishedAt: "2026/05/04 17:52",
    content: `
      应广大旅行者要求，五一限时充值赠礼活动延期至 5月10日 24:00 结束！
    `,
  },
];
