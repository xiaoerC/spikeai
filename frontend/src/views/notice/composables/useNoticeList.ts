/**
 * 公告中心业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { MOCK_NOTICES } from "@/data/mockNotices";
import type { NoticeCategory, NoticeItem } from "@/views/notice/types";
import { computed, ref } from "vue";

export function useNoticeList() {
  const notices = ref<NoticeItem[]>(MOCK_NOTICES);
  const currentCategory = ref<NoticeCategory>("all");
  const selectedNotice = ref<NoticeItem | null>(null);
  const isModalOpen = ref<boolean>(false);

  // 分类筛选列表
  const filteredNotices = computed(() => {
    if (currentCategory.value === "all") {
      return notices.value;
    }
    return notices.value.filter((n) => n.type === currentCategory.value);
  });

  // 公告总数统计
  const totalCount = computed(() => notices.value.length);

  function setCategory(cat: NoticeCategory): void {
    currentCategory.value = cat;
  }

  function openNoticeDetail(notice: NoticeItem): void {
    selectedNotice.value = notice;
    isModalOpen.value = true;
  }

  function closeNoticeDetail(): void {
    isModalOpen.value = false;
    selectedNotice.value = null;
  }

  return {
    notices: filteredNotices,
    totalCount,
    currentCategory,
    selectedNotice,
    isModalOpen,
    setCategory,
    openNoticeDetail,
    closeNoticeDetail,
  };
}
