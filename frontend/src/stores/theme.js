// Pinia store for the UI colour scheme.
// Responsible for tracking and persisting the light/dark mode preference
// to localStorage and exposing a toggle action.
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(localStorage.getItem('theme') === 'dark')

  // Keep <html> in sync so teleported elements (Teleport to="body") also
  // receive the .dark ancestor and Tailwind dark: variants work correctly.
  document.documentElement.classList.toggle('dark', isDark.value)

  function toggle() {
    isDark.value = !isDark.value
    localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
    document.documentElement.classList.toggle('dark', isDark.value)
  }

  return { isDark, toggle }
})
