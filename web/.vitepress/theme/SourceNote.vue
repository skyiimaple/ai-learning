<script setup>
import { useData, withBase } from 'vitepress'
const { frontmatter } = useData()
</script>
<template>
  <div v-if="frontmatter.sourcePath" class="source-note">
    <a :href="withBase('/' + frontmatter.sourcePath.split('/')[0] + '/')">{{ frontmatter.sourcePath.split('/')[0] }}</a>
    <span aria-hidden="true">/</span><span>{{ frontmatter.sourcePath.split('/').slice(1).join('/') }}</span>
  </div>
</template>
