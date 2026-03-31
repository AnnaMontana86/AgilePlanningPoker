// Composable for topic CRUD and selection within a room.
// Responsible for managing add/edit form state and sending topic create,
// reorder, delete, select, and patch requests to the API.
import { ref } from 'vue'

function isValidLink(link) {
  if (!link) return true
  try {
    const url = new URL(link)
    return url.protocol === 'http:' || url.protocol === 'https:'
  } catch {
    return false
  }
}

export function useTopics(roomId, roomStore, apiFetch, error) {
  const showAddTopic = ref(false)
  const newTopicKey = ref('')
  const newTopicHeadline = ref('')
  const newTopicLink = ref('')
  const newTopicLinkError = ref('')
  const editingTopic = ref(null)

  async function addTopic() {
    if (!newTopicKey.value.trim() || !newTopicHeadline.value.trim()) return
    const link = newTopicLink.value.trim()
    if (!isValidLink(link)) {
      newTopicLinkError.value = 'Please enter a valid URL (must start with http:// or https://).'
      return
    }
    newTopicLinkError.value = ''
    try {
      await apiFetch(`/api/rooms/${roomId}/topics`, 'POST', {
        key: newTopicKey.value.trim(),
        headline: newTopicHeadline.value.trim(),
        link,
      })
      newTopicKey.value = ''
      newTopicHeadline.value = ''
      newTopicLink.value = ''
      showAddTopic.value = false
    } catch (e) { error.value = e.message }
  }

  async function reorderTopics(fromIdx, toIdx) {
    if (fromIdx === toIdx) return
    const topics = [...roomStore.topics]
    const [moved] = topics.splice(fromIdx, 1)
    topics.splice(toIdx, 0, moved)
    try {
      await apiFetch(`/api/rooms/${roomId}/topics`, 'PUT', {
        topic_ids: topics.map(t => t.id),
      })
    } catch (e) { error.value = e.message }
  }

  async function deleteTopic(topicId) {
    try {
      await apiFetch(`/api/rooms/${roomId}/topics/${topicId}`, 'DELETE')
    } catch (e) { error.value = e.message }
  }

  async function selectTopic(topicId) {
    try {
      await apiFetch(`/api/rooms/${roomId}/topics/${topicId}/select`)
    } catch (e) { error.value = e.message }
  }

  function openEditTopic(topic) {
    editingTopic.value = topic
  }

  async function saveEditTopic(topicId, { key, headline, link }) {
    try {
      await apiFetch(`/api/rooms/${roomId}/topics/${topicId}`, 'PATCH', {
        key: key.trim(),
        headline: headline.trim(),
        link: link?.trim() ?? '',
      })
      editingTopic.value = null
    } catch (e) { error.value = e.message }
  }

  return {
    showAddTopic, newTopicKey, newTopicHeadline, newTopicLink, newTopicLinkError, editingTopic,
    addTopic, reorderTopics, deleteTopic, selectTopic,
    openEditTopic, saveEditTopic,
  }
}
