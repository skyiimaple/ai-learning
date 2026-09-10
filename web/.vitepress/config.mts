import { defineConfig } from 'vitepress'
import catalog from '../.generated/catalog.json'
import { tokenize } from '../scripts/search.mjs'

const base = process.env.VITEPRESS_BASE || '/'
if (!base.startsWith('/') || !base.endsWith('/')) throw new Error('VITEPRESS_BASE 必须以 / 开头和结尾')

export default defineConfig({
  lang: 'zh-CN',
  title: 'ai-learning',
  description: 'AI 学习笔记：Agent 工程讲义、每日学习记录与前端实践。',
  base,
  srcDir: '.generated',
  cleanUrls: false,
  // These are intentional links to separately started local demo services.
  ignoreDeadLinks: [/^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/|$)/],
  markdown: { languageAlias: { env: 'shellscript' } },
  head: [['link', { rel: 'icon', type: 'image/svg+xml', href: `${base}favicon.svg` }]],
  themeConfig: {
    logo: '/favicon.svg',
    siteTitle: 'ai-learning',
    nav: [
      { text: '首页', link: '/' },
      ...catalog.sections.map(s => ({ text: s.id, link: `/${s.id}/`, activeMatch: `^/${s.id}/` }))
    ],
    sidebar: Object.fromEntries(catalog.sections.map(s => [`/${s.id}/`, s.sidebar])),
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '文档目录',
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    skipToContentLabel: '跳到正文',
    footer: { message: '持续学习，认真记录。', copyright: 'ai-learning · 个人学习档案' },
    search: {
      provider: 'local',
      options: {
        miniSearch: {
          options: {
            tokenize
          }
        },
        locales: {
          root: {
            translations: {
              button: { buttonText: '搜索笔记', buttonAriaLabel: '搜索笔记' },
              modal: {
                displayDetails: '显示摘要', resetButtonTitle: '清空搜索', backButtonTitle: '返回',
                noResultsText: '没有找到相关笔记',
                footer: { selectText: '选择', selectKeyAriaLabel: '回车', navigateText: '切换', navigateUpKeyAriaLabel: '上方向键', navigateDownKeyAriaLabel: '下方向键', closeText: '关闭', closeKeyAriaLabel: 'Escape' }
              }
            }
          }
        }
      }
    }
  }
})
