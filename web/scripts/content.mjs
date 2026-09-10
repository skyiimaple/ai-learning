import { readdir, readFile, mkdir, writeFile, rm } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

export const webRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
export const repoRoot = path.resolve(webRoot, '..')
const excluded = new Set(['node_modules', '__pycache__', 'dist', 'build', 'coverage', 'videos', 'video'])
const natural = (a, b) => a.localeCompare(b, 'en', { numeric: true })
const slash = p => p.split(path.sep).join('/')
const sections = [
  { id: 'agent', label: 'Agent 工程', description: 'Agent 概念、工具协议与运行时的系统讲义。' },
  { id: 'python', label: '每日学习', description: '从 Python 基础到 AI 应用的逐日学习记录。' },
  { id: 'node', label: '前端实践', description: 'Next.js 应用与 AI 交互的实践项目。' }
]
const references = [
  ['ai-career-plan', 'A 路线 · AI 应用工程'],
  ['deep-plan', 'B 路线 · ML 工程师'],
  ['exam', '周考']
]

async function existsRead(file) {
  try { return await readFile(file, 'utf8') } catch (e) { if (e.code === 'ENOENT') return null; throw e }
}
async function walk(dir) {
  let entries
  try { entries = await readdir(dir, { withFileTypes: true }) } catch (e) { if (e.code === 'ENOENT') return []; throw e }
  const found = []
  for (const e of entries.sort((a, b) => natural(a.name, b.name))) {
    if (e.name.startsWith('.') || excluded.has(e.name) || e.isSymbolicLink()) continue
    const full = path.join(dir, e.name)
    if (e.isDirectory()) found.push(...await walk(full))
    else if (e.isFile()) found.push(full)
  }
  return found
}
const pagePath = source => source.replace(/(^|\/)README\.md$/i, '$1index.md')
const url = page => '/' + page.replace(/index\.md$/, '').replace(/\.md$/, '.html')
const titleOf = (text, fallback) => (text.match(/^#\s+(.+)$/m)?.[1] ?? fallback).replace(/`/g, '').trim()
const fm = data => '---\n' + Object.entries(data).map(([k, v]) => `${k}: ${JSON.stringify(v)}`).join('\n') + '\n---\n\n'

// Change document links, never the runnable examples inside fenced code blocks.
function rewriteReadmes(text) {
  let fence = null
  return text.split('\n').map(line => {
    const marker = line.match(/^\s{0,3}(`{3,}|~{3,})/)
    if (marker) {
      if (!fence) fence = marker[1]
      else if (marker[1][0] === fence[0] && marker[1].length >= fence.length) fence = null
      return line
    }
    if (fence) return line
    return line.replace(/(\]\()([^\s)]+)(\))/g, (all, left, target, right) => {
      if (/^(?:[a-z]+:|\/\/|#)/i.test(target)) return all
      return left + target.replace(/(^|\/)README\.md(?=[#?]|$)/i, '$1index.md') + right
    })
  }).join('\n')
}
function addMetadata(text, metadata) {
  if (text.startsWith('---\n')) return text.replace(/^---\n/, fm(metadata).replace(/---\n\n$/, ''))
  return fm(metadata) + text
}
function sidebarFor(docs, id, refs) {
  function branch(dir, root = false) {
    const below = docs.filter(d => d.page.startsWith(dir + '/'))
    const own = below.filter(d => path.posix.dirname(d.page) === dir)
    const folders = [...new Set(below.filter(d => path.posix.dirname(d.page) !== dir).map(d => d.page.slice(dir.length + 1).split('/')[0]))].sort(natural)
    const items = own.sort((a,b) => a.page.endsWith('/index.md') ? -1 : b.page.endsWith('/index.md') ? 1 : natural(a.page,b.page)).map(d => ({ text: d.page.endsWith('/index.md') ? '概览' : d.title, link: d.url }))
    if (root && !own.some(d => d.page.endsWith('/index.md'))) items.unshift({ text: '目录概览', link: `/${id}/` })
    for (const folder of folders) {
      const children = branch(dir + '/' + folder)
      if (children.length === 1) items.push(children[0])
      else items.push({ text: folder, collapsed: false, items: children })
    }
    return items
  }
  const items = branch(id, true)
  if (refs.length) items.push({ text: '现有资料', collapsed: false, items: refs.map(r => ({ text:r.title, link:r.url })) })
  return items
}

export async function syncSite(root = repoRoot) {
  const dest = path.join(root, 'web/.generated')
  const outputs = new Map()
  const catalog = { sections: [], totalDocuments: 0 }
  const refs = []
  for (const [name, title] of references) {
    const raw = await existsRead(path.join(root, 'python', name + '.html'))
    if (raw === null) continue
    outputs.set(`public/reference/python/${name}.html`, raw)
    outputs.set(`python/${name}.md`, fm({ title, sourcePath: `python/${name}.html`, outline: false, prev: false, next: false }) + `# ${title}\n\n<ReferencePage src="/reference/python/${name}.html" title="${title}" />\n`)
    refs.push({ title, url: `/python/${name}.html` })
  }
  if (refs.length) {
    const progress = await existsRead(path.join(root, 'python/progress.json'))
    if (progress !== null) outputs.set('public/reference/python/progress.json', progress)
    for (const file of await walk(path.join(root, 'python/exams'))) {
      if (file.endsWith('.json')) outputs.set('public/reference/' + slash(path.relative(root, file)), await readFile(file, 'utf8'))
    }
  }
  for (const section of sections) {
    const documents = []
    for (const file of await walk(path.join(root, section.id))) {
      if (!file.endsWith('.md')) continue
      const source = slash(path.relative(root, file))
      const page = pagePath(source)
      if (outputs.has(page)) throw new Error(`页面路径冲突：${page}`)
      const content = await readFile(file, 'utf8')
      const title = titleOf(content, path.basename(file, '.md'))
      const doc = { source, page, title, url: url(page) }
      documents.push(doc)
      outputs.set(page, addMetadata(rewriteReadmes(content), { title, sourcePath: source }))
    }
    documents.sort((a, b) => natural(a.source, b.source))
    const resourceLinks = section.id === 'python' ? refs : []
    const rootPage = section.id + '/index.md'
    if (!outputs.has(rootPage)) {
      outputs.set(rootPage, fm({ title: section.label, outline: false }) + `# ${section.label}\n\n${section.description}\n\n<DirectoryListing section="${section.id}" />\n`)
    }
    catalog.sections.push({ ...section, documents, resources: resourceLinks, sidebar: sidebarFor(documents, section.id, resourceLinks) })
    catalog.totalDocuments += documents.length
  }
  const homepage = await existsRead(path.join(root, 'web/pages/index.md'))
  outputs.set('index.md', homepage ?? fm({ layout: 'home' }) + '# AI Learning\n')
  outputs.set('catalog.json', JSON.stringify(catalog, null, 2) + '\n')
  for (const file of await walk(path.join(root, 'web/public'))) {
    outputs.set('public/' + slash(path.relative(path.join(root, 'web/public'), file)), await readFile(file))
  }
  let changed = 0
  for (const [rel, content] of outputs) {
    const target = path.join(dest, rel)
    const previous = await existsRead(target)
    if (previous !== null && previous === String(content)) continue
    await mkdir(path.dirname(target), { recursive: true })
    await writeFile(target, content)
    changed++
  }
  for (const file of await walk(dest)) {
    if (!outputs.has(slash(path.relative(dest, file)))) { await rm(file); changed++ }
  }
  return { catalog, changed }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const i = process.argv.indexOf('--root')
  const result = await syncSite(i === -1 ? repoRoot : path.resolve(process.argv[i+1]))
  console.log(`已同步 ${result.catalog.totalDocuments} 篇文档，${result.changed} 个文件变化。`)
}
