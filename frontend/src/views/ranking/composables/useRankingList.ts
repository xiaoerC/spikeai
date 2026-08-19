/**
 * 榜单业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_RANKING_USERS } from "@/data/mockRankings";
import type { RankingUserItem } from "@/views/ranking/types";
import { computed, ref } from "vue";

export function useRankingList() {
  const users = ref<RankingUserItem[]>(MOCK_RANKING_USERS);

  // 冠军 (No. 1)
  const champion = computed(() => users.value.find((u) => u.rank === 1));
  // 亚军 (No. 2)
  const runnerUp = computed(() => users.value.find((u) => u.rank === 2));
  // 季军 (No. 3)
  const thirdPlace = computed(() => users.value.find((u) => u.rank === 3));

  // 第 4 名及以后的排行列表
  const restUsers = computed(() => users.value.filter((u) => u.rank > 3));

  return {
    users,
    champion,
    runnerUp,
    thirdPlace,
    restUsers,
  };
}
