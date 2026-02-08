<template>
  <div class="prompt-editor-page">
    <!-- Toast 通知 -->
    <Transition name="toast">
      <div v-if="toast.show" :class="['toast', toast.type]">
        {{ toast.message }}
      </div>
    </Transition>

    <div class="container">
      <div class="page-header">
        <h1 class="page-title">{{ isEditMode ? t('editor.editTitle') : t('editor.createTitle') }}</h1>
        <div class="header-actions">
          <button class="btn-secondary" @click="saveDraft" :disabled="isSaving">
            {{ isSaving ? t('editor.saving') : t('editor.saveDraft') }}
          </button>
          <button class="btn-primary" @click="publish" :disabled="isSaving">
            {{ isSaving ? t('editor.processing') : (isEditMode ? t('editor.update') : t('editor.publish')) }}
          </button>
        </div>
      </div>

      <div class="editor-layout">
        <!-- 左侧：表单 -->
        <div class="form-section">
          <form @submit.prevent="publish">
            <section class="form-group">
              <h2 class="section-title">{{ t('editor.basicInfo') }}</h2>
              
              <div class="field">
                <label class="field-label">{{ t('editor.nameRequired') }}</label>
                <input 
                  v-model="form.name" 
                  type="text" 
                  class="field-input" 
                   :placeholder="t('editor.namePlaceholder')"
                  required
                />
              </div>

              <div class="field">
                <label class="field-label">{{ t('editor.englishName') }}</label>
                <input 
                  v-model="form.nameEn" 
                  type="text" 
                  class="field-input" 
                   :placeholder="t('editor.englishNamePlaceholder')"
                />
              </div>

              <div class="field-row">
                <div class="field">
                  <label class="field-label">{{ t('editor.categoryRequired') }}</label>
                  <select v-model="form.category" class="field-select" required>
                    <option value="">{{ t('editor.pleaseSelect') }}</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
                  </select>
                </div>

                <div class="field">
                  <label class="field-label">{{ t('editor.subcategory') }}</label>
                  <select v-model="form.subcategory" class="field-select">
                    <option value="">{{ t('editor.pleaseSelect') }}</option>
                    <option v-for="sub in subcategories" :key="sub" :value="sub">{{ sub }}</option>
                  </select>
                </div>
              </div>

              <div class="field">
                <label class="field-label">{{ t('editor.tagsComma') }}</label>
                <input 
                  v-model="tagsInput" 
                  type="text" 
                  class="field-input" 
                   :placeholder="t('editor.tagsPlaceholder')"
                />
                <div v-if="form.tags.length" class="tags-preview">
                  <span v-for="(tag, index) in form.tags" :key="index" class="tag">
                    {{ tag }}
                    <button type="button" @click="removeTag(index)" class="tag-remove">×</button>
                  </span>
                </div>
              </div>
            </section>

            <!-- AI 提示词 -->
            <section class="form-group">
              <h2 class="section-title">{{ t('editor.aiPromptRequired') }}</h2>
              <div class="field">
                <textarea 
                  v-model="form.prompt" 
                  class="field-textarea" 
                  rows="6"
                   :placeholder="t('editor.promptPlaceholder')"
                  required
                ></textarea>
                <p class="field-hint">{{ t('editor.charCount', { count: form.prompt.length }) }}</p>
              </div>
            </section>

            <!-- 代码（可选） -->
            <section class="form-group">
              <h2 class="section-title">
                {{ t('editor.codeExample') }}
                <span class="section-subtitle">{{ t('editor.codeExampleOptional') }}</span>
              </h2>

              <!-- HTML -->
              <div class="field">
                <label class="field-label">HTML</label>
                <textarea 
                  v-model="form.code.html" 
                  class="field-textarea code-textarea" 
                  rows="8"
                  placeholder="<div class=&quot;button&quot;>...</div>"
                  spellcheck="false"
                ></textarea>
              </div>

              <!-- CSS -->
              <div class="field">
                <label class="field-label">CSS</label>
                <textarea 
                  v-model="form.code.css" 
                  class="field-textarea code-textarea" 
                  rows="8"
                  placeholder=".button { ... }"
                  spellcheck="false"
                ></textarea>
              </div>

              <!-- JavaScript -->
              <div class="field">
                <label class="field-label">JavaScript</label>
                <textarea 
                  v-model="form.code.js" 
                  class="field-textarea code-textarea" 
                  rows="8"
                  placeholder="document.querySelector('.button').addEventListener(...);"
                  spellcheck="false"
                ></textarea>
              </div>
            </section>

            <section class="form-group">
              <h2 class="section-title">{{ t('editor.previewConfig') }}</h2>
              <div class="field">
                <label class="field-label">{{ t('editor.previewComponentName') }}</label>
                <input 
                  v-model="form.preview.component" 
                  type="text" 
                  class="field-input" 
                   :placeholder="t('editor.previewComponentPlaceholder')"
                />
                <p class="field-hint">{{ t('editor.previewHint') }}</p>
              </div>
            </section>
          </form>
        </div>

        <!-- 右侧：{{ t('editor.livePreview') }} -->
        <div class="preview-section">
          <div class="preview-sticky">
            <h3 class="preview-title">{{ t('editor.livePreview') }}</h3>
            
            <!-- 卡片预览 -->
            <div class="preview-card-wrapper">
              <PromptCard v-if="previewData.name" :item="previewData" />
              <div v-else class="preview-placeholder">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <p>{{ t('editor.fillForPreview') }}</p>
              </div>
            </div>

            <div v-if="hasCode" class="code-preview-section">
              <h4 class="code-preview-title">{{ t('editor.codePreview') }}</h4>
              <div class="code-tabs">
                <button 
                  v-if="form.code.html" 
                  :class="['code-tab', { active: activeCodeTab === 'html' }]"
                  @click="activeCodeTab = 'html'"
                >
                  HTML
                </button>
                <button 
                  v-if="form.code.css" 
                  :class="['code-tab', { active: activeCodeTab === 'css' }]"
                  @click="activeCodeTab = 'css'"
                >
                  CSS
                </button>
                <button 
                  v-if="form.code.js" 
                  :class="['code-tab', { active: activeCodeTab === 'js' }]"
                  @click="activeCodeTab = 'js'"
                >
                  JS
                </button>
              </div>
              <CodeBlock 
                v-if="activeCodeTab === 'html' && form.code.html"
                :code="form.code.html" 
                language="html" 
              />
              <CodeBlock 
                v-if="activeCodeTab === 'css' && form.code.css"
                :code="form.code.css" 
                language="css" 
              />
              <CodeBlock 
                v-if="activeCodeTab === 'js' && form.code.js"
                :code="form.code.js" 
                language="javascript" 
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import PromptCard from '@/components/prompt/PromptCard.vue'
import CodeBlock from '@/components/common/CodeBlock.vue'
import { promptsAPI, categoriesAPI } from '@/api'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const isEditMode = computed(() => !!route.params.id)
const isSaving = ref(false)
const categories = ref([])

