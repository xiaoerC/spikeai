# -*- coding: utf-8 -*-
"""Edge-TTS 语音合成服务单元测试。

验证:
1. 剧场动作括号描写、Markdown 语法、代码块与 Emoji 清洗过滤;
2. 预设精选音色列表结构;
3. 文本到语音二进制流合成。
"""

import pytest
from app.services.tts_service import TTSService


def test_clean_text_for_tts():
    """测试将复杂剧情文本清洗为适合 TTS 朗读的纯净自然对白。"""
    raw_text = (
        "（轻轻叹了口气，把手中的热茶递给你）旅人，你终于来了。\n"
        "```python\nprint('hello')\n```\n"
        "*微笑着看着远方的星空*\n"
        "【系统提示：好感度+10】今晚的月色真的很美呢…… 😊"
    )
    cleaned = TTSService.clean_text_for_tts(raw_text)

    # 验证括号、星号动作描写与代码块已被移除
    assert "轻轻叹了口气" not in cleaned
    assert "print('hello')" not in cleaned
    assert "微笑着看着远方的星空" not in cleaned
    assert "系统提示" not in cleaned
    assert "😊" not in cleaned

    # 验证自然对白完整保留
    assert "旅人，你终于来了" in cleaned
    assert "今晚的月色真的很美呢" in cleaned


def test_get_preset_voices():
    """测试获取精选音色清单。"""
    voices = TTSService.get_preset_voices()
    assert len(voices) >= 5
    voice_ids = [v["id"] for v in voices]
    assert "zh-CN-XiaoxiaoNeural" in voice_ids
    assert "zh-CN-YunxiNeural" in voice_ids


@pytest.mark.asyncio
async def test_synthesize_audio_stream():
    """测试异步流式语音合成产出有效音频数据。"""
    test_text = "你好，今夜星光格外璀璨。"
    audio_bytes = await TTSService.synthesize_audio_bytes(
        text=test_text,
        voice="zh-CN-XiaoxiaoNeural",
        rate="+0%",
        pitch="+0Hz",
    )
    assert len(audio_bytes) > 1000
    # MP3 帧通常包含 ID3 标识或 0xFF 0xFB/0xF3 同步头
    assert audio_bytes[:3] == b"ID3" or b"\xff" in audio_bytes[:100]


from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_tts_api_endpoints():
    """测试 TTS RESTful 接口。"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # 1. 获取音色列表
        res = await client.get("/api/v1/tts/voices")
        assert res.status_code == 200
        data = res.json()
        assert isinstance(data, list)
        assert len(data) >= 5

        # 2. 合成语音请求
        synth_res = await client.post(
            "/api/v1/tts/synthesize",
            json={
                "text": "欢迎光临叙梦世界。",
                "voice": "zh-CN-XiaoxiaoNeural",
                "rate": "+0%",
                "pitch": "+0Hz",
            },
        )
        assert synth_res.status_code == 200
        assert synth_res.headers["content-type"] == "audio/mpeg"
        assert len(synth_res.content) > 1000

