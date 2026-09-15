/**
 * Edge-TTS 语音合成前端强类型 API 服务。
 *
 * @packageDocumentation
 */

import api from "./api";

export interface TTSVoice {
  id: string;
  name: string;
  gender: "female" | "male";
  locale: string;
  tag: string;
}

export interface TTSSynthesizePayload {
  text: string;
  voice?: string;
  rate?: string;
  pitch?: string;
}

class TTSService {
  /**
   * 获取系统精选支持的 Edge-TTS 音色列表。
   */
  async getVoices(): Promise<TTSVoice[]> {
    const res = await api.get<TTSVoice[]>("/tts/voices");
    return res.data;
  }

  /**
   * 将对白文本合成为 MP3 二进制音频 Blob。
   */
  async synthesizeAudioBlob(payload: TTSSynthesizePayload): Promise<Blob> {
    const response = await fetch("/api/v1/tts/synthesize", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: payload.text,
        voice: payload.voice || "zh-CN-XiaoxiaoNeural",
        rate: payload.rate || "+0%",
        pitch: payload.pitch || "+0Hz",
      }),
    });

    if (!response.ok) {
      throw new Error(`TTS 语音合成请求失败: HTTP ${response.status}`);
    }

    return await response.blob();
  }
}

export const ttsService = new TTSService();
