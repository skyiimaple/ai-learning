<script setup>
import { withBase } from 'vitepress'
defineProps({ src: { type: String, required: true }, title: { type: String, required: true } })
</script>
<template>
  <div class="reference-page">
    <p><a :href="withBase(src)" target="_blank" rel="noopener">在新窗口完整阅读 {{ title }} ↗</a></p>
    <iframe :src="withBase(src)" :title="title" loading="lazy" class="reference-frame"></iframe>
  </div>
</template>
