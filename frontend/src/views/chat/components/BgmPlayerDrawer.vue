<script setup lang="ts">
/**
 * 氛围 BGM 背景音律与场景白噪音沉浸抽屉 (1:1 黑金拟物高保真)
 *
 * @packageDocumentation
 */

import { useBgmPlayer } from "@/views/chat/composables/useBgmPlayer";
import { Pause, Play, Volume2, X } from "lucide-vue-next";

defineProps<{
  isOpen: boolean;
  characterBgmUrl?: string;
  characterName?: string;
}>();

const emit = defineEmits<(e: "close") => void>();

const { currentTrackId, isPlaying, volume, presetTracks, setVolume, togglePlayTrack, pause } =
  useBgmPlayer();

function handleVolumeChange(e: Event): void {
  const target = e.target as HTMLInputElement;
  setVolume(Number(target.value));
}
</script>

<template>
  <!-- 遮罩与抽屉容器 -->
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm transition-opacity"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-md bg-[#141210]/95 border-t border-white/10 rounded-t-3xl p-5 shadow-2xl flex flex-col gap-4 animate-in slide-in-from-bottom duration-200"
    >
      <!-- 顶部把手与标题 -->
      <div class="flex flex-col items-center gap-2">
        <div class="w-10 h-1 rounded-full bg-white/20" />
        <div class="w-full flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="text-base">🎵</span>
            <h3 class="text-sm font-semibold text-white tracking-wide">
              场景音律 · BGM
            </h3>
          </div>
          <button
            type="button"
            @click="emit('close')"
            class="w-7 h-7 rounded-full flex items-center justify-center text-white/50 hover:text-white hover:bg-white/10 transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- 音轨列表 -->
      <div class="flex flex-col gap-2 my-1">
        <!-- 角色专属原声 BGM -->
        <div
          v-if="characterBgmUrl"
          @click="togglePlayTrack('character_bgm', characterBgmUrl)"
          :class="[
            'flex items-center justify-between px-3.5 py-3 rounded-xl border transition-all cursor-pointer select-none',
            currentTrackId === 'character_bgm' && isPlaying
              ? 'bg-[#F9C86D]/15 border-[#F9C86D]/50 shadow-[0_0_12px_rgba(249,200,109,0.2)]'
              : 'bg-gradient-to-r from-[#F9C86D]/10 to-transparent border-[#F9C86D]/20 hover:border-[#F9C86D]/40'
          ]"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">👑</span>
            <div class="flex flex-col">
              <span class="text-xs font-medium text-[#F9C86D]">
                {{ characterName || "角色" }} · 专属原声
              </span>
              <span class="text-[10px] text-white/50 truncate max-w-[200px]">
                {{ characterBgmUrl }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <div
              v-if="currentTrackId === 'character_bgm' && isPlaying"
              class="flex items-end gap-0.5 h-3.5"
            >
              <span class="w-0.5 h-2 bg-[#F9C86D] animate-bounce" style="animation-delay: 0ms;" />
              <span class="w-0.5 h-3.5 bg-[#F9C86D] animate-bounce" style="animation-delay: 150ms;" />
              <span class="w-0.5 h-2.5 bg-[#F9C86D] animate-bounce" style="animation-delay: 300ms;" />
            </div>
            <button
              type="button"
              class="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-white/80 hover:scale-105 active:scale-95 transition-all"
            >
              <Pause
                v-if="currentTrackId === 'character_bgm' && isPlaying"
                class="w-3.5 h-3.5 fill-current text-[#F9C86D]"
              />
              <Play
                v-else
                class="w-3.5 h-3.5 fill-current ml-0.5 text-white/70"
              />
            </button>
          </div>
        </div>

        <!-- 预设氛围白噪音 -->
        <div
          v-for="track in presetTracks"
          :key="track.id"
          @click="togglePlayTrack(track.id)"
          :class="[
            'flex items-center justify-between px-3.5 py-3 rounded-xl border transition-all cursor-pointer select-none',
            currentTrackId === track.id && isPlaying
              ? 'bg-[#F9C86D]/10 border-[#F9C86D]/40 shadow-[0_0_12px_rgba(249,200,109,0.15)]'
              : 'bg-white/5 border-white/5 hover:bg-white/10'
          ]"
        >
          <div class="flex items-center gap-3">
            <span class="text-xl">{{ track.icon }}</span>
            <div class="flex flex-col">
              <span class="text-xs font-medium text-white/90">
                {{ track.name }}
              </span>
              <span class="text-[10px] text-white/40">
                {{ track.tag }}
              </span>
            </div>
          </div>

          <!-- 播放/暂停指示 -->
          <div class="flex items-center gap-2">
            <!-- 律动声波条 (正在播放) -->
            <div
              v-if="currentTrackId === track.id && isPlaying"
              class="flex items-end gap-0.5 h-3.5"
            >
              <span class="w-0.5 h-2 bg-[#F9C86D] animate-bounce" style="animation-delay: 0ms;" />
              <span class="w-0.5 h-3.5 bg-[#F9C86D] animate-bounce" style="animation-delay: 150ms;" />
              <span class="w-0.5 h-2.5 bg-[#F9C86D] animate-bounce" style="animation-delay: 300ms;" />
            </div>
            <button
              type="button"
              class="w-7 h-7 rounded-full bg-white/10 flex items-center justify-center text-white/80 hover:scale-105 active:scale-95 transition-all"
            >
              <Pause
                v-if="currentTrackId === track.id && isPlaying"
                class="w-3.5 h-3.5 fill-current text-[#F9C86D]"
              />
              <Play
                v-else
                class="w-3.5 h-3.5 fill-current ml-0.5 text-white/70"
              />
            </button>
          </div>
        </div>
      </div>

      <!-- 音量控制滑轨 -->
      <div class="pt-2 border-t border-white/5 flex flex-col gap-2">
        <div class="flex items-center justify-between text-xs text-white/60">
          <div class="flex items-center gap-1.5">
            <Volume2 class="w-3.5 h-3.5 text-white/50" />
            <span>环境音量</span>
          </div>
          <span class="font-mono text-[11px] text-[#F9C86D]">{{ volume }}%</span>
        </div>
        <input
          type="range"
          min="0"
          max="100"
          :value="volume"
          @input="handleVolumeChange"
          class="w-full h-1.5 bg-white/10 rounded-lg appearance-none cursor-pointer accent-[#F9C86D]"
        />
      </div>
    </div>
  </div>
</template>
