import { ref, onBeforeUnmount } from 'vue'
import QRCode from 'qrcode'

export function useShare() {
  const copyToast = ref(false)
  let copyToastTimer = null

  const showQR = ref(false)
  const qrDataUrl = ref('')
  let qrHideTimer = null

  async function onShareEnter() {
    clearTimeout(qrHideTimer)
    qrDataUrl.value = await QRCode.toDataURL(window.location.href, { width: 160, margin: 1 })
    showQR.value = true
  }

  function onShareLeave() {
    qrHideTimer = setTimeout(() => { showQR.value = false }, 400)
  }

  function copyInviteLink() {
    navigator.clipboard.writeText(window.location.href)
    if (copyToastTimer) clearTimeout(copyToastTimer)
    copyToast.value = true
    copyToastTimer = setTimeout(() => { copyToast.value = false }, 2000)
  }

  onBeforeUnmount(() => {
    clearTimeout(copyToastTimer)
    clearTimeout(qrHideTimer)
  })

  return { copyToast, showQR, qrDataUrl, onShareEnter, onShareLeave, copyInviteLink }
}
