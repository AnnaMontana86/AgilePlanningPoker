// Composable for the unanimous-vote fireworks celebration animation.
// Responsible for watching for consensus after reveal and running a
// canvas particle burst animation for a fixed duration.
import { ref, computed, watch, onBeforeUnmount, nextTick } from 'vue'

export function useFireworks(roomStore) {
  const fireworksCanvas = ref(null)
  const fireworksActive = ref(false)
  let fireworksRaf = null

  const allSameVote = computed(() => {
    if (!roomStore.isRevealed) return false
    const votes = roomStore.participants.map(p => p.vote).filter(v => v != null)
    return votes.length >= 2 && votes.every(v => v === votes[0])
  })

  watch(allSameVote, (same) => {
    if (same) nextTick(launchFireworks)
  })

  function launchFireworks() {
    fireworksActive.value = true
    const canvas = fireworksCanvas.value
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
    const ctx = canvas.getContext('2d')
    const particles = []
    const COLORS = ['#ff4444','#ff8800','#ffdd00','#44ff44','#44aaff','#aa44ff','#ff44aa','#ffffff']
    const DURATION = 4000
    const start = performance.now()

    function spawnBurst() {
      const x = 0.2 * canvas.width + Math.random() * 0.6 * canvas.width
      const y = 0.1 * canvas.height + Math.random() * 0.45 * canvas.height
      const color = COLORS[Math.floor(Math.random() * COLORS.length)]
      const count = 80 + Math.floor(Math.random() * 40)
      for (let i = 0; i < count; i++) {
        const angle = (Math.PI * 2 * i) / count + (Math.random() - 0.5) * 0.3
        const speed = 2 + Math.random() * 5
        particles.push({
          x, y,
          vx: Math.cos(angle) * speed,
          vy: Math.sin(angle) * speed,
          alpha: 1,
          color,
          radius: 2 + Math.random() * 2,
        })
      }
    }

    let lastBurst = 0
    function frame(now) {
      const elapsed = now - start
      if (elapsed > DURATION) {
        ctx.clearRect(0, 0, canvas.width, canvas.height)
        fireworksActive.value = false
        return
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height)

      if (now - lastBurst > 600) {
        spawnBurst()
        lastBurst = now
      }

      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i]
        // Apply gravity, air resistance, and fade to each particle each frame.
        p.x += p.vx
        p.y += p.vy
        p.vy += 0.08
        p.vx *= 0.98
        p.alpha -= 0.013
        if (p.alpha <= 0) { particles.splice(i, 1); continue }
        ctx.globalAlpha = p.alpha
        ctx.fillStyle = p.color
        ctx.beginPath()
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
        ctx.fill()
      }
      ctx.globalAlpha = 1
      fireworksRaf = requestAnimationFrame(frame)
    }

    spawnBurst()
    fireworksRaf = requestAnimationFrame(frame)
  }

  onBeforeUnmount(() => {
    cancelAnimationFrame(fireworksRaf)
  })

  return { fireworksCanvas, fireworksActive }
}
