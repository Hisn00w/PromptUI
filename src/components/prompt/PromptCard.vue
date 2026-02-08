<template>
  <article class="prompt-card card" :style="{ '--card-delay': `${Math.min(index, 10) * 35}ms` }" @click="$emit('select', item)">
    <!-- 实时代码预览区域 -->
    <div class="preview-area">
      <iframe
        v-if="hasCode"
        :srcdoc="previewHTML"
        sandbox="allow-scripts"
        class="preview-iframe"
        scrolling="no"
      ></iframe>
      <div v-else class="preview-placeholder">
        <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="3" width="18" height="18" rx="2"/>
          <path d="M8 8h8M8 12h8M8 16h5"/>
        </svg>
      </div>
    </div>

    <div class="card-content">
      <div class="prompt-head">
        <span class="prompt-chip">PROMPT</span>
        <span class="prompt-meta">{{ promptLength }} chars</span>
      </div>

      <h3 class="card-title">{{ item.name }}</h3>
      <p class="prompt-snippet">{{ promptSnippet }}</p>

      <div class="card-tags">
        <span v-for="tag in item.tags?.slice(0, 3)" :key="tag" class="tag">{{ tag }}</span>
      </div>

      <div class="card-actions">
        <button class="detail-btn" @click.stop="$emit('select', item)">{{ t('common.viewDetail') }}</button>
        <CopyButton :text="item.prompt" @click.stop @copied="$emit('copied', item)" />
      </div>
    </div>
  </article>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CopyButton from '@/components/common/CopyButton.vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  },
  index: {
    type: Number,
    default: 0,
  }
})

defineEmits(['select', 'copied'])
const { t } = useI18n()

// 检查是否有代码
const hasCode = computed(() => {
  const code = props.item.code || props.item.codeAssets
  if (props.item.hasCodeAssets && code && typeof code === 'object' && Object.keys(code).length === 0) {
    return true
  }
  if (!code) return false
  if (code.preview && (code.preview.html || code.preview.css || code.preview.js)) return true
  // 支持两种格式：直接 {html, css, js} 或 {files: {...}}
  if (code.html || code.css || code.js) return true
  if (code.files) {
    return Object.keys(code.files).some(name => 
      name.endsWith('.html') || name.endsWith('.css') || name.endsWith('.js') || name.endsWith('.vue')
    )
  }
  return false
})

// 生成预览 HTML
const previewHTML = computed(() => {
  const code = props.item.code || props.item.codeAssets || {}
  
  let html = ''
  let css = ''
  let js = ''
  
  if (code.preview && (code.preview.html || code.preview.css || code.preview.js)) {
    html = String(code.preview.html || '')
    css = String(code.preview.css || '')
    js = String(code.preview.js || '')
  }
  // 支持两种格式
  else if (code.html || code.css || code.js) {
    html = code.html || ''
    css = code.css || ''
    js = code.js || ''
  } else if (code.files) {
    // 从 files 中提取代码
    for (const [name, content] of Object.entries(code.files)) {
      if (name.endsWith('.html') || name.endsWith('.vue')) {
        // 从 Vue 文件中提取 template 内容
        const templateMatch = content.match(/<template>([\s\S]*?)<\/template>/i)
        html = templateMatch ? templateMatch[1] : content
      }
      if (name.endsWith('.css')) {
        css += content
      }
      if (name.endsWith('.js')) {
        js += content
      }
    }
  }
  
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { 
      width: 100%; 
      height: 100%; 
      overflow: hidden;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    body {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 8px;
      background: #212121;
    }
    ${css}
  </style>
</head>
<body>
  ${html}
  <script>
    try { ${js} } catch(e) { console.error(e); }
  <\/script>
</body>
</html>
  `.trim()
})

const promptSnippet = computed(() => {
  const raw = (props.item.prompt || '').replace(/\s+/g, ' ').trim()
  return raw.length > 100 ? `${raw.slice(0, 100)}...` : raw
})

const promptLength = computed(() => (props.item.prompt || '').length)
</script>

<style scoped>
.prompt-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: all var(--transition-base);
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  animation: cardIn 360ms ease-out both;
  animation-delay: var(--card-delay, 0ms);
}

.prompt-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--border-color-strong);
}

.preview-area {
  position: relative;
  width: 100%;
  height: 200px;
  background: #f8f6f3;
  border-bottom: 1px solid var(--border-color);
  overflow: hidden;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  pointer-events: none;
  background: #f8f6f3;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  opacity: 0.34;
}

.card-content {
  padding: var(--spacing-md);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  flex: 1;
}

.prompt-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.prompt-chip {
  font-size: var(--font-size-xs);
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 24%, transparent);
  border-radius: var(--radius-full);
  padding: 4px 10px;
}

.prompt-meta {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.card-title {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.3;
  margin: 0;
}

.prompt-snippet {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--spacing-sm);
  margin: 0;
}

.card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.card-actions {
  margin-top: auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-sm);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-color);
}

.detail-btn {
  flex: 1;
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 600;
  border-radius: var(--radius-full);
  padding: 8px 16px;
  transition: all var(--transition-fast);
}

.detail-btn:hover {
  color: var(--text-primary);
  border-color: var(--border-color-strong);
  background: var(--bg-elevated);
}

@keyframes cardIn {
  from {
    opacity: 0;
    transform: translateY(14px) scale(0.985);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 640px) {
  .preview-area {
    height: 170px;
  }
}
</style>
