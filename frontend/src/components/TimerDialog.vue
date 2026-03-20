<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('close')"
  >
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-96 space-y-5">
      <h3 class="text-lg font-semibold">Set Timer</h3>

      <div class="flex gap-3">
        <input
          v-model.number="localInput"
          type="number"
          min="1"
          placeholder="Duration"
          class="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <select
          v-model="localUnit"
          class="rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        >
          <option value="seconds">sec</option>
          <option value="minutes">min</option>
        </select>
      </div>

      <div class="flex justify-between gap-3">
        <button
          v-if="timerRemaining !== null"
          @click="handleStop"
          class="rounded-lg border border-red-300 dark:border-red-700 px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
        >Delete Timer</button>
        <div class="flex gap-3 ml-auto">
          <button
            @click="$emit('close')"
            class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >Cancel</button>
          <button
            @click="handleStart"
            :disabled="!localInput || localInput < 1"
            class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >Start</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  open: Boolean,
  timerRemaining: { type: Number, default: null },
})

const emit = defineEmits(['start', 'stop', 'close'])

const localInput = ref(null)
const localUnit = ref('minutes')

function handleStart() {
  if (!localInput.value || localInput.value < 1) return
  const seconds = localUnit.value === 'minutes' ? localInput.value * 60 : localInput.value
  emit('start', seconds)
  emit('close')
}

function handleStop() {
  emit('stop')
  emit('close')
}
</script>
