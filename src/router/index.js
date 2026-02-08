import { createRouter, createWebHashHistory } from 'vue-router'
import api from '@/api'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Landing.vue')
  },
  {
    path: '/admin-setup',
    name: 'AdminSetup',
    component: () => import('../views/AdminSetup.vue'),
    meta: { skipAdminCheck: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/prompt/new',
    name: 'PromptNew',
    component: () => import('../views/PromptEditor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/prompt/edit/:id',
    name: 'PromptEdit',
    component: () => import('../views/PromptEditor.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/layouts',
    name: 'Layouts',
    component: () => import('../views/PageLayouts.vue')
  },
  {
    path: '/cards',
    name: 'Cards',
    component: () => import('../views/Cards.vue')
  },
  {
    path: '/components',
    name: 'Components',
    component: () => import('../views/Components.vue')
  },
  {
    path: '/animations',
    name: 'Animations',
    component: () => import('../views/Animations.vue')
  },
  {
    path: '/colors',
    name: 'Colors',
    component: () => import('../views/Colors.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

router.beforeEach(async (to, _from, next) => {
  if (to.meta.skipAdminCheck) {
    next()
    return
  }

  try {
    const status = await api.get('/auth/status', { timeout: 3000 })

    if (status?.needs_admin_setup === true && to.name !== 'AdminSetup') {
      next({ name: 'AdminSetup' })
      return
    }

    if (status?.needs_admin_setup === false && to.name === 'AdminSetup') {
      next({ name: 'Home' })
      return
    }
  } catch (error) {
    console.error('[Router] Failed to check admin status:', error)
    if (to.name === 'AdminSetup') {
      next()
      return
    }
    next({ name: 'AdminSetup' })
    return
  }

  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) {
    next({
      name: 'Login',
      query: { redirect: to.fullPath },
    })
    return
  }

  if (to.meta.requiresAdmin) {
    try {
      const me = await api.get('/auth/me', { timeout: 3000 })
      if (me?.role !== 'admin') {
        next({ name: 'Home' })
        return
      }
    } catch (error) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      next({
        name: 'Login',
        query: { redirect: to.fullPath },
      })
      return
    }
  }

  next()
})

export default router
