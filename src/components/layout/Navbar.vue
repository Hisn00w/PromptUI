<template>
  <nav class="navbar glass">
    <div class="navbar-container">
      <router-link to="/" class="logo">
        <img src="/logo.svg" alt="PromptUI" class="logo-icon" />
        <div class="logo-text-group">
          <span class="logo-text">PromptUI</span>
          <span class="logo-sub">{{ t('nav.premiumLibrary') }}</span>
        </div>
      </router-link>

      <div class="nav-links">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="nav-link" :class="{ active: $route.path === item.path }">
          {{ item.label }}
        </router-link>
      </div>

      <div class="nav-actions">
        <router-link to="/prompt/new" class="create-btn">
          {{ t('common.createPrompt') }}
        </router-link>

        <div class="search-wrapper">
          <svg class="search-icon" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clip-rule="evenodd"/>
          </svg>
          <input type="text" :placeholder="t('common.search')" class="search-input" />
        </div>

        <button class="action-btn" @click="toggleLocale" :title="locale === 'zh' ? t('common.switchToEnglish') : t('common.switchToChinese')">
          <span class="locale-text">{{ locale === 'zh' ? 'EN' : 'ZH' }}</span>
        </button>

        <button class="action-btn" @click="themeStore.toggleTheme" :title="themeStore.isDark ? t('common.lightMode') : t('common.darkMode')">
          <svg v-if="themeStore.isDark" viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"/></svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor" width="18" height="18"><path d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"/></svg>
        </button>

        <!-- auth state -->
        <template v-if="authStore.isAuthenticated">
          <div class="user-menu">
            <button class="user-avatar" @click="isUserMenuOpen = !isUserMenuOpen">
              {{ authStore.user?.username?.charAt(0).toUpperCase() }}
            </button>
            <div v-if="isUserMenuOpen" class="user-dropdown">
              <div class="user-info">
                <p class="user-name">{{ authStore.user?.username }}</p>
                <p class="user-email">{{ authStore.user?.email }}</p>
                <p v-if="authStore.user?.role === 'admin'" class="user-role">{{ t('common.admin') }}</p>
              </div>
              <div class="divider"></div>
              <router-link 
                v-if="authStore.user?.role === 'admin'" 
                to="/admin" 
                class="dropdown-item"
                @click="isUserMenuOpen = false"
              >
                {{ t('common.adminConsole') }}
              </router-link>
              <div v-if="authStore.user?.role === 'admin'" class="divider"></div>
              <button @click="handleLogout" class="dropdown-item logout-red">{{ t('common.logout') }}</button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="login-btn">
            {{ t('common.login') }}
          </router-link>
        </template>

        <button class="action-btn mobile-menu-btn" @click="isMobileMenuOpen = !isMobileMenuOpen" :aria-expanded="String(isMobileMenuOpen)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="20" height="20">
            <path v-if="!isMobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    </div>

    <transition name="slide">
      <div v-if="isMobileMenuOpen" class="mobile-menu">
        <router-link to="/prompt/new" class="mobile-nav-link mobile-create-link" @click="isMobileMenuOpen = false">
          {{ t('common.createPrompt') }}
        </router-link>
        <router-link v-for="item in navItems" :key="item.path" :to="item.path" class="mobile-nav-link" @click="isMobileMenuOpen = false">
          {{ item.label }}
        </router-link>
      </div>
    </transition>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useThemeStore } from '@/stores/theme'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const { t, locale } = useI18n()
const themeStore = useThemeStore()
const authStore = useAuthStore()
const router = useRouter()

const isMobileMenuOpen = ref(false)
const isUserMenuOpen = ref(false)

const navItems = computed(() => [
  { path: '/', label: t('nav.library') },
  { path: '/layouts', label: t('nav.layouts') },
  { path: '/cards', label: t('nav.cards') },
  { path: '/components', label: t('nav.components') },
  { path: '/animations', label: t('nav.animations') },
  { path: '/colors', label: t('nav.colors') }
])

const toggleLocale = () => {
  locale.value = locale.value === 'zh' ? 'en' : 'zh'
  localStorage.setItem('locale', locale.value)
}

const handleLogout = () => {
  authStore.logout()
  isUserMenuOpen.value = false
  router.push('/')
}
</script>

<style scoped>
.navbar { position: fixed; inset: 0 0 auto; height: var(--navbar-height); z-index: 1000; border-bottom: 1px solid var(--border-color); }
.navbar-container { max-width: var(--max-content-width); margin: 0 auto; height: 100%; display: flex; align-items: center; justify-content: space-between; gap: var(--spacing-md); padding: 0 var(--spacing-lg); }
.logo { display: flex; align-items: center; gap: 0.7rem; min-width: 220px; }
.logo-icon { width: 30px; height: 30px; border-radius: 8px; object-fit: cover; box-shadow: 0 6px 14px rgba(0,0,0,0.25); }
.logo-text-group { display: flex; flex-direction: column; line-height: 1.1; }
.logo-text { font-size: 0.96rem; font-weight: 700; color: var(--text-primary); }
.logo-sub { font-size: 0.62rem; letter-spacing: 0.03em; color: var(--text-tertiary); }

