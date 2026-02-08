<template>
  <div class="admin-dashboard">
    <header class="dashboard-header">
      <h1>{{ text.title }}</h1>
      <p class="subtitle">{{ text.subtitle }}</p>
    </header>

    <section class="stats-grid">
      <div class="stat-card">
        <div class="stat-label">{{ text.totalUsers }}</div>
        <div class="stat-value">{{ stats.totalUsers }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ text.totalPrompts }}</div>
        <div class="stat-value">{{ stats.totalPrompts }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ text.pendingReview }}</div>
        <div class="stat-value">{{ stats.pendingReview }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">{{ text.published }}</div>
        <div class="stat-value">{{ stats.published }}</div>
      </div>
    </section>

    <section class="section">
      <div class="section-header">
        <h2>{{ text.latestPrompts }}</h2>
        <div class="tabs">
          <button :class="{ active: currentTab === 'all' }" @click="currentTab = 'all'">{{ text.all }}</button>
          <button :class="{ active: currentTab === 'pending' }" @click="currentTab = 'pending'">{{ text.pending }}</button>
          <button :class="{ active: currentTab === 'published' }" @click="currentTab = 'published'">{{ text.publishedTab }}</button>
        </div>
      </div>

      <div v-if="loading" class="loading">{{ text.loading }}</div>
      <div v-else-if="filteredPrompts.length === 0" class="empty">{{ text.empty }}</div>

      <div v-else class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>{{ text.colTitle }}</th>
              <th>{{ text.colAuthor }}</th>
              <th>{{ text.colCategory }}</th>
              <th>{{ text.colStatus }}</th>
              <th>{{ text.colCreatedAt }}</th>
              <th>{{ text.colActions }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prompt in filteredPrompts" :key="prompt.id">
              <td class="title-cell">
                <div class="prompt-title">{{ prompt.title || '-' }}</div>
                <div class="prompt-desc">{{ trimPrompt(prompt.prompt_text) }}</div>
              </td>
              <td>{{ prompt.author_username || '-' }}</td>
              <td>{{ prompt.category_name || '-' }}</td>
              <td>
                <span :class="['status-badge', getStatusClass(prompt.status)]">{{ getStatusText(prompt.status) }}</span>
              </td>
              <td>{{ formatDate(prompt.created_at) }}</td>
              <td class="actions-cell">
                <button class="btn btn-view" @click="viewPrompt(prompt.id)">{{ text.view }}</button>
                <button
                  v-if="prompt.status === 'pending_review'"
                  class="btn btn-approve"
                  @click="approvePrompt(prompt.id)"
                >
                  {{ text.approve }}
                </button>
                <button class="btn btn-delete" @click="deletePrompt(prompt.id)">{{ text.delete }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { promptsAPI } from '@/api'

const { locale } = useI18n()
const router = useRouter()

const prompts = ref([])
const loading = ref(true)
const currentTab = ref('all')

const stats = computed(() => {
  const totalPrompts = prompts.value.length
  const pendingReview = prompts.value.filter((p) => p.status === 'pending_review').length
  const published = prompts.value.filter((p) => p.status === 'published').length
  const totalUsers = new Set(prompts.value.map((p) => p.author_id).filter(Boolean)).size

  return {
    totalUsers,
    totalPrompts,
    pendingReview,
    published,
  }
})

const filteredPrompts = computed(() => {
  if (currentTab.value === 'pending') {
    return prompts.value.filter((p) => p.status === 'pending_review')
  }
  if (currentTab.value === 'published') {
    return prompts.value.filter((p) => p.status === 'published')
  }
  return prompts.value
})

const text = computed(() => {
  if (locale.value === 'en') {
    return {
      title: 'Admin Dashboard',
      subtitle: 'System overview and prompt moderation',
      totalUsers: 'Total Users',
      totalPrompts: 'Total Prompts',
      pendingReview: 'Pending Review',
      published: 'Published',
      latestPrompts: 'Latest Prompts',
      all: 'All',
      pending: 'Pending',
      publishedTab: 'Published',
      loading: 'Loading...',
      empty: 'No data yet',
      colTitle: 'Title',
      colAuthor: 'Author',
      colCategory: 'Category',
      colStatus: 'Status',
      colCreatedAt: 'Created At',
      colActions: 'Actions',
      view: 'View',
      approve: 'Approve',
      delete: 'Delete',
      draft: 'Draft',
      pendingReviewText: 'Pending',
      publishedText: 'Published',
      archived: 'Archived',
      unknown: 'Unknown',
      approveConfirm: 'Approve this prompt?',
      deleteConfirm: 'Delete this prompt? This action cannot be undone.',
      actionSuccess: 'Operation completed',
      actionFailed: 'Operation failed',
    }
  }

  return {
    title: '管理员控制台',
    subtitle: '系统数据总览与内容审核',
    totalUsers: '总用户数',
    totalPrompts: '提示词总数',
    pendingReview: '待审核',
    published: '已发布',
    latestPrompts: '最新提交的提示词',
    all: '全部',
    pending: '待审核',
    publishedTab: '已发布',
    loading: '加载中...',
    empty: '暂无数据',
    colTitle: '标题',
    colAuthor: '作者',
    colCategory: '分类',
    colStatus: '状态',
    colCreatedAt: '创建时间',
    colActions: '操作',
    view: '查看',
    approve: '通过',
    delete: '删除',
    draft: '草稿',
    pendingReviewText: '待审核',
    publishedText: '已发布',
    archived: '已归档',
    unknown: '未知',
    approveConfirm: '确定通过这个提示词吗？',
    deleteConfirm: '确定删除这个提示词吗？此操作不可恢复。',
    actionSuccess: '操作成功',
    actionFailed: '操作失败',
  }
})

const getStatusClass = (status) => {
  if (status === 'pending_review') return 'status-pending'
  if (status === 'published') return 'status-published'
  if (status === 'archived') return 'status-archived'
  return 'status-draft'
}

const getStatusText = (status) => {
  if (status === 'pending_review') return text.value.pendingReviewText
  if (status === 'published') return text.value.publishedText
  if (status === 'archived') return text.value.archived
  if (status === 'draft') return text.value.draft
  return text.value.unknown
}

const trimPrompt = (promptText) => {
  if (!promptText) return '-'
  return promptText.length > 64 ? `${promptText.slice(0, 64)}...` : promptText
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString(locale.value === 'en' ? 'en-US' : 'zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const loadData = async () => {
  loading.value = true
  try {
    const data = await promptsAPI.getList({ page: 1, page_size: 100, sort: 'created_at', order: 'desc' })
    prompts.value = Array.isArray(data.items) ? data.items : []
  } catch (error) {
    console.error('Failed to load admin dashboard data:', error)
    prompts.value = []
  } finally {
    loading.value = false
  }
}

const viewPrompt = (id) => {
  router.push(`/prompt/edit/${id}`)
}

const approvePrompt = async (id) => {
  if (!window.confirm(text.value.approveConfirm)) return
  try {
    await promptsAPI.publish(id)
    await loadData()
  } catch (error) {
    console.error('Failed to approve prompt:', error)
    window.alert(text.value.actionFailed)
  }
}

const deletePrompt = async (id) => {
  if (!window.confirm(text.value.deleteConfirm)) return
  try {
    await promptsAPI.delete(id)
    await loadData()
  } catch (error) {
    console.error('Failed to delete prompt:', error)
    window.alert(text.value.actionFailed)
  }
}

onMounted(loadData)
</script>

<style scoped>
.admin-dashboard {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}

.dashboard-header {
  margin-bottom: 28px;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 750;
  color: var(--text-primary);
}

.subtitle {
  margin-top: 8px;
  color: var(--text-tertiary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  margin-bottom: 22px;
}

.stat-card {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 16px;
  background: var(--bg-elevated);
}

.stat-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.stat-value {
  margin-top: 6px;
  font-size: 28px;
  font-weight: 800;
  color: var(--text-primary);
}

.section {
  border: 1px solid var(--border-color);
  border-radius: 12px;
  background: var(--bg-elevated);
  padding: 18px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.section-header h2 {
  margin: 0;
  font-size: 18px;
  color: var(--text-primary);
}

.tabs {
  display: flex;
  gap: 8px;
}

.tabs button {
  padding: 7px 12px;
  border-radius: 999px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-secondary);
  font-weight: 600;
}

.tabs button.active {
  background: #111;
  border-color: #111;
  color: #fff;
}

.loading,
.empty {
  padding: 40px;
  text-align: center;
  color: var(--text-tertiary);
}

.table-wrap {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  vertical-align: top;
}

th {
  color: var(--text-tertiary);
  font-size: 12px;
  font-weight: 700;
}

td {
  color: var(--text-secondary);
  font-size: 14px;
}

.title-cell {
  min-width: 260px;
  max-width: 360px;
}

.prompt-title {
  color: var(--text-primary);
  font-weight: 700;
}

.prompt-desc {
  margin-top: 4px;
  color: var(--text-tertiary);
  font-size: 12px;
  line-height: 1.45;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.status-draft {
  background: var(--bg-tertiary);
  color: var(--text-tertiary);
}

.status-pending {
  background: color-mix(in srgb, #d97706 14%, transparent);
  color: #d97706;
}

.status-published {
  background: color-mix(in srgb, #15803d 14%, transparent);
  color: #15803d;
}

.status-archived {
  background: color-mix(in srgb, #991b1b 14%, transparent);
  color: #991b1b;
}

.actions-cell {
  white-space: nowrap;
}

.btn {
  margin-right: 6px;
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 650;
}

.btn-view:hover,
.btn-approve:hover,
.btn-delete:hover {
  border-color: var(--border-color-strong);
}

.btn-approve {
  background: #111;
  border-color: #111;
  color: #fff;
}

.btn-delete {
  color: #b91c1c;
}
</style>
