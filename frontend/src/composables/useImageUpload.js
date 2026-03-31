// Composable for drag-and-drop image upload in the note editor.
// Responsible for compressing dropped image files client-side to ≤ 500 KB,
// uploading them to the backend, and returning the served image URL.
import { ref } from 'vue'
import imageCompression from 'browser-image-compression'

const COMPRESSION_OPTIONS = {
  maxSizeMB: 0.5,
  maxWidthOrHeight: 1920,
  useWebWorker: true,
}

export function useImageUpload(roomId, apiFetch, error) {
  const uploading = ref(false)

  async function uploadImage(file) {
    if (!file.type.startsWith('image/')) {
      error.value = 'Only image files can be dropped here.'
      return null
    }
    uploading.value = true
    try {
      const compressed = await imageCompression(file, COMPRESSION_OPTIONS)
      const dataUrl = await imageCompression.getDataUrlFromFile(compressed)
      const result = await apiFetch(`/api/rooms/${roomId}/images`, 'POST', { data_url: dataUrl })
      return `/api/rooms/${roomId}/images/${result.image_id}`
    } catch (e) {
      error.value = e.message
      return null
    } finally {
      uploading.value = false
    }
  }

  return { uploading, uploadImage }
}
