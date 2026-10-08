# 第 14 周考试 · Memory 与多工具

- 时长：40 分钟
- 总分：100
- 范围：day27, day26
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

compress_if_needed 默认上限是 12 条。传入正好 12 条时会？

- A. 原样返回，不调用模型做摘要
- B. 去掉 system 后把其余消息全部摘要
- C. 只保留最后 6 条，丢掉 system
- D. 每条 content 截成 200 字后返回

## 第 2 题（单选 · 8 分）

消息超过 12 条时，送去摘要的是哪一段？

- A. 包含 system 的全部原文
- B. 去掉 system 之后，再去掉末尾 6 条；每条 content 最多 200 字
- C. 只有最初那条 system
- D. 只有最后 6 条原文

## 第 3 题（单选 · 8 分）

压缩成功后的列表结构是？

- A. 只剩一条 user 摘要
- B. 原来的第一条 system（如果有）+ 一条历史摘要 system + 最后 6 条原文
- C. 用摘要替换原来的 system，其余删除
- D. 删掉最后 6 条，只留摘要

## 第 4 题（单选 · 8 分）

delete_file 不传 confirm 时会？

- A. 立刻 unlink
- B. 返回 status 为 need_confirm，文件还在
- C. 直接返回 path not allowed
- D. 抛异常

## 第 5 题（单选 · 8 分）

confirm 为真，文件存在，但路径在 tmp_playground 外面。结果是？

- A. 删除成功
- B. 仍返回 need_confirm
- C. 返回 path not allowed，不删除
- D. 先返回 not found 再删除

## 第 6 题（多选 · 10 分）

关于 run_tool_with_retry（retries=2），哪些正确？

- A. 工具最多被调用 3 次
- B. 结果里出现 need_confirm 就立刻返回，不再 sleep
- C. 结果里出现 error 且不是在等确认时，会 sleep 后再试
- D. 成功 JSON 只要没有 confirm 字段就会被当成失败

## 第 7 题（简答 · 12 分）

删除为什么要在 Python 里检查 confirm 和 playground，而不是只在工具说明里写「请先问用户」？这和浏览器里用户点取消有什么对应？

## 第 8 题（简答 · 14 分）

结合 Agent：谁执行工具？何时停？步数到顶返回什么？compress_if_needed 应插在哪一次调用模型之前？

## 第 9 题（改错 · 12 分）

下面的判断把等待确认也拿去重试：err 包含 error 或 need_confirm，然后只要 err 为真就 sleep。问题在哪？

## 第 10 题（改错 · 12 分）

压缩函数只返回 system 加一条历史摘要，没有接上 rest 的最后 6 条。模型会忘记什么？
