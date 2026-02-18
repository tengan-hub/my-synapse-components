<script lang="ts" setup>
import { computed, useSlots } from 'vue';
const slots = useSlots();

const props = withDefaults(defineProps<{
  modelValue: any,
}>(), {
  modelValue: ''
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
  <q-input v-model="value" dense label-color="white" color="blue" no-error-icon>
    <slot />

    <template v-if="slots.prepend" #prepend>
      <slot name="prepend" />
    </template>

    <template v-if="slots.append" #append>
      <slot name="append" />
    </template>

    <template v-if="slots.before" #before>
      <slot name="before" />
    </template>
  </q-input>
</template>
