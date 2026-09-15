/**
 * 系统公告与运营活动管理 API 强类型封装 (CMS)
 *
 * 提供全站系统公告与运营活动的全生命周期管理 (检索/发布/更新/删除)。
 *
 * Usage:
 *   >>> import { getNoticeList, createNotice, updateNotice, deleteNotice } from '@/api/cms';
 *   >>> import { getActivityList, createActivity, updateActivity, deleteActivity } from '@/api/cms';
 */

import request from '@/utils/request';

// =================== 公告相关类型与 API ===================

export interface INoticeQuery {
  page?: number;
  size?: number;
  keyword?: string;
  category?: string;
}

export interface IAdminNoticeItem {
  id: string;
  title: string;
  category: string;
  date_text: string;
  badge_type: string;
  summary: string;
  content_html: string;
  created_at: string;
}

export interface IAdminNoticePageResult {
  total: number;
  page: number;
  size: number;
  list: IAdminNoticeItem[];
}

export interface IAdminNoticeForm {
  title: string;
  category: string;
  date_text: string;
  badge_type: string;
  summary: string;
  content_html?: string;
}

export function getNoticeList(params: INoticeQuery): Promise<IAdminNoticePageResult> {
  return request({
    url: '/admin/cms/notices',
    method: 'GET',
    params,
  });
}

export function createNotice(data: IAdminNoticeForm): Promise<IAdminNoticeItem> {
  return request({
    url: '/admin/cms/notices',
    method: 'POST',
    data,
  });
}

export function updateNotice(
  noticeId: string,
  data: Partial<IAdminNoticeForm>,
): Promise<IAdminNoticeItem> {
  return request({
    url: `/admin/cms/notices/${noticeId}`,
    method: 'PUT',
    data,
  });
}

export function deleteNotice(noticeId: string): Promise<{ code: number; message: string }> {
  return request({
    url: `/admin/cms/notices/${noticeId}`,
    method: 'DELETE',
  });
}

// =================== 活动相关类型与 API ===================

export interface IActivityQuery {
  page?: number;
  size?: number;
  keyword?: string;
  status?: string;
}

export interface IAdminActivityItem {
  id: string;
  title: string;
  tag: string;
  reward_text: string;
  date_range: string;
  status: string;
  rules: string[];
  created_at: string;
}

export interface IAdminActivityPageResult {
  total: number;
  page: number;
  size: number;
  list: IAdminActivityItem[];
}

export interface IAdminActivityForm {
  title: string;
  tag: string;
  reward_text: string;
  date_range: string;
  status: string;
  rules: string[];
}

export function getActivityList(params: IActivityQuery): Promise<IAdminActivityPageResult> {
  return request({
    url: '/admin/cms/activities',
    method: 'GET',
    params,
  });
}

export function createActivity(data: IAdminActivityForm): Promise<IAdminActivityItem> {
  return request({
    url: '/admin/cms/activities',
    method: 'POST',
    data,
  });
}

export function updateActivity(
  activityId: string,
  data: Partial<IAdminActivityForm>,
): Promise<IAdminActivityItem> {
  return request({
    url: `/admin/cms/activities/${activityId}`,
    method: 'PUT',
    data,
  });
}

export function deleteActivity(activityId: string): Promise<{ code: number; message: string }> {
  return request({
    url: `/admin/cms/activities/${activityId}`,
    method: 'DELETE',
  });
}
