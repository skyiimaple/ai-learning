# 第 5 周考试 · Prompt Engineering

- 时长：40 分钟
- 总分：100
- 范围：day12
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

Few-shot 和 Zero-shot 的差别是？

- A. Few-shot 在提示里给出输入输出例子，Zero-shot 不给例子
- B. Few-shot 会更新模型权重
- C. Zero-shot 必须打开 JSON mode
- D. Few-shot 就是 Tool Calling

## 第 2 题（单选 · 8 分）

System Prompt 在这条链路里负责什么？

- A. 只展示给用户看，模型不读
- B. 规定角色边界和输出格式，用户消息放具体任务
- C. 代替 API key
- D. 只能写一行

## 第 3 题（单选 · 8 分）

同一道题先 Zero-shot 再 Few-shot，是为了看什么？

- A. 例子会不会把格式和口径稳住
- B. 两个模型谁更贵
- C. 检索命中率
- D. 向量维度

## 第 4 题（单选 · 8 分）

response_format 设为 json_object 时，接口更可能返回什么？

- A. 一个 JSON 对象，而不是前后带解释的散文
- B. 执行好的 SQL 结果
- C. 已经通过 Pydantic 的对象，无需再校验
- D. 空的 messages

## 第 5 题（单选 · 8 分）

格式要求写在哪里，下一轮用户换一句话时还在？

- A. 只写在第一轮 user 里
- B. 写在 system 里，每轮请求都带着
- C. 写在 URL 路径里
- D. 写在模型文件名里

## 第 6 题（多选 · 10 分）

哪些做法和这一周一致？

- A. 例子的格式要和希望模型输出的格式一致
- B. system 里可以写「材料不足就说不知道」
- C. 提示里的例子会改掉模型权重
- D. 即使开了 json_object，仍要用 schema 再校验一次

## 第 7 题（简答 · 14 分）

给「根据名单写成绩摘要」写 system 时，角色边界和输出格式各要约束什么？各写一句即可。

## 第 8 题（简答 · 12 分）

Zero-shot 已经能答对大意时，为什么还要加 Few-shot？例子在什么情况下会帮倒忙？

## 第 9 题（改错 · 12 分）

格式要求只放在第一轮 user。第二轮 messages 里如果没有 system，约束还在吗？怎么改？

## 第 10 题（改错 · 12 分）

Few-shot 的例子里 pass_count 和名单对不上。模型更可能学到什么？例子要满足什么？
