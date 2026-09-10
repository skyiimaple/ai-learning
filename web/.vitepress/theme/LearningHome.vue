<script setup>
import { withBase } from 'vitepress'
import catalog from '../../.generated/catalog.json'

const sectionIcons = { agent: 'AG', python: 'PY', node: 'JS' }
const firstPage = section => section.documents.find(d => !d.source.endsWith('README.md'))?.url ?? `/${section.id}/`
const latestDays = catalog.sections.find(s => s.id === 'python').documents.filter(d => /\/day\d+\/day\d+\.md$/.test(d.source)).slice(-5).reverse()
const lectures = catalog.sections.find(s => s.id === 'agent').documents.filter(d => !d.source.endsWith('README.md'))
const shortTitle = title => title.replace(/^Day\s*\d+\s*[·—-]\s*/, '')
const day = title => title.match(/^Day\s*(\d+)/)?.[1] || '—'
</script>

<template>
  <main class="learning-home" id="learning-home">
    <header class="home-intro">
      <div>
        <p class="eyebrow"><span class="tiny-square"></span> 学习档案 <span class="eyebrow-divider">/</span> FIELD NOTES</p>
        <h1>AI 学习笔记<span class="title-dot">.</span></h1>
        <p class="intro-copy">记录学习过程，也留下理解问题的路径。</p>
      </div>
      <div class="archive-stats" aria-label="内容统计">
        <div><strong>{{ String(catalog.totalDocuments).padStart(2, '0') }}</strong><span>篇文档</span></div>
        <span class="stat-separator"></span>
        <div><strong>03</strong><span>个目录</span></div>
      </div>
    </header>

    <section aria-labelledby="directories-title" class="directory-section">
      <div class="section-heading"><h2 id="directories-title">从目录开始</h2><span>INDEX / 01</span></div>
      <div class="directory-grid">
        <article v-for="(section, i) in catalog.sections" :key="section.id" class="directory-card">
          <div class="card-top"><span class="directory-icon" :class="section.id">{{ sectionIcons[section.id] }}</span><span class="card-number">0{{ i + 1 }}</span></div>
          <a :href="withBase(`/${section.id}/`)" class="directory-title">{{ section.id }}<span>/</span><span class="card-arrow" aria-hidden="true">↗</span></a>
          <h3>{{ section.label }}</h3>
          <p>{{ section.description }}</p>
          <div class="card-bottom"><span>{{ section.documents.length }} 篇文档</span><a :href="withBase(firstPage(section))">开始阅读 <span aria-hidden="true">→</span></a></div>
        </article>
      </div>
    </section>

    <div class="home-columns">
      <section aria-labelledby="days-title" class="day-section">
        <div class="section-heading"><h2 id="days-title">每日学习记录</h2><a :href="withBase('/python/')">查看全部 <span aria-hidden="true">↗</span></a></div>
        <p class="section-caption">python/ · 按学习日倒序</p>
        <div class="day-list">
          <a v-for="doc in latestDays" :key="doc.source" :href="withBase(doc.url)" class="day-row">
            <span class="day-index"><span>DAY</span><strong>{{ day(doc.title) }}</strong></span>
            <div class="day-summary"><h3>{{ shortTitle(doc.title) }}</h3><span>{{ doc.source }}</span></div>
            <span class="row-arrow" aria-hidden="true">→</span>
          </a>
          <p v-if="!latestDays.length" class="empty-message">还没有每日学习记录。</p>
        </div>
      </section>
      <section aria-labelledby="agent-title" class="lecture-section">
        <div class="section-heading"><h2 id="agent-title">Agent 工程讲义</h2><span>TOPIC / 02</span></div>
        <p class="section-caption">agent/teaching/ · 按讲次阅读</p>
        <div class="lecture-list">
          <a v-for="(doc, i) in lectures" :key="doc.source" :href="withBase(doc.url)" class="lecture-item">
            <span class="lecture-index">{{ String(i).padStart(2, '0') }}</span>
            <div><h3>{{ doc.title.replace(/^Agent 工程\s*·\s*/, '') }}</h3><span>阅读讲义 <span aria-hidden="true">↗</span></span></div>
          </a>
          <p v-if="!lectures.length" class="empty-message">还没有专题讲义。</p>
        </div>
        <div class="reference-note"><span class="reference-mark" aria-hidden="true">↳</span><p>回看路线与阶段安排<a :href="withBase('/python/')">前往 python 目录 <span aria-hidden="true">→</span></a></p></div>
      </section>
    </div>
    <div class="home-colophon"><span>ai-learning</span><p>一点一点，积累成自己的知识。</p><span>LEARN · BUILD · REFLECT</span></div>
  </main>
</template>
