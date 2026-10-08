# 第 7 周考试 · Tool Calling

- 时长：40 分钟
- 总分：100
- 范围：day13, day14, day15
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

Tool Calling 里，函数真正在哪里执行？

- A. 模型在云端执行完，只把结果告诉你
- B. 你的代码看到 tool_calls 后执行，再以 role tool 写回
- C. 浏览器里的按钮执行
- D. 数据库触发器执行

## 第 2 题（单选 · 8 分）

某一轮响应里没有 tool_calls 时，循环应该？

- A. 继续空转
- B. 把这条 content 当作最终回答返回
- C. 必须再编一个工具调用
- D. 直接 500

## 第 3 题（单选 · 8 分）

day13 的 tool_loop 里 MAX_STEPS 是多少？

- A. 5
- B. 6
- C. 无限
- D. 1

## 第 4 题（单选 · 8 分）

写回历史时，带工具调用的 assistant 消息要包含？

- A. 只有 content
- B. content 和 tool_calls
- C. 只有 role tool
- D. 空对象

## 第 5 题（单选 · 8 分）

day15 的页面要展示什么？

- A. 只显示最终 answer
- B. answer 和 steps 调用轨迹
- C. 只显示 SQL
- D. 绕过 FastAPI，页面直接调模型

## 第 6 题（多选 · 10 分）

哪些说法正确？

- A. tools 描述工具名和参数形状
- B. tool 消息要用 tool_call_id 对上那一次调用
- C. 限步是为了避免模型一直调工具
- D. 响应里出现 tool_calls 就说明函数已经执行完

## 第 7 题（简答 · 14 分）

按顺序说出一轮工具调用：请求里有什么，模型回什么，谁执行，什么消息写回，什么时候停。

## 第 8 题（简答 · 12 分）

POST /agent/chat 为什么同时返回 answer 和 steps？页面对 502 和空回答要做什么？

## 第 9 题（改错 · 12 分）

循环执行了工具，但没有 append role 为 tool 的消息。下一轮模型会怎样？

## 第 10 题（改错 · 12 分）

超过 MAX_STEPS 时如果返回最后一次工具的原始 JSON，用户会看到什么？应该返回什么？
