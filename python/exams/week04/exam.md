# 第 4 周考试 · LLM API + Streaming

- 时长：40 分钟
- 总分：100
- 范围：day09, day10
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

LLM_API_KEY 应该放在哪里？

- A. 写进前端页面的常量
- B. 环境变量里，由服务端代发请求
- C. 放进浏览器地址栏的查询参数
- D. 提交进 git 仓库

## 第 2 题（单选 · 8 分）

多轮对话下一次请求要带上什么？

- A. 只带用户最新的一句
- B. system 加上此前的 user 和 assistant
- C. 只带 system，历史可以丢
- D. 每次都用空的 messages

## 第 3 题（单选 · 8 分）

POST /chat/stream 的响应类型是？

- A. application/json
- B. text/event-stream
- C. text/html
- D. application/octet-stream

## 第 4 题（单选 · 8 分）

day10 的一帧 SSE 长什么样？

- A. data: 加一段 JSON，帧之间空一行；结束时 data: [DONE]
- B. 等模型全部生成完，再返回一个大 JSON
- C. WebSocket 二进制帧
- D. 只在服务器终端打印，HTTP 不返回字

## 第 5 题（单选 · 8 分）

流式 chunk 里新增的文字在哪个字段？

- A. message.content 的全文
- B. choices[0].delta.content
- C. usage.total_tokens
- D. tool_calls

## 第 6 题（多选 · 10 分）

哪些说法正确？

- A. 流式和非流式可以共用同一份 messages
- B. 用 curl 能看到一块块 data: 才算流式走通
- C. 密钥留在服务端，浏览器不直接调用上游
- D. 前端拿着 API key 调用上游，和后端代发一样安全

## 第 7 题（简答 · 14 分）

为什么聊天页不能把 API key 放进前端包？上游返回 502 时，你自己的接口应该怎么对浏览器表现？

## 第 8 题（简答 · 12 分）

非流式一次拿到整段 content。流式为什么要把 delta 拼起来？对页面渲染差在哪？

## 第 9 题（改错 · 12 分）

有人写成 yield f"data: {piece}\n"，帧尾只有一个换行。浏览器或 curl 会怎样解析？应改成什么？

## 第 10 题（改错 · 12 分）

多轮循环里只 append 了 user，没有 append assistant。下一轮模型会漏掉什么？补上哪一条消息？
