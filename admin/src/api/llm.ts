/**
 * Admin 大模型 (LLM) API 渠道与模型上架配置 API 契约封装
 *
 * 负责多渠道 API 供应商管理、反代 Base URL 探测、上游 /v1/models 拉取、
 * 密钥掩码脱敏与 C 端模型上架调度。
 *
 * Usage:
 *   >>> import { getAdminLLMProviders, testLLMConnection } from '@/api/llm';
 *   >>> const res = await getAdminLLMProviders();
 */

import request from '@/utils/request';

export interface LLMModelItem {
  id: string;
  display_name: string;
  is_enabled: boolean;
  is_public: boolean;
  is_default: boolean;
  supports_streaming: boolean;
  supports_reasoning: boolean;
  cost: number;
  family: string;
  context_limit: number;
  sort_order: number;
}

export interface LLMProviderItem {
  id: string;
  name: string;
  provider_type: 'openai' | 'anthropic' | 'gemini' | 'ollama' | string;
  base_url: string;
  api_key: string;
  has_api_key: boolean;
  is_active: boolean;
  timeout_seconds: number;
  custom_headers: Record<string, string>;
  models: LLMModelItem[];
  models_count: number;
  public_models_count: number;
  description: string;
  sort_order: number;
  created_at?: string;
  updated_at?: string;
}

export interface LLMProviderCreate {
  name: string;
  provider_type?: string;
  base_url: string;
  api_key?: string;
  is_active?: boolean;
  timeout_seconds?: number;
  custom_headers?: Record<string, string>;
  models?: LLMModelItem[];
  description?: string;
  sort_order?: number;
}

export interface LLMProviderUpdate {
  name?: string;
  provider_type?: string;
  base_url?: string;
  api_key?: string;
  is_active?: boolean;
  timeout_seconds?: number;
  custom_headers?: Record<string, string>;
  models?: LLMModelItem[];
  description?: string;
  sort_order?: number;
}

export interface LLMTestConnectionRequest {
  base_url: string;
  api_key?: string;
  provider_id?: string;
  custom_headers?: Record<string, string>;
}

export interface LLMTestConnectionResponse {
  success: boolean;
  latency_ms: number;
  status_code?: number;
  discovered_models_count?: number;
  message: string;
}

export interface LLMFetchModelsRequest {
  base_url: string;
  api_key?: string;
  provider_id?: string;
  custom_headers?: Record<string, string>;
}

export interface LLMFetchModelsResponse {
  success: boolean;
  models: string[];
  message: string;
}

/**
 * 获取所有 API 渠道配置列表 (已脱敏)
 */
export function getAdminLLMProviders(): Promise<{
  code: number;
  data: LLMProviderItem[];
  message: string;
}> {
  return request({
    url: '/admin/llm/providers',
    method: 'get',
  });
}

/**
 * 新建大模型 API 渠道
 */
export function createAdminLLMProvider(data: LLMProviderCreate): Promise<{
  code: number;
  data: LLMProviderItem;
  message: string;
}> {
  return request({
    url: '/admin/llm/providers',
    method: 'post',
    data,
  });
}

/**
 * 更新大模型 API 渠道配置
 */
export function updateAdminLLMProvider(
  id: string,
  data: LLMProviderUpdate,
): Promise<{
  code: number;
  data: LLMProviderItem;
  message: string;
}> {
  return request({
    url: `/admin/llm/providers/${id}`,
    method: 'put',
    data,
  });
}

/**
 * 删除指定大模型 API 渠道
 */
export function deleteAdminLLMProvider(id: string): Promise<{
  code: number;
  data: { deleted: boolean; provider_id: string };
  message: string;
}> {
  return request({
    url: `/admin/llm/providers/${id}`,
    method: 'delete',
  });
}

/**
 * 快捷切换渠道启用/停用状态
 */
export function toggleAdminLLMProviderActive(id: string): Promise<{
  code: number;
  data: LLMProviderItem;
  message: string;
}> {
  return request({
    url: `/admin/llm/providers/${id}/toggle-active`,
    method: 'post',
  });
}

/**
 * 快捷切换特定模型的 C 端上架状态
 */
export function toggleAdminLLMModelPublic(
  providerId: string,
  modelId: string,
): Promise<{
  code: number;
  data: LLMProviderItem;
  message: string;
}> {
  return request({
    url: `/admin/llm/providers/${providerId}/models/${encodeURIComponent(modelId)}/toggle-public`,
    method: 'post',
  });
}

/**
 * 测试上游端点连通性 (Ping 测速)
 */
export function testLLMConnection(data: LLMTestConnectionRequest): Promise<{
  code: number;
  data: LLMTestConnectionResponse;
  message: string;
}> {
  return request({
    url: '/admin/llm/test-connection',
    method: 'post',
    data,
  });
}

/**
 * 请求上游 /v1/models 在线拉取可用模型
 */
export function fetchUpstreamLLMModels(data: LLMFetchModelsRequest): Promise<{
  code: number;
  data: LLMFetchModelsResponse;
  message: string;
}> {
  return request({
    url: '/admin/llm/fetch-models',
    method: 'post',
    data,
  });
}
