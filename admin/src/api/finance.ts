/**
 * 平台财务中心与充值订单结算 API 强类型封装
 *
 * 提供全站充值订单与对账大盘检索、宏观财务指标汇总、退款冲正处置。
 *
 * Usage:
 *   >>> import { getFinanceOrders, refundOrderTransaction } from '@/api/finance';
 */

import request from '@/utils/request';

export interface IFinanceOrderQuery {
  page?: number;
  size?: number;
  keyword?: string;
  type?: string;
  currency?: string;
}

export interface IAdminFinanceSummary {
  total_star_recharged: number;
  total_moon_recharged: number;
  total_transactions_count: number;
  today_transactions_count: number;
}

export interface IAdminOrderTransactionItem {
  id: string;
  user_id: string;
  user_name: string;
  user_email: string;
  user_avatar: string;
  type: string;
  currency: string;
  amount: number;
  balance_after: number;
  description?: string | null;
  created_at: string;
}

export interface IAdminOrderPageResult {
  total: number;
  page: number;
  size: number;
  list: IAdminOrderTransactionItem[];
  summary: IAdminFinanceSummary;
}

/** 分页多维查询全站充值订单与流水大盘 */
export function getFinanceOrders(params: IFinanceOrderQuery): Promise<IAdminOrderPageResult> {
  return request({
    url: '/admin/finance/orders',
    method: 'GET',
    params,
  });
}

/** 金融级退款冲正处置 */
export function refundOrderTransaction(
  txId: string,
  data: { reason: string },
): Promise<{ code: number; message: string; data: any }> {
  return request({
    url: `/admin/finance/orders/${txId}/refund`,
    method: 'POST',
    data,
  });
}
