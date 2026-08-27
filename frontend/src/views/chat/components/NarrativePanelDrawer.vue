<script setup lang="ts">
/**
 * AI 聊天界面 - 叙梦面板/聊天信息面板抽屉 (1:1 Figma 原型高保真)
 *
 * 严格按照 Figma 原型 (83:6511 / 85:7316 / 88:2 / 91:1327 / 92:2745 / 94:4096) 构建：
 * 包含 6 大 Tab 选项卡（状态/背包/技能/社交/任务/历史）：
 * 1. 👤 状态: 时空背景 + 玩家状态 (5项) + 时空表格 + 玩家状态表
 * 2. 🎒 背包: 消耗品/道具 + 重要物品（带红条）+ 消耗品/道具表格 + 重要物品表格
 * 3. ⚔️ 技能: 未装备技能（极限控精/金色进度条）+ 所有技能 + 技能表 (11列)
 * 4. 👥 社交: 社交关系 2x2 四宫格总览 + 4 大 NPC 角色好感度卡片 + 角色特征表格 + 角色与<user>社交表格
 * 5. 📜 任务: 进行中的任务（普通/进行中三联栏）+ 任务/命令/约定表格
 * 6. 📖 历史: 33 个总事件、5 天跨度、9 种角色筛选药丸、按日期分组的真实时间轴事件流 (周一/周日/周六/周五) + 历史事件表格
 *
 * @packageDocumentation
 */

import {
  Backpack,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Clock,
  Database,
  Edit2,
  Plus,
  Scroll,
  Sparkles,
  Swords,
  Trash2,
  User,
  Users,
  X,
} from "lucide-vue-next";
import { computed, ref } from "vue";

const props = defineProps<{
  open: boolean;
}>();

const emit = defineEmits<(e: "update:open", val: boolean) => void>();

// 记忆增强状态
const isMemoryEnhanced = ref(true);

// 6 大分类选项卡 (1: 状态, 2: 背包, 3: 技能, 4: 社交, 5: 任务, 6: 历史)
const tabs = [
  { id: 1, name: "状态", icon: User },
  { id: 2, name: "背包", icon: Backpack },
  { id: 3, name: "技能", icon: Swords },
  { id: 4, name: "社交", icon: Users },
  { id: 5, name: "任务", icon: Scroll },
  { id: 6, name: "历史", icon: BookOpen },
];
const activeTab = ref(6); // 默认打开历史 Tab 进行验证

// 是否展开原始表格数据
const isRawTablesExpanded = ref(true);

// 玩家状态 Mock 数据 (Tab 1)
const playerStates = ref([
  {
    id: 1,
    type: "家境/环境",
    name: "家中名声",
    currentVal: 25,
    maxVal: "100",
    desc: "小圈子暗传 · 丽丽和萱萱在姐妹圈里将你作为‘需要训练的秒射处男’进行八卦和传播",
  },
  {
    id: 2,
    type: "家境/环境",
    name: "家中凌乱度",
    currentVal: 65,
    maxVal: "100",
    desc: "一片狼藉 · 丽丽和萱萱在沙发上对你进行粗暴训练，汗水、前列腺液洇湿了沙发和衣物，茶几上的外卖红油进一步弄脏了靠垫",
  },
  {
    id: 3,
    type: "社交计数",
    name: "丽丽到来次数",
    currentVal: 3,
    maxVal: "-",
    desc: "丽丽首次拜访",
  },
  {
    id: 4,
    type: "社交计数",
    name: "萱萱到来次数",
    currentVal: 2,
    maxVal: "-",
    desc: "萱萱首次拜访",
  },
  {
    id: 5,
    type: "社交计数",
    name: "黄媛媛到来次数",
    currentVal: 1,
    maxVal: "-",
    desc: "黄媛媛首次拜访",
  },
]);

// 背包 Mock 数据 (Tab 2)
const consumables = ref([
  {
    id: 1,
    name: "精酿啤酒",
    count: -2,
    type: "饮品",
    effect: "消暑、微醺",
    source: "冰箱库存",
    desc: "被丽丽和萱萱拿去饮用",
  },
]);

const importantItems = ref([
  {
    id: 1,
    owner: "黄媛媛",
    name: "粉色苹果手机",
    desc: "最新款粉色苹果手机，最大内存，套有手机壳并贴膜",
    importance: "徐暮云赠送，用于随时与母亲联系报平安，也是媛媛极其珍视的物品",
  },
]);

// 技能 Mock 数据 (Tab 3)
const skills = ref([
  {
    id: 1,
    name: "极限控精",
    type: "被动/房中术",
    level: "LV.1",
    proficiency: "15%",
    proficiencyCurrent: 15,
    proficiencyMax: 100,
    cost: "体力",
    cooldown: "无",
    effect:
      "在临近射精边缘时，通过深呼吸、绷紧大腿及转移注意力（如想二舅）来强行憋回，延长战斗时间",
    source: "丽丽与萱萱的粗暴打骂训练",
    status: "已掌握",
    isEquipped: false,
  },
]);

