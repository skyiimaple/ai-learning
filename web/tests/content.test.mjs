import { test } from 'node:test'
import assert from 'node:assert/strict'
import { mkdtemp, mkdir, writeFile, readFile, readdir, rm } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { spawnSync } from 'node:child_process'

const script = resolve('scripts/content.mjs')
async function fixture(t) {
  const root = await mkdtemp(join(tmpdir(), 'ai-learning-web-'))
  t.after(() => rm(root, { recursive: true, force: true }))
  async function put(path, value) {
    await mkdir(join(root, path, '..'), { recursive: true })
    await writeFile(join(root, path), value)
  }
  async function sync() {
    const r = spawnSync(process.execPath, [script, '--root', root], { encoding: 'utf8' })
    assert.equal(r.status, 0, r.stderr)
    return JSON.parse(await readFile(join(root, 'web/.generated/catalog.json'), 'utf8'))
  }
  return { root, put, sync, read: p => readFile(join(root, 'web/.generated', p), 'utf8') }
}

test('keeps real directories, natural ordering, complete prose and README navigation', async t => {
  const f = await fixture(t)
  await f.put('agent/README.md', '# Agent\n\n[讲义](./teaching/README.md)')
  await f.put('agent/teaching/README.md', '# 讲义\n\n[协议](./01-协议.md)')
  await f.put('agent/teaching/01-协议.md', '# 工具协议\n\n[目录](./README.md)\n\n```js\nconst x = "[目录](./README.md)"\n```')
  await f.put('python/day10/day10.md', '# Day 10 · 流式\n\n正文应完整保留。')
  await f.put('python/day2/day2.md', '# Day 2 · CSV\n\n第二天。')
  const data = await f.sync()
  assert.deepEqual(data.sections.map(s => s.id), ['agent', 'python', 'node'])
  assert.deepEqual(data.sections[1].documents.map(d => d.source), ['python/day2/day2.md', 'python/day10/day10.md'])
  assert.match(await f.read('agent/index.md'), /\.\/teaching\/index\.md/)
  const lesson = await f.read('agent/teaching/01-协议.md')
  assert.match(lesson, /\[目录\]\(\.\/index\.md\)/)
  assert.match(lesson, /const x = "\[目录\]\(\.\/README\.md\)"/)
  assert.match(await f.read('python/day10/day10.md'), /正文应完整保留。/)
  assert.equal(data.sections[2].documents.length, 0)
})

test('does not publish hidden files, dependencies, source secrets or video directories', async t => {
  const f = await fixture(t)
  await f.put('agent/README.md', '# Agent')
  for (const path of ['python/.venv/leak.md', 'node/demo/node_modules/pkg/README.md', 'node/demo/.env.local', '.env.local', 'videos/README.md', 'agent/videos/README.md', 'agent/.hidden.md']) {
    await f.put(path, 'SECRET_MUST_NOT_BE_PUBLISHED')
  }
  const data = await f.sync()
  assert.equal(data.sections.flatMap(s => s.documents).length, 1)
  assert.doesNotMatch(JSON.stringify(data), /SECRET_MUST_NOT_BE_PUBLISHED|leak\.md/)
  assert.deepEqual((await readdir(join(f.root, 'web/.generated'))).filter(n => ['.env.local', 'videos'].includes(n)), [])
})

test('updates and removes generated pages when source files change', async t => {
  const f = await fixture(t)
  await f.put('python/day01/day01.md', '# Day 01\n\nold')
  await f.sync()
  await f.put('python/day01/day01.md', '# Day 01\n\nnew')
  await f.sync()
  assert.match(await f.read('python/day01/day01.md'), /new/)
  await rm(join(f.root, 'python/day01/day01.md'))
  const data = await f.sync()
  assert.equal(data.sections[1].documents.length, 0)
  await assert.rejects(f.read('python/day01/day01.md'), { code: 'ENOENT' })
})

test('copies only known standalone reference pages and keeps relative supporting data', async t => {
  const f = await fixture(t)
  await f.put('python/ai-career-plan.html', '<html>路线</html>')
  await f.put('python/progress.json', '{"currentDay":19}')
  await f.put('python/private.html', '<html>private</html>')
  await f.sync()
  assert.match(await f.read('public/reference/python/ai-career-plan.html'), /路线/)
  assert.match(await f.read('public/reference/python/progress.json'), /19/)
  await assert.rejects(f.read('public/reference/python/private.html'), { code: 'ENOENT' })
  assert.match(await f.read('python/ai-career-plan.md'), /ReferencePage/)
})
