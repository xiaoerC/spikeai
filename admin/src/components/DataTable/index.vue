<template>
  <div
    ref="mainRef"
    :class="[
      'w-full flex flex-col bg-white dark:bg-[#18181b] rounded-2xl border border-slate-200/80 dark:border-zinc-800/80 shadow-[0_1px_3px_0_rgba(0,0,0,0.04)] p-5 transition-all duration-200',
      isFullscreen ? '!fixed !inset-0 !z-50 !p-6 !rounded-none !shadow-2xl overflow-auto h-full' : ''
    ]"
  >
    <!-- 顶部筛选与操作工具栏 -->
    <div v-if="isShowHeader" ref="headerRef" class="flex flex-col gap-3.5 pb-2">
      <!-- 自定义搜索插槽 -->
      <div v-if="$slots.filter" class="w-full">
        <slot name="filter"></slot>
      </div>

      <!-- 按钮组与表格工具栏 -->
      <div class="flex items-center justify-between gap-3 w-full">
        <!-- 左侧业务操作按钮组 -->
        <div class="flex items-center gap-3 flex-wrap flex-1">
          <!-- 可选表名与数据量微徽章 -->
          <div v-if="tableTitle" class="flex items-center gap-2 mr-1">
            <span class="text-base font-semibold text-slate-800 dark:text-zinc-100 tracking-tight">{{ tableTitle }}</span>
            <span class="text-xs font-medium px-2 py-0.5 rounded-full bg-slate-100 dark:bg-zinc-800 text-slate-500 dark:text-zinc-400">
              {{ displayTotal }}
            </span>
          </div>

          <slot name="option-group"></slot>
          <slot name="options"></slot>
        </div>

        <!-- 右侧辅助按钮与系统工具 (现代幽灵工具栏) -->
        <div class="flex items-center gap-2 shrink-0">
          <slot name="options-right"></slot>

          <template v-if="showTableSetting">
            <div class="data-table-toolbar-group">
              <!-- 刷新表格数据 -->
              <el-tooltip content="刷新数据" placement="top" :show-after="150">
                <button
                  type="button"
                  class="data-table-toolbar-btn"
                  @click="refreshTable"
                >
                  <el-icon :size="16"><Refresh /></el-icon>
                </button>
              </el-tooltip>

              <!-- 全屏展开切换 -->
              <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏展示'" placement="top" :show-after="150">
                <button
                  type="button"
                  class="data-table-toolbar-btn"
                  @click="toggleFullscreen"
                >
                  <el-icon :size="16">
                    <FullScreen v-if="!isFullscreen" />
                    <Aim v-else />
                  </el-icon>
                </button>
              </el-tooltip>

              <!-- 列设置与拖拽排序 Popover -->
              <el-popover v-if="treeDefaultNode === null" :width="280" placement="bottom-end" trigger="click">
                <template #reference>
                  <div>
                    <el-tooltip content="自定义列" placement="top" :show-after="150">
                      <button
                        type="button"
                        class="data-table-toolbar-btn"
                      >
                        <el-icon :size="16"><Operation /></el-icon>
                      </button>
                    </el-tooltip>
                  </div>
                </template>
              <template #default>
                <div class="flex flex-col gap-2">
                  <div class="flex items-center justify-between pb-2 border-b border-gray-100 dark:border-zinc-800">
                    <span class="font-medium text-sm text-slate-800 dark:text-zinc-200">列显隐与固定排序</span>
                    <el-button link type="primary" size="small" @click="rowReset">重置</el-button>
                  </div>

                  <el-scrollbar max-height="360px">
                    <div class="flex items-center justify-between py-1 px-1">
                      <span class="text-xs text-slate-600 dark:text-zinc-400">显示序号列</span>
                      <el-switch v-model="showSeq" size="small" @change="onSelChange" />
                    </div>

                    <!-- 固定在左侧的列 -->
                    <div class="mt-2">
                      <p class="text-xs text-slate-400 dark:text-zinc-500 mb-1">固定在左侧</p>
                      <draggable
                        v-model="user_table_config.top_row"
                        animation="300"
                        filter=".unmover"
                        group="menu"
                        handle=".mover"
                        item-key="index"
                        @end="end"
                      >
                        <template #item="{ element }">
                          <div :class="{ unmover: element.type === 'seq' }" class="flex items-center py-1 px-1 hover:bg-slate-50 dark:hover:bg-zinc-800/60 rounded">
                            <el-icon :size="14" class="mover cursor-grab text-slate-400">
                              <svg-icon v-if="element.type !== 'seq'" icon-class="dragable" />
                            </el-icon>
                            <el-checkbox
                              v-model="element.visible"
                              :disabled="element.type === 'seq'"
                              :label="element"
                              class="!ml-2"
                              @change="() => xTable?.refreshColumn()"
                            >
                              <div class="flex items-center gap-1.5 text-xs">
                                <svg-icon :icon-class="element.visible ? 'eye-open' : 'eye'" />
                                <span>{{ element.title }}</span>
                              </div>
                            </el-checkbox>
                          </div>
                        </template>
                      </draggable>
                    </div>

                    <!-- 不固定的常规列 -->
                    <div class="mt-2">
                      <p class="text-xs text-slate-400 dark:text-zinc-500 mb-1">常规列 (可自由拖拽)</p>
                      <draggable
                        v-model="user_table_config.center_row"
                        animation="300"
                        group="menu"
                        handle=".mover"
                        item-key="index"
                        @end="end"
                      >
                        <template #item="{ element }">
                          <div class="flex items-center py-1 px-1 hover:bg-slate-50 dark:hover:bg-zinc-800/60 rounded">
                            <el-icon :size="14" class="mover cursor-grab text-slate-400">
                              <svg-icon icon-class="dragable" />
                            </el-icon>
                            <el-checkbox
                              v-model="element.visible"
                              :label="element"
                              class="!ml-2"
                              @change="() => xTable?.refreshColumn()"
                            >
                              <div class="flex items-center gap-1.5 text-xs">
                                <svg-icon :icon-class="element.visible ? 'eye-open' : 'eye'" />
                                <span>{{ element.title }}</span>
                              </div>
                            </el-checkbox>
                          </div>
                        </template>
                      </draggable>
                    </div>

                    <!-- 固定在右侧的列 -->
                    <div class="mt-2">
                      <p class="text-xs text-slate-400 dark:text-zinc-500 mb-1">固定在右侧</p>
                      <draggable
                        v-model="user_table_config.bottom_row"
                        animation="300"
                        filter=".unmover"
                        group="menu"
                        handle=".mover"
                        item-key="index"
                        @end="end"
                      >
                        <template #item="{ element }">
                          <div :class="{ unmover: element.title === '操作' }" class="flex items-center py-1 px-1 hover:bg-slate-50 dark:hover:bg-zinc-800/60 rounded">
                            <el-icon :size="14" class="mover cursor-grab text-slate-400">
                              <svg-icon v-if="element.title !== '操作'" icon-class="dragable" />
                            </el-icon>
                            <el-checkbox
                              v-model="element.visible"
                              :disabled="element.title === '操作'"
                              :label="element"
                              class="!ml-2"
                              @change="() => xTable?.refreshColumn()"
                            >
                              <div class="flex items-center gap-1.5 text-xs">
                                <svg-icon :icon-class="element.visible ? 'eye-open' : 'eye'" />
                                <span>{{ element.title }}</span>
                              </div>
                            </el-checkbox>
                          </div>
                        </template>
                      </draggable>
                    </div>
                  </el-scrollbar>
                </div>
              </template>
            </el-popover>
            </div>
          </template>
        </div>
      </div>
    </div>

    <!-- vxe-table 核心表格区 (清爽自适应内容高度，外层带圆角微边框卡片) -->
    <div
      :class="[
        'w-full rounded-xl border border-[#eef1f6] dark:border-zinc-800/80 shadow-[0_1px_2px_0_rgba(0,0,0,0.03)] overflow-hidden transition-all duration-200',
        displayList.length === 0 ? 'min-h-[260px]' : ''
      ]"
    >
      <vxe-table
        ref="xTable"
        :border="(border as any)"
        :cell-class-name="cellClassName"
        :cell-style="cellStyle"
        :checkbox-config="checkboxConfig"
        :column-config="{ resizable: true }"
        :data="displayList"
        :edit-config="editConfig"
        :footer-cell-class-name="footerCellClassName"
        :footer-method="footerMethod"
        :header-align="(headerAlign as any)"
        :header-cell-style="headerCellStyle"
        :max-height="computedMaxHeight"
        :height="tableFixedHeight"
        :keep-source="keepSource"
        :loading="loading"
        :mouse-config="{ selected: true }"
        :radio-config="radioConfig"
        :row-class-name="rowClassName"
        :row-config="{ keyField: identify && identify !== 'NO' ? identify : 'id' }"
        :cell-config="({ isCurrent: true, isHover: true, ...(rowHeight && Number(rowHeight) > 0 ? { height: Number(rowHeight) } : {}) } as any)"
        :row-style="rowStyle"
        :scroll-y="scrollY"
        :seq-config="treeDefaultNode !== null ? {} : seqConfig"
        :show-footer="showFooter"
        :show-header-overflow="(showHeaderOverflow as any)"
        :show-overflow="(showOverflow as any)"
        :size="(size as any)"
        :sort-config="sortConfig"
        :stripe="stripe"
        :tree-config="treeDefaultNode"
        align="left"
        show-footer-overflow
        class="w-full"
        @scroll="scrollEvent"
        @checkbox-all="selectionChange($event.records)"
        @checkbox-change="selectionChange($event.records)"
        @radio-change="radioChange"
        @resizable-change="resizableChange"
        @cell-click="cellClick"
        @edit-closed="editClosed"
        @edit-actived="editActivated"
      >
        <template #empty>
          <slot name="empty">
            <el-empty description="暂无相关数据" :image-size="64" class="py-6" />
          </slot>
        </template>

        <!-- 多选列 -->
        <vxe-column
          v-if="showCheckbox"
          header-align="center"
          align="center"
          fixed="left"
          type="checkbox"
          width="60"
        />

        <!-- 单选列 -->
        <vxe-column
          v-if="showRadio"
          header-align="center"
          align="center"
          fixed="left"
          type="radio"
          width="60"
        />

        <!-- 序号列 -->
        <vxe-column
          v-if="showSeq && showIndex"
          :width="colSize > 1 ? 90 : 70"
          align="center"
          header-align="center"
          fixed="left"
          title="序号"
          type="seq"
        />

        <!-- 动态数据列 -->
        <vxe-column
          v-for="col in props.columns"
          :key="col.field"
          :field="col.field"
          :title="col.title"
          :width="col.width"
          :min-width="col.minWidth || col['min-width']"
          :align="(col.align as any) || 'left'"
          :header-align="(col.headerAlign as any) || (col.align as any) || 'left'"
          :fixed="(col.fixed as any)"
          :tree-node="col.treeNode"
          :show-overflow="((col.showOverflow ?? (col.slot ? false : showOverflow)) as any)"
          :sortable="col.sortable"
        >
          <template v-if="col.headerSlot" #header="slotProps">
            <slot :name="col.headerSlot" v-bind="slotProps" />
          </template>
          <template #default="slotProps">
            <slot v-if="col.slot" :name="col.slot" v-bind="slotProps" />
            <span v-else>{{ slotProps.row[col.field] }}</span>
          </template>
        </vxe-column>

        <!-- 支持插槽式扩展列 (如复杂分组列或自定义排序列) -->
        <slot></slot>

        <!-- 操作菜单列 (支持自动折叠与下拉收纳) -->
        <vxe-column v-if="optionMenus.length > 0" :width="optionWidth" fixed="right" title="操作" align="center" header-align="center">
          <template #default="{ row, rowIndex }">
            <div class="flex items-center justify-center gap-1">
              <!-- 当操作按钮不超过2个时平铺 -->
              <template
                v-if="getVisibleOptionMenus(row).length <= 2"
              >
                <el-button
                  v-for="(item, idx) in getVisibleOptionMenus(row)"
                  :key="idx"
                  :disabled="item.disabled && item.disabled(row)"
                  :type="(item.type as any) || 'primary'"
                  link
                  size="small"
                  @click="item.click && item.click(row, rowIndex)"
                >
                  <template #icon>
                    <svg-icon v-if="item.icon" :icon-class="item.icon" />
                    <i v-if="item.iconfont" :class="item.iconfont" />
                  </template>
                  {{ item.text }}
                </el-button>
              </template>

              <!-- 超过2个按钮时，前2个平铺，其余收纳至 ElDropdown -->
              <template v-else>
                <el-button
                  v-for="(item, idx) in getVisibleOptionMenus(row).slice(0, 2)"
                  :key="idx"
                  :disabled="item.disabled && item.disabled(row)"
                  :type="(item.type as any) || 'primary'"
                  link
                  size="small"
                  @click="item.click && item.click(row, rowIndex)"
                >
                  <template #icon>
                    <svg-icon v-if="item.icon" :icon-class="item.icon" />
                    <i v-if="item.iconfont" :class="item.iconfont" />
                  </template>
                  {{ item.text }}
                </el-button>


                <el-dropdown :hide-on-click="hideOnClick" trigger="click">
                  <el-button link size="small" class="!px-1">
                    <template #icon>
                      <svg-icon icon-class="more" />
                    </template>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item
                        v-for="(item, idx) in getVisibleOptionMenus(row).slice(2)"
                        :key="idx"
                        :disabled="item.disabled && item.disabled(row)"
                        @click="item.click && item.click(row, rowIndex)"
                      >
                        <div class="flex items-center gap-1.5" :class="getOptionMenuColor(item.type)">
                          <svg-icon v-if="item.icon" :icon-class="item.icon" />
                          <i v-if="item.iconfont" :class="item.iconfont" />
                          <span>{{ item.text }}</span>
                        </div>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </div>
          </template>
        </vxe-column>
      </vxe-table>
    </div>

    <!-- 底部标准分页控制条 (左右平衡，左侧数据摘要，右侧精致无缝分页) -->
    <div v-if="showPager" class="flex flex-wrap items-center justify-between gap-3 pt-3 mt-1 text-xs text-slate-500 dark:text-zinc-400">
      <div class="flex items-center gap-2">
        <span>共 <strong class="text-slate-800 dark:text-zinc-200 font-semibold">{{ displayTotal }}</strong> 条数据</span>
        <span
          v-if="selectionRow.length > 0"
          class="text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/40 px-2 py-0.5 rounded-full font-medium"
        >
          已选择 {{ selectionRow.length }} 项
        </span>
      </div>

      <el-pagination
        :current-page="localPage"
        :page-size="localSize"
        :page-sizes="[5, 10, 20, 30, 40, 50, 100]"
        :small="isPageSmall"
        :teleported="pageTeleported"
        :total="displayTotal"
        background
        layout="sizes, prev, pager, next, jumper"
        @current-change="onLocalPageChange"
        @size-change="onLocalSizeChange"
      />
    </div>
  </div>
