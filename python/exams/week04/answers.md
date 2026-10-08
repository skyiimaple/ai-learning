# 第 4 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

B. 环境变量里，由服务端代发请求

## 第 2 题

B. system 加上此前的 user 和 assistant

## 第 3 题

B. text/event-stream

## 第 4 题

A. data: 加一段 JSON，帧之间空一行；结束时 data: [DONE]

## 第 5 题

B. choices[0].delta.content

## 第 6 题

A、B、C
- A. 流式和非流式可以共用同一份 messages
- B. 用 curl 能看到一块块 data: 才算流式走通
- C. 密钥留在服务端，浏览器不直接调用上游

## 第 7 题

前端包会被下载，密钥会泄漏。502 表示上游失败，应转成自己的错误信息，不要把密钥或上游内部地址回给浏览器。

## 第 8 题

每个 chunk 只是新增加的几个字，按到达顺序接上才是完整回答。SSE 可以边到边画，整段 JSON 要等生成结束才出现文字。

## 第 9 题

SSE 用空行分帧。只有一个换行时，下一帧会粘在上一帧后面。应写成 data: ... 然后两个换行。

## 第 10 题

模型看不到自己上一轮说过的话，上下文断了。拿到 reply 后要 append role 为 assistant、content 为 reply 的消息。
