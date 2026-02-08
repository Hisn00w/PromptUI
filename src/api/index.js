import axios from 'axios'

// 鍒涘缓 axios 瀹炰緥
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 璇锋眰鎷︽埅鍣?- 鑷姩娣诲姞 Token
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

// 鍝嶅簲鎷︽埅鍣?- 澶勭悊 Token 杩囨湡
api.interceptors.response.use(
    (response) => {
        return response.data
    },
    async (error) => {
        const originalRequest = error.config

        // Token 杩囨湡锛屽皾璇曞埛鏂?
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
                // 鍒锋柊澶辫触锛屾竻闄?Token 骞惰烦杞櫥褰?
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

// ==================== 璁よ瘉鐩稿叧 API ====================

export const authAPI = {
    // 鉴权状态（是否需要管理员初始化）
    status: () => api.get('/auth/status'),

    // 鐢ㄦ埛娉ㄥ唽
    register: (data) => api.post('/auth/register', data),

    // 鐢ㄦ埛鐧诲綍
    login: (credentials) => api.post('/auth/login', credentials),

    // 鐢ㄦ埛鐧诲嚭
    logout: () => api.post('/auth/logout'),

    // 鑾峰彇褰撳墠鐢ㄦ埛淇℃伅
    getMe: () => api.get('/auth/me'),

    // 鏇存柊涓汉璧勬枡
    updateProfile: (data) => api.put('/auth/profile', data),

    // 鍒锋柊 Token
    refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken })
}

// ==================== Prompt 鐩稿叧 API ====================

export const promptsAPI = {
    // 鑾峰彇 Prompt 鍒楄〃锛堟敮鎸佹悳绱€佸垎椤点€佹帓搴忥級
    getList: (params) => api.get('/prompts', { params }),

    // 鑾峰彇鍗曚釜 Prompt 璇︽儏
    getById: (id) => api.get(`/prompts/${id}`),

    // 鍒涘缓 Prompt
    create: (data) => api.post('/prompts', data),

    // 鏇存柊 Prompt
    update: (id, data) => api.patch(`/prompts/${id}`, data),

    // 鍒犻櫎 Prompt
    delete: (id) => api.delete(`/prompts/${id}`),

    // 鍙戝竷 Prompt锛堣崏绋?-> 鍙戝竷锛?
    publish: (id) => api.post(`/prompts/${id}/publish`),

    // 涓嬬嚎 Prompt
    unpublish: (id, reason) => api.post(`/prompts/${id}/offline`, { reason }),

    // 鑾峰彇 Prompt 鐗堟湰鍘嗗彶
    getVersions: (id) => api.get(`/prompts/${id}/versions`),

    // 鐐硅禐 Prompt
    like: (id) => api.post(`/prompts/${id}/like`),

    // 鍙栨秷鐐硅禐
    unlike: (id) => api.delete(`/prompts/${id}/like`),

    // 璁板綍澶嶅埗鎿嶄綔
    recordCopy: (id, source = 'web') => api.post(`/interactions/prompts/${id}/copy`, { source })
}

// ==================== 鏀惰棌鐩稿叧 API ====================

export const favoritesAPI = {
    // 鑾峰彇鎴戠殑鏀惰棌鍒楄〃
    getList: (params) => api.get('/favorites', { params }),

    // 鏀惰棌 Prompt
    add: (promptId) => api.post(`/favorites/${promptId}`),

    // 鍙栨秷鏀惰棌
    remove: (promptId) => api.delete(`/favorites/${promptId}`),

    // 妫€鏌ユ槸鍚﹀凡鏀惰棌
    check: (promptId) => api.get(`/favorites/${promptId}/check`)
}

// ==================== 鍒嗙被鐩稿叧 API ====================

export const categoriesAPI = {
    // 鑾峰彇鎵€鏈夊垎绫?
    getList: () => api.get('/categories'),

    // 鑾峰彇鍒嗙被涓嬬殑 Prompts
    getPrompts: (categoryId, params) => api.get('/prompts', { params: { category_id: categoryId, ...params } })
}

// ==================== 鐢ㄦ埛鐩稿叧 API ====================

export const usersAPI = {
    // 鑾峰彇鐢ㄦ埛鍏紑璧勬枡
    getProfile: (userId) => api.get(`/users/${userId}`),

    // 鑾峰彇鐢ㄦ埛鐨勫叕寮€ Prompts
    getPrompts: (userId, params) => api.get(`/users/${userId}/prompts`, { params }),

    // 鑾峰彇鎴戠殑 Prompts锛堝寘鎷崏绋匡級
    getMyPrompts: (params) => api.get('/me/prompts', { params })
}

// ==================== 鎼滅储鐩稿叧 API ====================

export const searchAPI = {
    // 鍏ㄥ眬鎼滅储
    search: (query, params) => api.get('/search', { params: { q: query, ...params } }),

    // 鎼滅储寤鸿
    suggestions: (query) => api.get('/search/suggestions', { params: { q: query } })
}

// ==================== 绠＄悊鍛樼浉鍏?API ====================

export const adminAPI = {
    // 鑾峰彇寰呭鏍?Prompts
    getPendingPrompts: (params) => api.get('/admin/prompts/pending', { params }),

    // 瀹℃牳閫氳繃
    approvePrompt: (id) => api.post(`/admin/prompts/${id}/approve`),

    // 瀹℃牳鎷掔粷
    rejectPrompt: (id, reason) => api.post(`/admin/prompts/${id}/reject`, { reason }),

    // 涓嬬嚎 Prompt
    unpublishPrompt: (id, reason) => api.post(`/admin/prompts/${id}/unpublish`, { reason }),

    // 鑾峰彇鐢ㄦ埛鍒楄〃
    getUsers: (params) => api.get('/admin/users', { params }),

    // 绂佺敤鐢ㄦ埛
    banUser: (userId, reason) => api.post(`/admin/users/${userId}/ban`, { reason }),

    // 瑙ｇ鐢ㄦ埛
    unbanUser: (userId) => api.post(`/admin/users/${userId}/unban`),

    // 鑾峰彇鎿嶄綔鏃ュ織
    getLogs: (params) => api.get('/admin/logs', { params })
}

// ==================== 鏂囦欢涓婁紶 API ====================

export const uploadAPI = {
    // 涓婁紶鍥剧墖
    uploadImage: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/upload/image', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    // 涓婁紶澶村儚
    uploadAvatar: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/upload/avatar', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    }
}

export default api