</template>

<script lang="ts" setup>
import Draggable from 'vuedraggable';

export interface IColumnConfig {
  field: string;
  title: string;
  width?: string | number;
  minWidth?: string | number;
  align?: string;
  headerAlign?: string;
  fixed?: 'left' | 'right';
  treeNode?: boolean;
  showOverflow?: boolean | string;
  sortable?: boolean;
  slot?: string;
  headerSlot?: string;
  visible?: boolean;
  [key: string]: any;
}

export interface IOptionMenu {
  text: string;
  type?: string;
  icon?: string;
  iconfont?: string;
  show?: (row: any) => boolean;
  disabled?: (row: any) => boolean;
  click?: (row: any, rowIndex?: number) => void;
}

const props = withDefaults(
  defineProps<{
    tableTitle?: string;
    columns?: IColumnConfig[];
    tableQuery?: { page?: number; size?: number; [key: string]: any };
    treeDefaultNode?: any;
    checkboxConfig?: any;
    radioConfig?: any;
    stripe?: boolean;
    headerCellStyle?: (row: any) => any;
    optionWidth?: number;
    showCheckbox?: boolean;
    showRadio?: boolean;
    showIndex?: boolean;
    headerAlign?: string;
    isShowHeader?: boolean;
    identify?: string;
    size?: string;
    showPager?: boolean;
    showTableSetting?: boolean;
    scrollY?: any;
    editConfig?: any;
    optionMenus?: IOptionMenu[];
    tableData?: any;
    border?: boolean | string;
    rowClassName?: (row: any) => any;
    cellClassName?: (row: any) => any;
    rowStyle?: (row: any) => any;
    cellStyle?: (row: any) => any;
    sortConfig?: any;
    showMaxHeight?: boolean;
    pageTeleported?: boolean;
    maxHeight?: number | string;
    rowHeight?: number | string;
    isPageSmall?: boolean;
    showFooter?: boolean;
    showHeaderOverflow?: boolean | string;
    showOverflow?: boolean | string;
    keepSource?: boolean;
    footerMethod?: (row: any) => any;
    footerCellClassName?: (row: any) => any;
    loading?: boolean;
    hideOnClick?: boolean;
  }>(),
  {
    tableTitle: '',
    columns: () => [],
    tableQuery: () => ({ page: 1, size: 20 }),
    treeDefaultNode: null,
    checkboxConfig: { highlight: true },
    radioConfig: null,
    stripe: false,
    headerCellStyle: () => {},
    optionWidth: 220,
    showCheckbox: false,
    showRadio: false,
    showIndex: true,
    headerAlign: 'left',
    isShowHeader: true,
    identify: 'NO',
    size: '',
    showPager: true,
    showTableSetting: true,
    scrollY: { enabled: false, gt: 0 },
    editConfig: null,
    optionMenus: () => [],
    tableData: {
      totalPages: 0,
      total: 0,
      number: 0,
      size: 0,
      list: [],
      hasNext: false,
      hasPrevious: false,
      isFirst: false,
      isLast: false,
    },
    border: 'inner',
    rowClassName: () => {},
    cellClassName: () => {},
    rowStyle: () => {},
    cellStyle: () => {},
    sortConfig: {},
    showMaxHeight: true,
    pageTeleported: true,
    maxHeight: '',
    rowHeight: '',
    isPageSmall: false,
    showFooter: false,
    showHeaderOverflow: true,
    showOverflow: true,
    keepSource: false,
    footerMethod: () => {},
    footerCellClassName: () => {},
    loading: false,
    hideOnClick: false,
  },
);