// 社交 Mock 数据 (Tab 4)
const socialCharacters = ref([
  {
    id: 1,
    name: "丽丽",
    relationTag: "友好",
    tagColor: "bg-[#EAB308]",
    favorability: 60,
    favorBarColor: "bg-[#EAB308]",
    relation: "暧昧微信好友",
    location: "客厅L型沙发",
    attitude: "戏谑、背德挑逗、关切",
    bodyFeature:
      "20岁，粉发干枯，眼线粗黑，死亡芭比粉唇，右肩有发绿玫瑰纹身，胸D罩杯，脚后跟有水泡",
    personality: "大大咧咧，混不吝，嘴硬，带点无赖",
    job: "无固定职业（KTV/夜店/直播三头跑）",
    hobby: "抽电子烟、唱歌",
    favorite: "麻辣烫、舒服的沙发、精酿啤酒",
    residence: "未知（本该去14楼，走错到15楼）",
    otherInfo:
      "自封大姐头，男友阿龙；家庭破碎，母亲改嫁赌鬼，15岁出来打拼做过学徒/前台，常被要钱，内心因家庭深感自卑",
  },
  {
    id: 2,
    name: "萱萱",
    relationTag: "友好",
    tagColor: "bg-[#EAB308]",
    favorability: 62,
    favorBarColor: "bg-[#EAB308]",
    relation: "病态暧昧好友",
    location: "客厅L型沙发",
    attitude: "病态占有、背德挑逗、恶劣戏谑",
    bodyFeature:
      "18岁，黑低双马尾，齐刘海，灰粉色美瞳，重卧蚕，颈戴黑色皮质铃铛颈圈，身穿灰色oversize老爹衫",
    personality: "病娇，伪萝莉，敏锐，占有欲强，有窥探欲",
    job: "无业（偶尔做网店模特）",
    hobby: "未知",
    favorite: "粉红色网红气泡水、水果盒",
    residence: "未知",
    otherInfo:
      "丽丽的发小，嫌弃男友；出身于高压控制欲极强的教师/公务员家庭，17岁离家出走，具有病态的占有欲和反叛倾向",
  },
  {
    id: 3,
    name: "黄媛媛",
    relationTag: "挚友",
    tagColor: "bg-[#22C55E]",
    favorability: 90,
    favorBarColor: "bg-[#22C55E]",
    relation: "寄宿依赖",
    location: "<user>家次卧",
    attitude: "傲娇、依恋、极度依赖",
    bodyFeature: "身高152cm，极细腰，胸C（童颜巨乳），黑色齐耳短发",
    personality: "满口脏话，外表可爱但内心叛逆，警惕性高",
    job: "九中初二三班学生",
    hobby: "吃水果",
    favorite: "粉色苹果手机、红油火锅",
    residence: "<user>家次卧",
    otherInfo: "16岁，父母离异；已被<user>送入9中初二三班复学；拥有一部粉色苹果手机",
  },
  {
    id: 4,
    name: "黄媛媛母亲",
    relationTag: "亲密",
    tagColor: "bg-[#22C55E]",
    favorability: 80,
    favorBarColor: "bg-[#22C55E]",
    relation: "暧昧微信好友",
    location: "与刘姓男友同居处",
    attitude: "依恋、挑逗、感激",
    bodyFeature:
      "34岁左右，深栗色大波浪，浓妆，身穿酒红色紧身针织连衣裙、黑色细高跟，身材丰满有性张力",
    personality: "软弱、市井、对女儿有病态的关切与愧疚",
    job: "未知",
    hobby: "未知",
    favorite: "未知",
    residence: "与刘姓男友同居处",
    otherInfo:
      "真名陈美兰；性格软弱，默认了同居男友对女儿的骚扰，但在关键时刻为了女儿安全同意其寄宿在<user>处",
  },
]);

// 任务 Mock 数据 (Tab 5)
const ongoingTasks = ref([
  {
    id: 1,
    role: "<user>",
    task: "把甄芬变成自己老婆",
    typeTag: "普通",
    statusTag: "进行中",
    location: "苍星中学",
    duration: "长期",
  },
]);

// 历史 Tab 角色筛选选项 (9 项)
const characterFilters = [
  { id: "all", name: "全部", count: 33 },
  { id: "lili", name: "丽丽", count: 1 },
  { id: "lili_xuan", name: "丽丽、萱萱", count: 13 },
  { id: "lili_huang", name: "丽丽、黄媛媛", count: 2 },
  { id: "user_huang_lili", name: "<user>、黄媛媛、丽丽", count: 3 },
  { id: "user_huang", name: "<user>、黄媛媛", count: 6 },
  {
    id: "user_huang_mother",
    name: "<user>、黄媛媛、黄媛媛母亲",
    count: 4,
  },
  { id: "huang_mother", name: "黄媛媛母亲", count: 3 },
  { id: "user_mother", name: "<user>、黄媛媛母亲", count: 1 },
];
const activeFilter = ref("all");

