import { spawn } from 'node:child_process'
import path from 'node:path'
import { syncSite, webRoot } from './content.mjs'

await syncSite()
const child = spawn(process.execPath, [path.join(webRoot, 'node_modules/vitepress/bin/vitepress.js'), 'dev', '--host', '127.0.0.1', '--port', '5173', ...process.argv.slice(2)], { cwd: webRoot, stdio: 'inherit' })
let busy = false
const timer = setInterval(async () => {
  if (busy) return
  busy = true
  try {
    const { changed } = await syncSite()
    if (changed) console.log(`[content] 已同步 ${changed} 个文件变化`)
  } catch (error) { console.error('[content]', error.message) }
  finally { busy = false }
}, 1500)
const stop = signal => { clearInterval(timer); child.kill(signal) }
process.on('SIGINT', () => stop('SIGINT'))
process.on('SIGTERM', () => stop('SIGTERM'))
child.on('error', error => { console.error(error); clearInterval(timer); process.exitCode = 1 })
child.on('exit', code => { clearInterval(timer); process.exitCode = code ?? 0 })