const emit = defineEmits([
  'selection-change',
  'current-change',
  'size-change',
  'radio-change',
  'cell-click',
  'edit-closed',
  'edit-actived',
  'on-refresh',
  'scroll',
]);

const mainRef = ref<HTMLDivElement>();
const headerRef = ref<HTMLDivElement>();
const xTable = ref<any>(null);
const isFullscreen = ref(false);

const tableHeight = ref<number>(0);
const showSeq = ref(true);
const colSize = ref(0);

const user_table_config = ref<any>({
  top_row: [],
  center_row: [],
  bottom_row: [],
  checkbox_row: [],
});

const selectionRow = ref<any[]>([]);

// 数据源归一化：无缝兼容纯数组 Array 与分页响应对象 { list, total }
const displayList = computed<any[]>(() => {
  if (Array.isArray(props.tableData)) {
    return props.tableData;
  }
  return props.tableData?.list || [];
});

const displayTotal = computed<number>(() => {
  if (Array.isArray(props.tableData)) {
    return props.tableData.length;
  }
  return props.tableData?.total || 0;
});

// 弹性最大高度与固定高度计算 (内容少时紧凑自适应，绝无大面积无意义空白)
const computedMaxHeight = computed<string | number>(() => {
  if (props.maxHeight) return props.maxHeight;
  if (isFullscreen.value) return tableHeight.value > 100 ? tableHeight.value : '100%';
  return tableHeight.value > 200 ? tableHeight.value : 650;
});

