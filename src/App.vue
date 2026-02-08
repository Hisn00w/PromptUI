<template>
  <div id="app-root">
    <Navbar />
    <main class="main-content">
      <router-view v-slot="{ Component }"><component :is="Component" /></router-view>
    </main>
    <footer class="footer">
      <div class="container footer-content">
        <p>© 2026 PromptUI · Open source on <a href="https://github.com/Hisn00w/PromptUI" target="_blank" class="github-footer-link">GitHub</a></p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useThemeStore } from './stores/theme'
import { useAuthStore } from './stores/auth'
import Navbar from './components/layout/Navbar.vue'

const themeStore = useThemeStore()
const authStore = useAuthStore()

onMounted(() => {
  themeStore.initTheme()
  authStore.fetchUser()
})
</script>

<style scoped>
#app-root { min-height: 100vh; display: flex; flex-direction: column; }
.main-content { flex: 1; padding-top: var(--navbar-height); }
.footer { padding: 1.2rem 0 1.6rem; border-top: 1px solid var(--border-color); background: color-mix(in srgb, var(--bg-primary) 86%, transparent); }
.footer-content { text-align: center; }
.footer-content p { font-size: 0.82rem; color: var(--text-tertiary); }
.github-footer-link { color: var(--color-primary); font-weight: 600; }
</style>
