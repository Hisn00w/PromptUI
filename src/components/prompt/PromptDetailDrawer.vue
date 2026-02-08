<template>
  <Teleport to="body">
    <Transition name="drawer">
      <div v-if="isOpen" class="drawer-overlay" @click="handleClose">
        <div class="drawer-container" @click.stop>
          <header class="drawer-header">
            <button class="btn-back" @click="handleClose">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              {{ t('common.back') }}
            </button>
            <h2 class="drawer-title">{{ item?.name }}</h2>
            <button class="btn-copy-prompt" @click="copyPrompt" :class="{ copied: promptCopied }">
              <svg v-if="!promptCopied" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
              {{ promptCopied ? t('common.copied') : t('common.copy') }}
            </button>
          </header>

          <div class="drawer-body">
            <div class="preview-section">
              <div class="preview-wrapper">
                <iframe
                  v-if="previewSrcdoc"
                  :srcdoc="previewSrcdoc"
                  class="preview-frame"
                  sandbox="allow-scripts"
                  title="Prompt preview"
                />
                <div v-else class="preview-placeholder">
                  <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <path d="M9 3v18M15 3v18M3 9h18M3 15h18"/>
                  </svg>
                  <p>{{ t('common.noPreview') }}</p>
                </div>
              </div>
            </div>

            <div class="code-section">
              <div class="content-tabs">
                <button
                  v-for="tab in contentTabs"
                  :key="tab.key"
                  :class="['content-tab', { active: activeContentTab === tab.key }]"
                  @click="activeContentTab = tab.key"
                >
                  {{ tab.label }}
                </button>
              </div>

              <div class="tab-content">
                <div v-if="activeContentTab === 'prompt'" class="prompt-content">
                  <p>{{ item?.prompt }}</p>
                </div>

                <div v-else class="code-playground">
                  <aside v-if="frameworkTabs.length" class="framework-tabs">
                    <button
                      v-for="tab in frameworkTabs"
                      :key="tab.key"
                      :class="['framework-tab', { active: activeFrameworkTab === tab.key }]"
                      @click="activeFrameworkTab = tab.key"
                    >
                      {{ tab.label }}
                    </button>
                  </aside>

                  <div class="code-playground-main">
                    <CodeBlock
                      v-if="activeFrameworkCode"
                      :code="activeFrameworkCode.content"
                      :language="activeFrameworkCode.language"
                    />
                    <div v-else class="no-code">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/>
                      </svg>
                      <p>{{ t('common.noCodeAssets') }}</p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="item?.tags?.length" class="tags-section">
                <span class="tags-label">{{ t('common.tags') }}:</span>
                <span v-for="tag in item.tags" :key="tag" class="tag">#{{ tag }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import CodeBlock from '../common/CodeBlock.vue'
import { promptsAPI } from '@/api'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  item: { type: Object, default: null }
})

const emit = defineEmits(['close'])
const { t } = useI18n()

const activeContentTab = ref('prompt')
const activeFrameworkTab = ref('')
const promptCopied = ref(false)

const inferLanguage = (name) => {
  const lower = name.toLowerCase()
  if (lower.includes('tailwind')) return 'html'
  if (lower === 'vue') return 'html'
  if (lower === 'react') return 'javascript'
  if (lower === 'svelte') return 'html'
  if (lower === 'lit') return 'javascript'
  if (lower.endsWith('.vue')) return 'html'
  if (lower.endsWith('.css')) return 'css'
  if (lower.endsWith('.js') || lower.endsWith('.ts')) return 'javascript'
  if (lower.endsWith('.json')) return 'json'
  return 'plaintext'
}

const extractFromVueSfc = (source) => {
  const text = String(source || '')
  const templateMatch = text.match(/<template>([\s\S]*?)<\/template>/i)
  const styleMatches = [...text.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)]
  const scriptMatch = text.match(/<script[^>]*>([\s\S]*?)<\/script>/i)

  return {
    html: (templateMatch?.[1] || '').trim(),
    css: styleMatches.map((m) => m[1].trim()).filter(Boolean).join('\n\n'),
    js: (scriptMatch?.[1] || '').trim(),
  }
}

