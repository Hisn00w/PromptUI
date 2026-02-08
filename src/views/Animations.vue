<template>
  <PromptCategoryPage
    category-key="animations"
    title-key="categories.animations.title"
    description-key="categories.animations.description"
    :subcategory-labels="subcategoryLabels"
  />
</template>

<script setup>
import PromptCategoryPage from '@/components/prompt/PromptCategoryPage.vue'

const subcategoryLabels = {
  entrance: { zh: '入场动画', en: 'Entrance' },
  hover: { zh: '悬浮反馈', en: 'Hover' },
  loading: { zh: '加载状态', en: 'Loading' },
  micro: { zh: '微交互', en: 'Micro' },
}
</script>