// 历史剧情事件时间轴按日期分组 Mock 数据 (Tab 6 - 严格 1:1 Figma 94:4096)
const historyDateGroups = ref([
  {
    id: "d1",
    dateText: "2026-07-06（周一）",
    eventCount: "7 个事件",
    events: [
      {
        id: 101,
        characters: "丽丽、萱萱",
        location: "客厅L型沙发",
        mood: "背德、痛苦、极度亢奋",
        desc: "两女压制了<user>的反抗，解释因各自有男友不能真做，且要求<user>必须为黄媛媛保留第一次；随后在沙发上用手脚进行粗暴套弄，并在其临近射精时强行憋回，对其展开耐力训练。",
      },
      {
        id: 102,
        characters: "丽丽、萱萱",
        location: "客厅L型沙发",
        mood: "羞愤、亢奋、荒诞",
        desc: "【补记】两女为了‘感谢’<user>，主动提出帮其训练忍耐力，让其坐在沙发上用手脚进行粗暴套弄，并在射精边缘强行憋回，开启极限控精训练。",
      },
      {
        id: 103,
        characters: "丽丽、萱萱",
        location: "客厅L型沙发",
        mood: "背德、亢奋、荒诞",
        desc: "三人转移到沙发，两女一左一右躺靠在<user>身上，一边粗俗聊起各自与男友的性生活，一边动手将<user>撩拨至生理极限并放肆嘲弄其处男身份。",
      },
      {
        id: 104,
        characters: "丽丽、萱萱",
        location: "玄关/客厅/厨房吧台",
        mood: "八卦、戏谑、挑逗",
        desc: "下午两点半，丽丽带着萱萱再次到访，发现家里变干净后八卦询问，得知黄媛媛已上学后十分震惊，随后在吧台喝精酿啤酒并对<user>进行言语挑逗。",
      },
      {
        id: 105,
        characters: "黄媛媛母亲",
        location: "客厅/次卧",
        mood: "暧昧、挑逗、克制",
        desc: "上午特意来到公寓帮<user>彻底打扫了房间，期间两人在沙发上有暧昧的言语和肢体互动，陈美兰挑逗<user>并表达了感激与依赖。",
      },
      {
        id: 106,
        characters: "<user>、黄媛媛、黄媛媛母亲",
        location: "主卧/次卧/九中/玄关",
        mood: "温馨、调情、局促、暧昧",
        desc: "清晨<user>抱赖床的黄媛媛起床并照顾洗漱穿衣，穿鞋时被媛媛用脚勾弄挑逗至勃起；随后<user>送其至九中入学，返回后在玄关遇到前来打扫的陈美兰。",
      },
    ],
  },
  {
    id: "d2",
    dateText: "2026-07-05（周日）",
    eventCount: "6 个事件",
    events: [
      {
        id: 201,
        characters: "<user>、黄媛媛母亲",
        location: "主卧大床",
        mood: "亢奋、背德",
        desc: "徐暮云将睡着的黄媛媛抱回次卧，随后在主卧与黄媛媛母亲微信聊骚，被其露骨言语和照片撩拨至生理勃起，两人在暧昧言语中拉扯试探。",
      },
      {
        id: 202,
        characters: "<user>、黄媛媛",
        location: "客厅L型沙发前",
        mood: "温馨、依赖、羞涩",
        desc: "黄媛媛嘲讽<user>是萝莉控惹其羞恼，随后却主动拥抱并靠在<user>怀中，流露对明天开学的紧张并表达了深切依赖。",
      },
      {
        id: 203,
        characters: "<user>、黄媛媛",
        location: "客厅L型沙发",
        mood: "温馨、戏谑、羞涩",
        desc: "徐暮云接黄媛媛放学回家，黄媛媛兴奋分享校园生活，随后将脚搭在徐暮云大腿上让其按摩，并用脚隔着裤子套弄挑逗。",
      },
      {
        id: 204,
        characters: "<user>、黄媛媛、黄媛媛母亲",
        location: "客厅L型沙发",
        mood: "吃惊、局促、试探",
        desc: "徐暮云带黄媛媛去9中报道入学，媛媛留校熟悉环境；随后媛媛母亲来到徐暮云家拜访，对高档公寓感到吃惊并对徐暮云的为人进行试探。",
      },
    ],
  },
  {
    id: "d3",
    dateText: "2026-07-04（周六）",
    eventCount: "12 个事件",
    events: [
      {
        id: 301,
        characters: "黄媛媛母亲",
        location: "公寓主卧/微信",
        mood: "露骨、讨好、背德",
        desc: "深夜与<user>微信长聊，话题逐渐变质，发送露骨自拍照并提出以自身肉体为筹码换取<user>不动女儿，在道德边缘疯狂试探。",
      },
      {
        id: 302,
        characters: "<user>、黄媛媛、黄媛媛母亲",
        location: "公寓主卧/次卧",
        mood: "温馨、唏嘘、责任感",
        desc: "回到公寓后，黄媛媛洗澡换上可爱猫耳睡衣并入住次卧；徐暮云深夜与媛媛母亲微信长聊，得知其前夫去世、依附同居男友的凄凉经历，心生同情与保护欲。",
      },
      {
        id: 303,
        characters: "<user>、黄媛媛",
        location: "万象城商场",
        mood: "别扭、极度感激、温馨",
        desc: "徐暮云带黄媛媛在万象城购买了最新款粉色苹果手机，并带她吃了她许久未吃的红油火锅，媛媛嘴硬但内心极度感激。",
      },
      {
        id: 304,
        characters: "<user>、黄媛媛、丽丽",
        location: "咖啡馆",
        mood: "悲伤、对立、释怀",
        desc: "三人与黄媛媛母亲在咖啡馆谈判，母亲起初因警惕不同意，后在丽丽帮腔和<user>施压下，考虑到家庭恶劣环境最终同意媛媛寄宿在徐暮云处。",
      },
    ],
  },
  {
    id: "d4",
    dateText: "2026-07-03（周五）",
    eventCount: "7 个事件",
    events: [
      {
        id: 401,
        characters: "丽丽、萱萱",
        location: "客厅L型沙发",
        mood: "丽丽戏谑顾忌，萱萱极度背德亢奋，<user>理智崩溃边缘",
        desc: "萱萱接着男友电话并用甜美声音撒谎，右手却在裤裆里疯狂套弄<user>；丽丽因顾忌男友阿龙而死守底线，三人陷入荒诞混乱的极度刺激之中。",
      },
      {
        id: 402,
        characters: "丽丽、萱萱",
        location: "客厅L型沙发",
        mood: "丽丽狂笑嘲讽，萱萱病态兴奋，<user>羞愤交加",
        desc: "发现<user>是处男后极其亢奋，开启粗俗口嗨模式，丽丽用脚底套弄，萱萱用手指抠弄掐捏并舔舐前列腺液，对<user>进行双重极度羞辱与调戏。",
      },
      {
        id: 403,
        characters: "丽丽",
        location: "客厅L型沙发",
        mood: "尴尬且无赖",
        desc: "走错楼层进入15-03，因脚痛和饥饿赖在<user>家沙发上不走，并试图蹭吃麻辣烫，两人由此展开初次荒诞交集。",
      },
    ],
  },
]);

// 扁平化全部事件供表格使用
const allHistoryFlat = computed(() => {
  const list: Array<{
    id: number;
    dateText: string;
    characters: string;
    location: string;
    mood: string;
    desc: string;
  }> = [];
  let index = 1;
  for (const group of historyDateGroups.value) {
    for (const ev of group.events) {
      list.push({
        id: index++,
        dateText: group.dateText,
        characters: ev.characters,
        location: ev.location,
        mood: ev.mood,
        desc: ev.desc,
      });
    }
  }
  return list;
});

function handleClose(): void {
  emit("update:open", false);
}
</script>

