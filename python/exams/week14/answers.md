# 第 14 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

A. 原样返回，不调用模型做摘要

## 第 2 题

B. 去掉 system 之后，再去掉末尾 6 条；每条 content 最多 200 字

## 第 3 题

B. 原来的第一条 system（如果有）+ 一条历史摘要 system + 最后 6 条原文

## 第 4 题

B. 返回 status 为 need_confirm，文件还在

## 第 5 题

C. 返回 path not allowed，不删除

## 第 6 题

A、B、C
- A. 工具最多被调用 3 次
- B. 结果里出现 need_confirm 就立刻返回，不再 sleep
- C. 结果里出现 error 且不是在等确认时，会 sleep 后再试

## 第 7 题

说明只是给模型看的，模型仍可能直接调用。真正 unlink 的是执行层，所以没确认就不能删，确认了也只能删演示目录里的文件。浏览器点取消对应 confirm 仍为假：不删，并返回需要确认。

## 第 8 题

模型只提议，run_tool 执行。没有 tool_calls 就停。到顶返回达到步数上限。压缩要在历史变长之后、下一次 chat_completions 之前。

## 第 9 题

need_confirm 不会因为多试几次就变成用户同意。遇到 need_confirm 应立刻返回，只有 error 才 sleep 重试。

## 第 10 题

忘记刚发生的工具结果和用户原话。返回值还要接上没被摘要的最后 6 条。
