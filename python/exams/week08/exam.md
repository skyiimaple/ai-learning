# 第 8 周考试 · Next.js AI 产品化

- 时长：40 分钟
- 总分：100
- 范围：day16, day17, day18, day19
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

环境变量名带 NEXT_PUBLIC_ 时，它会出现在哪里？

- A. 只在服务器内存里
- B. 打进浏览器能下载到的前端包
- C. 自动加密后再给模型
- D. 只在测试用例里

## 第 2 题（单选 · 8 分）

Day18 之后，成绩 Agent 页面应请求哪里？

- A. 浏览器直接请求 127.0.0.1:8015
- B. 同源的 /api/agent，由服务端再去请求 Python
- C. 浏览器携带 LLM_API_KEY 请求智谱
- D. 一个静态 JSON 文件

## 第 3 题（单选 · 8 分）

useChat 在这周主要负责？

- A. 建 SQLite 表
- B. 维护多轮消息，并把流式增量画到页面上
- C. 训练模型
- D. 做 SQL JOIN

## 第 4 题（单选 · 8 分）

AI SDK 里工具参数用什么描述？

- A. Pydantic
- B. zod
- C. argparse
- D. csv.DictReader

## 第 5 题（单选 · 8 分）

streamText 的 maxSteps: 5 对应之前哪一种限制？

- A. Python 里手写的有限步工具循环
- B. SQL 的 LIMIT 5
- C. 表格分页
- D. CSS 动画步数

## 第 6 题（多选 · 10 分）

哪些说法正确？

- A. LLM_API_KEY 放在服务端环境变量
- B. BFF 让浏览器不必知道 Python 的内网端口
- C. SDK 的多步和手写 tool_calls 循环都要限制步数
- D. NEXT_PUBLIC_LLM_API_KEY 是放置密钥的推荐写法

## 第 7 题（简答 · 14 分）

为什么 Agent 也要经过 /api/agent，而不是页面直接 fetch 127.0.0.1:8015？

## 第 8 题（简答 · 12 分）

AI SDK 自动多步和 Day13 手写循环，差在谁负责把 tool 结果写回？工具函数仍由谁执行？

## 第 9 题（改错 · 12 分）

客户端组件里写了 process.env.LLM_API_KEY。构建进浏览器后通常是什么？调用应放在哪？

## 第 10 题（改错 · 12 分）

页面仍使用 NEXT_PUBLIC_AGENT_URL 直连 8015。这和 Day18 的目标差在哪？应改成请求什么？
