/**
 * 创作者专区业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_CREATORS } from "@/data/mockCreators";
import type { CreatorItem } from "@/views/creator/types";
import { ref } from "vue";

export function useCreatorList() {
  const creators = ref<CreatorItem[]>(JSON.parse(JSON.stringify(MOCK_CREATORS)));

  /**
   * 切换关注状态 (乐观更新)
   * @param creatorId - 创作者唯一标识
   */
  function toggleFollow(creatorId: string): void {
    const target = creators.value.find((c) => c.id === creatorId);
    if (target) {
      target.isFollowed = !target.isFollowed;
    }
  }

  return {
    creators,
    toggleFollow,
  };
}
