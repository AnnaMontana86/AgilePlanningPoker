// Composable for post-reveal vote statistics.
// Responsible for computing highest/lowest outlier participant IDs,
// the numeric average, the most popular vote, and a compact estimate
// frequency map for the topic list.
import { computed } from 'vue'

export function useVoteAnalysis(roomStore) {
  const voteExtremes = computed(() => {
    if (!roomStore.isRevealed) return { highest: new Set(), lowest: new Set() }
    const numeric = roomStore.participants
      .map(p => ({ id: p.id, n: parseFloat(p.vote) }))
      .filter(p => !isNaN(p.n))
    if (numeric.length < 2) return { highest: new Set(), lowest: new Set() }
    const max = Math.max(...numeric.map(p => p.n))
    const min = Math.min(...numeric.map(p => p.n))
    if (max === min) return { highest: new Set(), lowest: new Set() }
    return {
      highest: new Set(numeric.filter(p => p.n === max).map(p => p.id)),
      lowest:  new Set(numeric.filter(p => p.n === min).map(p => p.id)),
    }
  })

  const numericAverage = computed(() => {
    if (!roomStore.isRevealed) return null
    const nums = roomStore.participants
      .map(p => parseFloat(p.vote))
      .filter(n => !isNaN(n))
    if (!nums.length) return null
    return (nums.reduce((a, b) => a + b, 0) / nums.length).toFixed(1)
  })

  const mostPopularVote = computed(() => {
    if (!roomStore.isRevealed) return null
    const votes = roomStore.participants.map(p => p.vote).filter(v => v != null)
    if (!votes.length) return null
    const counts = {}
    for (const v of votes) counts[v] = (counts[v] ?? 0) + 1
    const max = Math.max(...Object.values(counts))
    if (max < 2) return null
    const winners = Object.keys(counts).filter(v => counts[v] === max)
    return winners.join(' / ')
  })

  // Groups identical estimate values so the topic list shows "5 (3x)" instead of "5, 5, 5".
  function compactEstimates(estimates) {
    const counts = {}
    for (const e of estimates) counts[e] = (counts[e] ?? 0) + 1
    return Object.entries(counts).map(([value, count]) => ({ value, count, label: value }))
  }

  return { voteExtremes, numericAverage, mostPopularVote, compactEstimates }
}
