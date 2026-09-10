# ai-learning / web

基于 VitePress 的个人学习文档站，按仓库中的 `agent`、`python`、`node` 三个实际目录组织。

## 本地使用

需要 Node.js 20 或更新版本。

```bash
cd /Users/maple/code/ai-learning/web
npm install
npm run dev
```

打开终端显示的本地地址，默认 http://127.0.0.1:5173。开发服务每 1.5 秒检查内容变化，原文新增、修改、删除后自动同步。

```bash
npm run check   # 内容同步测试、生产构建、站内链接验证
npm run preview # 预览最近一次构建，默认 http://127.0.0.1:4173
```

## 目录与内容

- `agent/` → Agent 目录，`teaching/` 层级及文档标题保持不变。
- `python/` → 该目录下的每日记录，包含原本就放在这里的 Next.js 学习内容。
- `node/` → 该目录下实践项目的 README 及其他 Markdown。
- `python` 目录里的路线图和周考 HTML 在该栏目下提供原页面入口。

页面标题来自 Markdown 的一级标题，排序按文件路径自然排序。`README.md` 映射为该层级的 `index.html`，相对 README 导航同步转换。搜索在浏览器本地完成，使用中文分词。

原文是唯一内容源：继续在仓库对应目录编写讲义即可。不要编辑 `.generated/` 中的页面；它们在开发或构建时自动生成。网站不会修改原文或学习进度，也不会启动 Next.js/FastAPI 演示服务。

## 网站文件

```text
web/
├── .vitepress/config.mts     # 导航、搜索、目录、中文界面
├── .vitepress/theme/         # 首页、文档辅助组件与样式
├── pages/index.md            # 首页配置
├── public/favicon.svg       # 网站图标
├── scripts/content.mjs      # 内容同步与目录生成
├── scripts/dev.mjs          # 开发服务与源文档监测
├── scripts/check-links.mjs  # 构建后验证站内页面和资源
├── tests/content.test.mjs   # 内容同步行为测试
└── .generated/              # 自动生成、忽略提交
```

仅导入三个目录中的 Markdown，跳过隐藏文件、依赖、缓存、构建产物和视频目录。HTML 资料采用显式白名单；不会把整个仓库作为公共资源目录。新增独立 HTML 资料需更新 `scripts/content.mjs` 的 `references`，新增普通 Markdown 不需要改网站配置。

## 静态部署

```bash
npm run build
```

静态产物为 `.vitepress/dist/`。使用保留 `.html` 的链接，可部署在普通静态服务器，不需要 SPA 路由回退。

如果部署到子路径，需要在构建时指定 base，例如：

```bash
VITEPRESS_BASE=/ai-learning/ npm run build
```

此站点只展示学习资料。现有周考页面若缺少对应试题 JSON，会沿用原页面的提示；不会自动生成试题或记录完成状态。

## Vercel 自动部署

仓库根目录的 `vercel.json` 已配置安装、检查、构建和静态产物路径。

- 导入 Git 仓库时，Root Directory 保持仓库根目录 `.`，不要选择 `web` 或 `node/day16-help`。
- Framework Preset 为 Other；安装命令为 `npm --prefix web ci`。
- 构建命令为 `npm --prefix web run check`，输出目录为 `web/.vitepress/dist`。
- 网站不需要模型 API Key，也不需要添加环境变量。
- 连接 `main` 分支后，每次推送文档或网站改动都会重新构建发布。

使用仓库根目录是因为内容同步器需要读取 `agent/`、`python/`、`node/` 中的 Markdown。部署的是静态文档，不会运行这些目录中的学习应用。
