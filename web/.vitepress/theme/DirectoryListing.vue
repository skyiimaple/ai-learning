<script setup>
import { computed } from 'vue'
import { withBase } from 'vitepress'
import catalog from '../../.generated/catalog.json'
const props = defineProps({ section: { type: String, required: true } })
const content = computed(() => catalog.sections.find(s => s.id === props.section))
</script>
<template>
  <div v-if="content" class="directory-listing">
    <p class="listing-count">{{ content.id }}/ · {{ content.documents.length }} 篇文档</p>
    <a v-for="doc in content.documents" :key="doc.source" :href="withBase(doc.url)" class="listing-row">
      <div><strong>{{ doc.title }}</strong><span>{{ doc.source }}</span></div><span aria-hidden="true">→</span>
    </a>
    <p v-if="!content.documents.length">该目录暂时没有 Markdown 文档。</p>
    <template v-if="content.resources.length">
      <h2>现有资料</h2>
      <a v-for="resource in content.resources" :key="resource.url" :href="withBase(resource.url)" class="listing-row"><strong>{{ resource.title }}</strong><span aria-hidden="true">↗</span></a>
    </template>
  </div>
</template>
