/**
 * 剧情对白音频播放器 Composable (单例调度器)。
 *
 * 保证同一时间全站仅发声一条语音，支持加载态、动态声波以及资源安全释放。
 *
 * @packageDocumentation
 */

import { ttsService } from "@/services/tts";
import { ref } from "vue";

// 全局单例播放状态
const currentMessageId = ref<string | null>(null);
const isPlaying = ref<boolean>(false);
const isLoading = ref<boolean>(false);
let globalAudio: HTMLAudioElement | null = null;
let currentObjectUrl: string | null = null;

export function useAudioPlayer() {
  /**
   * 清理当前正在播放的音频与临时对象 URL
   */
  function cleanupCurrentAudio(): void {
    if (globalAudio) {
      globalAudio.pause();
      globalAudio.src = "";
      globalAudio.onended = null;
      globalAudio.onerror = null;
      globalAudio = null;
    }
    if (currentObjectUrl) {
      URL.revokeObjectURL(currentObjectUrl);
      currentObjectUrl = null;
    }
    isPlaying.value = false;
    isLoading.value = false;
  }

  /**
   * 停止当前朗读
   */
  function stop(): void {
    cleanupCurrentAudio();
    currentMessageId.value = null;
  }

  /**
   * 播放或暂停指定消息文本语音
   */
  async function togglePlay(
    messageId: string,
    text: string,
    voice = "zh-CN-XiaoxiaoNeural",
  ): Promise<void> {
    // 1. 如果点击的是当前正在播放的消息，则暂停/停止
    if (currentMessageId.value === messageId) {
      if (isPlaying.value) {
        globalAudio?.pause();
        isPlaying.value = false;
      } else if (globalAudio) {
        await globalAudio.play();
        isPlaying.value = true;
      }
      return;
    }

    // 2. 如果点击的是其他消息，先安全停止上一条
    cleanupCurrentAudio();
    currentMessageId.value = messageId;
    isLoading.value = true;

    try {
      // 请求后端合成流
      const blob = await ttsService.synthesizeAudioBlob({
        text,
        voice,
      });

      // 异步返回时若已被切走，则直接废弃
      if (currentMessageId.value !== messageId) {
        return;
      }

      currentObjectUrl = URL.createObjectURL(blob);
      globalAudio = new Audio(currentObjectUrl);

      globalAudio.onended = () => {
        cleanupCurrentAudio();
        currentMessageId.value = null;
      };

      globalAudio.onerror = (e) => {
        console.error("音频播放异常:", e);
        cleanupCurrentAudio();
        currentMessageId.value = null;
      };

      await globalAudio.play();
      isPlaying.value = true;
    } catch (err) {
      console.error("TTS 朗读失败:", err);
      cleanupCurrentAudio();
      currentMessageId.value = null;
    } finally {
      isLoading.value = false;
    }
  }

  return {
    currentMessageId,
    isPlaying,
    isLoading,
    play: togglePlay,
    stop,
    togglePlay,
  };
}
