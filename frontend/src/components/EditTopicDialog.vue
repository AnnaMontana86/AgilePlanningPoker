<template>
  <div
    v-if="topic"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click.self="$emit('cancel')"
  >
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 w-[32rem] space-y-4">
      <h3 class="text-lg font-semibold">Edit Topic</h3>
      <div class="space-y-3">
        <div class="flex gap-2">
          <input
            v-model="draftKey"
            placeholder="Key"
            @keydown.enter="save"
            class="w-28 shrink-0 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <input
            v-model="draftHeadline"
            placeholder="Headline"
            @keydown.enter="save"
            class="flex-1 min-w-0 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div class="space-y-1">
          <input
            v-model="draftLink"
            placeholder="Link (optional)"
            @keydown.enter="save"
            @input="linkError = ''"
            :class="[
              'w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-2 bg-white dark:bg-gray-700',
              linkError
                ? 'border-red-400 focus:ring-red-400'
                : 'border-gray-300 dark:border-gray-600 focus:ring-indigo-500',
            ]"
          />
          <p v-if="linkError" class="text-xs text-red-500">{{ linkError }}</p>
        </div>
      </div>
      <div class="flex justify-end gap-3">
        <button
          @click="$emit('cancel')"
          class="rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >Cancel</button>
        <button
          @click="save"
          :disabled="!draftKey.trim() || !draftHeadline.trim()"
          class="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >Save</button>
      </div>
    </div>
  </div>
</template>

<script setup>
// Modal dialog for editing a topic's key, headline, and optional link.
// Responsible for initialising draft fields from the topic prop and
// emitting a save event with trimmed values on confirm.
import { ref, watch } from 'vue'

const props = defineProps({
  topic: { type: Object, default: null },
})

const emit = defineEmits(['save', 'cancel'])

const draftKey = ref('')
const draftHeadline = ref('')
const draftLink = ref('')
const linkError = ref('')

watch(() => props.topic, (t) => {
  if (t) {
    draftKey.value = t.key
    draftHeadline.value = t.headline
    draftLink.value = t.link ?? ''
    linkError.value = ''
  }
}, { immediate: true })

function isValidLink(link) {
  if (!link) return true
  try {
    const url = new URL(link)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

function save() {
  if (!draftKey.value.trim() || !draftHeadline.value.trim()) return
  const link = draftLink.value.trim()
  if (!isValidLink(link)) {
    linkError.value = 'Please enter a valid URL (must start with http:// or https://).'
    return
  }
  linkError.value = ''
  emit('save', { key: draftKey.value.trim(), headline: draftHeadline.value.trim(), link })
}
</script>
