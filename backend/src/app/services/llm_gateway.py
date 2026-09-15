"""LLM 多模型统一网关与流式生成适配器模块。

提供 OpenAI、MIMO (mimo-v2.5)、LongCat (LongCat-2.0)、DeepSeek、GLM、Ollama 等多厂商大模型的统一抽象接入，
支持异步流式生成、`<thinking>` 深度思维链解析与本地 Mock 高保真回退。

Usage:
    >>> from app.services.llm_gateway import llm_gateway
    >>> messages = [{"role": "system", "content": "..."}, {"role": "user", "content": "你好"}]
    >>> async for event_type, chunk in llm_gateway.stream_chat(messages, model="mimo-v2.5"):
    >>>     print(f"[{event_type}] {chunk}")
"""

import asyncio
import json
import logging
import re
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseLLMClient(ABC):
    """LLM 客户端抽象基类。"""

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.8,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        seed: int | None = None,
        stop: list[str] | None = None,
        reasoning_effort: str | None = None,
        supports_reasoning: bool = True,
    ) -> AsyncGenerator[tuple[str, str], None]:
        """异步流式对话。

        Args:
            messages: OpenAI 格式的消息列表
            model: 模型标识字符串
            temperature: 采样温度
            max_tokens: 最大生成 Token 数
            top_p: 核采样概率阈值
            frequency_penalty: 词频惩罚
            presence_penalty: 存在惩罚
            seed: 随机种子
            stop: 自定义终止字符串列表
            reasoning_effort: 思维链强度参数 (low/medium/high)
            supports_reasoning: 是否允许并开启思维链/思考流输出

        Yields:
            tuple[str, str]: (event_type, chunk_text)
                - event_type 为 "thinking" 时，chunk_text 为思维链片段
                - event_type 为 "message" 时，chunk_text 为正文片段
        """
        yield "message", ""


