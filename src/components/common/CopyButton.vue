<template>
  <button
    class="copy-btn"
    :class="{ copied: isCopied }"
    @click="copyToClipboard"
  >
    <svg v-if="!isCopied" viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
    </svg>
    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" width="16" height="16" aria-hidden="true">
      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
    </svg>
    <span class="copy-text">{{ isCopied ? t('common.copied') : t('common.copy') }}</span>
  </button>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  text: {
    type: String,
    required: true
  }
})
const emit = defineEmits(['copied'])

const { t } = useI18n()
const isCopied = ref(false)

const copyToClipboard = async () => {
  try {
    await navigator.clipboard.writeText(props.text)
    emit('copied')
    isCopied.value = true
    setTimeout(() => {
      isCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>

<style scoped>
.copy-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  padding: 0.42rem 0.9rem;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-primary);
  background: color-mix(in srgb, var(--color-primary) 12%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 20%, transparent);
  border-radius: var(--radius-full);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.copy-btn:hover {
  transform: translateY(-1px);
  background: color-mix(in srgb, var(--color-primary) 16%, transparent);
  border-color: color-mix(in srgb, var(--color-primary) 30%, transparent);
}

.copy-btn.copied {
  color: var(--color-success);
  border-color: color-mix(in srgb, var(--color-success) 35%, transparent);
  background: color-mix(in srgb, var(--color-success) 14%, transparent);
}

.copy-text {
  white-space: nowrap;
}
</style>