// Toast 状态
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

const showToast = (message, type = 'success') => {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// 表单数据
const form = ref({
  name: '',
  nameEn: '',
  category: '',
  subcategory: '',
  tags: [],
  tagsEn: [],
  prompt: '',
  code: {
    html: '',
    css: '',
    js: ''
  },
  preview: {
    type: 'component',
    component: ''
  }
})

const tagsInput = ref('')
const activeCodeTab = ref('html')

// 获取分类
onMounted(async () => {
  try {
    categories.value = await categoriesAPI.getList()
  } catch (error) {
    console.error(t('editor.fetchCategoriesFailed'), error)
  }
})

const subcategories = computed(() => {
  const categoryMap = {
    layouts: ['hero', 'dashboard', 'auth', 'landing', 'admin', 'sidebar', 'grid', 'masonry', 'split'],
    cards: ['product', 'user', 'stats', 'pricing', 'feature'],
    components: ['buttons', 'forms', 'navigation', 'modals', 'tables', 'inputs', 'navbar', 'tabs'],
    animations: ['hover', 'scroll', 'loading', 'transitions', 'micro', 'entrance'],
    colors: ['gradients', 'palettes', 'themes', 'business', 'creative', 'neutral', 'warm', 'dark']
  }
  // 找到选中分类的 key
  const selectedCat = categories.value.find(c => c.id === form.value.category)
  return selectedCat ? (categoryMap[selectedCat.key] || []) : []
})

// 监听标签输入
watch(tagsInput, (newVal) => {
  if (newVal) {
    form.value.tags = newVal.split(/[,，]/).map(t => t.trim()).filter(Boolean)
  }
})

// 预览数据
const previewData = computed(() => ({
  id: 'preview',
  name: form.value.name,
  nameEn: form.value.nameEn,
  prompt: form.value.prompt,
  tags: form.value.tags.length ? form.value.tags : undefined,
  codeAssets: form.value.code
}))

// 是否有代码
const hasCode = computed(() => {
  return form.value.code.html || form.value.code.css || form.value.code.js
})

// 移除标签
const removeTag = (index) => {
  form.value.tags.splice(index, 1)
  tagsInput.value = form.value.tags.join(', ')
}

// 构建 API 请求数据
const buildRequestData = () => {
  return {
    title: form.value.name,
    title_en: form.value.nameEn || null,
    prompt_text: form.value.prompt,
    tags: form.value.tags,
    tags_en: form.value.tagsEn.length ? form.value.tagsEn : form.value.tags,
    category_id: form.value.category,
    subcategory: form.value.subcategory || null,
    preview_component: form.value.preview.component || null,
    code_assets: {
      html: form.value.code.html || '',
      css: form.value.code.css || '',
      js: form.value.code.js || ''
    }
  }
}

// 保存草稿
const saveDraft = async () => {
  isSaving.value = true
  try {
    const data = buildRequestData()
    
    if (isEditMode.value) {
      await promptsAPI.update(route.params.id, data)
      showToast(t('editor.draftSaved'))
    } else {
      const result = await promptsAPI.create(data)
      showToast(t('editor.draftSaved'))
      router.push(`/prompt/edit/${result.id}`)
    }
  } catch (error) {
    console.error(t('editor.saveDraftFailed'), error)
    showToast(error.response?.data?.detail || t('editor.saveFailedRetry'), 'error')
  } finally {
    isSaving.value = false
  }
}

// 发布
const publish = async () => {
  // 验证必填字段
  if (!form.value.name || !form.value.category || !form.value.prompt) {
    showToast(t('editor.fillRequiredFields'), 'error')
    return
  }

  isSaving.value = true
  try {
    const data = buildRequestData()
    let promptId = route.params.id
    
    if (isEditMode.value) {
      // 编辑模式：更新后发布
      await promptsAPI.update(promptId, data)
    } else {
      // 新建模式：先创建草稿
      const result = await promptsAPI.create(data)
      promptId = result.id
    }
    
    // 调用发布 API
    try {
      await promptsAPI.publish(promptId)
      showToast(t('editor.publishSuccess'))
      setTimeout(() => router.push('/components'), 1000)
    } catch (publishError) {
      // 发布失败，可能是权限问题
      console.warn(t('editor.publishNeedsAdmin'))
      showToast(t('editor.savedNeedAdminPublish'))
      setTimeout(() => router.push('/components'), 1000)
    }
  } catch (error) {
    console.error(t('editor.publishFailed'), error)
    // 解析验证错误
    let message = t('editor.publishFailedRetry')
    const detail = error.response?.data?.detail
    if (Array.isArray(detail)) {
      message = detail.map(e => e.msg).join('; ')
    } else if (typeof detail === 'string') {
      message = detail
    }
    showToast(message, 'error')
  } finally {
    isSaving.value = false
  }
}

// 如果是编辑模式，加载数据
if (isEditMode.value) {
  promptsAPI.getById(route.params.id).then(data => {
    form.value = {
      name: data.title || '',
      nameEn: data.title_en || '',
      category: data.category_id || '',
      subcategory: data.subcategory || '',
      tags: data.tags || [],
      tagsEn: data.tags_en || [],
      prompt: data.prompt_text || '',
      code: data.code_assets || { html: '', css: '', js: '' },
      preview: { type: 'component', component: data.preview_component || '' }
    }
    tagsInput.value = data.tags?.join(', ') || ''
  }).catch(error => {
    console.error(t('editor.loadFailed'), error)
    showToast(t('editor.loadFailedShort'), 'error')
    router.push('/')
  })
}
</script>

<style scoped>
/* Toast */
.toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: 600;
  z-index: 9999;
  box-shadow: var(--shadow-lg);
}

