# 第 7 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

B. 你的代码看到 tool_calls 后执行，再以 role tool 写回

## 第 2 题

B. 把这条 content 当作最终回答返回

## 第 3 题

A. 5

## 第 4 题

B. content 和 tool_calls

## 第 5 题

B. answer 和 steps 调用轨迹

## 第 6 题

A、B、C
- A. tools 描述工具名和参数形状
- B. tool 消息要用 tool_call_id 对上那一次调用
- C. 限步是为了避免模型一直调工具

## 第 7 题

请求带 tools 和 messages。模型回 tool_calls。本地 run_tool 执行。先写回 assistant（含 tool_calls），再写 role 为 tool 的结果。没有 tool_calls 就停；到 MAX_STEPS 也停并说明超时。

## 第 8 题

steps 让人核对查了哪个学生、算了什么，而不是只看一句结论。页面要有 loading，并把 502 和空回答显示成错误，而不是当成正常答案。

## 第 9 题

看不到观察结果，可能重复调用，或自己编一个数。必须把 tool_call_id 和执行结果写回 messages。

## 第 10 题

会看到一截工具 JSON，不像一句回答。应返回明确的超过步数上限、没有最终回答。