.nav-links { display: flex; align-items: center; justify-content: center; gap: 0.3rem; padding: 0.26rem; border-radius: var(--radius-full); background: color-mix(in srgb, var(--bg-tertiary) 70%, transparent); border: 1px solid var(--border-color); flex: 1; min-width: 0; }
.nav-links { flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; }
.nav-links::-webkit-scrollbar { display: none; }
.nav-link { display: inline-flex; align-items: center; justify-content: center; min-height: 34px; padding: 0.38rem 0.82rem; font-size: var(--font-size-sm); color: var(--text-secondary); border-radius: var(--radius-full); font-weight: 600; transition: all var(--transition-fast); white-space: nowrap; word-break: keep-all; flex-shrink: 0; line-height: 1.15; }
.nav-link:hover { color: var(--text-primary); background: color-mix(in srgb, var(--bg-primary) 82%, transparent); }
.nav-link.active { color: var(--text-inverse); background: linear-gradient(180deg, #1a1a1a 0%, #000000 100%); box-shadow: 0 6px 12px rgba(0,0,0,0.25); }

.nav-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  min-width: fit-content;
}
.create-btn {
  height: 32px;
  display: inline-flex;
  align-items: center;
  padding: 0 12px;
  border-radius: 10px;
  background: linear-gradient(180deg,#1a1a1a,#000000);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .01em;
  border: 1px solid #0f0f0f;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  white-space: nowrap;
}
.create-btn:hover { filter: brightness(1.04); transform: translateY(-1px); }
.search-wrapper {
  position: relative;
  flex-shrink: 1;
}
.search-icon { position: absolute; left: 10px; top: 50%; transform: translateY(-50%); color: var(--text-tertiary); width: 15px; height: 15px; }
.search-input { width: 180px; padding: 7px 10px 7px 30px; border-radius: 10px; border: 1px solid var(--border-color); background: color-mix(in srgb, var(--bg-primary) 86%, transparent); color: var(--text-primary); outline: none; transition: all var(--transition-fast); }
.search-input:focus { width: 220px; border-color: color-mix(in srgb, var(--color-primary) 65%, var(--border-color)); box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 18%, transparent); }
.action-btn { width: 32px; height: 32px; display: grid; place-items: center; border-radius: 10px; border: 1px solid var(--border-color); background: color-mix(in srgb, var(--bg-primary) 82%, transparent); color: var(--text-secondary); transition: all var(--transition-fast); }
.action-btn:hover { color: var(--text-primary); border-color: var(--border-color-strong); }
.locale-text { font-weight: 700; font-size: 0.72rem; }
.mobile-menu-btn { display: none; }

.mobile-menu { position: absolute; top: calc(100% + 8px); left: var(--spacing-md); right: var(--spacing-md); background: var(--bg-elevated); border: 1px solid var(--border-color); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); padding: var(--spacing-sm); }
.mobile-nav-link { display: block; padding: 0.7rem 0.85rem; color: var(--text-secondary); border-radius: var(--radius-md); font-weight: 600; }
.mobile-nav-link:hover { color: var(--text-primary); background: color-mix(in srgb, var(--bg-tertiary) 68%, transparent); }
.mobile-create-link { background: linear-gradient(180deg,#1a1a1a,#000000); color: #fff; margin-bottom: 6px; }
.login-btn { 
  height: 36px; 
  display: inline-flex; 
  align-items: center; 
  padding: 0 16px; 
  border-radius: 10px; 
  background: var(--bg-tertiary); 
  color: var(--text-primary); 
  font-size: 13px; 
  font-weight: 700; 
  border: 1px solid var(--border-color);
  transition: all var(--transition-fast);
  flex-shrink: 0;
  white-space: nowrap;
}
.login-btn:hover { background: var(--bg-elevated); border-color: var(--border-color-strong); }

.user-menu { position: relative; }
.user-avatar { 
  width: 36px; height: 36px; border-radius: 50%; 
  background: linear-gradient(180deg, #2a2a2a, #0f0f0f); 
  color: white; font-weight: 700; border: none; cursor: pointer; display: grid; place-items: center; 
}
.user-dropdown { 
  position: absolute; top: calc(100% + 10px); right: 0; width: 220px; 
  background: var(--bg-elevated); border: 1px solid var(--border-color); 
  border-radius: 12px; box-shadow: var(--shadow-lg); padding: 8px; z-index: 1001; 
}
.user-info { padding: 8px 12px; }
.user-name { font-weight: 700; color: var(--text-primary); margin: 0; font-size: 14px; }
.user-email { font-size: 12px; color: var(--text-tertiary); margin: 2px 0 0 0; }
.user-role { 
  display: inline-block; 
  font-size: 11px; 
  color: #000; 
  background: #fff; 
  padding: 2px 8px; 
  border-radius: 4px; 
  margin: 6px 0 0 0; 
  font-weight: 600; 
}
.divider { height: 1px; background: var(--border-color); margin: 8px 0; }
.dropdown-item { 
  width: 100%; text-align: left; padding: 10px 12px; border-radius: 8px; border: none; 
  background: transparent; color: var(--text-secondary); font-size: 13px; font-weight: 600; cursor: pointer; 
  display: block; text-decoration: none;
}
.dropdown-item:hover { background: var(--bg-tertiary); color: var(--text-primary); }
.logout-red { color: #ef4444; }

@media (max-width: 1024px) {
  .search-wrapper, .logo-sub, .create-btn { display: none; }
  .logo { min-width: auto; }
}

@media (max-width: 768px) {
  .navbar-container { padding: 0 var(--spacing-md); }
  .nav-links, .create-btn, .login-btn { display: none; }
  .mobile-menu-btn { display: grid; }
}
</style>
