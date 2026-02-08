<template>
  <div class="code-block">
    <div class="code-header">
      <span class="code-language">{{ language.toUpperCase() }}</span>
      <button @click="copyCode" class="btn-copy-code" :class="{ copied }">
        <svg v-if="!copied" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
          <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
        </svg>
        <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
        {{ copied ? t('common.copied') : t('common.copyCode') }}
      </button>
    </div>
    <pre :style="{ '--max-lines': String(maxLines) }"><code :class="`language-${language}`" v-html="highlightedCode"></code></pre>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import hljs from 'highlight.js/lib/core'
import javascript from 'highlight.js/lib/languages/javascript'
import xml from 'highlight.js/lib/languages/xml' // HTML
import css from 'highlight.js/lib/languages/css'

// 注册语言
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('html', xml)
hljs.registerLanguage('xml', xml)
hljs.registerLanguage('css', css)

const props = defineProps({
  code: {
    type: String,
    required: true
  },
  language: {
    type: String,
    default: 'html'
  },
  maxLines: {
    type: Number,
    default: 20
  }
})

const copied = ref(false)
const { t } = useI18n()

const normalizeCode = (source, lang) => {
  const text = String(source || '').replace(/\r\n/g, '\n')
  if (text.includes('\n')) return text

  if (lang === 'css') {
    return text
      .replace(/\{/g, ' {\n  ')
      .replace(/;/g, ';\n  ')
      .replace(/\}\s*/g, '\n}\n')
      .replace(/\n\s*\n+/g, '\n')
      .replace(/\n {2}\n/g, '\n')
      .trim()
  }

  if (lang === 'javascript' || lang === 'js') {
    return text
      .replace(/\{/g, ' {\n')
      .replace(/;/g, ';\n')
      .replace(/\}\s*/g, '\n}\n')
      .replace(/\n{2,}/g, '\n')
      .trim()
  }

  if (lang === 'html' || lang === 'xml') {
    return text
      .replace(/></g, '>\n<')
      .trim()
  }

  return text
}

const displayCode = computed(() => normalizeCode(props.code, props.language))

const highlightedCode = computed(() => {
  try {
    return hljs.highlight(displayCode.value, { language: props.language }).value
  } catch (e) {
    console.error('Highlight error:', e)
    return displayCode.value
  }
})

const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(props.code)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.code-block {
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.code-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-tertiary);
  border-bottom: 1px solid var(--border-color);
}

.code-language {
  font-size: var(--font-size-xs);
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.05em;
}

.btn-copy-code {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  font-size: var(--font-size-xs);
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-copy-code:hover {
  color: var(--text-primary);
  border-color: var(--border-color-strong);
  background: var(--bg-elevated);
}

.btn-copy-code.copied {
  color: var(--color-success);
  border-color: var(--color-success);
}

.btn-copy-code svg {
  flex-shrink: 0;
}

pre {
  margin: 0;
  padding: var(--spacing-md);
  max-height: calc(var(--max-lines, 20) * 1.6em + (var(--spacing-md) * 2));
  overflow-y: auto;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: var(--font-size-sm);
  line-height: 1.6;
  white-space: pre;
  word-break: normal;
  tab-size: 2;
}

code {
  display: block;
  color: var(--text-primary);
}

/* 代码高亮样式 - 浅色主题 */
:root {
  --hljs-keyword: #d73a49;
  --hljs-string: #032f62;
  --hljs-function: #6f42c1;
  --hljs-number: #005cc5;
  --hljs-comment: #6a737d;
  --hljs-tag: #22863a;
  --hljs-attr: #6f42c1;
}

/* 代码高亮样式 - 深色主题 */
.dark {
  --hljs-keyword: #ff7b72;
  --hljs-string: #a5d6ff;
  --hljs-function: #d2a8ff;
  --hljs-number: #79c0ff;
  --hljs-comment: #8b949e;
  --hljs-tag: #7ee787;
  --hljs-attr: #d2a8ff;
}

/* Highlight.js 样式覆盖 */
:deep(.hljs-keyword),
:deep(.hljs-selector-tag),
:deep(.hljs-literal),
:deep(.hljs-section),
:deep(.hljs-link) {
  color: var(--hljs-keyword);
  font-weight: 600;
}

:deep(.hljs-string),
:deep(.hljs-title),
:deep(.hljs-name),
:deep(.hljs-type),
:deep(.hljs-attribute),
:deep(.hljs-symbol),
:deep(.hljs-bullet),
:deep(.hljs-addition),
:deep(.hljs-variable),
:deep(.hljs-template-tag),
:deep(.hljs-template-variable) {
  color: var(--hljs-string);
}

:deep(.hljs-comment),
:deep(.hljs-quote),
:deep(.hljs-deletion),
:deep(.hljs-meta) {
  color: var(--hljs-comment);
  font-style: italic;
}

:deep(.hljs-doctag),
:deep(.hljs-strong) {
  font-weight: 700;
}

:deep(.hljs-emphasis) {
  font-style: italic;
}

:deep(.hljs-tag) {
  color: var(--hljs-tag);
}

:deep(.hljs-attr) {
  color: var(--hljs-attr);
}

:deep(.hljs-number) {
  color: var(--hljs-number);
}

:deep(.hljs-function) {
  color: var(--hljs-function);
}
</style>
