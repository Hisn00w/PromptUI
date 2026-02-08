import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => {
        return Promise.reject(error)
    }
)

api.interceptors.response.use(
    (response) => {
        return response.data
    },
    async (error) => {
        const originalRequest = error.config

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true

            try {
                const refreshToken = localStorage.getItem('refresh_token')
                const { data } = await axios.post(
                    `${api.defaults.baseURL}/auth/refresh`,
                    { refresh_token: refreshToken }
                )

                localStorage.setItem('access_token', data.access_token)
                originalRequest.headers.Authorization = `Bearer ${data.access_token}`

                return api(originalRequest)
            } catch (refreshError) {
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                const hashPath = (window.location.hash || '').replace(/^#/, '') || '/'
                const redirect = hashPath.startsWith('/login') ? '/' : hashPath
                window.location.href = `/#/login?redirect=${encodeURIComponent(redirect)}`
                return Promise.reject(refreshError)
            }
        }

        return Promise.reject(error)
    }
)


export const authAPI = {
    status: () => api.get('/auth/status'),

    register: (data) => api.post('/auth/register', data),

    login: (credentials) => api.post('/auth/login', credentials),

    logout: () => api.post('/auth/logout'),

    getMe: () => api.get('/auth/me'),

    updateProfile: (data) => api.put('/auth/profile', data),

    refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken })
}


export const promptsAPI = {
    getList: (params) => api.get('/prompts', { params }),

    getById: (id) => api.get(`/prompts/${id}`),

    create: (data) => api.post('/prompts', data),

    update: (id, data) => api.patch(`/prompts/${id}`, data),

    delete: (id) => api.delete(`/prompts/${id}`),

    publish: (id) => api.post(`/prompts/${id}/publish`),

    unpublish: (id, reason) => api.post(`/prompts/${id}/offline`, { reason }),

    getVersions: (id) => api.get(`/prompts/${id}/versions`),

    like: (id) => api.post(`/prompts/${id}/like`),

    unlike: (id) => api.delete(`/prompts/${id}/like`),

    recordCopy: (id, source = 'web') => api.post(`/interactions/prompts/${id}/copy`, { source })
}


export const favoritesAPI = {
    getList: (params) => api.get('/favorites', { params }),

    add: (promptId) => api.post(`/favorites/${promptId}`),

    remove: (promptId) => api.delete(`/favorites/${promptId}`),

    check: (promptId) => api.get(`/favorites/${promptId}/check`)
}


export const categoriesAPI = {
    getList: () => api.get('/categories'),

    getPrompts: (categoryId, params) => api.get('/prompts', { params: { category_id: categoryId, ...params } })
}


export const usersAPI = {
    getProfile: (userId) => api.get(`/users/${userId}`),

    getPrompts: (userId, params) => api.get(`/users/${userId}/prompts`, { params }),

    getMyPrompts: (params) => api.get('/me/prompts', { params })
}


export const searchAPI = {
    search: (query, params) => api.get('/search', { params: { q: query, ...params } }),

    suggestions: (query) => api.get('/search/suggestions', { params: { q: query } })
}


export const adminAPI = {
    getPendingPrompts: (params) => api.get('/admin/prompts/pending', { params }),

    approvePrompt: (id) => api.post(`/admin/prompts/${id}/approve`),

    rejectPrompt: (id, reason) => api.post(`/admin/prompts/${id}/reject`, { reason }),

    unpublishPrompt: (id, reason) => api.post(`/admin/prompts/${id}/unpublish`, { reason }),

    getUsers: (params) => api.get('/admin/users', { params }),

    banUser: (userId, reason) => api.post(`/admin/users/${userId}/ban`, { reason }),

    unbanUser: (userId) => api.post(`/admin/users/${userId}/unban`),

    getLogs: (params) => api.get('/admin/logs', { params })
}


export const uploadAPI = {
    uploadImage: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/upload/image', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    uploadAvatar: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/upload/avatar', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    }
}

export default api

