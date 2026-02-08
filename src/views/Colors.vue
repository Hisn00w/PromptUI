<template>
  <PromptCategoryPage
    category-key="colors"
    title-key="categories.colors.title"
    description-key="categories.colors.description"
    :subcategory-labels="subcategoryLabels"
  />
</template>

<script setup>
import PromptCategoryPage from '@/components/prompt/PromptCategoryPage.vue'

const subcategoryLabels = {
  business: { zh: '商业配色', en: 'Business' },
  neutral: { zh: '中性配色', en: 'Neutral' },
  warm: { zh: '暖色方案', en: 'Warm' },
  dark: { zh: '深色方案', en: 'Dark' },
}
</script>
