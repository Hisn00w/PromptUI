<template>
  <div class="login-page">
    <div class="grain" aria-hidden="true"></div>
    <div class="login-shell">
      <div class="login-card">
        <div class="login-header">
          <div class="brand">
            <img src="/logo.svg" alt="PromptUI" class="brand-icon" />
            <div>
              <p class="brand-name">PromptUI</p>
              <p class="brand-sub">Secure Access</p>
            </div>
          </div>
          <h1>{{ isRegister ? text.registerTitle : text.loginTitle }}</h1>
          <p class="subtitle">{{ isRegister ? text.registerSubtitle : text.loginSubtitle }}</p>
        </div>

        <form @submit.prevent="handleSubmit" class="login-form">
          <div class="field">
            <label>{{ isRegister ? text.username : text.account }}</label>
            <input
              v-model="form.username"
              type="text"
              :placeholder="isRegister ? text.usernamePlaceholder : text.accountPlaceholder"
              required
              minlength="3"
            />
          </div>

          <div v-if="isRegister" class="field">
            <label>{{ text.email }}</label>
            <input
              v-model="form.email"
              type="email"
              :placeholder="text.emailPlaceholder"
            />
          </div>

          <div class="field">
            <label>{{ text.password }}</label>
            <input
              v-model="form.password"
              type="password"
              :placeholder="text.passwordPlaceholder"
              required
              minlength="6"
            />
          </div>

          <div v-if="isRegister" class="field">
            <label>{{ text.confirmPassword }}</label>
            <input
              v-model="form.confirmPassword"
              type="password"
              :placeholder="text.confirmPasswordPlaceholder"
              required
            />
          </div>

          <p v-if="error" class="error-message">{{ error }}</p>

          <button type="submit" class="submit-btn" :disabled="isLoading">
            {{ isLoading ? text.processing : (isRegister ? text.registerAction : text.loginAction) }}
          </button>
        </form>

        <div class="switch-mode">
          <span>{{ isRegister ? text.hasAccount : text.noAccount }}</span>
          <button type="button" @click="isRegister = !isRegister" class="switch-btn">
            {{ isRegister ? text.switchToLogin : text.switchToRegister }}
          </button>
        </div>

        <button class="back-btn" @click="router.push('/')">{{ text.backHome }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import { authAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const { locale } = useI18n()
const authStore = useAuthStore()

const isRegister = ref(false)
const isLoading = ref(false)
const error = ref('')
const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const text = computed(() => {
  const zh = locale.value === 'zh'
  return zh
    ? {
        loginTitle: '登录',
        registerTitle: '创建账号',
        loginSubtitle: '使用你的账号进入 PromptUI',
        registerSubtitle: '创建普通用户账号',
        username: '用户名',
        account: '账号',
        usernamePlaceholder: '请输入用户名',
        accountPlaceholder: '请输入用户名或邮箱',
        email: '邮箱',
        emailPlaceholder: '选填：请输入邮箱地址',
        password: '密码',
        passwordPlaceholder: '请输入密码（至少 6 位）',
        confirmPassword: '确认密码',
        confirmPasswordPlaceholder: '请再次输入密码',
        processing: '处理中...',
        registerAction: '注册',
        loginAction: '登录',
        hasAccount: '已有账号？',
        noAccount: '没有账号？',
        switchToLogin: '立即登录',
        switchToRegister: '立即注册',
        backHome: '返回首页',
        passwordMismatch: '两次输入的密码不一致',
        passwordTooShort: '密码至少需要 6 位',
        requestFailed: '操作失败，请重试'
      }
    : {
        loginTitle: 'Sign In',
        registerTitle: 'Create Account',
        loginSubtitle: 'Sign in to access PromptUI',
        registerSubtitle: 'Create a regular user account',
        username: 'Username',
        account: 'Account',
        usernamePlaceholder: 'Enter your username',
        accountPlaceholder: 'Enter username or email',
        email: 'Email',
        emailPlaceholder: 'Optional: enter your email',
        password: 'Password',
        passwordPlaceholder: 'Enter password (min 6 chars)',
        confirmPassword: 'Confirm Password',
        confirmPasswordPlaceholder: 'Re-enter password',
        processing: 'Processing...',
        registerAction: 'Register',
        loginAction: 'Sign In',
        hasAccount: 'Already have an account?',
        noAccount: "Don't have an account?",
        switchToLogin: 'Sign in now',
        switchToRegister: 'Register now',
        backHome: 'Back to Home',
        passwordMismatch: 'Passwords do not match',
        passwordTooShort: 'Password must be at least 6 characters',
        requestFailed: 'Request failed, please try again'
      }
})

onMounted(async () => {
  try {
    const status = await authAPI.status()
    if (status?.needs_admin_setup) {
      router.replace('/admin-setup')
    }
  } catch (err) {
    console.warn('Auth status check failed on login page:', err?.message || err)
    router.replace('/admin-setup')
  }
})

const handleSubmit = async () => {
  error.value = ''

  if (isRegister.value) {
    if (form.value.password !== form.value.confirmPassword) {
      error.value = text.value.passwordMismatch
      return
    }
    if (form.value.password.length < 6) {
      error.value = text.value.passwordTooShort
      return
    }
  }

  isLoading.value = true
  try {
    const response = isRegister.value
      ? await authAPI.register({
          username: form.value.username,
          email: form.value.email,
          password: form.value.password
        })
      : await authAPI.login({
          username: form.value.username,
          password: form.value.password
        })

    localStorage.setItem('access_token', response.tokens.access_token)
    localStorage.setItem('refresh_token', response.tokens.refresh_token)
    await authStore.fetchUser()

    const redirect = String(route.query.redirect || '/')
    const safeRedirect = redirect.startsWith('/') ? redirect : '/'
    router.push(safeRedirect)
  } catch (err) {
    console.error('Auth failed:', err)
    error.value = err.response?.data?.detail || text.value.requestFailed
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  position: relative;
  display: grid;
  place-items: center;
  padding: 24px;
  color-scheme: light;
  background:
    radial-gradient(1200px 420px at 10% -10%, color-mix(in srgb, var(--color-primary) 8%, transparent), transparent 60%),
    radial-gradient(1000px 420px at 95% 120%, color-mix(in srgb, var(--color-primary) 6%, transparent), transparent 55%),
    var(--bg-secondary);
}

.grain {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0.14;
  background-image: radial-gradient(rgba(255, 255, 255, 0.26) 0.7px, transparent 0.7px);
  background-size: 3px 3px;
}

.login-shell {
  position: relative;
  width: 100%;
  max-width: 460px;
}

.login-card {
  border-radius: 20px;
  padding: 34px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color-strong);
  box-shadow: var(--shadow-lg);
}

.login-header {
  margin-bottom: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.brand-icon {
  width: 42px;
  height: 42px;
  border-radius: 10px;
  object-fit: cover;
  border: 1px solid var(--border-color);
}

.brand-name {
  margin: 0;
  color: var(--text-primary);
  font-size: 22px;
  font-weight: 750;
}

.brand-sub {
  margin: 2px 0 0;
  color: var(--text-tertiary);
  font-size: 12px;
}

.login-header h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 740;
}

.subtitle {
  margin: 8px 0 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.login-form {
  display: grid;
  gap: 16px;
}

.field {
  display: grid;
  gap: 8px;
}

.field label {
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 620;
}

.field input {
  width: 100%;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-primary);
  padding: 12px 14px;
  font-size: 15px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.field input::placeholder {
  color: var(--text-tertiary);
}

.field input:focus {
  outline: none;
  border-color: var(--border-color-strong);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-primary) 12%, transparent);
}

.error-message {
  margin: 0;
  color: var(--color-danger);
  font-size: 13px;
}

.submit-btn {
  margin-top: 4px;
  border: 1px solid #0f0f0f;
  border-radius: 12px;
  background: linear-gradient(180deg, #1a1a1a, #000000);
  color: #ffffff;
  font-size: 15px;
  font-weight: 700;
  padding: 12px 16px;
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  filter: brightness(1.08);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.38);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.switch-mode {
  margin-top: 18px;
  text-align: center;
  font-size: 13px;
  color: var(--text-tertiary);
}

.switch-btn {
  margin-left: 6px;
  background: none;
  border: none;
  color: var(--text-primary);
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.back-btn {
  width: 100%;
  margin-top: 12px;
  padding: 10px;
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  border-radius: 10px;
  cursor: pointer;
}

.back-btn:hover {
  color: var(--text-primary);
  border-color: var(--border-color-strong);
}

[data-theme='dark'] .login-page {
  color-scheme: dark;
  background:
    radial-gradient(1200px 420px at 10% -10%, color-mix(in srgb, #ffffff 10%, transparent), transparent 62%),
    radial-gradient(1000px 420px at 95% 120%, color-mix(in srgb, #ffffff 8%, transparent), transparent 57%),
    var(--bg-secondary);
}

[data-theme='dark'] .grain {
  opacity: 0.08;
  background-image: radial-gradient(rgba(255, 255, 255, 0.14) 0.7px, transparent 0.7px);
}

[data-theme='dark'] .login-card {
  background: color-mix(in srgb, var(--bg-elevated) 86%, #000000 14%);
  border-color: color-mix(in srgb, var(--border-color) 85%, #ffffff 15%);
  box-shadow: 0 26px 56px rgba(0, 0, 0, 0.65);
}

[data-theme='dark'] .field input {
  background: var(--bg-tertiary);
  border-color: color-mix(in srgb, var(--border-color) 82%, #ffffff 18%);
}

[data-theme='dark'] .submit-btn {
  border-color: #2a2a2a;
  background: linear-gradient(180deg, #222222, #080808);
}

[data-theme='dark'] .submit-btn:hover:not(:disabled) {
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.55);
}

@media (max-width: 560px) {
  .login-page {
    padding: 14px;
  }

  .login-card {
    padding: 24px;
    border-radius: 16px;
  }

  .brand-name {
    font-size: 20px;
  }
}
</style>
