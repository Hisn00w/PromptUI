<template>
  <div class="category-page">
    <div class="page-header">
      <div class="container">
        <p class="page-kicker">Prompt Collection</p>
        <h1 class="page-title">{{ t(titleKey) }}</h1>
        <p class="page-description">{{ t(descriptionKey) }}</p>
      </div>
    </div>

    <div class="filters-bar glass">
      <div class="container">
        <div class="filter-tabs">
          <button
            v-for="sub in subcategories"
            :key="sub.key"
            class="filter-tab"
            :class="{ active: activeFilter === sub.key }"
            @click="activeFilter = sub.key"
          >
            {{ locale === 'zh' ? sub.label : sub.labelEn }}
          </button>
        </div>
      </div>
    </div>

    <div class="content-section">
      <div class="container">
        <div v-if="loading" class="loading-grid">
          <div v-for="n in 6" :key="n" class="loading-card"></div>
        </div>
        <div v-else-if="error" class="state-card state-error">{{ error }}</div>
        <div v-else class="prompts-grid">
          <PromptCard
            v-for="(item, index) in filteredItems"
            :key="item.id"
            :item="localizedItem(item)"
            :index="index"
            @select="openDetail"
            @copied="recordCopy"
          />
        </div>
      </div>
    </div>

    <PromptDetailDrawer
      :is-open="isDetailOpen"
      :item="selectedItem ? localizedItem(selectedItem) : null"
      @close="closeDetail"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { categoriesAPI, promptsAPI } from '@/api'
import PromptCard from '@/components/prompt/PromptCard.vue'
import PromptDetailDrawer from '@/components/prompt/PromptDetailDrawer.vue'

const props = defineProps({
  categoryKey: { type: String, required: true },
  titleKey: { type: String, required: true },
  descriptionKey: { type: String, required: true },
  subcategoryLabels: { type: Object, default: () => ({}) },
})

const { t, locale } = useI18n()
const activeFilter = ref('all')
const isDetailOpen = ref(false)
const selectedItem = ref(null)
const loading = ref(true)
const error = ref('')
const items = ref([])

const normalizePromptItem = (item) => ({
  id: item.id,
  category: props.categoryKey,
  subcategory: item.subcategory || 'uncategorized',
  name: item.title,
  nameEn: item.title_en || item.title,
  tags: item.tags || [],
  tagsEn: item.tags_en || item.tags || [],
  prompt: item.prompt_text,
  codeAssets: item.code_assets || item.codeAssets || {},
  hasCodeAssets: Boolean(item.has_code_assets ?? item.hasCodeAssets),
  preview: {
    type: 'component',
    component: item.preview_component || null,
  },
})

const hasRenderableCode = (item) => {
  const code = item?.codeAssets || {}
  if (code.preview && (code.preview.html || code.preview.css || code.preview.js)) return true
  if (code.html || code.css || code.js) return true
  if (code.files && typeof code.files === 'object') return Object.keys(code.files).length > 0
  return false
}

const subcategories = computed(() => {
  const keys = new Set(items.value.map((item) => item.subcategory).filter(Boolean))
  const mapped = [...keys].map((key) => {
    const label = props.subcategoryLabels[key]
    return {
      key,
      label: label?.zh || key,
      labelEn: label?.en || key,
    }
  })
  return [{ key: 'all', label: t('common.all'), labelEn: t('common.all') }, ...mapped]
})

const filteredItems = computed(() => {
  if (activeFilter.value === 'all') return items.value
  return items.value.filter((item) => item.subcategory === activeFilter.value)
})

const localizedItem = (item) => ({
  ...item,
  name: locale.value === 'zh' ? item.name : (item.nameEn || item.name),
  tags: locale.value === 'zh' ? item.tags : (item.tagsEn || item.tags),
})

const openDetail = async (item) => {
  isDetailOpen.value = true
  selectedItem.value = item
  try {
    const detail = await promptsAPI.getById(item.id)
    selectedItem.value = normalizePromptItem(detail)
  } catch {
    // keep list payload as fallback
  }
}

const closeDetail = () => {
  isDetailOpen.value = false
}

const recordCopy = async (item) => {
  if (!item?.id) return
  try {
    await promptsAPI.recordCopy(item.id, 'web')
  } catch {
    // ignore analytics failures
  }
}