const tableFixedHeight = computed<number | undefined>(() => {
  if (isFullscreen.value) return tableHeight.value;
  return undefined;
});

// 初始化列显隐与固定排序
const initColumnsConfig = () => {
  const top: any[] = [];
  const center: any[] = [];
  const bottom: any[] = [];

  (props.columns || []).forEach((col) => {
    const item = {
      ...col,
      visible: col.visible !== false,
    };
    if (col.fixed === 'left') {
      top.push(item);
    } else if (col.fixed === 'right') {
      bottom.push(item);
    } else {
      center.push(item);
    }
  });

  user_table_config.value.top_row = top;
  user_table_config.value.center_row = center;
  user_table_config.value.bottom_row = bottom;
};

watch(
  () => props.columns,
  () => {
    initColumnsConfig();
  },
  { immediate: true, deep: true },
);

// 序号计算配置
const seqConfig = reactive<any>({
  seqMethod({ rowIndex }: { rowIndex: number }) {
    return ((props.tableQuery.page || 1) - 1) * props.tableQuery.size + rowIndex + 1;
  },
});

// 操作按钮过滤
const getVisibleOptionMenus = (row: any) => {
  return props.optionMenus.filter((m) => m.show === undefined || m.show(row));
};

const getOptionMenuColor = (type?: string) => {
  if (type === 'danger') return 'text-red-500';
  if (type === 'warning') return 'text-amber-500';
  if (type === 'success') return 'text-emerald-500';
  return 'text-blue-500';
};

