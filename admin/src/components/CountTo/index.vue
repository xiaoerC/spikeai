<template>
  <span>{{ prefix }}{{ outputValue }}{{ suffix }}</span>
</template>

<script lang="ts" setup>
import { TransitionPresets, useTransition } from '@vueuse/core';
import { computed, onMounted, ref, watch } from 'vue';

interface Props {
  startVal?: number;
  endVal?: number;
  duration?: number;
  decimals?: number;
  decimal?: string;
  separator?: string;
  prefix?: string;
  suffix?: string;
  autoplay?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  startVal: 0,
  endVal: 2024,
  duration: 2000,
  decimals: 0,
  decimal: '.',
  separator: ',',
  prefix: '',
  suffix: '',
  autoplay: true,
});

const source = ref(props.startVal);
const output = useTransition(source, {
  duration: props.duration,
  transition: TransitionPresets.easeOutExpo,
});

const formatNumber = (num: number) => {
  const fixed = num.toFixed(props.decimals);
  const parts = fixed.split('.');
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, props.separator);
  return parts.join(props.decimal);
};

const outputValue = computed(() => formatNumber(output.value));

onMounted(() => {
  if (props.autoplay) {
    source.value = props.endVal;
  }
});

watch(
  () => props.endVal,
  (val) => {
    source.value = val;
  },
);
</script>
