import { readdir, readFile, stat } from 'node:fs/promises'
import path from 'node:path'
import { webRoot } from './content.mjs'
const root = path.join(webRoot, '.vitepress/dist')
const base = process.env.VITEPRESS_BASE || '/'
async function files(dir) {
  const results = []
  for (const entry of await readdir(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) results.push(...await files(full))
    else if (entry.name.endsWith('.html')) results.push(full)
  }
  return results
}
const errors = []
let checked = 0
for (const file of await files(root)) {
  const html = (await readFile(file, 'utf8')).replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, '')
  const page = path.relative(root, file).split(path.sep).join('/')
  for (const match of html.matchAll(/<(?:a|link|img|iframe|source|script)\b[^>]*?\b(?:href|src)=["']([^"']+)["']/gi)) {
    const href = match[1].replace(/&amp;/g, '&')
    if (/^(?:[a-z][a-z\d+.-]*:|\/\/|#)/i.test(href) || href.includes('${')) continue
    const resolved = new URL(href, `https://site.invalid${base}${page}`)
    let pathname = decodeURIComponent(resolved.pathname)
    if (!pathname.startsWith(base)) { errors.push(`${page}: 跳出站点 base 的链接 ${href}`); continue }
    pathname = pathname.slice(base.length)
    if (pathname.endsWith('/') || !pathname) pathname += 'index.html'
    const target = path.resolve(root, pathname)
    if (!target.startsWith(root + path.sep)) { errors.push(`${page}: 无效路径 ${href}`); continue }
    try {
      const info = await stat(target)
      if (!info.isFile()) throw new Error('Not a file')
      checked++
    } catch { errors.push(`${page}: 缺少 ${href}`) }
  }
}
if (errors.length) { console.error(errors.join('\n')); process.exitCode = 1 }
else console.log(`通过：${checked} 个站内页面及资源链接均存在。`)