// 全屏展开与恢复
const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value;
  nextTick(() => {
    updateTableHeight();
    xTable.value?.recalculate();
  });
};

const selectionChange = (records: any[]) => {
  selectionRow.value = records;
  emit('selection-change', records);
};

const radioChange = ({ row }: { row: any }) => {
  emit('radio-change', row);
};

const cellClick = (data: any) => {
  emit('cell-click', data);
};

const editClosed = (data: any) => {
  emit('edit-closed', data);
};

const editActivated = (data: any) => {
  emit('edit-actived', data);
};

const scrollEvent = (data: any) => {
  emit('scroll', data);
};

const rowReset = () => {
  initColumnsConfig();
  xTable.value?.resetColumn();
};

const refreshTable = () => {
  emit('on-refresh');
};

const refreshTableConfig = () => {
  xTable.value?.refreshColumn();
};

const reloadData = (data: any[]) => {
  nextTick(() => {
    xTable.value?.reloadData(data);
  });
};

// 复选框操作 API
const setCheckboxRow = (rows: any[], checked: boolean) => {
  nextTick(() => {
    xTable.value?.setCheckboxRow(rows, checked);
  });
};

const getCheckboxRecords = (isFull = false) => {
  return xTable.value?.getCheckboxRecords(isFull) || [];
};