const fetchCategoryPrompts = async () => {
  loading.value = true
  error.value = ''
  try {
    const categories = await categoriesAPI.getList()
    const category = categories.find((item) => item.key === props.categoryKey)
    if (!category) {
      // Category not yet created in backend — show empty state
      items.value = []
      return
    }

    const pageSize = 100
    let page = 1
    let total = 0
    const allItems = []

    do {
      const result = await promptsAPI.getList({
        category_id: category.id,
        page,
        page_size: pageSize,
        sort_by: 'updated_at',
        sort_order: 'desc',
      })
      total = Number(result.total || 0)
      allItems.push(...(result.items || []))
      page += 1
    } while (allItems.length < total)

    const normalized = allItems.map(normalizePromptItem)

    const needHydration = normalized.filter((item) => item.hasCodeAssets && !hasRenderableCode(item))
    if (needHydration.length) {
      const detailResults = await Promise.allSettled(
        needHydration.map((item) => promptsAPI.getById(item.id))
      )
      const detailMap = new Map()
      detailResults.forEach((result, idx) => {
        if (result.status === 'fulfilled') {
          detailMap.set(needHydration[idx].id, normalizePromptItem(result.value))
        }
      })
      items.value = normalized.map((item) => detailMap.get(item.id) || item)
    } else {
      items.value = normalized
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || e?.message || t('common.loadBackendFailed')
  } finally {
    loading.value = false
  }
}

onMounted(fetchCategoryPrompts)
</script>

<style scoped>
.category-page { min-height: calc(100vh - var(--navbar-height)); }
.page-header { text-align: center; padding: 1.1rem 0 0.65rem; }
.page-kicker { display: inline-block; padding: .2rem .5rem; border-radius: var(--radius-full); border: 1px solid var(--border-color); background: var(--bg-elevated); color: var(--text-secondary); font-size: .68rem; text-transform: uppercase; letter-spacing: .06em; }
.page-title { margin-top: .42rem; font-size: clamp(2rem, 4vw, 2.6rem); font-weight: 750; letter-spacing: -0.02em; }
.page-description { margin-top: .24rem; font-size: 1.02rem; color: var(--text-secondary); }
.filters-bar { position: sticky; top: var(--navbar-height); z-index: 100; border-top: 1px solid var(--border-color); border-bottom: 1px solid var(--border-color); padding: .68rem 0; }
.filter-tabs { display: flex; gap: .36rem; overflow-x: auto; }
.filter-tab { padding: .42rem .86rem; border-radius: var(--radius-full); border: 1px solid transparent; background: transparent; color: var(--text-secondary); font-size: var(--font-size-sm); font-weight: 600; white-space: nowrap; transition: all var(--transition-fast); }
.filter-tab:hover { color: var(--text-primary); background: color-mix(in srgb, var(--bg-tertiary) 62%, transparent); }
.filter-tab.active { color: var(--text-inverse); background: linear-gradient(180deg,#ce7b43,#b66a36); }
.content-section { padding: var(--spacing-xl) 0 var(--spacing-2xl); }
.prompts-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(292px, 1fr)); gap: var(--spacing-lg); }
.loading-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(292px, 1fr)); gap: var(--spacing-lg); }
.loading-card {
  height: 360px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
  background:
    linear-gradient(
      108deg,
      color-mix(in srgb, var(--bg-tertiary) 96%, transparent) 28%,
      color-mix(in srgb, var(--bg-primary) 95%, transparent) 42%,
      color-mix(in srgb, var(--bg-tertiary) 96%, transparent) 56%
    );
  background-size: 240% 100%;
  animation: shimmer 1.4s linear infinite;
}
.state-card { border-radius: var(--radius-md); border: 1px solid var(--border-color); background: var(--bg-elevated); padding: 1rem; color: var(--text-secondary); }
.state-error { color: #9f3f22; border-color: color-mix(in srgb, #9f3f22 35%, var(--border-color)); }
@keyframes shimmer {
  from { background-position: 100% 0; }
  to { background-position: -120% 0; }
}
@media (max-width: 768px) { .page-title { font-size: var(--font-size-3xl); } .prompts-grid,.loading-grid { grid-template-columns: 1fr; } }
</style>
