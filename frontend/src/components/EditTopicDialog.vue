<template>
  <div
    v-if="topic"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('cancel')"
  >
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-96 space-y-4">
      <h3 class="text-lg font-semibold">Edit Topic</h3>
      <div class="space-y-3">
        <input
          v-model="draftName"
          placeholder="Short name"
          @keydown.enter="save"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <input
          v-model="draftLink"
          placeholder="Link (optional)"
          @keydown.enter="save"
          class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>
      <div class="flex justify-end gap-3">
        <button
          @click="$emit('cancel')"
          class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >Cancel</button>
        <button
          @click="save"
          :disabled="!draftName.trim()"
          class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >Save</button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Modal dialog for editing a topic's short name and optional link.
// Responsible for initialising draft fields from the topic prop and
// emitting a save event with trimmed values on confirm.
import { ref, watch } from 'vue'

const props = defineProps({
  topic: { type: Object, default: null },
})

const emit = defineEmits(['save', 'cancel'])

const draftName = ref('')
const draftLink = ref('')

watch(() => props.topic, (t) => {
  if (t) {
    draftName.value = t.short_name
    draftLink.value = t.link ?? ''
  }
}, { immediate: true })

function save() {
  if (!draftName.value.trim()) return
  emit('save', { short_name: draftName.value.trim(), link: draftLink.value.trim() })
}
</script>