const clearCheckboxRow = () => {
  nextTick(() => {
    xTable.value?.clearCheckboxRow();
    selectionRow.value = [];
  });
};

const toggleCheckboxRow = (row: any) => {
  nextTick(() => {
    xTable.value?.toggleCheckboxRow(row);
  });
};

const toggleAllCheckboxRow = () => {
  nextTick(() => {
    xTable.value?.toggleAllCheckboxRow();
  });
};

const reverseSelectionCheckboxRow = (isFull = false) => {
  const list = displayList.value || [];
  list.forEach((row: any) => {
    xTable.value?.toggleCheckboxRow(row);
  });
  const select = getCheckboxRecords(isFull);
  selectionChange(select);
};

const setTreeExpand = (rows: any[], checked = true) => {
  xTable.value?.setTreeExpand(rows, checked);
};

const setAllTreeExpand = (status: boolean) => {
  xTable.value?.setAllTreeExpand(status);
};

// 拖拽列位置与固定
const end = async () => {
  user_table_config.value.top_row.forEach((v: any) => {
    v.fixed = 'left';
  });
  user_table_config.value.bottom_row.forEach((v: any) => {
    v.fixed = 'right';
  });
  user_table_config.value.center_row.forEach((v: any) => {
    v.fixed = undefined;
  });
  await xTable.value?.reloadColumn([
    ...user_table_config.value.checkbox_row,
    ...user_table_config.value.top_row,
    ...user_table_config.value.center_row,
    ...user_table_config.value.bottom_row,
  ]);
  xTable.value?.refreshColumn();
};

