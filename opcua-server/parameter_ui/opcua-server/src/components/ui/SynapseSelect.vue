<script lang="ts" setup>
import { computed, useSlots } from 'vue';

const slots = useSlots();

const props = withDefaults(defineProps<{
  modelValue: any,
  useChips?: boolean
}>(), {
  modelValue: '',
  useChips: false
});

const value = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    if (props.modelValue !== newValue) {
      emit('update:modelValue', newValue);
    }
  }
});

// eslint-disable-next-line func-call-spacing
const emit = defineEmits<{
  (e: 'update:modelValue', newValue: any): void,
}>();

</script>

<template>
  <q-select
    v-model="value" map-options emit-value dense options-dense :use-chips="useChips"
    label-color="white" color="blue" style="white-space: nowrap;" no-error-icon
  >
    <template v-if="slots.after" #after>
      <slot name="after" />
    </template>
    <template v-if="slots.option" #option="{ itemProps, opt, selected, toggleOption }">
      <slot
        name="option" :item-props="itemProps" :opt="opt" :selected="selected" :toggle-option="toggleOption"
      />
    </template>
    <template v-if="!useChips" #selected-item="scope">
      <slot v-if="slots.selectedItem" name="selectedItem" :opt="scope.opt" />
      <span v-else class="ellipsis">{{ scope.opt.label ?? scope.opt }}</span>
    </template>
  </q-select>
</template>
