# 第 8 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

B. 打进浏览器能下载到的前端包

## 第 2 题

B. 同源的 /api/agent，由服务端再去请求 Python

## 第 3 题

B. 维护多轮消息，并把流式增量画到页面上

## 第 4 题

B. zod

## 第 5 题

A. Python 里手写的有限步工具循环

## 第 6 题

A、B、C
- A. LLM_API_KEY 放在服务端环境变量
- B. BFF 让浏览器不必知道 Python 的内网端口
- C. SDK 的多步和手写 tool_calls 循环都要限制步数

## 第 7 题

浏览器会暴露内网端口，还可能撞上 CORS。密钥和上游地址应留在 route handler。页面只请求同源的 /api/agent。

## 第 8 题

手写循环要自己 append assistant 和 tool。SDK 在 maxSteps 内代劳多步。execute 仍是你的函数，模型只提议调用。

## 第 9 题

客户端拿不到未公开的服务端变量，多半是 undefined。调用和密钥应放在 route handler，不放进客户端组件。

## 第 10 题

浏览器仍然知道并直连 Python。应改为请求 /api/agent，由服务端 fetch Python。
