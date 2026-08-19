/**
 * 官方活动真实高保真 Mock 数据源
 *
 * @packageDocumentation
 */

import type { ActivityItem } from "@/views/activity/types";

export const MOCK_ACTIVITIES: ActivityItem[] = [
  {
    id: "act-001",
    title: "推广者招募计划",
    category: "welfare",
    status: "ongoing",
    statusText: "进行中",
    dateRange: "2026/03/10 - 2027/01/10",
    summary:
      "🚀 参与推广 · 获取长期分红返利\n\n📌 活动说明：我们正在招募社区推广者。如果你有渠道或愿意帮助推广平台，可以申请成为推广伙伴。\n\n💰 推广收益：你邀请的用户产生付费，系统将按照一定比例进行返利，返利将以 USDT 形式发放，收益长期有效。\n\n📮 参与方式：加入 Discord 社区联系管理员「薯条鸽」申请开通推广返利权限。",
    fullHtmlContent: `
      <div class="space-y-3 text-xs text-[#D6D3D1] leading-relaxed">
        <div class="p-2.5 rounded-lg bg-[#292524] border border-[#57534E]/50">
          <h4 class="font-bold text-[#F9C86D] text-sm mb-1">🚀 参与推广 · 获取长期分红返利</h4>
          <p>我们正在招募社区推广者。如果你有推广渠道或愿意帮助平台成长，欢迎成为官方推广伙伴。</p>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">💰 推广收益说明</h5>
          <ul class="list-disc list-inside space-y-1 text-[#A8A29E]">
            <li>邀请用户产生付费，系统自动按固定比例实时返还。</li>
            <li>返利支持以 <span class="text-[#F9C86D] font-medium">USDT</span> 形式灵活提现。</li>
            <li>长期分红绑定，收益永久有效。</li>
          </ul>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">📮 参与方式</h5>
          <p class="text-[#A8A29E]">加入官方 Discord 社区联系管理员 <span class="text-[#F9C86D]">「薯条鸽」</span> 开通推广专属权限。</p>
        </div>
      </div>
    `,
    rewardsSummary: "USDT 长期返利",
  },
  {
    id: "act-002",
    title: "AI聊天提示词征集活动",
    category: "character",
    status: "ongoing",
    statusText: "进行中",
    dateRange: "2026/02/22 - 2027/01/02",
    summary:
      "🧠 强化沉浸 · 提升风味 · 优化游玩体验\n\n📌 活动说明：征集可直接用于 AI 聊天的高质量提示词（Prompt）。\n\n🧾 投稿要求：完整提示词正文、适用场景说明、示例对话（建议前后对比）。\n\n🎁 活动奖励：系统助手收录 + 社区奖励发放 200 星元！",
    fullHtmlContent: `
      <div class="space-y-3 text-xs text-[#D6D3D1] leading-relaxed">
        <div class="p-2.5 rounded-lg bg-[#292524] border border-[#57534E]/50">
          <h4 class="font-bold text-[#F9C86D] text-sm mb-1">🧠 强化沉浸 · 提升风味 · 优化体验</h4>
          <p>征集可直接用于 AI 角色扮演与沉浸式对话的高质量 System Prompt 与前/后置提示词。</p>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">🎯 征集方向示例</h5>
          <div class="flex flex-wrap gap-1.5 mt-1">
            <span class="px-2 py-0.5 rounded bg-[#383330] text-[#F9C86D] text-[11px]">风味增强</span>
            <span class="px-2 py-0.5 rounded bg-[#383330] text-[#F9C86D] text-[11px]">高张力描写</span>
            <span class="px-2 py-0.5 rounded bg-[#383330] text-[#F9C86D] text-[11px]">OOC修正</span>
            <span class="px-2 py-0.5 rounded bg-[#383330] text-[#F9C86D] text-[11px]">细节扩写</span>
          </div>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">🎁 活动奖励</h5>
          <p class="text-[#A8A29E]">通过审核的优秀提示词将收录进官方 <span class="text-[#F9C86D]">「Naro助手 · 系统助手」</span> 供全服调用，并奖励 <span class="text-[#F9C86D] font-bold">200 星元</span>！</p>
        </div>
      </div>
    `,
    rewardsSummary: "200 星元 + 官方收录",
  },
  {
    id: "act-003",
    title: "画师串征集活动",
    category: "creation",
    status: "ongoing",
    statusText: "进行中",
    dateRange: "2026/01/18 - 2027/01/18",
    summary:
      "🎨 文生图 · 画师串征集活动\n\n🖌️ 活动说明：稳定 · 可复用 · 风格明确的画师 Prompt 征集。重点考察提示词在不同场景下的一致性与实际出图效果。\n\n🎁 活动奖励：通过官方审核的画师串作者，将获得 生图次数 × 100 次 奖励！",
    fullHtmlContent: `
      <div class="space-y-3 text-xs text-[#D6D3D1] leading-relaxed">
        <div class="p-2.5 rounded-lg bg-[#292524] border border-[#57534E]/50">
          <h4 class="font-bold text-[#F9C86D] text-sm mb-1">🎨 稳定 · 可复用 · 风格明确的画师 Prompt</h4>
          <p>面向所有文生图创作者，征集可直接使用的画师串（Prompt / 画师人格模型风格）。</p>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">🧾 投稿要求</h5>
          <ul class="list-disc list-inside space-y-1 text-[#A8A29E]">
            <li>必须包含完整 Prompt 与负面词 Negative Prompt。</li>
            <li>至少提供 10 张不同构图/光影的 SFW 与 NSFW 风格示例图。</li>
            <li>画面审美明确、风格稳定。</li>
          </ul>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">🎁 专属奖励</h5>
          <p class="text-[#A8A29E]">官方审核通过后，直接向账户发放 <span class="text-[#F9C86D] font-bold">生图次数 × 100 次</span>！</p>
        </div>
      </div>
    `,
    rewardsSummary: "生图次数 × 100 次",
  },
  {
    id: "act-004",
    title: "长期活动与福利",
    category: "welfare",
    status: "ongoing",
    statusText: "进行中",
    isNew: true,
    dateRange: "2025/11/11 - 2026/07/12",
    summary:
      "🌟 长期活动与福利中心 —— Naro叙梦 官方持续奖励计划\n\n💫 一、邀请好友奖励计划：每邀请 50 位好友注册并互动，额外获得一张完整月卡！\n\n🚨 二、原创监督计划：举报冒充原创或未经授权的搬运作品，经审核属实奖励 200 星元。",
    fullHtmlContent: `
      <div class="space-y-3 text-xs text-[#D6D3D1] leading-relaxed">
        <div class="p-2.5 rounded-lg bg-[#292524] border border-[#57534E]/50">
          <h4 class="font-bold text-[#F9C86D] text-sm mb-1">🌟 Naro 叙梦官方持续奖励计划</h4>
          <p>长期开放的社区生态建设与福利发放通道。</p>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">💫 1. 邀请好友计划</h5>
          <p class="text-[#A8A29E]">邀请好友加入叙梦，每累计邀请 50 人有效互动，直接赠送 <span class="text-[#F9C86D] font-medium">VIP 完整月卡一张</span>！</p>
        </div>
        <div>
          <h5 class="font-semibold text-white mb-1">🚨 2. 原创监督计划</h5>
          <p class="text-[#A8A29E]">举报盗用冒充原创或侵权搬运角色卡，审核属实每次奖励 <span class="text-[#F9C86D] font-bold">200 星元</span>！</p>
        </div>
      </div>
    `,
    rewardsSummary: "免费月卡 + 200 星元",
  },
];