const resizableChange = (v: any) => {
  const resizeWidth = (name: string, list: any[], size: number) => {
    list.forEach((item: any) => {
      if (name === item.field) {
        item.width = size;
      }
    });
  };
  resizeWidth(v.column.field, user_table_config.value.top_row, v.resizeWidth);
  resizeWidth(v.column.field, user_table_config.value.center_row, v.resizeWidth);
  resizeWidth(v.column.field, user_table_config.value.bottom_row, v.resizeWidth);
};

const onSelChange = async (val: any) => {
  if (val) {
    xTable.value?.reloadColumn([
      ...user_table_config.value.checkbox_row,
      ...user_table_config.value.top_row,
      ...user_table_config.value.center_row,
      ...user_table_config.value.bottom_row,
    ]);
  } else {
    xTable.value?.reloadColumn([
      ...user_table_config.value.checkbox_row,
      ...user_table_config.value.top_row.filter((s: any) => s.type !== 'seq'),
      ...user_table_config.value.center_row,
      ...user_table_config.value.bottom_row,
    ]);
  }
};

// 动态高度与弹性视口计算 (保证大屏与缩放均自适应)
const updateTableHeight = () => {
  if (!mainRef.value) return;
  const windowH = window.innerHeight;
  const rect = mainRef.value.getBoundingClientRect();
  // 视口可用高度 = 屏幕高度 - 容器距离顶部距离 - 底部安全外边距(24px)
  let availableH = windowH - rect.top - 24;
  if (props.isShowHeader && headerRef.value) {
    availableH -= headerRef.value.clientHeight || 0;
  }
  if (props.showPager) {
    availableH -= 56;
  }
  // 扣除卡片自身 padding (20px * 2) 与边框
  availableH -= 44;
  tableHeight.value = availableH > 200 ? availableH : 600;
};

let tableResizeObserver: ResizeObserver | null = null;
onMounted(() => {
  window.addEventListener('resize', updateTableHeight);
  if (typeof ResizeObserver !== 'undefined') {
    tableResizeObserver = new ResizeObserver(() => {
      nextTick(() => {
        updateTableHeight();
      });
    });
    if (headerRef.value) tableResizeObserver.observe(headerRef.value);
    if (mainRef.value) tableResizeObserver.observe(mainRef.value);
  }
  nextTick(() => {
    updateTableHeight();
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateTableHeight);
  if (tableResizeObserver) {
    tableResizeObserver.disconnect();
    tableResizeObserver = null;
  }
});

// 分页同步
const localPage = ref(props.tableQuery.page);
const localSize = ref(props.tableQuery.size);

watch(
  () => props.tableQuery.page,
  (val) => {
    localPage.value = val;
  },
);
watch(
  () => props.tableQuery.size,
  (val) => {
    localSize.value = val;
  },
);

function onLocalPageChange(val: number) {
  emit('current-change', val);
}
function onLocalSizeChange(val: number) {
  emit('size-change', val);
}

// 暴露全部对外方法 (100% 保持兼容，可以多不能少)
defineExpose({
  clearKeywords: () => {},
  getCheckboxRecords,
  getSelectionRows: getCheckboxRecords, // 兼容 el-table 别名
  setCheckboxRow,
  clearCheckboxRow,
  clearSelection: clearCheckboxRow, // 兼容 el-table 别名
  setAllTreeExpand,
  toggleCheckboxRow,
  toggleRowSelection: toggleCheckboxRow, // 兼容 el-table 别名
  toggleAllCheckboxRow,
  reverseSelectionCheckboxRow,
  setTreeExpand,
  reloadData,
  refreshTable,
  refreshTableConfig,
  rowReset,
  toggleFullscreen,
  xTable,
});
</script>