class OpenAILLMClient(BaseLLMClient):
    """OpenAI 兼容协议客户端 (支持 MIMO, LongCat, OpenAI, DeepSeek, GLM, Ollama 等)。"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        default_model: str | None = None,
        custom_headers: dict[str, str] | None = None,
        timeout: float = 60.0,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.custom_headers = custom_headers or {}
        self.timeout = timeout

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.8,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        seed: int | None = None,
        stop: list[str] | None = None,
        reasoning_effort: str | None = None,
        supports_reasoning: bool = True,
    ) -> AsyncGenerator[tuple[str, str], None]:
        """通过 httpx 发起 SSE 请求并流式解析 chunk。"""
        # 确定实际请求所用的模型名称
        effective_model = self.default_model or model
        if "xiaomimimo" in self.base_url:
            effective_model = "mimo-v2.5"
        elif "longcat" in self.base_url:
            effective_model = "LongCat-2.0"
        elif "deepseek" in self.base_url and self.default_model:
            effective_model = self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.custom_headers:
            headers.update(self.custom_headers)

        payload: dict[str, Any] = {
            "model": effective_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": True,
        }
        if seed is not None and seed >= 0:
            payload["seed"] = seed
        if stop:
            payload["stop"] = stop
        # 仅当模型明确支持思考且传入了 reasoning_effort 时，才向下游传递该参数
        if supports_reasoning and reasoning_effort:
            payload["reasoning_effort"] = reasoning_effort
        elif not supports_reasoning:
            # 针对支持 thinking 控制的推理大模型协议 (如 DeepSeek, Claude, SiliconFlow 等)，显式下发关闭思考
            payload["thinking"] = {"type": "disabled"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # 优先尝试流式连接
                stream_ctx = client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                stream_response = await stream_ctx.__aenter__()

                # 若上游不识别 thinking: {type: disabled} 返回 400，降级去除 thinking 重试流
                if stream_response.status_code == 400 and "thinking" in payload:
                    await stream_ctx.__aexit__(None, None, None)
                    payload.pop("thinking", None)
                    stream_ctx = client.stream(
                        "POST",
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                    )
                    stream_response = await stream_ctx.__aenter__()

                try:
                    if stream_response.status_code != 200:
                        err_body = await stream_response.aread()
                        err_text = err_body.decode(errors="ignore")
                        logger.error(
                            "LLM API returned error %d: %s",
                            stream_response.status_code,
                            err_text,
                        )
                        yield "error", f"LLM API 响应异常 ({stream_response.status_code}): {err_text[:100]}"
                        return

                    is_inside_thinking_tag = False

                    async for line in stream_response.aiter_lines():
                        if not line:
                            continue
                        # 过滤 SSE 注释行 (例如 : PROCESSING)
                        if line.startswith(":"):
                            continue
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break

                        try:
                            data_json = json.loads(data_str)
                            choices = data_json.get("choices")
                            if not choices or not isinstance(choices, list) or len(choices) == 0:
                                continue
                            choice = choices[0]
                            delta = choice.get("delta", {})

                            # 1. 适配 DeepSeek-R1 / GLM / MIMO 的原生 reasoning_content 字段
                            reasoning = delta.get("reasoning_content") or delta.get("reasoning")
                            if reasoning and supports_reasoning:
                                yield "thinking", reasoning

                            # 2. 适配正文 content (同时兼容 <think> 与 <thinking> 标签)
                            content = delta.get("content")
                            if content:
                                tag_open = "<think>" if "<think>" in content else ("<thinking>" if "<thinking>" in content else None)
                                tag_close = "</think>" if "</think>" in content else ("</thinking>" if "</thinking>" in content else None)

                                if tag_open and tag_close and content.find(tag_open) < content.find(tag_close):
                                    parts_before = content.split(tag_open, 1)[0]
                                    middle_and_after = content.split(tag_open, 1)[1]
                                    think_part, after_part = middle_and_after.split(tag_close, 1)
                                    if parts_before:
                                        yield "message", parts_before
                                    if think_part and supports_reasoning:
                                        yield "thinking", think_part
                                    if after_part:
                                        yield "message", after_part
                                    is_inside_thinking_tag = False
                                elif tag_open:
                                    is_inside_thinking_tag = True
                                    parts = content.split(tag_open, 1)
                                    if parts[0]:
                                        yield "message", parts[0]
                                    if len(parts) > 1 and parts[1] and supports_reasoning:
                                        yield "thinking", parts[1]
                                elif tag_close:
                                    is_inside_thinking_tag = False
                                    parts = content.split(tag_close, 1)
                                    if parts[0] and supports_reasoning:
                                        yield "thinking", parts[0]
                                    if len(parts) > 1 and parts[1]:
                                        yield "message", parts[1]
                                else:
                                    if is_inside_thinking_tag:
                                        if supports_reasoning:
                                            yield "thinking", content
                                    else:
                                        yield "message", content
                        except json.JSONDecodeError:
                            continue
                finally:
                    await stream_ctx.__aexit__(None, None, None)
            except httpx.TimeoutException:
                logger.warning("LLM upstream request timed out")
                yield "error", "上游大模型服务响应超时（网络拥堵或排队中），请重试"
            except httpx.ConnectError:
                logger.error("LLM upstream connect error")
                yield "error", "无法连接到上游大模型服务节点，请检查网络"
            except Exception as e:
                logger.exception("LLM stream request failed: %s", e)
                yield "error", f"网络连接或流式生成异常: {e}"


class MockLLMClient(BaseLLMClient):
    """高保真本地 Mock LLM 驱动（仅作为最后备选兜底）。"""

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.8,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        seed: int | None = None,
        stop: list[str] | None = None,
        reasoning_effort: str | None = None,
        supports_reasoning: bool = True,
    ) -> AsyncGenerator[tuple[str, str], None]:
        """模拟真实的流式输出与思考链。"""
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user" and not last_user_msg:
                last_user_msg = m.get("content", "")

        if supports_reasoning:
            thinking_paragraphs = [
                f"正在解析玩家输入「{last_user_msg[:20]}...」的情绪基调与剧情意图……",
                "检索当前剧情分支与人物好感度状态机，匹配当下场景氛围与语气……",
                "设定人物性格响应策略：保持专属口吻，推进剧情冲突与情绪互动。",
            ]

            for p in thinking_paragraphs:
                for char in p:
                    yield "thinking", char
                    await asyncio.sleep(0.005)
                yield "thinking", "\n"
                await asyncio.sleep(0.01)

            await asyncio.sleep(0.05)

        reply_body = (
            f"（微微抬眸注视着你，眼神中闪过一丝复杂的神色）\n\n"
            f"「{last_user_msg}」……哼，你总是能在最意想不到的时候说出这种话呢。\n\n"
            f"不过既然你已经做出了选择，那无论接下来的命运走向何方，我都不会轻易放手了。"
            f"准备好了吗？前面的路可不会是一帆风顺的。"
        )

        for char in reply_body:
            yield "message", char
            await asyncio.sleep(0.008)


class LLMGateway:
    """LLM 多模型统一网关。"""

    def __init__(self) -> None:
        self.mock_client = MockLLMClient()

    async def _get_client(self, model: str) -> BaseLLMClient:
        """依据模型在系统数据库配置与环境变量中动态获取可用客户端。"""
        # 0. 单测环境或指定 mock 模型
        if settings.ENV == "test" or model == "mock":
            return self.mock_client

        # 1. 优先从数据库动态查询该模型是否有活跃的渠道配置
        try:
            from app.core.database import AsyncSessionLocal
            from app.services.llm_service import LLMService

            async with AsyncSessionLocal() as db:
                creds = await LLMService.get_provider_credentials_for_model(db, model)
                if creds:
                    base_url, api_key, custom_headers, timeout_sec = creds
                    logger.info("已动态命中数据库 LLM 渠道配置: model=%s, base_url=%s", model, base_url)
                    return OpenAILLMClient(
                        api_key=api_key,
                        base_url=base_url,
                        default_model=model,
                        custom_headers=custom_headers,
                        timeout=float(timeout_sec),
                    )
        except Exception as e:
            logger.warning("动态查询数据库 LLM 渠道配置异常，回退至默认逻辑: %s", e)

        model_lower = model.lower()

        # 2. 小米 MIMO (mimo-v2.5)
        if "mimo" in model_lower:
            return OpenAILLMClient(
                api_key=settings.MIMO_API_KEY,
                base_url=settings.MIMO_BASE_URL,
                default_model="mimo-v2.5",
            )

        # 3. LongCat (LongCat-2.0)
        if "longcat" in model_lower:
            return OpenAILLMClient(
                api_key=settings.LONGCAT_API_KEY,
                base_url=settings.LONGCAT_BASE_URL,
                default_model="LongCat-2.0",
            )

        # 4. DeepSeek 系列 (支持 deepseek-v4-flash / deepseek-chat / deepseek-reasoner / ds4f 等)
        if ("deepseek" in model_lower or "ds4f" in model_lower) and settings.DEEPSEEK_API_KEY:
            actual_model = "deepseek-v4-flash" if ("flash" in model_lower or "ds4f" in model_lower) else model
            return OpenAILLMClient(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com",
                default_model=actual_model,
            )

        # 5. OpenAI 系列
        if ("gpt" in model_lower or "o1" in model_lower) and settings.OPENAI_API_KEY:
            return OpenAILLMClient(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )

        # 6. 本地 Ollama
        if "ollama" in model_lower or "local" in model_lower:
            return OpenAILLMClient(
                api_key="ollama",
                base_url=f"{settings.OLLAMA_BASE_URL}/v1",
            )

        # 7. 默认首选真实 MIMO 大模型 (只要配置了 Key 就直连真实模型)
        if settings.MIMO_API_KEY:
            return OpenAILLMClient(
                api_key=settings.MIMO_API_KEY,
                base_url=settings.MIMO_BASE_URL,
                default_model="mimo-v2.5",
            )

        # 8. 备用 LongCat
        if settings.LONGCAT_API_KEY:
            return OpenAILLMClient(
                api_key=settings.LONGCAT_API_KEY,
                base_url=settings.LONGCAT_BASE_URL,
                default_model="LongCat-2.0",
            )

        # 9. 最后回退至 Mock 客户端
        return self.mock_client

    async def stream_chat(
        self,
        messages: list[dict[str, str]],
        model: str = "mimo-v2.5",
        temperature: float = 0.8,
        max_tokens: int = 2048,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        seed: int | None = None,
        stop: list[str] | None = None,
        reasoning_effort: str | None = None,
        supports_reasoning: bool = True,
    ) -> AsyncGenerator[tuple[str, str], None]:
        """统一流式生成入口。

        Args:
            messages: 上下文消息列表
            model: 模型标识 (如 "mimo-v2.5" 或 "LongCat-2.0")
            temperature: 温度
            max_tokens: 最大 tokens
            top_p: 核采样
            frequency_penalty: 频率惩罚
            presence_penalty: 存在惩罚
            seed: 随机种子
            stop: 自定义终止词序列列表
            reasoning_effort: 思维链推理强度 (low/medium/high)
            supports_reasoning: 是否启用思维链

        Yields:
            tuple[str, str]: (event_type, chunk_text)
        """
        client = await self._get_client(model)
        async for event_type, chunk in client.stream_chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            seed=seed,
            stop=stop,
            reasoning_effort=reasoning_effort,
            supports_reasoning=supports_reasoning,
        ):
            yield event_type, chunk


# 全局单例
llm_gateway = LLMGateway()