.toast.success {
  background: linear-gradient(135deg, #10b981, #059669);
  color: white;
}

.toast.error {
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white;
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(-20px);
}

.prompt-editor-page {
  min-height: calc(100vh - var(--navbar-height));
  padding: var(--spacing-xl) 0;
  background: var(--bg-primary);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.btn-secondary,
.btn-primary {
  padding: 10px 20px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary {
  background: var(--bg-elevated);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover:not(:disabled) {
  color: var(--text-primary);
  border-color: var(--border-color-strong);
}

.btn-primary {
  background: #1a1a1a;
  color: white;
  border: 1px solid #0f0f0f;
}

.btn-primary:hover:not(:disabled) {
  background: #111;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.btn-secondary:disabled,
.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 布局 */
.editor-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: var(--spacing-xl);
}

/* 表单 */
.form-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
}

.form-group {
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-xl);
  border-bottom: 1px solid var(--border-color);
}

.form-group:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.section-subtitle {
  font-size: var(--font-size-sm);
  font-weight: 400;
  color: var(--text-tertiary);
}

.field {
  margin-bottom: var(--spacing-md);
}

.field:last-child {
  margin-bottom: 0;
}

.field-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}

.field-label {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.field-input,
.field-select,
.field-textarea {
  width: 100%;
  padding: 10px 14px;
  font-size: var(--font-size-base);
  color: var(--text-primary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.field-input:focus,
.field-select:focus,
.field-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, #000 10%, transparent);
}

.field-textarea {
  resize: vertical;
  font-family: inherit;
  line-height: 1.6;
}

.code-textarea {
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: var(--font-size-sm);
}

.field-hint {
  margin-top: 6px;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.tags-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
}

.tag-remove {
  padding: 0;
  background: none;
  border: none;
  color: var(--text-tertiary);
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
}

.tag-remove:hover {
  color: var(--text-primary);
}

/* 预览 */
.preview-section {
  position: relative;
}

.preview-sticky {
  position: sticky;
  top: calc(var(--navbar-height) + var(--spacing-lg));
}

.preview-title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

.preview-card-wrapper {
  margin-bottom: var(--spacing-lg);
}

.preview-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  background: var(--bg-elevated);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  color: var(--text-tertiary);
}

.preview-placeholder svg {
  margin-bottom: var(--spacing-sm);
}

.preview-placeholder p {
  font-size: var(--font-size-sm);
  margin: 0;
}

.code-preview-section {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.code-preview-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  padding: var(--spacing-md);
  margin: 0;
  border-bottom: 1px solid var(--border-color);
}

.code-tabs {
  display: flex;
  gap: 4px;
  padding: var(--spacing-sm) var(--spacing-md) 0;
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.code-tab {
  padding: 8px 16px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.code-tab:hover {
  color: var(--text-primary);
}

.code-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

/* 响应式 */
@media (max-width: 1024px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }

  .preview-section {
    order: -1;
  }

  .preview-sticky {
    position: static;
  }
}

@media (max-width: 640px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-md);
  }

  .header-actions {
    width: 100%;
  }

  .btn-secondary,
  .btn-primary {
    flex: 1;
  }

  .field-row {
    grid-template-columns: 1fr;
  }
}
</style>