<template>
  <!-- 抽屉蒙层 -->
  <Transition name="fade">
    <div
      v-if="open"
      @click="handleClose"
      class="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm transition-opacity"
    />
  </Transition>

  <!-- 右侧抽屉 (1:1 Figma 规格: width: 100%, max-w-[440px], background: #292524) -->
  <Transition name="slide-right">
    <aside
      v-if="open"
      class="fixed top-0 right-0 bottom-0 z-50 w-full max-w-[440px] bg-[#292524] text-[#F5F5F4] flex flex-col shadow-[0_8px_32px_rgba(249,200,109,0.15)] border-t-2 border-b-2 border-[#F9C86D] overflow-hidden select-none"
    >
      <!-- 1. 顶部 Header 与控制区 (双行黑金磨砂) -->
      <header class="w-full bg-gradient-to-br from-[#F9C86D]/15 via-[#44403C]/80 to-[#292524] border-b border-[#F9C86D] backdrop-blur-md pt-safe px-3 pt-3 pb-2.5 flex flex-col gap-2 shrink-0">
        
        <!-- 第一行: 标题「叙梦面板」+「记忆增强·ON」胶囊 + 关闭按钮 -->
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Swords class="w-4 h-4 text-[#F9C86D]" />
            <h2 class="text-[15px] font-bold text-[#F9C86D] tracking-wide">
              叙梦面板
            </h2>
          </div>

          <div class="flex items-center gap-2">
            <!-- 记忆增强 ON/OFF 胶囊按钮 -->
            <button
              type="button"
              @click="isMemoryEnhanced = !isMemoryEnhanced"
              class="h-[30px] px-2.5 rounded-lg border border-[#F9C86D] bg-[#F9C86D]/20 hover:bg-[#F9C86D]/30 active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer"
            >
              <span
                class="w-2 h-2 rounded-full transition-colors"
                :class="isMemoryEnhanced ? 'bg-[#22C55E]' : 'bg-[#78716C]'"
              />
              <BookOpen class="w-3.5 h-3.5 text-[#F9C86D]" />
              <span class="text-[11px] font-semibold text-[#F9C86D]">
                记忆增强 · {{ isMemoryEnhanced ? 'ON' : 'OFF' }}
              </span>
            </button>

            <!-- 方形关闭按钮 -->
            <button
              type="button"
              @click="handleClose"
              class="w-[30px] h-[30px] rounded-lg border border-[#D1A35C] bg-[#F9C86D]/15 hover:bg-[#F9C86D]/25 active:scale-95 transition-all flex items-center justify-center text-[#F9C86D] cursor-pointer"
              title="关闭"
            >
              <X class="w-4 h-4" />
            </button>
          </div>
        </div>

        <!-- 第二行: 右对齐的「整理」与「备份与恢复」操作按钮 -->
        <div class="flex items-center justify-end gap-2 pt-0.5">
          <button
            type="button"
            class="h-7 px-2.5 rounded-[7px] border border-[#F9C86D]/20 bg-[#44403C]/80 hover:border-[#F9C86D]/50 active:scale-95 transition-all flex items-center gap-1.5 text-xs text-[#A8A29E] hover:text-[#F5F5F4] cursor-pointer"
          >
            <Sparkles class="w-3.5 h-3.5 text-[#F9C86D]" />
            <span>整理</span>
          </button>

          <button
            type="button"
            class="h-7 px-2.5 rounded-[7px] border border-[#F9C86D]/20 bg-[#44403C]/80 hover:border-[#F9C86D]/50 active:scale-95 transition-all flex items-center gap-1.5 text-xs text-[#A8A29E] hover:text-[#F5F5F4] cursor-pointer"
          >
            <Database class="w-3.5 h-3.5 text-[#A8A29E]" />
            <span>备份与恢复</span>
          </button>
        </div>

      </header>

      <!-- 2. 6 大 Tab 选项卡导航栏 (从左到右: 👤状态 / 🎒背包 / ⚔️技能 / 👥社交 / 📜任务 / 📖历史) -->
      <nav class="h-11 px-2 py-1.5 flex items-center gap-1 border-b border-[#44403C] bg-[#292524] shrink-0 overflow-x-auto [scrollbar-width:none] [-ms-overflow-style:none] [&::-webkit-scrollbar]:hidden">
        <button
          v-for="t in tabs"
          :key="t.id"
          type="button"
          @click="activeTab = t.id"
          :class="[
            'px-2.5 h-8 rounded-lg flex items-center gap-1.5 transition-all shrink-0 cursor-pointer text-xs font-medium',
            activeTab === t.id
              ? 'border border-[#F9C86D] bg-gradient-to-br from-[#F9C86D]/25 to-[#F9C86D]/15 text-[#F9C86D] shadow-[0_0_12px_rgba(249,200,109,0.15)]'
              : 'border border-[#44403C] bg-transparent text-[#A8A29E] hover:text-[#F5F5F4] hover:bg-white/5'
          ]"
        >
          <component :is="t.icon" class="w-3.5 h-3.5" />
          <span>{{ t.name }}</span>
        </button>
      </nav>

      <!-- 3. 主体内容滚动区域 (带底边充足留白) -->
      <main class="flex-1 overflow-y-auto p-3 flex flex-col gap-3 pb-12">
        
        <!-- ==================== TAB 1: 状态 (时空背景 + 玩家状态) ==================== -->
        <template v-if="activeTab === 1">
          <!-- (1) 时空背景卡片 -->
          <section class="p-4 rounded-xl border border-[#44403C]/60 bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col">
            <div class="pb-2 flex items-center gap-2 border-b border-[#F9C86D]/20">
              <span class="text-xs">🕒</span>
              <h3 class="text-[13px] font-semibold text-[#F9C86D] tracking-tight">
                时空背景
              </h3>
            </div>

            <div class="pt-3 grid grid-cols-1 gap-2">
              <div class="flex flex-col gap-0.5">
                <span class="text-xs text-[#A8A29E]">日期</span>
                <span class="text-base font-semibold text-[#F5F5F4] tracking-tight">
                  2026-07-06（周一）
                </span>
              </div>

              <div class="flex flex-col gap-0.5 pt-1">
                <span class="text-xs text-[#A8A29E]">时间</span>
                <span class="text-base font-semibold text-[#F5F5F4] font-mono">
                  15:20
                </span>
              </div>
            </div>

            <div class="mt-3 p-3.5 rounded-lg bg-[#F9C86D]/15 border border-[#F9C86D]/30 flex flex-col gap-1">
              <div class="flex items-center gap-1.5">
                <span class="text-xs text-[#A8A29E]">📍</span>
                <span class="text-sm font-semibold text-[#A8A29E]">当前地点</span>
              </div>
              <span class="text-[15px] text-[#F5F5F4] pl-5 font-medium">
                客厅L型沙发
              </span>
            </div>

            <div class="mt-3 pt-2 border-t border-[#F9C86D]/15 flex flex-col gap-2">
              <div class="flex items-center gap-1.5">
                <span class="text-xs">👥</span>
                <span class="text-[13px] font-semibold text-[#F9C86D]">在场角色</span>
                <span class="text-xs text-[#78716C] font-mono">(1)</span>
              </div>

              <div class="flex flex-wrap gap-2 pt-1">
                <div class="px-3 py-1.5 rounded-full border border-white/10 bg-black/40 text-sm font-medium text-[#F5F5F4]">
                  &lt;user&gt;、丽丽、萱萱
                </div>
              </div>
            </div>
          </section>

          <!-- (2) 玩家状态卡片列表 (5项) -->
          <section class="p-3.5 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.15)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <span class="text-xs">📊</span>
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                玩家状态
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ playerStates.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="state in playerStates"
                :key="state.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2 hover:border-[#F9C86D]/40 transition-colors"
              >
                <div class="flex items-center justify-between">
                  <span class="text-[15px] font-semibold text-[#F5F5F4]">
                    {{ state.name }}
                  </span>
                  <span class="text-base font-bold text-[#F9C86D] font-mono">
                    {{ state.currentVal }} / {{ state.maxVal }}
                  </span>
                </div>

                <div class="pt-2 border-t border-[#F9C86D]/15 text-[13px] text-[#A8A29E] leading-relaxed">
                  {{ state.desc }}
                </div>
              </div>
            </div>
          </section>
        </template>

        <!-- ==================== TAB 2: 背包 (1:1 原型 Frame 85:7316) ==================== -->
        <template v-else-if="activeTab === 2">
          
          <!-- (1) 🎒 消耗品/道具 (1) -->
          <section class="p-3.5 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <Backpack class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                消耗品/道具
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ consumables.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="item in consumables"
                :key="item.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2 hover:border-[#F9C86D]/40 transition-colors"
              >
                <div class="flex items-center justify-between">
                  <span class="text-[15px] font-semibold text-[#F5F5F4]">
                    {{ item.name }}
                  </span>
                  <span class="px-2 py-0.5 rounded-full bg-[#F9C86D] text-[#0C0A09] text-xs font-bold font-mono">
                    x{{ item.count }}
                  </span>
                </div>

                <div class="flex flex-col gap-1 text-[13px] pt-1">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#78716C] font-medium">效果:</span>
                    <span class="text-[#F5F5F4]">{{ item.effect }}</span>
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#78716C] font-medium">来源:</span>
                    <span class="text-[#F5F5F4]">{{ item.source }}</span>
                  </div>
                </div>

                <div class="pt-2 border-t border-[#F9C86D]/15 text-[13px] text-[#A8A29E]">
                  {{ item.desc }}
                </div>
              </div>
            </div>
          </section>

          <!-- (2) ◇ 重要物品 (1) (带红色左边框指示条) -->
          <section class="p-3.5 rounded-xl border border-[#44403C] bg-red-500/10 shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <span class="text-xs text-[#F9C86D]">◇</span>
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                重要物品
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ importantItems.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="item in importantItems"
                :key="item.id"
                class="p-3 rounded-lg border-l-4 border-l-[#EF4444] border-t border-r border-b border-[#44403C] bg-[#292524] flex flex-col gap-2"
              >
                <div class="flex items-baseline gap-1.5">
                  <span class="text-base font-bold text-[#F5F5F4]">
                    {{ item.name }}
                  </span>
                  <span class="text-[13px] text-[#A8A29E]">
                    ({{ item.owner }})
                  </span>
                </div>

                <p class="text-sm text-[#A8A29E] leading-relaxed">
                  {{ item.desc }}
                </p>

                <div class="text-[13px] leading-relaxed">
                  <span class="font-medium text-[#EF4444]">重要性: </span>
                  <span class="text-[#EF4444]">{{ item.importance }}</span>
                </div>
              </div>
            </div>
          </section>

        </template>

        <!-- ==================== TAB 3: 技能 (1:1 原型 Frame 88:2) ==================== -->
        <template v-else-if="activeTab === 3">
          
          <!-- (1) 未装备技能 (1) -->
          <section class="p-4 rounded-xl border border-[#44403C] bg-[#44403C] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                未装备技能
              </h3>
              <span class="text-xs text-[#78716C] font-mono">(1)</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="skill in skills"
                :key="skill.id"
                class="p-3.5 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2.5"
              >
                <div class="flex items-center gap-2">
                  <span class="text-[15px] font-bold text-[#F5F5F4]">
                    {{ skill.name }}
                  </span>
                  <span class="px-1.5 py-0.5 rounded bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold font-mono">
                    Lv.1
                  </span>
                </div>

                <p class="text-[13px] text-[#A8A29E] leading-relaxed">
                  {{ skill.effect }}
                </p>

                <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-4 text-xs">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">消耗</span>
                    <span class="font-semibold text-[#F5F5F4]">{{ skill.cost }}</span>
                  </div>
                  <span class="text-[#44403C]">|</span>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">冷却</span>
                    <span class="font-semibold text-[#F5F5F4]">{{ skill.cooldown }}</span>
                  </div>
                </div>

                <div class="flex flex-col gap-1.5 pt-0.5">
                  <div class="flex items-center justify-between text-[11px] text-[#A8A29E]">
                    <span>熟练度 {{ skill.proficiencyCurrent }}/{{ skill.proficiencyMax }}</span>
                    <span class="font-mono">{{ skill.proficiency }}</span>
                  </div>
                  <div class="w-full h-1.5 rounded-full bg-[#44403C] overflow-hidden">
                    <div
                      class="h-full rounded-full bg-[#F9C86D]"
                      :style="{ width: `${skill.proficiencyCurrent}%` }"
                    />
                  </div>
                </div>

                <div class="p-2 rounded-md bg-[#F9C86D]/15 text-xs text-[#A8A29E]">
                  {{ skill.source }}
                </div>
              </div>
            </div>
          </section>

          <!-- (2) 所有技能 (1) -->
          <section class="p-4 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                所有技能
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ skills.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="skill in skills"
                :key="skill.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2"
              >
                <div class="flex items-center justify-between">
                  <span class="text-[15px] font-semibold text-[#F5F5F4]">
                    {{ skill.name }}
                  </span>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[11px] font-semibold text-[#3B82F6]">
                      {{ skill.type }}
                    </span>
                    <span class="px-1.5 py-0.2 rounded bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold font-mono">
                      Lv.{{ skill.level }}
                    </span>
                    <span class="text-[11px] font-semibold text-[#F9C86D]">
                      {{ skill.status }}
                    </span>
                  </div>
                </div>

                <div class="pt-1 text-[13px] leading-relaxed flex items-start gap-1">
                  <span class="text-[#A8A29E] shrink-0">效果:</span>
                  <span class="text-[#F5F5F4]">{{ skill.effect }}</span>
                </div>

                <div class="flex items-center gap-1.5 text-[13px]">
                  <span class="text-[#A8A29E]">熟练度:</span>
                  <span class="text-[#F5F5F4] font-mono">{{ skill.proficiency }}</span>
                </div>

                <div class="flex items-center gap-4 text-[13px]">
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">消耗:</span>
                    <span class="text-[#F5F5F4]">{{ skill.cost }}</span>
                  </div>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[#A8A29E]">冷却:</span>
                    <span class="text-[#F5F5F4]">{{ skill.cooldown }}</span>
                  </div>
                </div>

                <div class="flex items-center gap-1.5 text-[13px]">
                  <span class="text-[#A8A29E] shrink-0">来源:</span>
                  <span class="text-[#F5F5F4]">{{ skill.source }}</span>
                </div>
              </div>
            </div>
          </section>

        </template>

        <!-- ==================== TAB 4: 社交 (1:1 原型 Frame 91:1327) ==================== -->
        <template v-else-if="activeTab === 4">
          
          <!-- (1) 社交关系总览 四宫格状态矩阵 -->
          <section class="p-3.5 rounded-xl border border-[#F9C86D]/20 bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <Users class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                社交关系总览
              </h3>
            </div>

            <div class="grid grid-cols-2 gap-2 pt-1">
              <div class="p-2.5 rounded-lg bg-[#22C55E]/10 border border-[#22C55E]/20 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">亲密</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">2</span>
              </div>

              <div class="p-2.5 rounded-lg bg-[#EAB308]/10 border border-[#EAB308]/20 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">友好</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">2</span>
              </div>

              <div class="p-2.5 rounded-lg bg-[#EF4444]/10 border border-[#EF4444]/20 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">敌对</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">0</span>
              </div>

              <div class="p-2.5 rounded-lg bg-[#F9C86D]/15 border border-[#F9C86D]/30 flex flex-col items-center justify-center gap-0.5">
                <span class="text-[13px] text-[#A8A29E]">总计</span>
                <span class="text-[22px] font-bold text-[#F5F5F4] font-mono leading-tight">4</span>
              </div>
            </div>
          </section>

          <!-- (2) 角色关系卡片列表 (4个卡片) -->
          <div class="flex flex-col gap-2.5">
            <div
              v-for="char in socialCharacters"
              :key="char.id"
              class="p-3 rounded-xl border border-[#44403C] bg-[#292524] flex flex-col gap-2.5 hover:border-[#F9C86D]/40 transition-colors shadow-md"
            >
              <div class="flex items-center justify-between">
                <h4 class="text-[15px] font-bold text-[#F5F5F4]">
                  {{ char.name }}
                </h4>
                <span
                  :class="[
                    'px-2 py-0.5 rounded-full text-xs font-semibold text-[#0C0A09]',
                    char.tagColor
                  ]"
                >
                  {{ char.relationTag }}
                </span>
              </div>

              <div class="flex items-center gap-2">
                <div class="flex-1 h-1.5 rounded-full bg-[#44403C] overflow-hidden">
                  <div
                    :class="['h-full rounded-full transition-all', char.favorBarColor]"
                    :style="{ width: `${char.favorability}%` }"
                  />
                </div>
                <span class="text-xs font-bold text-[#F5F5F4] font-mono w-6 text-right">
                  {{ char.favorability }}
                </span>
              </div>

              <div class="flex flex-col gap-1 text-xs">
                <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-2">
                  <span class="text-[#A8A29E] shrink-0">关系</span>
                  <span class="font-semibold text-[#F5F5F4]">{{ char.relation }}</span>
                </div>
                <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-2">
                  <span class="text-[#A8A29E] shrink-0">位置</span>
                  <span class="text-[#F5F5F4]">{{ char.location }}</span>
                </div>
              </div>
            </div>
          </div>

        </template>

        <!-- ==================== TAB 5: 任务 (1:1 原型 Frame 92:2745) ==================== -->
        <template v-else-if="activeTab === 5">
          
          <!-- (1) 进行中的任务 (1) -->
          <section class="p-4 rounded-xl border border-[#44403C] bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <Scroll class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                进行中的任务
              </h3>
              <span class="text-xs text-[#78716C] font-mono">({{ ongoingTasks.length }})</span>
            </div>

            <div class="flex flex-col gap-2 pt-1">
              <div
                v-for="task in ongoingTasks"
                :key="task.id"
                class="p-3 rounded-lg border border-[#44403C] bg-[#292524] flex flex-col gap-2.5"
              >
                <!-- 顶行: 角色名 + 状态胶囊 -->
                <div class="flex items-center justify-between">
                  <span class="text-[13px] font-bold text-[#F5F5F4]">
                    {{ task.role }}
                  </span>
                  <div class="flex items-center gap-1.5">
                    <span class="text-[11px] font-semibold text-[#EAB308]">
                      {{ task.typeTag }}
                    </span>
                    <span class="px-2 py-0.5 rounded bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold">
                      {{ task.statusTag }}
                    </span>
                  </div>
                </div>

                <!-- 任务描述 -->
                <p class="text-[13px] text-[#A8A29E] leading-relaxed">
                  {{ task.task }}
                </p>

                <!-- 任务详情三联栏 -->
                <div class="grid grid-cols-3 gap-1.5 text-xs">
                  <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-1">
                    <span class="text-[#A8A29E] shrink-0">角色:</span>
                    <span class="font-semibold text-[#F5F5F4] truncate">{{ task.role }}</span>
                  </div>
                  <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-1">
                    <span class="text-[#A8A29E] shrink-0">地点:</span>
                    <span class="font-semibold text-[#F5F5F4] truncate">{{ task.location }}</span>
                  </div>
                  <div class="p-2 rounded-md bg-[#1C1917] flex items-center gap-1">
                    <span class="text-[#A8A29E] shrink-0">持续时间:</span>
                    <span class="font-semibold text-[#F5F5F4] truncate">{{ task.duration }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

        </template>

        <!-- ==================== TAB 6: 历史 (1:1 原型 Frame 94:4096) ==================== -->
        <template v-else-if="activeTab === 6">
          
          <!-- (1) 重要事件历史总览与角色筛选卡片 -->
          <section class="p-3.5 rounded-xl border border-[#F9C86D]/20 bg-[#292524] shadow-[0_2px_8px_rgba(0,0,0,0.30)] flex flex-col gap-2.5">
            <div class="pb-1.5 flex items-center gap-1.5 border-b border-[#F9C86D]/15">
              <BookOpen class="w-3.5 h-3.5 text-[#F9C86D]" />
              <h3 class="text-[13px] font-semibold text-[#F9C86D]">
                重要事件历史
              </h3>
            </div>

            <!-- 总事件与时间跨度 -->
            <div class="flex items-center gap-4 text-sm font-bold text-[#F5F5F4] pt-0.5">
              <span>总事件: 33</span>
              <span>时间跨度: 5 天</span>
            </div>

            <!-- 角色筛选标签网格 -->
            <div class="flex flex-col gap-1.5 pt-1">
              <span class="text-xs text-[#A8A29E]">角色筛选:</span>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="filter in characterFilters"
                  :key="filter.id"
                  type="button"
                  @click="activeFilter = filter.id"
                  :class="[
                    'px-2.5 py-1 rounded-md text-xs font-medium transition-all cursor-pointer border',
                    activeFilter === filter.id
                      ? 'border-[#F9C86D] bg-[#292524] text-[#F9C86D] font-bold shadow-[0_0_8px_rgba(249,200,109,0.2)]'
                      : 'border-transparent bg-[#F9C86D]/15 text-[#F5F5F4] hover:bg-[#F9C86D]/25'
                  ]"
                >
                  {{ filter.name }} ({{ filter.count }})
                </button>
              </div>
            </div>
          </section>

          <!-- (2) 时间轴事件流列表 (按日期分组) -->
          <div class="flex flex-col gap-4 pt-1">
            <div
              v-for="group in historyDateGroups"
              :key="group.id"
              class="flex flex-col gap-2"
            >
              <!-- 日期标题行 -->
              <div class="px-3 py-1.5 rounded-lg bg-[#292524] border border-[#44403C]/60 flex items-center justify-between">
                <span class="text-[13px] font-bold text-[#F5F5F4]">
                  {{ group.dateText }}
                </span>
                <span class="px-2 py-0.5 rounded-full bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold">
                  {{ group.eventCount }}
                </span>
              </div>

              <!-- 时间轴卡片群 (左侧纵线) -->
              <div class="pl-4 ml-3 border-l-2 border-[#44403C] flex flex-col gap-2.5 relative">
                <div
                  v-for="ev in group.events"
                  :key="ev.id"
                  class="p-3 rounded-xl border border-[#44403C] bg-[#292524] flex flex-col gap-2 relative hover:border-[#F9C86D]/40 transition-colors shadow-sm"
                >
                  <!-- 节点小圆点 -->
                  <div class="w-2.5 h-2.5 rounded-full bg-[#78716C] border-2 border-[#292524] absolute -left-[22px] top-4.5" />

                  <!-- 顶行: 角色 + 地点 + 氛围/情绪标签 -->
                  <div class="flex items-center justify-between gap-1 flex-wrap">
                    <div class="flex items-center gap-2">
                      <span class="text-xs font-semibold text-[#F9C86D]">
                        {{ ev.characters }}
                      </span>
                      <span class="text-xs text-[#A8A29E]">
                        {{ ev.location }}
                      </span>
                    </div>

                    <span class="px-2 py-0.5 rounded-md bg-[#F9C86D] text-[#0C0A09] text-[11px] font-semibold">
                      {{ ev.mood }}
                    </span>
                  </div>

                  <!-- 事件描述段落 -->
                  <p class="text-[13px] text-[#F5F5F4] leading-relaxed pt-0.5">
                    {{ ev.desc }}
                  </p>
                </div>
              </div>
            </div>
          </div>

        </template>

        <!-- (3) 查看原始表格数据手风琴折叠卡片 -->
        <section class="flex flex-col gap-3">
          <!-- 折叠切换条 -->
          <button
            type="button"
            @click="isRawTablesExpanded = !isRawTablesExpanded"
            class="w-full px-3.5 py-2.5 rounded-lg border border-[#44403C] bg-[#292524] hover:bg-[#332D28] active:scale-[0.99] transition-all flex items-center justify-between cursor-pointer"
          >
            <div class="flex items-center gap-2">
              <component
                :is="isRawTablesExpanded ? ChevronUp : ChevronDown"
                class="w-4 h-4 text-[#F9C86D]"
              />
              <span class="text-xs font-semibold text-[#F9C86D]">
                查看原始表格数据
              </span>
            </div>

            <span class="text-[11px] font-semibold text-[#A8A29E]">
              ({{ activeTab === 1 || activeTab === 2 || activeTab === 4 ? '2' : '1' }}个相关表格)
            </span>
          </button>

          <!-- 展开后的表格列表 -->
          <div v-if="isRawTablesExpanded" class="flex flex-col gap-4 pt-1">
            
            <!-- 历史专属表格: 历史事件表格 (Tab 6) -->
            <div v-if="activeTab === 6" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  历史事件表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">发生日期</th>
                      <th class="py-2 px-2 font-medium">参与角色</th>
                      <th class="py-2 px-2 font-medium">地点</th>
                      <th class="py-2 px-2 font-medium">情绪/氛围</th>
                      <th class="py-2 px-2 font-medium">事件经过</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="ev in allHistoryFlat"
                      :key="ev.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ ev.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ ev.dateText }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#F9C86D]">{{ ev.characters }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ ev.location }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#EAB308]">{{ ev.mood }}</td>
                      <td class="py-2 px-2 max-w-[200px] truncate" :title="ev.desc">{{ ev.desc }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 任务专属表格: 任务/命令/约定表格 (Tab 5) -->
            <div v-if="activeTab === 5" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  任务/命令/约定表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">角色</th>
                      <th class="py-2 px-2 font-medium">任务</th>
                      <th class="py-2 px-2 font-medium">地点</th>
                      <th class="py-2 px-2 font-medium">持续时间</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="t in ongoingTasks"
                      :key="t.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ t.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ t.role }}</td>
                      <td class="py-2 px-2 max-w-[180px] truncate" :title="t.task">{{ t.task }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ t.location }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ t.duration }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 社交专属表格 1: 角色特征表格 (Tab 4) -->
            <div v-if="activeTab === 4" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  角色特征表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">角色名</th>
                      <th class="py-2 px-2 font-medium">身体特征</th>
                      <th class="py-2 px-2 font-medium">性格</th>
                      <th class="py-2 px-2 font-medium">职业</th>
                      <th class="py-2 px-2 font-medium">爱好</th>
                      <th class="py-2 px-2 font-medium">喜爱的事物</th>
                      <th class="py-2 px-2 font-medium">住所</th>
                      <th class="py-2 px-2 font-medium">其他重要信息</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="c in socialCharacters"
                      :key="c.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ c.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ c.name }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate" :title="c.bodyFeature">{{ c.bodyFeature }}</td>
                      <td class="py-2 px-2 max-w-[120px] truncate" :title="c.personality">{{ c.personality }}</td>
                      <td class="py-2 px-2 max-w-[100px] truncate">{{ c.job }}</td>
                      <td class="py-2 px-2 max-w-[90px] truncate">{{ c.hobby }}</td>
                      <td class="py-2 px-2 max-w-[100px] truncate">{{ c.favorite }}</td>
                      <td class="py-2 px-2 max-w-[100px] truncate">{{ c.residence }}</td>
                      <td class="py-2 px-2 max-w-[160px] truncate text-[#A8A29E]" :title="c.otherInfo">{{ c.otherInfo }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 社交专属表格 2: 角色与<user>社交表格 (Tab 4) -->
            <div v-if="activeTab === 4" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  角色与&lt;user&gt;社交表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">角色名</th>
                      <th class="py-2 px-2 font-medium">对&lt;user&gt;关系</th>
                      <th class="py-2 px-2 font-medium">对&lt;user&gt;态度</th>
                      <th class="py-2 px-2 font-medium">对&lt;user&gt;好感</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="c in socialCharacters"
                      :key="c.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ c.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ c.name }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#F9C86D]">{{ c.relation }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate" :title="c.attitude">{{ c.attitude }}</td>
                      <td class="py-2 px-2 font-mono font-semibold">{{ c.favorability }} ({{ c.relationTag }})</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 技能专属表格: 技能表 (Tab 3) -->
            <div v-if="activeTab === 3" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  技能表
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">技能名</th>
                      <th class="py-2 px-2 font-medium">技能类型</th>
                      <th class="py-2 px-2 font-medium">等级</th>
                      <th class="py-2 px-2 font-medium">熟练度</th>
                      <th class="py-2 px-2 font-medium">消耗</th>
                      <th class="py-2 px-2 font-medium">冷却时间</th>
                      <th class="py-2 px-2 font-medium">效果描述</th>
                      <th class="py-2 px-2 font-medium">学习来源</th>
                      <th class="py-2 px-2 font-medium">状态</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="s in skills"
                      :key="s.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ s.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ s.name }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#3B82F6]">{{ s.type }}</td>
                      <td class="py-2 px-2 font-mono">{{ s.level }}</td>
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ s.proficiency }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ s.cost }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ s.cooldown }}</td>
                      <td class="py-2 px-2 max-w-[200px] truncate" :title="s.effect">{{ s.effect }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate text-[#A8A29E]" :title="s.source">{{ s.source }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#F9C86D]">{{ s.status }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 背包专属表格 1: 重要物品表格 (Tab 2) -->
            <div v-if="activeTab === 2" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  重要物品表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">拥有人</th>
                      <th class="py-2 px-2 font-medium">物品描述</th>
                      <th class="py-2 px-2 font-medium">物品名</th>
                      <th class="py-2 px-2 font-medium">重要原因</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in importantItems"
                      :key="item.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ item.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ item.owner }}</td>
                      <td class="py-2 px-2 max-w-[140px] truncate" :title="item.desc">{{ item.desc }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ item.name }}</td>
                      <td class="py-2 px-2 max-w-[160px] truncate text-[#EF4444]" :title="item.importance">{{ item.importance }}</td>
                      <td class="py-2 px-2 text-center whitespace-nowrap">
                        <div class="flex items-center justify-center gap-1">
                          <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]">
                            <Edit2 class="w-3.5 h-3.5" />
                          </button>
                          <button type="button" class="text-[#A8A29E] hover:text-red-400">
                            <Trash2 class="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 背包专属表格 2: 消耗品/道具表格 (Tab 2) -->
            <div v-if="activeTab === 2" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  消耗品/道具表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">物品名</th>
                      <th class="py-2 px-2 font-medium">数量</th>
                      <th class="py-2 px-2 font-medium">类型</th>
                      <th class="py-2 px-2 font-medium">效果/属性</th>
                      <th class="py-2 px-2 font-medium">获得方式</th>
                      <th class="py-2 px-2 font-medium">备注</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="item in consumables"
                      :key="item.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ item.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ item.name }}</td>
                      <td class="py-2 px-2 font-mono font-bold text-[#F9C86D]">{{ item.count }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#A8A29E]">{{ item.type }}</td>
                      <td class="py-2 px-2 whitespace-nowrap">{{ item.effect }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#A8A29E]">{{ item.source }}</td>
                      <td class="py-2 px-2 text-[#A8A29E] max-w-[140px] truncate" :title="item.desc">
                        {{ item.desc }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 状态专属表格 1: 时空表格 (Tab 1) -->
            <div v-if="activeTab === 1" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  时空表格
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">日期</th>
                      <th class="py-2 px-2 font-medium">时间</th>
                      <th class="py-2 px-2 font-medium">地点（当前描写）</th>
                      <th class="py-2 px-2 font-medium">此地角色</th>
                      <th class="py-2 px-2 font-medium text-center">操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">1</td>
                      <td class="py-2 px-2 whitespace-nowrap">2026-07-06 (周一)</td>
                      <td class="py-2 px-2 font-mono">15:20</td>
                      <td class="py-2 px-2 whitespace-nowrap">客厅L型沙发</td>
                      <td class="py-2 px-2 whitespace-nowrap">&lt;user&gt;、丽丽、萱萱</td>
                      <td class="py-2 px-2 text-center">
                        <button type="button" class="text-[#A8A29E] hover:text-[#F9C86D]" title="编辑">
                          <Edit2 class="w-3.5 h-3.5" />
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 状态专属表格 2: 玩家状态表 (Tab 1) -->
            <div v-if="activeTab === 1" class="p-3 rounded-xl border border-[#F9C86D]/40 bg-[#1C1917] flex flex-col gap-2.5 shadow-lg">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-bold text-[#F9C86D]">
                  玩家状态表
                </h4>
                <div class="flex items-center gap-1.5">
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#F9C86D] hover:bg-[#F9C86D]/20 transition-colors flex items-center gap-1 cursor-pointer"
                  >
                    <Plus class="w-3 h-3" />
                    <span>新增</span>
                  </button>
                  <button
                    type="button"
                    class="px-2 py-1 rounded bg-[#44403C] text-[11px] font-medium text-[#A8A29E] hover:text-[#F5F5F4] transition-colors cursor-pointer"
                  >
                    批量管理
                  </button>
                </div>
              </div>

              <div class="w-full overflow-x-auto">
                <table class="w-full text-left text-xs border-collapse font-sans">
                  <thead>
                    <tr class="border-b border-[#44403C] text-[#A8A29E] bg-[#292524]/60">
                      <th class="py-2 px-2 font-medium">#</th>
                      <th class="py-2 px-2 font-medium">属性类型</th>
                      <th class="py-2 px-2 font-medium">属性名</th>
                      <th class="py-2 px-2 font-medium">当前值</th>
                      <th class="py-2 px-2 font-medium">最大值</th>
                      <th class="py-2 px-2 font-medium">备注</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="state in playerStates"
                      :key="state.id"
                      class="border-b border-[#44403C]/40 text-[#F5F5F4] hover:bg-white/5"
                    >
                      <td class="py-2 px-2 font-mono text-[#F9C86D]">{{ state.id }}</td>
                      <td class="py-2 px-2 whitespace-nowrap text-[#A8A29E]">{{ state.type }}</td>
                      <td class="py-2 px-2 whitespace-nowrap font-medium">{{ state.name }}</td>
                      <td class="py-2 px-2 font-mono text-[#F9C86D] font-bold">{{ state.currentVal }}</td>
                      <td class="py-2 px-2 font-mono text-[#A8A29E]">{{ state.maxVal }}</td>
                      <td class="py-2 px-2 max-w-[200px] truncate text-[#A8A29E]" :title="state.desc">
                        {{ state.desc }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </section>

      </main>

    </aside>
  </Transition>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(100%);
}
</style>
