<template>
  <div class="admin-setup-page">
    <div class="setup-card">
      <div class="setup-header">
        <div class="logo">
          <img src="/logo.svg" alt="PromptUI" class="logo-icon" />
          <span class="logo-text">PromptUI</span>
        </div>
        <h1>{{ text.title }}</h1>
        <p class="setup-desc">{{ text.desc }}</p>
      </div>

      <form @submit.prevent="handleSubmit" class="setup-form">
        <div class="field">
          <label>{{ text.username }}</label>
          <input
            v-model="form.username"
            type="text"
            :placeholder="text.usernamePlaceholder"
            required
            minlength="3"
          />
        </div>

        <div class="field">
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

        <div class="field">
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
          {{ isLoading ? text.creating : text.createAdmin }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { authAPI } from '@/api'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const { locale } = useI18n()
const authStore = useAuthStore()

const form = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const isLoading = ref(false)
const error = ref('')

const text = computed(() => {
  const zh = locale.value === 'zh'
  return zh
    ? {
        title: '创建管理员账号',
        desc: '系统检测到尚未设置管理员，请创建第一个管理员账号',
        username: '用户名',
        usernamePlaceholder: '请输入用户名',
        email: '邮箱',
        emailPlaceholder: '选填：请输入管理员邮箱',
        password: '密码',
        passwordPlaceholder: '请输入密码（至少 6 位）',
        confirmPassword: '确认密码',
        confirmPasswordPlaceholder: '请再次输入密码',
        creating: '创建中...',
        createAdmin: '创建管理员账号',
        passwordMismatch: '两次输入的密码不一致',
        passwordTooShort: '密码至少需要 6 位',
        createFailed: '创建失败，请重试'
      }
    : {
        title: 'Create Admin Account',
        desc: 'No admin account exists yet. Please create the first administrator.',
        username: 'Username',
        usernamePlaceholder: 'Enter admin username',
        email: 'Email',
        emailPlaceholder: 'Optional: enter admin email',
        password: 'Password',
        passwordPlaceholder: 'Enter password (min 6 chars)',
        confirmPassword: 'Confirm Password',
        confirmPasswordPlaceholder: 'Re-enter password',
        creating: 'Creating...',
        createAdmin: 'Create Admin Account',
        passwordMismatch: 'Passwords do not match',
        passwordTooShort: 'Password must be at least 6 characters',
        createFailed: 'Create failed, please try again'
      }
})

const handleSubmit = async () => {
  error.value = ''

  if (form.value.password !== form.value.confirmPassword) {
    error.value = text.value.passwordMismatch
    return
  }

  if (form.value.password.length < 6) {
    error.value = text.value.passwordTooShort
    return
  }

  isLoading.value = true
  try {
    const response = await authAPI.register({
      username: form.value.username,
      email: form.value.email,
      password: form.value.password
    })

    localStorage.setItem('access_token', response.tokens.access_token)
    localStorage.setItem('refresh_token', response.tokens.refresh_token)

    await authStore.fetchUser()
    router.push('/admin')
  } catch (err) {
    console.error('Admin setup failed:', err)
    error.value = err.response?.data?.detail || text.value.createFailed
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.admin-setup-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  padding: 20px;
}

.setup-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color-strong);
  border-radius: var(--radius-lg);
  padding: 48px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-lg);
}

.setup-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 24px;
}

.logo-icon {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  object-fit: cover;
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  color: var(--text-primary);
}

.setup-header h1 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 10px 0;
}

.setup-desc {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

.setup-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.field input {
  padding: 11px 14px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  transition: all 0.15s ease;
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
  color: var(--color-danger);
  font-size: 13px;
  text-align: center;
  margin: 0;
}

.submit-btn {
  padding: 13px 20px;
  font-size: 15px;
  font-weight: 600;
  color: #ffffff;
  background: linear-gradient(180deg, #1a1a1a, #000000);
  border: 1px solid #0f0f0f;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  margin-top: 6px;
}

.submit-btn:hover:not(:disabled) {
  filter: brightness(1.06);
  transform: translateY(-1px);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

[data-theme='dark'] .admin-setup-page {
  background: #080808;
}

[data-theme='dark'] .setup-card {
  background: #121212;
  border-color: rgba(255, 255, 255, 0.14);
}
</style>
