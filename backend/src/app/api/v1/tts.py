# -*- coding: utf-8 -*-
"""Edge-TTS 异步音频服务路由模块。

提供:
1. GET  /api/v1/tts/voices     - 获取支持的精选高质音色清单
2. POST /api/v1/tts/synthesize - 文本流式转换为 MP3 音频流
"""

import logging
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.services.tts_service import TTSService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tts", tags=["TTS语音合成"])


class TTSSynthesizeRequest(BaseModel):
    """TTS 语音合成入参契约。"""

    text: str = Field(..., min_length=1, max_length=10000, description="待合成的剧情文本或角色对白")
    voice: str = Field(default="zh-CN-XiaoxiaoNeural", description="Edge-TTS 音色 ID")
    rate: str = Field(default="+0%", description="语速调整 (例如: +10%, -10%)")
    pitch: str = Field(default="+0Hz", description="音调调整 (例如: +0Hz, +5Hz)")


@router.get("/voices", response_model=List[Dict[str, Any]])
async def get_supported_voices() -> List[Dict[str, Any]]:
    """获取系统支持的官方精选音色预设库。"""
    return TTSService.get_preset_voices()


@router.post("/synthesize")
async def synthesize_speech(req: TTSSynthesizeRequest) -> StreamingResponse:
    """将对白文本异步合成为 MP3 音频流 (audio/mpeg)。

    自动过滤动作描写与标点干扰，支持浏览器边下边播。
    """
    try:
        audio_stream = TTSService.synthesize_audio_stream(
            text=req.text,
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch,
        )

        return StreamingResponse(
            audio_stream,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": 'inline; filename="tts_audio.mp3"',
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
            },
        )
    except Exception as exc:
        logger.error(f"TTS 语音合成失败: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS 语音合成发生异常: {str(exc)}",
        )
