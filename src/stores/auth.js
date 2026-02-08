import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authAPI } from '@/api'

export const useAuthStore = defineStore('auth', () => {
    const user = ref(null)
    const isLoading = ref(false)

    const isAuthenticated = computed(() => !!user.value)

    async function fetchUser() {
        if (!localStorage.getItem('access_token')) return

        isLoading.value = true
        try {
            const data = await authAPI.getMe()
            user.value = data
        } catch (error) {
            console.error('Failed to fetch user:', error)
            logout()
        } finally {
            isLoading.value = false
        }
    }

    function logout() {
        user.value = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
    }

    return {
        user,
        isLoading,
        isAuthenticated,
        fetchUser,
        logout
    }
})
