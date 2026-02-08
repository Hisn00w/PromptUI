<template>
  <PromptCategoryPage
    category-key="cards"
    title-key="categories.cards.title"
    description-key="categories.cards.description"
    :subcategory-labels="subcategoryLabels"
  />
</template>

<script setup>
import PromptCategoryPage from '@/components/prompt/PromptCategoryPage.vue'

const subcategoryLabels = {
  product: { zh: '产品卡片', en: 'Product' },
  user: { zh: '用户卡片', en: 'User' },
  stats: { zh: '统计卡片', en: 'Stats' },
  pricing: { zh: '定价卡片', en: 'Pricing' },
  feature: { zh: '功能卡片', en: 'Feature' },
}
</script>