const pickPreviewFromFiles = (files) => {
  const fileEntries = Object.entries(files || {})
  if (!fileEntries.length) return { html: '', css: '', js: '' }

  const html = fileEntries.find(([name]) => /\.html?$/i.test(name))?.[1] || ''
  const css = fileEntries.filter(([name]) => /\.css$/i.test(name)).map(([, content]) => String(content || '')).join('\n\n')
  const js = fileEntries
    .filter(([name]) => /\.(js|mjs|cjs|ts)$/i.test(name))
    .map(([, content]) => String(content || ''))
    .join('\n\n')

  if (html || css || js) {
    return { html: String(html || ''), css, js }
  }

  const vueLike = fileEntries.find(([name]) => /\.vue$/i.test(name))?.[1] || ''
  if (vueLike) {
    return extractFromVueSfc(vueLike)
  }

  return { html: '', css: '', js: '' }
}

const previewBundle = computed(() => {
  const preview = props.item?.codeAssets?.preview || {}
  const html = String(preview.html || '')
  const css = String(preview.css || '')
  const js = String(preview.js || '')
  if (html || css || js) return { html, css, js }

  const raw = props.item?.codeAssets || {}
  const rawHtml = String(raw.html || '')
  const rawCss = String(raw.css || '')
  const rawJs = String(raw.js || '')
  if (rawHtml || rawCss || rawJs) return { html: rawHtml, css: rawCss, js: rawJs }

  return pickPreviewFromFiles(props.item?.codeAssets?.files || {})
})

