import { test } from 'node:test'
import assert from 'node:assert/strict'
import MiniSearch from 'minisearch'
import { configureLocalSearch } from '../scripts/search.mjs'

test('Chinese phrases remain searchable after site config crosses JSON serialization', () => {
  const theme = { search: { provider: 'local', options: { locales: { root: { label: '搜索' } } } } }
  configureLocalSearch(theme)
  const indexOptions = { fields: ['title', 'text'], storeFields: ['title'], ...theme.search.options.miniSearch.options }
  const index = new MiniSearch(indexOptions)
  index.addAll([{ id: 'agent', title: '工具调用协议', text: '工具调用的参数通过消息传递。' }, { id: 'python', title: 'Python 基础', text: '学习列表与字典。' }])
  const clientTheme = JSON.parse(JSON.stringify(theme))
  configureLocalSearch(clientTheme)
  const browserIndex = MiniSearch.loadJSON(JSON.stringify(index), { fields: ['title', 'text'], storeFields: ['title'], ...clientTheme.search.options.miniSearch.options })
  assert.equal(browserIndex.search('调用协议')[0]?.id, 'agent')
  assert.equal(browserIndex.search('Python')[0]?.id, 'python')
  assert.equal(clientTheme.search.options.locales.root.label, '搜索')
})
