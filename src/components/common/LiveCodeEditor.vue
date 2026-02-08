<template>
  <div class="live-code-editor">
    <!-- 编辑/预览切换 -->
    <div class="editor-header">
      <div class="mode-tabs">
        <button 
          :class="['mode-tab', { active: mode === 'edit' }]"
          @click="mode = 'edit'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          编辑代码
        </button>
        <button 
          :class="['mode-tab', { active: mode === 'preview' }]"
          @click="mode = 'preview'"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
          </svg>
          实时预览
        </button>
      </div>
      <button class="btn-reset" @click="resetCode" title="重置代码">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 12a9 9 0 019-9 9.75 9.75 0 016.74 2.74L21 8"/>
          <path d="M21 3v5h-5"/>
        </svg>
      </button>
    </div>

    <!-- 编辑模式 -->
    <div v-if="mode === 'edit'" class="editor-mode">
      <div class="code-tabs">
        <button 
          v-for="lang in languages" 
          :key="lang.key"
          :class="['code-tab', { active: activeLanguage === lang.key }]"
          @click="activeLanguage = lang.key"
        >
          {{ lang.label }}
        </button>
      </div>
      <div class="code-editor">
        <textarea 
          v-model="editableCode[activeLanguage]"
          :placeholder="`输入 ${languages.find(l => l.key === activeLanguage)?.label} 代码...`"
          spellcheck="false"
          @input="debouncedUpdate"
        ></textarea>
      </div>
    </div>

    <!-- 预览模式 -->
    <div v-else class="preview-mode">
      <div class="live-preview-container">
        <iframe 
          ref="previewFrame"
          :srcdoc="previewHTML"
          sandbox="allow-scripts"
          class="preview-iframe"
        ></iframe>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  initialCode: {
    type: Object,
    default: () => ({ html: '', css: '', js: '' })
  }
})

const mode = ref('preview') // 'edit' or 'preview'
const activeLanguage = ref('html')
const editableCode = ref({
  html: props.initialCode.html || '',
  css: props.initialCode.css || '',
  js: props.initialCode.js || ''
})

const languages = [
  { key: 'html', label: 'HTML' },
  { key: 'css', label: 'CSS' },
  { key: 'js', label: 'JavaScript' }
]

const previewFrame = ref(null)

// 生成预览 HTML
const previewHTML = computed(() => {
  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      padding: 20px;
      background: #f5f5f5;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    ${editableCode.value.css}
  </style>
</head>
<body>
  ${editableCode.value.html}
  <script>
    try {
      ${editableCode.value.js}
    } catch (e) {
      console.error('JavaScript Error:', e);
    }
  <\/script>
</body>
</html>
  `.trim()
})

// 防抖更新
let updateTimer = null
const debouncedUpdate = () => {
  clearTimeout(updateTimer)
  updateTimer = setTimeout(() => {
    // 自动切换到预览模式查看效果
    if (mode.value === 'edit') {
      mode.value = 'preview'
    }
  }, 1000)
}

// 重置代码
const resetCode = () => {
  if (confirm('确定要重置代码吗？')) {
    editableCode.value = {
      html: props.initialCode.html || '',
      css: props.initialCode.css || '',
      js: props.initialCode.js || ''
    }
  }
}

// 监听初始代码变化
watch(() => props.initialCode, (newCode) => {
  editableCode.value = {
    html: newCode.html || '',
    css: newCode.css || '',
    js: newCode.js || ''
  }
}, { deep: true })
</script>

<style scoped>
.live-code-editor {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg-primary);
}

.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
}

.mode-tabs {
  display: flex;
  gap: 8px;
}

.mode-tab {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-tab:hover {
  color: var(--text-primary);
  border-color: var(--border-color-strong);
}

.mode-tab.active {
  color: white;
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
}

.btn-reset {
  padding: 8px;
  color: var(--text-secondary);
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-reset:hover {
  color: var(--text-primary);
  border-color: var(--border-color-strong);
}

/* 编辑模式 */
.editor-mode {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.code-tabs {
  display: flex;
  gap: 4px;
  padding: 12px 16px 0;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
}

.code-tab {
  padding: 8px 16px;
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.code-tab:hover {
  color: var(--text-primary);
}

.code-tab.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
}

.code-editor {
  flex: 1;
  overflow: hidden;
}

.code-editor textarea {
  width: 100%;
  height: 100%;
  padding: 16px;
  font-family: 'Monaco', 'Menlo', 'Consolas', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-primary);
  background: var(--bg-primary);
  border: none;
  outline: none;
  resize: none;
  tab-size: 2;
}

.code-editor textarea::placeholder {
  color: var(--text-tertiary);
}

/* 预览模式 */
.preview-mode {
  flex: 1;
  overflow: hidden;
  background: #f5f5f5;
}

.live-preview-container {
  width: 100%;
  height: 100%;
  position: relative;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: white;
}

/* 深色主题适配 */
.dark .preview-mode {
  background: #1a1a1a;
}

.dark .preview-iframe {
  background: #2a2a2a;
}
</style>
