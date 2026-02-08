<template>
  <teleport to="body">
    <transition name="drawer">
      <div v-if="isOpen" class="drawer-overlay" @click="$emit('close')">
        <aside class="drawer" @click.stop>
          <header class="drawer-header glass">
            <div>
              <h2 class="drawer-title">{{ item?.name }}</h2>
              <p class="drawer-sub">{{ t('common.prompt') }}</p>
            </div>
            <button class="close-btn" @click="$emit('close')" aria-label="Close">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="20" height="20">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
              </svg>
            </button>
          </header>

          <section class="drawer-tags" v-if="item?.tags?.length">
            <span class="section-label">{{ t('common.tags') }}</span>
            <div class="tags-list">
              <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
          </section>

          <section class="drawer-prompt">
            <div class="prompt-header">
              <span class="section-label">{{ t('common.prompt') }}</span>
              <CopyButton :text="item?.prompt || ''" />
            </div>
            <div class="prompt-content"><pre>{{ item?.prompt }}</pre></div>
          </section>
        </aside>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import CopyButton from '@/components/common/CopyButton.vue'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  item: {
    type: Object,
    default: null
  }
})

defineEmits(['close'])

const { t } = useI18n()
</script>

<style scoped>
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(7, 10, 16, 0.45);
  backdrop-filter: blur(6px);
  z-index: 2000;
  display: flex;
  justify-content: flex-end;
}

.drawer {
  width: 100%;
  max-width: 620px;
  height: 100%;
  background: var(--bg-primary);
  border-left: 1px solid var(--border-color);
  box-shadow: var(--shadow-xl);
  overflow-y: auto;
}

.drawer-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.drawer-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--text-primary);
}

.drawer-sub {
  margin-top: 0.2rem;
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.close-btn {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 1px solid var(--border-color);
  background: var(--bg-elevated);
  border-radius: 10px;
  color: var(--text-secondary);
}

.close-btn:hover {
  color: var(--text-primary);
}

.drawer-tags,
.drawer-prompt {
  padding: 0 var(--spacing-lg) var(--spacing-lg);
}

.drawer-tags {
  padding-top: var(--spacing-lg);
}

.section-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-secondary);
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.38rem;
  margin-top: 0.58rem;
}

.prompt-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.58rem;
}

.prompt-content {
  border: 1px solid var(--border-color);
  background: color-mix(in srgb, var(--bg-tertiary) 78%, var(--bg-primary));
  border-radius: 12px;
  padding: 0.95rem;
}

.prompt-content pre {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 0.84rem;
  color: var(--text-primary);
  white-space: pre-wrap;
  line-height: 1.65;
  margin: 0;
}

.drawer-enter-active,
.drawer-leave-active {
  transition: opacity var(--transition-base);
}

.drawer-enter-active .drawer,
.drawer-leave-active .drawer {
  transition: transform var(--transition-base);
}

.drawer-enter-from,
.drawer-leave-to {
  opacity: 0;
}

.drawer-enter-from .drawer,
.drawer-leave-to .drawer {
  transform: translateX(100%);
}
</style>
