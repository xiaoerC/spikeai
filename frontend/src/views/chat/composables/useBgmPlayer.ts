/**
 * 氛围 BGM 背景音律与场景白噪音 Composable。
 *
 * 基于 Web Audio API 纯程序化合成极其逼真沉浸的自然氛围白噪音（零外部大体积音频加载依赖），
 * 包含：雨夜客栈 (Rain)、壁炉篝火 (Campfire)、深空星辰 (Starlight)。
 *
 * @packageDocumentation
 */

import { ref } from "vue";

export interface BgmTrack {
  id: string;
  name: string;
  tag: string;
  icon: string;
}

export const PRESET_BGM_TRACKS: BgmTrack[] = [
  { id: "rain", name: "雨夜客栈", tag: "细雨微澜 · 瓦檐雨滴", icon: "🌧️" },
  { id: "fire", name: "壁炉微光", tag: "柴火噼啪 · 温暖静谧", icon: "🔥" },
  { id: "star", name: "深邃星辰", tag: "浩瀚虚空 · 冥想空灵", icon: "✨" },
];

const currentTrackId = ref<string | null>(null);
const isPlaying = ref<boolean>(false);
const volume = ref<number>(60); // 0 ~ 100

// Web Audio API 引擎单例
let audioCtx: AudioContext | null = null;
let masterGain: GainNode | null = null;
let currentNodes: AudioNode[] = [];
let customAudioEl: HTMLAudioElement | null = null;

function getAudioContext(): AudioContext {
  if (!audioCtx) {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    audioCtx = new AudioContextClass();
    masterGain = audioCtx.createGain();
    masterGain.gain.setValueAtTime(volume.value / 100, audioCtx.currentTime);
    masterGain.connect(audioCtx.destination);
  }
  if (audioCtx.state === "suspended") {
    audioCtx.resume();
  }
  return audioCtx;
}

/**
 * 停止并断开当前的程序化音轨
 */
function stopNodes(): void {
  if (customAudioEl) {
    customAudioEl.pause();
  }
  for (const node of currentNodes) {
    try {
      if ((node as any).stop) {
        (node as any).stop();
      }
      node.disconnect();
    } catch {
      // 忽略断开已停止节点的异常
    }
  }
  currentNodes = [];
}

/**
 * 生成粉红噪声/雨声缓冲源
 */
function createRainSynth(ctx: AudioContext): AudioNode[] {
  const bufferSize = ctx.sampleRate * 2;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  let b0 = 0,
    b1 = 0,
    b2 = 0,
    b3 = 0,
    b4 = 0,
    b5 = 0,
    b6 = 0;
  for (let i = 0; i < bufferSize; i++) {
    const white = Math.random() * 2 - 1;
    b0 = 0.99886 * b0 + white * 0.0555179;
    b1 = 0.99332 * b1 + white * 0.0750759;
    b2 = 0.969 * b2 + white * 0.153852;
    b3 = 0.8665 * b3 + white * 0.3104856;
    b4 = 0.55 * b4 + white * 0.5329522;
    b5 = -0.7616 * b5 - white * 0.016898;
    data[i] = (b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362) * 0.06;
    b6 = white * 0.115926;
  }

  const noise = ctx.createBufferSource();
  noise.buffer = buffer;
  noise.loop = true;

  const filter = ctx.createBiquadFilter();
  filter.type = "lowpass";
  filter.frequency.setValueAtTime(1200, ctx.currentTime);

  noise.connect(filter);
  filter.connect(masterGain!);
  noise.start();

  return [noise, filter];
}

/**
 * 生成壁炉微光音轨 (低频沉木与噼啪微声)
 */
function createFireSynth(ctx: AudioContext): AudioNode[] {
  const bufferSize = ctx.sampleRate * 2;
  const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
  const data = buffer.getChannelData(0);
  for (let i = 0; i < bufferSize; i++) {
    const crackle = Math.random() < 0.003 ? (Math.random() * 2 - 1) * 0.8 : 0;
    data[i] = Math.random() * 0.05 + crackle;
  }

  const noise = ctx.createBufferSource();
  noise.buffer = buffer;
  noise.loop = true;

  const filter = ctx.createBiquadFilter();
  filter.type = "bandpass";
  filter.frequency.setValueAtTime(600, ctx.currentTime);
  filter.Q.setValueAtTime(2.0, ctx.currentTime);

  noise.connect(filter);
  filter.connect(masterGain!);
  noise.start();

  return [noise, filter];
}

/**
 * 生成深邃星辰音轨 (微弱正弦长音空灵音律)
 */
function createStarSynth(ctx: AudioContext): AudioNode[] {
  const osc1 = ctx.createOscillator();
  const osc2 = ctx.createOscillator();
  const gain = ctx.createGain();

  osc1.type = "sine";
  osc1.frequency.setValueAtTime(174, ctx.currentTime); // 174Hz 治愈声频

  osc2.type = "triangle";
  osc2.frequency.setValueAtTime(285, ctx.currentTime);

  gain.gain.setValueAtTime(0.08, ctx.currentTime);

  osc1.connect(gain);
  osc2.connect(gain);
  gain.connect(masterGain!);

  osc1.start();
  osc2.start();

  return [osc1, osc2, gain];
}

export function useBgmPlayer() {
  function setVolume(val: number): void {
    volume.value = Math.max(0, Math.min(100, val));
    if (masterGain && audioCtx) {
      masterGain.gain.setValueAtTime(volume.value / 100, audioCtx.currentTime);
    }
    if (customAudioEl) {
      customAudioEl.volume = volume.value / 100;
    }
  }

  function playTrack(trackId: string, customUrl?: string): void {
    stopNodes();

    if (trackId === "custom" || trackId === "character_bgm") {
      if (customUrl) {
        if (!customAudioEl) {
          customAudioEl = new Audio(customUrl);
          customAudioEl.loop = true;
        } else {
          customAudioEl.src = customUrl;
        }
        customAudioEl.volume = volume.value / 100;
        customAudioEl.play().catch((err) => {
          console.warn("BGM 播放受限:", err);
        });
      }
    } else {
      const ctx = getAudioContext();
      if (trackId === "rain") {
        currentNodes = createRainSynth(ctx);
      } else if (trackId === "fire") {
        currentNodes = createFireSynth(ctx);
      } else if (trackId === "star") {
        currentNodes = createStarSynth(ctx);
      }
    }

    currentTrackId.value = trackId;
    isPlaying.value = true;
  }

  function togglePlayTrack(trackId: string, customUrl?: string): void {
    if (currentTrackId.value === trackId && isPlaying.value) {
      pause();
    } else {
      playTrack(trackId, customUrl);
    }
  }

  function pause(): void {
    stopNodes();
    isPlaying.value = false;
  }

  return {
    currentTrackId,
    isPlaying,
    volume,
    presetTracks: PRESET_BGM_TRACKS,
    setVolume,
    playTrack,
    togglePlayTrack,
    pause,
  };
}
