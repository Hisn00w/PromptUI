<template>
  <PromptCategoryPage
    category-key="components"
    title-key="categories.components.title"
    description-key="categories.components.description"
    :subcategory-labels="subcategoryLabels"
  />
</template>

<script setup>
import PromptCategoryPage from '@/components/prompt/PromptCategoryPage.vue'

const subcategoryLabels = {
  buttons: { zh: '按钮', en: 'Buttons' },
  inputs: { zh: '输入框', en: 'Inputs' },
  navbar: { zh: '导航栏', en: 'Navbar' },
  modal: { zh: '弹窗', en: 'Modal' },
  tabs: { zh: '选项卡', en: 'Tabs' },
}
</script>
