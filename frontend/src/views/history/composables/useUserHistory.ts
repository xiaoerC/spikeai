/**
 * 个人历史记录与人设/指令/画师串/总结提示词/记忆增强模型/Mod模组中心/合集/Mod设置业务逻辑组合式 Hook
 *
 * @packageDocumentation
 */

import { type CharacterDetail, characterService } from "@/services/character";
import { chatService } from "@/services/chat";
import type {
  ArtistPromptItem,
  CollectionModEntry,
  CollectionSubTab,
  CommandItem,
  CreatedModEntry,
  CreatedModItem,
  CustomSubCategory,
  HistoryViewMode,
  ModCategoryTag,
  ModCollectionItem,
  ModItem,
  ModSortType,
  ModSubCategory,
  PersonaItem,
  PurchasedModItem,
  UploadSubCategory,
  UserHistoryCategory,
  UserHistoryItem,
} from "@/views/history/types";
import { computed, onMounted, ref } from "vue";

export function useUserHistory() {
  const historyList = ref<UserHistoryItem[]>([]);
  const isLoadingHistory = ref<boolean>(false);
  const currentCategory = ref<UserHistoryCategory>("story");
  const uploadSubCategory = ref<UploadSubCategory>("story"); // 上传记录二级分类 (剧情卡 / 绅士卡)
  const customSubCategory = ref<CustomSubCategory>("persona"); // 自定义二级分类 (人设 / 指令 / 画师串 / 总结提示词 / 记忆增强模型)
  const viewMode = ref<HistoryViewMode>("grid"); // 默认改为网格视图 (1:1 原型高保真)
  const isBatchMode = ref<boolean>(false);
  const selectedIds = ref<Set<string>>(new Set());
  const editingRemarkItem = ref<UserHistoryItem | null>(null);
  const isRemarkModalOpen = ref<boolean>(false);

  // 0. 真实历史会话数据加载
  async function fetchHistory(): Promise<void> {
    isLoadingHistory.value = true;
    try {
      const sessions = await chatService.getChatSessions();
      historyList.value = sessions.map((s) => ({
        id: s.id,
        characterId: s.character_id,
        title: s.title,
        avatar: s.avatar || s.banner_url || "",
        avatarUrl: s.avatar || s.banner_url || "",
        remark: s.remark,
        category: "story" as const,
        isPinned: s.is_pinned,
        lastMessage: s.last_message,
        lastMessageTime: s.last_message_time,
        messageCount: s.message_count,
        tags: [],
        gender: "female" as const,
        createdAt: s.updated_at,
      }));
    } catch (err) {
      console.error("获取真实历史会话失败:", err);
    } finally {
      isLoadingHistory.value = false;
    }
  }

  // 0. 我上传的角色卡状态机
  const myUploadedCharacters = ref<CharacterDetail[]>([]);
  const isLoadingMyCharacters = ref<boolean>(false);

  const filteredMyUploadedCharacters = computed(() => {
    if (uploadSubCategory.value === "nsfw") {
      return myUploadedCharacters.value.filter((c) => c.category === "nsfw");
    }
    return myUploadedCharacters.value.filter((c) => c.category !== "nsfw");
  });

  async function fetchMyCharacters(): Promise<void> {
    isLoadingMyCharacters.value = true;
    try {
      const list = await characterService.getMyCharacters();
      myUploadedCharacters.value = list;
    } catch (err) {
      console.error("获取我上传的角色卡失败:", err);
    } finally {
      isLoadingMyCharacters.value = false;
    }
  }

  async function toggleCharacterStatus(
    char: CharacterDetail,
    newStatus: "published" | "draft",
  ): Promise<void> {
    try {
      const updated = await characterService.updateCharacterStatus(char.id, newStatus);
      const idx = myUploadedCharacters.value.findIndex((c) => c.id === char.id);
      if (idx !== -1) {
        myUploadedCharacters.value[idx] = updated;
      }
      showToast(
        newStatus === "published"
          ? `角色《${char.name}》已成功上架到社区`
          : `角色《${char.name}》已下架（设为草稿）`,
      );
    } catch (err) {
      console.error("更新角色发布状态失败:", err);
      showToast("更新角色状态失败，请检查网络或登录状态");
    }
  }

  async function deleteUploadedCharacter(char: CharacterDetail): Promise<void> {
    try {
      await characterService.deleteCharacter(char.id);
      myUploadedCharacters.value = myUploadedCharacters.value.filter((c) => c.id !== char.id);
      showToast(`角色《${char.name}》已成功删除`);
    } catch (err) {
      console.error("删除角色卡失败:", err);
      showToast("删除角色失败，请检查网络或登录状态");
    }
  }

  onMounted(() => {
    fetchHistory();
    fetchMyCharacters();
  });

  // 1. 人设状态机
  const personaList = ref<PersonaItem[]>([]);
  const isPersonaModalOpen = ref<boolean>(false);
  const editingPersona = ref<PersonaItem | null>(null);

  // 2. 指令状态机 (Figma 81:2925 高保真)
  const commandList = ref<CommandItem[]>([
    {
      id: "cmd-1",
      label: "这是一个指令",
      content: "这是一个指令",
      order: 1,
      createdAt: "2026/8/22",
    },
  ]);
  const isCommandModalOpen = ref<boolean>(false);
  const editingCommand = ref<CommandItem | null>(null);

  // 3. 画师串状态机 (Figma 84:6799 高保真)
  const artistList = ref<ArtistPromptItem[]>([
    {
      id: "artist-1",
      name: "二次元",
      description: "日系动漫风格，鲜艳的色彩和动态构图",
      prompt:
        "0.55::meion::,0.55::aoisakura(seak5545)::,0.75::qiandaiyiyu::,0.75::akitahika::,0.75::dishwasher1910 ::,0.75::ke-ta::,0.95::wakaba(945599620)::,0.95::omone_hokoma_agm ::,1.25::mignon::,1.25::rebun::,1.45::cohi27151463 ::,1.55::myomomoo::,-1::ai-generated, ai-assisted, ::,-1::unfinished::, chiaroscuro",
      negativePrompt: "lowres, bad anatomy, bad hands, missing fingers",
      isActive: true,
      createdAt: "2026/5/18",
    },
  ]);
  const isArtistModalOpen = ref<boolean>(false);
  const editingArtist = ref<ArtistPromptItem | null>(null);

  // 4. 总结提示词状态机 (Figma 86:8397 高保真)
  const summaryModel = ref<string>("claude-sonnet-4.5");
  const summaryPrompt = ref<string>("");

  // 5. 记忆增强模型状态机 (Figma 90:1083 高保真)
  const memoryEnhanceModel = ref<string>("system");

  // 6. Mod 模组中心状态机 (Figma 93:3270 / 106:8347 / 106:8552 / 106:8718 / 111:13235 高保真)
  const modSubCategory = ref<ModSubCategory>("square"); // 广场 / 我创作的 / 我购买的 / 合集 / Mod设置
  const modSearchQuery = ref<string>("");
  const modSort = ref<ModSortType>("hot");
  const modTag = ref<ModCategoryTag>("all");
  const modList = ref<ModItem[]>([
    {
      id: "mod-1",
      title: "强制输出4000～8000字",
      description: "强制ai输出4000～8000字，不OOC，不水文",
      author: "@李小白K",
      rating: 4.5,
      likes: 5,
      price: 5,
      isPurchased: true,
      categoryTag: "system",
    },
    {
      id: "mod-2",
      title: "超级无敌新版哈基米顶级助手",
      description: "最新版，字数增加，防神话，防绝望，抑制发情，丰富NPC情感，其他模型应该也能用",
      author: "@萌羽不萌",
      rating: 4.4,
      likes: 5,
      price: 20,
      isPurchased: true,
      categoryTag: "author",
    },
    {
      id: "mod-3",
      title: "破甲",
      description: "强破甲，小克可破。",
      author: "@为止8",
      rating: 3.5,
      likes: 6,
      price: 100,
      isPurchased: false,
      categoryTag: "regex",
    },
    {
      id: "mod-4",
      title: "小穴特点强化（32种）",
      description:
        "可以强化小穴特点，细致描写阴户外形特点，ai自动识别小穴，馒头穴, 蝴蝶穴, 一线天穴, 花瓣穴, 马蹄穴, 水滴穴, 荷包穴, 海葵穴, 白虎穴, 布条穴, 柳叶穴, 闭合穴, 鲱鱼子穴, 印笼穴, 章鱼壶穴, 梯田穴, 波浪穴, 开扇穴, 心型穴, 弯月穴, 锥型穴, 玫瑰穴, 瓜瓢穴, 展翅穴, 章鱼吸盘穴, 九曲回肠穴, 春蚕吐丝穴, 千层浪穴, 重楼穴, 龙珠穴, 螺旋绞索穴, 含羞草穴 ，总共32种。（注意mod同时开太多，可能卡顿或者混乱）",
      author: "@李小白K",
      rating: 5.0,
      likes: 2,
      price: 20,
      isPurchased: false,
      categoryTag: "system",
    },
    {
      id: "mod-5",
      title: "综合姿势特化·十项全开",
      description:
        "整合口交、骑乘、后入、乳交、足交、手冲、舔逼、前戏等姿势的细节增强，自动识别用户行为并应用对应描写模组。无需频繁切换Mod。",
      author: "@小nao",
      rating: 5.0,
      likes: 1,
      price: 2,
      isPurchased: false,
      categoryTag: "system",
    },
    {
      id: "mod-6",
      title: "性感受提升（32种）",
      description:
        "详细描述性交时的感受，配合小穴特点强化使用效果更佳。支持丰富的情感反馈与触感细节描绘。",
      author: "@李小白K",
      rating: 4.8,
      likes: 12,
      price: 40,
      isPurchased: false,
      categoryTag: "system",
    },
    {
      id: "mod-7",
      title: "破甲幼",
      description:
        "(已重新修改试试看，有问题评论告诉我) 破甲幼，破除常规限制，强化极端语义下的响应能力。",
      author: "@小可爱",
      rating: 4.2,
      likes: 8,
      price: 1,
      isPurchased: true,
      categoryTag: "regex",
    },
  ]);

  // 7. 我创作的 Mod 状态机 (Figma 106:8347 / 106:8552)
  const myCreatedModList = ref<CreatedModItem[]>([
    {
      id: "my-mod-1",
      name: "123",
      description: "123",
      status: "draft",
      entries: [],
      createdAt: "2026/8/23",
    },
  ]);
  const isModEditModalOpen = ref<boolean>(false);
  const editingCreatedMod = ref<CreatedModItem | null>(null);

  // 8. 我购买的 Mod 状态机 (Figma 106:8718 / 111:13235 高保真)
  const purchasedModList = ref<PurchasedModItem[]>([
    {
      id: "purchased-3",
      title: "色色幼女",
      description: "增加与幼女做爱时的色情度",
      isActive: true,
      createdAt: "2026/8/21",
    },
    {
      id: "purchased-1",
      title: "强力破甲词，可破幼",
      description: "短小精悍的破甲词，可以破幼",
      isActive: true,
      createdAt: "2026/8/20",
    },
    {
      id: "purchased-0",
      title: "强制输出4000～8000字",
      description: "强制ai输出4000～8000字，不OOC，不水文",
      isActive: true,
      createdAt: "2026/8/19",
    },
    {
      id: "purchased-2",
      title: "性爱过程详细",
      description: "将性交，调教等过程详细化",
      isActive: false,
      createdAt: "2026/8/20",
    },
    {
      id: "purchased-4",
      title: "防发情",
      description: "防止角色莫名其妙发情，当然了，r18场面不影响",
      isActive: false,
      createdAt: "2026/8/21",
    },
    {
      id: "purchased-5",
      title: "防止人物ooc",
      description: "人物性格大变，奴化，黑化，魔神化......让她们恢复本来的样子",
      isActive: false,
      createdAt: "2026/8/22",
    },
    {
      id: "purchased-6",
      title: "萝莉/幼女/合法萝莉特化",
      description:
        "针对萝莉体型角色（合法年龄），强化娇小身材、紧致度、反应稚嫩等特点。包含身体数据（身高、胸围、骨架）、插入时的疼痛/快感比例、声音尖细、眼泪描写等。强调保护欲与征服感并存。",
      isActive: false,
      createdAt: "2026/8/22",
    },
    {
      id: "purchased-7",
      title: "破甲幼",
      description: "（已重新修改试试看，有问题评论告诉我）破甲幼，双子星。",
      isActive: false,
      createdAt: "2026/8/23",
    },
    {
      id: "purchased-8",
      title: "让ai不能替你做决定",
      description:
        "预防ai替你推进动作，比如你输入‘你拉起她的手’。而ai输出‘你拉起她的手，并干了她’。预防这种情况",
      isActive: false,
      createdAt: "2026/8/23",
    },
    {
      id: "purchased-9",
      title: "女性人物增强活人感",
      description: "单人女性角色卡增强活人感，减少魅化，增强人物性格",
      isActive: false,
      createdAt: "2026/8/23",
    },
    {
      id: "purchased-10",
      title: "现代都市增强活人感",
      description: "适用于多人世界卡，按需开启",
      isActive: false,
      createdAt: "2026/8/23",
    },
  ]);

  // 9. Mod 合集状态机 (Figma 109:12064 / 109:11681)
  const collectionSubTab = ref<CollectionSubTab>("mine");
  const myCollectionList = ref<ModCollectionItem[]>([
    {
      id: "coll-1",
      title: "123",
      description: "123",
      modCount: 15,
      statsText:
        "15 个 Mod · 世界书 16 条 / 常量 14 条（10916 字） / 关键词触发 2 条（588 字） · 提示词 3 条 · 历史指令 2 条",
      mods: [
        { id: "mod-c1", title: "123", description: "123" },
        {
          id: "mod-c2",
          title: "强力破甲词，可破幼",
          description: "短小精悍的破甲词，可以破幼",
        },
        {
          id: "mod-c3",
          title: "超级无敌新版哈基米顶级助手",
          description:
            "最新版，字数增加，防神话，防绝望，抑制发情，丰富NPC情感，其他模型应该也能用",
        },
        {
          id: "mod-c4",
          title: "强制输出4000～8000字",
          description: "强制ai输出4000～8000字，不OOC，不水文",
        },
      ],
      createdAt: "2026/8/23",
    },
  ]);

  const publicCollectionList = ref<ModCollectionItem[]>([
    {
      id: "pub-coll-1",
      title: "沉浸式深度角色扮演通用增强套件",
      description: "整合破甲、防发情、防OOC与长文本输出控制，适用于各类世界卡与单人卡。",
      modCount: 8,
      statsText: "8 个 Mod · 世界书 12 条 · 提示词 4 条 · 正则 2 条",
      mods: [
        {
          id: "mod-p1",
          title: "强制输出4000～8000字",
          description: "强制ai输出4000～8000字，不OOC，不水文",
        },
        {
          id: "mod-p2",
          title: "防止人物ooc",
          description: "保持人物性格稳定，避免莫名失控",
        },
        {
          id: "mod-p3",
          title: "防发情",
          description: "防止角色莫名其妙发情，提升剧情质感",
        },
      ],
      author: "@官方精选",
      createdAt: "2026/8/22",
    },
  ]);

  const isCollectionModalOpen = ref<boolean>(false);
  const editingCollection = ref<ModCollectionItem | null>(null);
  const isCollectionPreviewOpen = ref<boolean>(false);
  const previewingCollection = ref<ModCollectionItem | null>(null);

  const toastMessage = ref<string | null>(null);

  function showToast(msg: string) {
    toastMessage.value = msg;
    setTimeout(() => {
      toastMessage.value = null;
    }, 2000);
  }

  // 数量统计
  const storyCount = computed(() => historyList.value.length);
  const tavernCount = computed(() => myUploadedCharacters.value.length);
  const customCount = computed(
    () => personaList.value.length + commandList.value.length + artistList.value.length,
  );
  const moduleCount = computed(
    () => modList.value.length + myCreatedModList.value.length + myCollectionList.value.length,
  );

  // 10. Mod 设置激活优先级列表 (Figma 111:13235 高保真)
  const activeModsList = computed(() => {
    return purchasedModList.value.filter((m) => m.isActive);
  });

  function moveActiveMod(index: number, direction: "up" | "down"): void {
    const activeIndices: number[] = [];
    purchasedModList.value.forEach((m, idx) => {
      if (m.isActive) activeIndices.push(idx);
    });

    if (direction === "up" && index > 0) {
      const currentIdx = activeIndices[index];
      const targetIdx = activeIndices[index - 1];
      const temp = purchasedModList.value[currentIdx];
      purchasedModList.value[currentIdx] = purchasedModList.value[targetIdx];
      purchasedModList.value[targetIdx] = temp;
      showToast("优先级已调整");
    } else if (direction === "down" && index < activeIndices.length - 1) {
      const currentIdx = activeIndices[index];
      const targetIdx = activeIndices[index + 1];
      const temp = purchasedModList.value[currentIdx];
      purchasedModList.value[currentIdx] = purchasedModList.value[targetIdx];
      purchasedModList.value[targetIdx] = temp;
      showToast("优先级已调整");
    }
  }

  function deactivateMod(id: string): void {
    const mod = purchasedModList.value.find((m) => m.id === id);
    if (mod) {
      mod.isActive = false;
      showToast(`已停用 Mod《${mod.title}》`);
    }
  }

  // 过滤与排序个人对话历史列表 (置顶优先)
  const filteredList = computed(() => {
    const list = historyList.value.filter((h) => h.category === currentCategory.value);
    return [...list].sort((a, b) => {
      if (a.isPinned && !b.isPinned) return -1;
      if (!a.isPinned && b.isPinned) return 1;
      return 0;
    });
  });

  // 过滤 Mod 广场列表
  const filteredModList = computed(() => {
    let list = [...modList.value];

    if (modSearchQuery.value.trim()) {
      const q = modSearchQuery.value.trim().toLowerCase();
      list = list.filter(
        (m) =>
          m.title.toLowerCase().includes(q) ||
          m.description.toLowerCase().includes(q) ||
          m.author.toLowerCase().includes(q),
      );
    }

    if (modTag.value !== "all") {
      list = list.filter((m) => m.categoryTag === modTag.value);
    }

    if (modSort.value === "rating") {
      list.sort((a, b) => b.rating - a.rating);
    } else if (modSort.value === "likes") {
      list.sort((a, b) => b.likes - a.likes);
    } else if (modSort.value === "latest") {
      list.reverse();
    }

    return list;
  });

  function setCategory(cat: UserHistoryCategory): void {
    currentCategory.value = cat;
    selectedIds.value.clear();
  }

  function setUploadSubCategory(cat: UploadSubCategory): void {
    uploadSubCategory.value = cat;
  }

  function setCustomSubCategory(cat: CustomSubCategory): void {
    customSubCategory.value = cat;
  }

  function setModSubCategory(cat: ModSubCategory): void {
    modSubCategory.value = cat;
  }

  function setCollectionSubTab(tab: CollectionSubTab): void {
    collectionSubTab.value = tab;
  }

  function setModSort(sort: ModSortType): void {
    modSort.value = sort;
  }

  function setModTag(tag: ModCategoryTag): void {
    modTag.value = modTag.value === tag ? "all" : tag;
  }

  function buyMod(id: string): void {
    const mod = modList.value.find((m) => m.id === id);
    if (mod) {
      if (mod.isPurchased) {
        showToast("您已购买过此 Mod");
        return;
      }
      mod.isPurchased = true;
      purchasedModList.value.unshift({
        id: `purchased-${Date.now()}`,
        title: mod.title,
        description: mod.description,
        isActive: false,
        createdAt: new Date().toLocaleDateString(),
      });
      showToast(`已成功购买 Mod《${mod.title}》！`);
    }
  }

  // --- 我购买的 Mod 业务方法 (Figma 106:8718) ---
  function togglePurchasedModActive(id: string): void {
    const mod = purchasedModList.value.find((m) => m.id === id);
    if (mod) {
      mod.isActive = !mod.isActive;
      showToast(mod.isActive ? `已激活 Mod《${mod.title}》` : `已关闭 Mod《${mod.title}》`);
    }
  }

  function deletePurchasedMod(id: string): void {
    const idx = purchasedModList.value.findIndex((m) => m.id === id);
    if (idx !== -1) {
      const deleted = purchasedModList.value.splice(idx, 1)[0];
      showToast(`已从已购买列表中移除《${deleted.title}》`);
    }
  }

  // --- 我创作的 Mod 业务方法 (Figma 106:8347 / 106:8552) ---
  function openCreateModModal(): void {
    editingCreatedMod.value = null;
    isModEditModalOpen.value = true;
  }

  function openEditCreatedModModal(mod: CreatedModItem): void {
    editingCreatedMod.value = mod;
    isModEditModalOpen.value = true;
  }

  function saveCreatedMod(payload: {
    id?: string;
    name: string;
    description: string;
    entries: CreatedModEntry[];
  }): void {
    if (!payload.name.trim()) {
      showToast("请输入 Mod 名称");
      return;
    }

    if (payload.id) {
      const idx = myCreatedModList.value.findIndex((m) => m.id === payload.id);
      if (idx !== -1) {
        myCreatedModList.value[idx] = {
          ...myCreatedModList.value[idx],
          name: payload.name.trim(),
          description: payload.description.trim(),
          entries: payload.entries,
          updatedAt: new Date().toLocaleDateString(),
        };
        showToast("Mod 已保存");
      }
    } else {
      const newMod: CreatedModItem = {
        id: `my-mod-${Date.now()}`,
        name: payload.name.trim(),
        description: payload.description.trim(),
        status: "draft",
        entries: payload.entries,
        createdAt: new Date().toLocaleDateString(),
      };
      myCreatedModList.value.unshift(newMod);
      showToast("Mod 草稿创建成功");
    }

    isModEditModalOpen.value = false;
    editingCreatedMod.value = null;
  }

  function publishCreatedMod(id: string): void {
    const mod = myCreatedModList.value.find((m) => m.id === id);
    if (mod) {
      mod.status = mod.status === "published" ? "draft" : "published";
      showToast(
        mod.status === "published"
          ? `Mod《${mod.name}》已成功发布到广场！`
          : `Mod《${mod.name}》已转为私密草稿`,
      );
    }
  }

  function deleteCreatedMod(id: string): void {
    const idx = myCreatedModList.value.findIndex((m) => m.id === id);
    if (idx !== -1) {
      const deleted = myCreatedModList.value.splice(idx, 1)[0];
      showToast(`已删除 Mod《${deleted.name}》`);
    }
  }

  // --- Mod 合集业务方法 (Figma 109:12064 / 109:11681) ---
  function openCreateCollectionModal(): void {
    editingCollection.value = null;
    isCollectionModalOpen.value = true;
  }

  function openEditCollectionModal(coll: ModCollectionItem): void {
    editingCollection.value = coll;
    isCollectionModalOpen.value = true;
  }

  function openPreviewCollectionModal(coll: ModCollectionItem): void {
    previewingCollection.value = coll;
    isCollectionPreviewOpen.value = true;
  }

  function saveCollection(payload: {
    id?: string;
    title: string;
    description: string;
    mods: CollectionModEntry[];
  }): void {
    if (!payload.title.trim()) {
      showToast("请输入合集名称");
      return;
    }

    if (payload.id) {
      const idx = myCollectionList.value.findIndex((c) => c.id === payload.id);
      if (idx !== -1) {
        myCollectionList.value[idx] = {
          ...myCollectionList.value[idx],
          title: payload.title.trim(),
          description: payload.description.trim(),
          mods: payload.mods,
          modCount: payload.mods.length,
          statsText: `${payload.mods.length} 个 Mod · 世界书 ${payload.mods.length * 4} 条 · 提示词 3 条`,
          updatedAt: new Date().toLocaleDateString(),
        };
        showToast("合集已更新");
      }
    } else {
      const newColl: ModCollectionItem = {
        id: `coll-${Date.now()}`,
        title: payload.title.trim(),
        description: payload.description.trim(),
        mods: payload.mods,
        modCount: payload.mods.length,
        statsText: `${payload.mods.length} 个 Mod · 世界书 ${payload.mods.length * 4} 条 · 提示词 3 条`,
        createdAt: new Date().toLocaleDateString(),
      };
      myCollectionList.value.unshift(newColl);
      showToast("合集创建成功");
    }

    isCollectionModalOpen.value = false;
    editingCollection.value = null;
  }

  function deleteCollection(id: string): void {
    const idx = myCollectionList.value.findIndex((c) => c.id === id);
    if (idx !== -1) {
      const deleted = myCollectionList.value.splice(idx, 1)[0];
      showToast(`已删除合集《${deleted.title}》`);
    }
  }

  function shareCollection(id: string): void {
    const coll = myCollectionList.value.find((c) => c.id === id);
    if (coll) {
      navigator.clipboard?.writeText?.(`https://naro.ai/collection/${coll.id}`);
      showToast(`已生成合集《${coll.title}》专属分享链接并复制到剪贴板！`);
    }
  }

  function toggleViewMode(): void {
    viewMode.value = viewMode.value === "grid" ? "list" : "grid";
  }

  function toggleBatchMode(): void {
    isBatchMode.value = !isBatchMode.value;
    selectedIds.value.clear();
  }

  function toggleSelectItem(id: string): void {
    if (selectedIds.value.has(id)) {
      selectedIds.value.delete(id);
    } else {
      selectedIds.value.add(id);
    }
  }

  async function togglePin(id: string): Promise<void> {
    try {
      const isPinned = await chatService.togglePinSession(id);
      const item = historyList.value.find((h) => h.id === id);
      if (item) {
        item.isPinned = isPinned;
        // 重新排序：置顶在前
        historyList.value.sort((a, b) => (b.isPinned ? 1 : 0) - (a.isPinned ? 1 : 0));
        showToast(isPinned ? "已置顶该角色" : "已取消置顶");
      }
    } catch (err) {
      console.error("置顶失败:", err);
      showToast("置顶操作失败");
    }
  }

  async function clearChatHistory(id: string): Promise<void> {
    try {
      await chatService.clearSessionMessages(id);
      const item = historyList.value.find((h) => h.id === id);
      if (item) {
        item.messageCount = 1;
        showToast(`已清空《${item.title}》对话历史并重置开场白`);
      }
    } catch (err) {
      console.error("清空历史失败:", err);
      showToast("清空历史失败");
    }
  }

  async function deleteHistory(id: string): Promise<void> {
    try {
      await chatService.deleteSession(id);
      const idx = historyList.value.findIndex((h) => h.id === id);
      if (idx !== -1) {
        const deleted = historyList.value.splice(idx, 1)[0];
        showToast(`已删除《${deleted.title}》历史记录`);
      }
    } catch (err) {
      console.error("删除历史失败:", err);
      showToast("删除历史失败");
    }
  }

  async function batchDeleteSelected(): Promise<void> {
    if (selectedIds.value.size === 0) {
      showToast("请先选择要删除的历史记录");
      return;
    }
    const ids = Array.from(selectedIds.value);
    try {
      await Promise.all(ids.map((id) => chatService.deleteSession(id)));
      historyList.value = historyList.value.filter((h) => !selectedIds.value.has(h.id));
      showToast(`已成功删除 ${ids.length} 项历史记录`);
      selectedIds.value.clear();
      isBatchMode.value = false;
    } catch (err) {
      console.error("批量删除失败:", err);
      showToast("部分历史删除失败");
    }
  }

  function updateCharacterCard(item: UserHistoryItem): void {
    showToast(`已同步《${item.title}》最新设定`);
  }

  function openRemarkModal(item: UserHistoryItem): void {
    editingRemarkItem.value = item;
    isRemarkModalOpen.value = true;
  }

  async function saveRemark(remark: string): Promise<void> {
    if (!editingRemarkItem.value) return;
    try {
      const saved = await chatService.updateSessionRemark(
        editingRemarkItem.value.id,
        remark.trim(),
      );
      const target = historyList.value.find((h) => h.id === editingRemarkItem.value?.id);
      if (target) {
        target.remark = saved;
      }
      showToast("备注保存成功");
    } catch (err) {
      console.error("保存备注失败:", err);
      showToast("保存备注失败");
    } finally {
      isRemarkModalOpen.value = false;
      editingRemarkItem.value = null;
    }
  }

  function triggerCloudBackup(): void {
    showToast("云端备份同步完成");
  }

  function claimRewards(): void {
    showToast("已成功领取今日社区创作者分成与激励金！");
  }

  function uploadToCommunity(): void {
    showToast("请选择您要发布到社区的原创或修改角色卡");
  }

  // --- 人设管理业务逻辑 ---
  function openCreatePersonaModal(): void {
    if (personaList.value.length >= 10) {
      showToast("人设数量已达上限 (10/10)");
      return;
    }
    editingPersona.value = null;
    isPersonaModalOpen.value = true;
  }

  function openEditPersonaModal(persona: PersonaItem): void {
    editingPersona.value = persona;
    isPersonaModalOpen.value = true;
  }

  function savePersona(payload: {
    id?: string;
    name: string;
    displayName?: string;
    content: string;
    isDefault: boolean;
  }): void {
    if (!payload.name.trim()) {
      showToast("请输入人设名称");
      return;
    }
    if (!payload.content.trim()) {
      showToast("请输入人设内容");
      return;
    }

    if (payload.isDefault) {
      for (const p of personaList.value) {
        p.isDefault = false;
      }
    }

    if (payload.id) {
      const idx = personaList.value.findIndex((p) => p.id === payload.id);
      if (idx !== -1) {
        personaList.value[idx] = {
          ...personaList.value[idx],
          name: payload.name.trim(),
          displayName: payload.displayName?.trim() || undefined,
          content: payload.content.trim(),
          isDefault: payload.isDefault,
          updatedAt: new Date().toLocaleString(),
        };
        showToast("人设修改成功");
      }
    } else {
      const newPersona: PersonaItem = {
        id: `persona-${Date.now()}`,
        name: payload.name.trim(),
        displayName: payload.displayName?.trim() || undefined,
        content: payload.content.trim(),
        isDefault: Boolean(payload.isDefault || personaList.value.length === 0),
        createdAt: new Date().toLocaleString(),
      };
      personaList.value.push(newPersona);
      showToast("人设创建成功");
    }

    isPersonaModalOpen.value = false;
    editingPersona.value = null;
  }

  function deletePersona(id: string): void {
    const idx = personaList.value.findIndex((p) => p.id === id);
    if (idx !== -1) {
      personaList.value.splice(idx, 1);
      showToast("人设已删除");
    }
  }

  function setDefaultPersona(id: string): void {
    for (const p of personaList.value) {
      p.isDefault = p.id === id;
    }
    showToast("已设为默认人设");
  }

  // --- 指令管理业务逻辑 ---
  function openCreateCommandModal(): void {
    editingCommand.value = null;
    isCommandModalOpen.value = true;
  }

  function openEditCommandModal(cmd: CommandItem): void {
    editingCommand.value = cmd;
    isCommandModalOpen.value = true;
  }

  function saveCommand(payload: {
    id?: string;
    label: string;
    content: string;
  }): void {
    if (!payload.label.trim()) {
      showToast("请输入按钮标签");
      return;
    }
    if (!payload.content.trim()) {
      showToast("请输入指令内容");
      return;
    }

    if (payload.id) {
      const idx = commandList.value.findIndex((c) => c.id === payload.id);
      if (idx !== -1) {
        commandList.value[idx] = {
          ...commandList.value[idx],
          label: payload.label.trim(),
          content: payload.content.trim(),
          updatedAt: new Date().toLocaleString(),
        };
        showToast("指令修改成功");
      }
    } else {
      const dateStr = new Date();
      const createdAt = `${dateStr.getFullYear()}/${dateStr.getMonth() + 1}/${dateStr.getDate()}`;
      const newCmd: CommandItem = {
        id: `cmd-${Date.now()}`,
        label: payload.label.trim(),
        content: payload.content.trim(),
        order: commandList.value.length + 1,
        createdAt,
      };
      commandList.value.push(newCmd);
      showToast("指令新建成功");
    }

    isCommandModalOpen.value = false;
    editingCommand.value = null;
  }

  function deleteCommand(id: string): void {
    const idx = commandList.value.findIndex((c) => c.id === id);
    if (idx !== -1) {
      commandList.value.splice(idx, 1);
      showToast("指令已删除");
    }
  }

  function moveCommand(index: number, direction: "up" | "down"): void {
    if (direction === "up" && index > 0) {
      const temp = commandList.value[index];
      commandList.value[index] = commandList.value[index - 1];
      commandList.value[index - 1] = temp;
    } else if (direction === "down" && index < commandList.value.length - 1) {
      const temp = commandList.value[index];
      commandList.value[index] = commandList.value[index + 1];
      commandList.value[index + 1] = temp;
    }
  }

  function saveCommandOrder(): void {
    commandList.value.forEach((cmd, idx) => {
      cmd.order = idx + 1;
    });
    showToast("排序已保存");
  }

  // --- 画师串管理业务逻辑 (Figma 84:6799 / 84:7007) ---
  function openCreateArtistModal(): void {
    if (artistList.value.length >= 50) {
      showToast("画师串数量已达上限 (50/50)");
      return;
    }
    editingArtist.value = null;
    isArtistModalOpen.value = true;
  }

  function openEditArtistModal(artist: ArtistPromptItem): void {
    editingArtist.value = artist;
    isArtistModalOpen.value = true;
  }

  function saveArtist(payload: {
    id?: string;
    name: string;
    prompt: string;
    description?: string;
    negativePrompt?: string;
    isActive: boolean;
  }): void {
    if (!payload.name.trim()) {
      showToast("请输入画师串名称");
      return;
    }
    if (!payload.prompt.trim()) {
      showToast("请输入提示词文本");
      return;
    }

    if (payload.isActive) {
      for (const a of artistList.value) {
        a.isActive = false;
      }
    }

    if (payload.id) {
      const idx = artistList.value.findIndex((a) => a.id === payload.id);
      if (idx !== -1) {
        artistList.value[idx] = {
          ...artistList.value[idx],
          name: payload.name.trim(),
          prompt: payload.prompt.trim(),
          description: payload.description?.trim() || undefined,
          negativePrompt: payload.negativePrompt?.trim() || undefined,
          isActive: payload.isActive,
          updatedAt: new Date().toLocaleString(),
        };
        showToast("画师串修改成功");
      }
    } else {
      const dateStr = new Date();
      const createdAt = `${dateStr.getFullYear()}/${dateStr.getMonth() + 1}/${dateStr.getDate()}`;
      const newArtist: ArtistPromptItem = {
        id: `artist-${Date.now()}`,
        name: payload.name.trim(),
        prompt: payload.prompt.trim(),
        description: payload.description?.trim() || undefined,
        negativePrompt: payload.negativePrompt?.trim() || undefined,
        isActive: Boolean(payload.isActive || artistList.value.length === 0),
        createdAt,
      };
      artistList.value.push(newArtist);
      showToast("画师串创建成功");
    }

    isArtistModalOpen.value = false;
    editingArtist.value = null;
  }

  function deleteArtist(id: string): void {
    const idx = artistList.value.findIndex((a) => a.id === id);
    if (idx !== -1) {
      artistList.value.splice(idx, 1);
      showToast("画师串已删除");
    }
  }

  function setActiveArtist(id: string): void {
    for (const a of artistList.value) {
      a.isActive = a.id === id;
    }
    showToast("已激活该画师串");
  }

  // --- 总结提示词业务逻辑 (Figma 86:8397) ---
  function saveSummarySettings(payload: {
    model: string;
    prompt: string;
  }): void {
    summaryModel.value = payload.model;
    summaryPrompt.value = payload.prompt;
    showToast("总结提示词设置已保存");
  }

  function resetSummarySettings(): void {
    summaryModel.value = "claude-sonnet-4.5";
    summaryPrompt.value = "";
    showToast("已恢复系统默认总结提示词");
  }

  // --- 记忆增强模型业务逻辑 (Figma 90:1083) ---
  function saveMemoryModel(model: string): void {
    memoryEnhanceModel.value = model;
    showToast("记忆增强模型设置已保存");
  }

  function resetMemoryModel(): void {
    memoryEnhanceModel.value = "system";
    showToast("已恢复系统默认记忆增强模型");
  }

  return {
    historyList: filteredList,
    currentCategory,
    uploadSubCategory,
    customSubCategory,
    modSubCategory,
    collectionSubTab,
    modSearchQuery,
    modSort,
    modTag,
    modList: filteredModList,
    rawModList: modList,
    myCreatedModList,
    purchasedModList,
    activeModsList,
    myCollectionList,
    publicCollectionList,
    isModEditModalOpen,
    editingCreatedMod,
    isCollectionModalOpen,
    editingCollection,
    isCollectionPreviewOpen,
    previewingCollection,
    viewMode,
    storyCount,
    tavernCount,
    customCount,
    moduleCount,
    isBatchMode,
    selectedIds,
    editingRemarkItem,
    isRemarkModalOpen,
    personaList,
    isPersonaModalOpen,
    editingPersona,
    commandList,
    isCommandModalOpen,
    editingCommand,
    artistList,
    isArtistModalOpen,
    editingArtist,
    summaryModel,
    summaryPrompt,
    memoryEnhanceModel,
    toastMessage,
    setCategory,
    setUploadSubCategory,
    setCustomSubCategory,
    setModSubCategory,
    setCollectionSubTab,
    setModSort,
    setModTag,
    buyMod,
    togglePurchasedModActive,
    deletePurchasedMod,
    moveActiveMod,
    deactivateMod,
    openCreateModModal,
    openEditCreatedModModal,
    saveCreatedMod,
    publishCreatedMod,
    deleteCreatedMod,
    openCreateCollectionModal,
    openEditCollectionModal,
    openPreviewCollectionModal,
    saveCollection,
    deleteCollection,
    shareCollection,
    toggleViewMode,
    toggleBatchMode,
    toggleSelectItem,
    togglePin,
    clearChatHistory,
    deleteHistory,
    batchDeleteSelected,
    updateCharacterCard,
    openRemarkModal,
    saveRemark,
    triggerCloudBackup,
    claimRewards,
    uploadToCommunity,
    openCreatePersonaModal,
    openEditPersonaModal,
    savePersona,
    deletePersona,
    setDefaultPersona,
    openCreateCommandModal,
    openEditCommandModal,
    saveCommand,
    deleteCommand,
    moveCommand,
    saveCommandOrder,
    openCreateArtistModal,
    openEditArtistModal,
    saveArtist,
    deleteArtist,
    setActiveArtist,
    saveSummarySettings,
    resetSummarySettings,
    saveMemoryModel,
    resetMemoryModel,
    myUploadedCharacters,
    filteredMyUploadedCharacters,
    isLoadingMyCharacters,
    fetchMyCharacters,
    toggleCharacterStatus,
    deleteUploadedCharacter,
  };
}
