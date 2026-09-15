# -*- coding: utf-8 -*-
"""Edge-TTS 异步语音合成服务模块。

提供文本清洗过滤（剥离动作括号与非语言字符）、多角色精选音色列表查询以及
高质量低延迟音频流合成能力。

Usage:
    audio_bytes = await TTSService.synthesize_audio_bytes("你好呀", "zh-CN-XiaoxiaoNeural")
"""

import re
import logging
from typing import AsyncGenerator, Dict, List, Any
import edge_tts

logger = logging.getLogger(__name__)


class TTSService:
    """Edge-TTS 语音合成业务引擎。"""

    # 精选高品质音色预设库
    PRESET_VOICES: List[Dict[str, str]] = [
        {
            "id": "zh-CN-XiaoxiaoNeural",
            "name": "晓晓 (暖心温柔 · 少女/女主)",
            "gender": "female",
            "locale": "zh-CN",
            "tag": "温柔 / 治愈 / 情感共鸣",
        },
        {
            "id": "zh-CN-YunxiNeural",
            "name": "云希 (阳光少年 · 青年/男主)",
            "gender": "male",
            "locale": "zh-CN",
            "tag": "阳光 / 澄澈 / 活力",
        },
        {
            "id": "zh-CN-XiaoyiNeural",
            "name": "晓伊 (灵动娇俏 · 萝莉/妹妹)",
            "gender": "female",
            "locale": "zh-CN",
            "tag": "活泼 / 傲娇 / 灵动",
        },
        {
            "id": "zh-CN-YunjianNeural",
            "name": "云健 (沉稳厚重 · 青年/大叔)",
            "gender": "male",
            "locale": "zh-CN",
            "tag": "沉稳 / 威严 / 旁白",
        },
        {
            "id": "zh-CN-YunyangNeural",
            "name": "云扬 (清朗专业 · 播音/叙述)",
            "gender": "male",
            "locale": "zh-CN",
            "tag": "专业 / 明快 / 故事叙述",
        },
        {
            "id": "zh-CN-shaanxi-XiaoniNeural",
            "name": "晓妮 (俏皮个性 · 方言特色)",
            "gender": "female",
            "locale": "zh-CN-shaanxi",
            "tag": "热情 / 亲和 / 特色",
        },
    ]

    @classmethod
    def clean_text_for_tts(cls, raw_text: str) -> str:
        """清洗剧情对白文本，剥离括号动作描写、Markdown 语法、代码块与 Emoji。

        Args:
            raw_text: 大模型回复的原始多模态对白（包含动作括号、Markdown 标签等）。

        Returns:
            纯净自然的口语音频输入文本。
        """
        if not raw_text:
            return ""

        text = raw_text

        # 1. 过滤多行代码块 ```...``` 与 行内代码 `...`
        text = re.sub(r"```(?:[\s\S]*?)```", "", text)
        text = re.sub(r"`[^`]*`", "", text)

        # 2. 过滤括号内的剧场动作与心理活动描写
        # 中文全角括号 （...）
        text = re.sub(r"（[^）\n]*）", "", text)
        # 英文半角圆括号 (...)
        text = re.sub(r"\([^)\n]*\)", "", text)
        # 剧本动作描写 *...*
        text = re.sub(r"\*[^*\n]*\*", "", text)
        # 系统提示与说明 【...】 与 [...]
        text = re.sub(r"【[^】\n]*】", "", text)
        text = re.sub(r"\[[^\]\n]*\]", "", text)

        # 3. 剥离 Markdown 标题、粗体、斜体、引用符号
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"[*_~]", "", text)
        text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)

        # 4. 剥离 4 字节 Emoji 表情符号
        emoji_pattern = re.compile(r"[\U00010000-\U0010ffff]", flags=re.UNICODE)
        text = emoji_pattern.sub("", text)

        # 5. 清理多余空行与连续空白字符
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned = " ".join(lines).strip()

        # 防御性回退：如果清洗后字符为空（例如全篇全是描写），保留原句的纯文本部分
        if not cleaned:
            cleaned = re.sub(r"[#*_~`]", "", raw_text).strip()

        return cleaned

    @classmethod
    def get_preset_voices(cls) -> List[Dict[str, str]]:
        """获取系统精选支持的 Edge-TTS 音色列表。"""
        return list(cls.PRESET_VOICES)

    @classmethod
    async def synthesize_audio_bytes(
        cls,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> bytes:
        """异步合成文本为完整 MP3 音频字节。

        Args:
            text: 待合成文本。
            voice: Edge-TTS 音色 ID。
            rate: 语速调节（如 "+10%", "-10%"）。
            pitch: 音调调节（如 "+0Hz"）。

        Returns:
            合成的 MP3 二进制数据字节流。
        """
        cleaned = cls.clean_text_for_tts(text)
        if not cleaned:
            cleaned = "……"

        communicate = edge_tts.Communicate(
            text=cleaned,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )

        audio_chunks: List[bytes] = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunks.append(chunk["data"])

        return b"".join(audio_chunks)

    @classmethod
    async def synthesize_audio_stream(
        cls,
        text: str,
        voice: str = "zh-CN-XiaoxiaoNeural",
        rate: str = "+0%",
        pitch: str = "+0Hz",
    ) -> AsyncGenerator[bytes, None]:
        """异步生成音频分块数据流，支持 HTTP 流式边下边播。

        Args:
            text: 待合成文本。
            voice: Edge-TTS 音色 ID。
            rate: 语速调节。
            pitch: 音调调节。

        Yields:
            音频分块数据字节。
        """
        cleaned = cls.clean_text_for_tts(text)
        if not cleaned:
            cleaned = "……"

        communicate = edge_tts.Communicate(
            text=cleaned,
            voice=voice,
            rate=rate,
            pitch=pitch,
        )

        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