const previewSrcdoc = computed(() => {
  const html = previewBundle.value.html.trim()
  const css = previewBundle.value.css.trim()
  const js = previewBundle.value.js.trim()
  if (!html && !css && !js) return ''

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    :root { color-scheme: light; }
    * { box-sizing: border-box; }
    html, body { margin: 0; width: 100%; min-height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f4f4f4; }
    body { display: flex; align-items: center; justify-content: center; padding: 24px; }
    #app { width: 100%; max-width: 680px; }
    ${css}
  </style>
</head>
<body>
  <div id="app">${html}</div>
  <script>
    try {
      ${js}
    } catch (err) {
      const pre = document.createElement('pre');
      pre.textContent = String(err);
      pre.style.color = '#b00020';
      pre.style.background = '#fff0f0';
      pre.style.padding = '8px 10px';
      pre.style.borderRadius = '8px';
      document.body.appendChild(pre);
    }
  <\/script>
</body>
</html>`
})

const normalizedFrameworks = computed(() => {
  const frameworks = props.item?.codeAssets?.frameworks || {}
  const frameworkEntries = Object.entries(frameworks).map(([key, value]) => {
    const label =
      value?.label ||
      (key === 'html_tailwind'
        ? 'HTML + TailwindCSS'
        : key.replace(/_/g, ' ').replace(/\b\w/g, (s) => s.toUpperCase()))
    return {
      key,
      label,
      language: value?.language || inferLanguage(key),
      content: String(value?.code || ''),
    }
  })
  return frameworkEntries.filter((entry) => entry.content.trim().length > 0)
})

const legacyCodeFiles = computed(() => {
  const files = props.item?.codeAssets?.files || {}
  return Object.entries(files).map(([name, content]) => ({
    key: `legacy:${name}`,
    label: name,
    language: inferLanguage(name),
    content: String(content || ''),
  }))
})

const rawCodeTabs = computed(() => {
  const code = props.item?.codeAssets || {}
  const tabs = []
  if (String(code.html || '').trim()) {
    tabs.push({
      key: 'raw:html',
      label: 'HTML',
      language: 'html',
      content: String(code.html || ''),
    })
  }
  if (String(code.css || '').trim()) {
    tabs.push({
      key: 'raw:css',
      label: 'CSS',
      language: 'css',
      content: String(code.css || ''),
    })
  }
  if (String(code.js || '').trim()) {
    tabs.push({
      key: 'raw:js',
      label: 'JavaScript',
      language: 'javascript',
      content: String(code.js || ''),
    })
  }
  return tabs
})

const frameworkTabs = computed(() => {
  if (normalizedFrameworks.value.length > 0) return normalizedFrameworks.value
  if (rawCodeTabs.value.length > 0) return rawCodeTabs.value
  return legacyCodeFiles.value
})

const activeFrameworkCode = computed(() => {
  if (!activeFrameworkTab.value) return null
  return frameworkTabs.value.find((f) => f.key === activeFrameworkTab.value) || null
})

const contentTabs = computed(() => {
  const tabs = [{ key: 'prompt', label: t('common.prompt') }]
  if (frameworkTabs.value.length > 0) {
    tabs.push({ key: 'code', label: t('common.code') })
  }
  return tabs
})

const copyPrompt = async () => {
  if (!props.item?.prompt) return
  try {
    await navigator.clipboard.writeText(props.item.prompt)
    if (props.item?.id) await promptsAPI.recordCopy(props.item.id, 'drawer')
    promptCopied.value = true
    setTimeout(() => {
      promptCopied.value = false
    }, 1800)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}

const handleClose = () => emit('close')

watch(
  () => props.isOpen,
  (val) => {
    if (val) {
      activeContentTab.value = frameworkTabs.value.length > 0 ? 'code' : 'prompt'
      activeFrameworkTab.value = frameworkTabs.value[0]?.key || ''
      promptCopied.value = false
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
  }
)

watch(
  frameworkTabs,
  (tabs) => {
    if (!props.isOpen) return
    if (!tabs.length) {
      activeContentTab.value = 'prompt'
      activeFrameworkTab.value = ''
      return
    }
    if (!activeFrameworkTab.value || !tabs.some((t) => t.key === activeFrameworkTab.value)) {
      activeFrameworkTab.value = tabs[0].key
    }
    if (activeContentTab.value !== 'code') {
      activeContentTab.value = 'code'
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

.drawer-container {
  width: 100%;
  max-width: 1400px;
  height: 90vh;
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2xl);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.drawer-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-elevated);
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.drawer-title {
  flex: 1;
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.btn-copy-prompt {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-inverse);
  background: linear-gradient(180deg, #1a1a1a 0%, #000000 100%);
  border: none;
  border-radius: var(--radius-md);
}

.btn-copy-prompt.copied {
  background: var(--color-success);
}

.drawer-body {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  overflow: hidden;
}

.preview-section {
  background: var(--bg-tertiary);
  border-right: 1px solid var(--border-color);
  overflow: auto;
}

.preview-wrapper {
  min-height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
}

.preview-frame {
  width: 100%;
  height: 100%;
  min-height: 340px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  background: #f5f3ef;
}

.preview-placeholder {
  text-align: center;
  color: var(--text-tertiary);
  opacity: 0.5;
}

.code-section {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.content-tabs {
  display: flex;
  gap: 4px;
  padding: var(--spacing-md) var(--spacing-lg) 0;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
  overflow-x: auto;
}

.content-tab {
  padding: 10px 14px;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  white-space: nowrap;
}

.content-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.tab-content {
  flex: 1;
  overflow: auto;
  padding: var(--spacing-lg);
}

.prompt-content {
  font-size: var(--font-size-base);
  line-height: 1.8;
  color: var(--text-primary);
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
}

.code-playground {
  display: grid;
  grid-template-columns: 170px 1fr;
  gap: var(--spacing-md);
  height: 100%;
}

.framework-tabs {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 2px;
  border-right: 1px solid var(--border-color);
}

.framework-tab {
  text-align: left;
  padding: 10px 12px;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 600;
}

.framework-tab:hover {
  background: var(--bg-tertiary);
  color: var(--text-primary);
}

.framework-tab.active {
  background: var(--bg-elevated);
  border-color: var(--border-color);
  color: var(--text-primary);
}

.code-playground-main {
  min-width: 0;
}

.no-code {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 260px;
  color: var(--text-tertiary);
}

.tags-section {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
  padding: var(--spacing-md) var(--spacing-lg);
  border-top: 1px solid var(--border-color);
  background: var(--bg-elevated);
}

.tags-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--text-secondary);
}

.tag {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  padding: 4px 10px;
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity 0.3s ease;
}

.drawer-enter-active .drawer-container,
.drawer-leave-active .drawer-container {
  transition: transform 0.3s ease;
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer-container,
.drawer-leave-to .drawer-container {
  transform: scale(0.95);
}

@media (max-width: 968px) {
  .drawer-body {
    grid-template-columns: 1fr;
    grid-template-rows: 300px 1fr;
  }

  .preview-section {
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }

  .code-playground {
    grid-template-columns: 1fr;
  }

  .framework-tabs {
    flex-direction: row;
    overflow-x: auto;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
  }

  .framework-tab {
    white-space: nowrap;
  }
}

@media (max-width: 640px) {
  .drawer-overlay {
    padding: 0;
  }

  .drawer-container {
    max-width: 100%;
    height: 100vh;
    border-radius: 0;
  }

  .drawer-header {
    padding: var(--spacing-md);
  }

  .drawer-title {
    font-size: var(--font-size-lg);
  }

  .btn-copy-prompt {
    padding: 8px 12px;
    font-size: var(--font-size-xs);
  }
}
</style>
