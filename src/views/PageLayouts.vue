<template>
  <PromptCategoryPage
    category-key="layouts"
    title-key="categories.layouts.title"
    description-key="categories.layouts.description"
    :subcategory-labels="subcategoryLabels"
  />
</template>

<script setup>
import PromptCategoryPage from '@/components/prompt/PromptCategoryPage.vue'

const subcategoryLabels = {
  hero: { zh: '首屏', en: 'Hero' },
  sidebar: { zh: '侧栏', en: 'Sidebar' },
  grid: { zh: '网格布局', en: 'Grid' },
  masonry: { zh: '瀑布流', en: 'Masonry' },
  split: { zh: '分屏布局', en: 'Split' },
}
</script>

