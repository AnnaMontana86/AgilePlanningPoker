import { ref } from 'vue'

export function useTopics(roomId, roomStore, apiFetch, error) {
  const showAddTopic = ref(false)
  const newTopicName = ref('')
  const newTopicLink = ref('')
  const editingTopic = ref(null)
  const editTopicName = ref('')
  const editTopicLink = ref('')

  async function addTopic() {
    if (!newTopicName.value.trim()) return
    try {
      await apiFetch(`/api/rooms/${roomId}/topics`, 'POST', {
        short_name: newTopicName.value.trim(),
        link: newTopicLink.value.trim(),
      })
      newTopicName.value = ''
      newTopicLink.value = ''
      showAddTopic.value = false
    } catch (e) { error.value = e.message }
  }

  async function moveTopic(idx, dir) {
    const topics = [...roomStore.topics]
    const newIdx = idx + dir
    if (newIdx < 0 || newIdx >= topics.length) return
    ;[topics[idx], topics[newIdx]] = [topics[newIdx], topics[idx]]
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
      if (!roomStore.isRevealed) roomStore.applyEvent({ type: 'votes_reset', data: {} })
    } catch (e) { error.value = e.message }
  }

  function openEditTopic(topic) {
    editingTopic.value = topic
    editTopicName.value = topic.short_name
    editTopicLink.value = topic.link
  }

  async function saveEditTopic() {
    if (!editTopicName.value.trim() || !editingTopic.value) return
    try {
      await apiFetch(`/api/rooms/${roomId}/topics/${editingTopic.value.id}`, 'PATCH', {
        short_name: editTopicName.value.trim(),
        link: editTopicLink.value.trim(),
      })
      editingTopic.value = null
      if (!roomStore.isRevealed) roomStore.applyEvent({ type: 'votes_reset', data: {} })
    } catch (e) { error.value = e.message }
  }

  return {
    showAddTopic, newTopicName, newTopicLink,
    editingTopic, editTopicName, editTopicLink,
    addTopic, moveTopic, deleteTopic, selectTopic,
    openEditTopic, saveEditTopic,
  }
}
