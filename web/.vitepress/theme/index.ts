import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import LearningHome from './LearningHome.vue'
import SourceNote from './SourceNote.vue'
import DirectoryListing from './DirectoryListing.vue'
import ReferencePage from './ReferencePage.vue'
import './style.css'
import { configureLocalSearch } from '../../scripts/search.mjs'

export default {
  extends: DefaultTheme,
  Layout: () => h(DefaultTheme.Layout, null, {
    'home-hero-before': () => h(LearningHome),
    'doc-before': () => h(SourceNote)
  }),
  enhanceApp({ app, siteData }) {
    configureLocalSearch(siteData.value.themeConfig)
    app.component('DirectoryListing', DirectoryListing)
    app.component('ReferencePage', ReferencePage)
  }
}
