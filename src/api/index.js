import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
    baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
    timeout: 10000,
    headers: {
        'Content-Type': 'application/json'
    }
})

// 请求拦截器：自动附带 access token
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

// 响应拦截器：401 时自动刷新 token 并重试请求
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
                // 刷新失败：清理本地凭证并跳转登录页
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

// 认证相关 API
export const authAPI = {
    // 系统鉴权状态（是否需要管理员初始化）
    status: () => api.get('/auth/status'),

    // 注册
    register: (data) => api.post('/auth/register', data),

    // 登录
    login: (credentials) => api.post('/auth/login', credentials),

    // 登出
    logout: () => api.post('/auth/logout'),

    // 当前用户信息
    getMe: () => api.get('/auth/me'),

    // 更新个人资料
    updateProfile: (data) => api.put('/auth/profile', data),

    // 刷新 token
    refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken })
}

// Prompt 相关 API
export const promptsAPI = {
    // 列表查询（支持搜索/分页/排序）
    getList: (params) => api.get('/prompts', { params }),

    // 详情
    getById: (id) => api.get(`/prompts/${id}`),

    // 创建
    create: (data) => api.post('/prompts', data),

    // 更新
    update: (id, data) => api.patch(`/prompts/${id}`, data),

    // 删除
    delete: (id) => api.delete(`/prompts/${id}`),

    // 发布
    publish: (id) => api.post(`/prompts/${id}/publish`),

    // 下线
    unpublish: (id, reason) => api.post(`/prompts/${id}/offline`, { reason }),

    // 版本历史
    getVersions: (id) => api.get(`/prompts/${id}/versions`),

    // 点赞
    like: (id) => api.post(`/prompts/${id}/like`),

    // 取消点赞
    unlike: (id) => api.delete(`/prompts/${id}/like`),

    // 记录复制行为
    recordCopy: (id, source = 'web') => api.post(`/interactions/prompts/${id}/copy`, { source })
}

// 收藏相关 API
export const favoritesAPI = {
    // 我的收藏列表
    getList: (params) => api.get('/favorites', { params }),

    // 添加收藏
    add: (promptId) => api.post(`/favorites/${promptId}`),

    // 取消收藏
    remove: (promptId) => api.delete(`/favorites/${promptId}`),

    // 校验是否已收藏
    check: (promptId) => api.get(`/favorites/${promptId}/check`)
}

// 分类相关 API
export const categoriesAPI = {
    // 全部分类
    getList: () => api.get('/categories'),

    // 分类下 prompts
    getPrompts: (categoryId, params) => api.get('/prompts', { params: { category_id: categoryId, ...params } })
}

// 用户相关 API
export const usersAPI = {
    // 用户公开资料
    getProfile: (userId) => api.get(`/users/${userId}`),

    // 用户公开 prompts
    getPrompts: (userId, params) => api.get(`/users/${userId}/prompts`, { params }),

    // 当前用户 prompts（含草稿）
    getMyPrompts: (params) => api.get('/me/prompts', { params })
}

// 搜索相关 API
export const searchAPI = {
    // 全局搜索
    search: (query, params) => api.get('/search', { params: { q: query, ...params } }),

    // 搜索建议
    suggestions: (query) => api.get('/search/suggestions', { params: { q: query } })
}

// 管理员相关 API
export const adminAPI = {
    // 待审核 prompts
    getPendingPrompts: (params) => api.get('/admin/prompts/pending', { params }),

    // 审核通过
    approvePrompt: (id) => api.post(`/admin/prompts/${id}/approve`),

    // 审核拒绝
    rejectPrompt: (id, reason) => api.post(`/admin/prompts/${id}/reject`, { reason }),

    // 下线 prompt
    unpublishPrompt: (id, reason) => api.post(`/admin/prompts/${id}/unpublish`, { reason }),

    // 用户列表
    getUsers: (params) => api.get('/admin/users', { params }),

    // 封禁用户
    banUser: (userId, reason) => api.post(`/admin/users/${userId}/ban`, { reason }),

    // 解禁用户
    unbanUser: (userId) => api.post(`/admin/users/${userId}/unban`),

    // 操作日志
    getLogs: (params) => api.get('/admin/logs', { params })
}

// 上传相关 API
export const uploadAPI = {
    // 上传图片
    uploadImage: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/upload/image', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    },

    // 上传头像
    uploadAvatar: (file) => {
        const formData = new FormData()
        formData.append('file', file)
        return api.post('/upload/avatar', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        })
    }
}

export default api
