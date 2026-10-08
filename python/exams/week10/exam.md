# 第 10 周考试 · RAG 实现

- 时长：40 分钟
- 总分：100
- 范围：day22, day23
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

换成 Chroma 之后，近邻检索靠什么完成？

- A. 仍要自己写余弦公式
- B. collection.query
- C. SQL JOIN
- D. 不保存向量

## 第 2 题（单选 · 8 分）

改了 day20/docs 里的笔记之后，要？

- A. 什么都不用做，旧库自动更新
- B. 重新运行 build_chroma.py
- C. 只改 gold.json 的题干
- D. 重启进程就会用上新文本

## 第 3 题（单选 · 8 分）

eval_retrieve.py 的命中率在评什么？

- A. 回答写得优不优雅
- B. Top-K 结果里有没有期望的 source
- C. Python 语法
- D. 接口延迟

## 第 4 题（单选 · 8 分）

Day22 演示页加载的是哪一套索引？

- A. Chroma
- B. Day21 落盘的 docs.json 和 vectors.npy
- C. 不检索，直接让模型回答
- D. Langfuse 里的 trace

## 第 5 题（单选 · 8 分）

gold.json 里的一条用例至少要有？

- A. 问题和期望命中的来源文件
- B. 模型权重
- C. 一条 SQL
- D. 前端路由

## 第 6 题（多选 · 10 分）

哪些说法正确？

- A. PersistentClient 把向量库放在本地目录
- B. metadata 里要有 source，命中率才能对文件名
- C. 库里只有三篇笔记时，Top-K 很容易把文件都盖住，命中率会偏高
- D. 这个脚本会给回答的文采打分

## 第 7 题（简答 · 14 分）

为什么先评「该命中哪个文件」，而不是先评答案句子好不好看？

## 第 8 题（简答 · 12 分）

引用区里的 source、score、text 分别让用户核对什么？

## 第 9 题（改错 · 12 分）

建库用 embedding-3，查询时换成了另一个向量模型。检索结果会怎样？

## 第 10 题（改错 · 12 分）

命中判断写成结果集合必须和 expect_sources 完全相等。Top-K 里多了一篇别的笔记就算失败。应怎么判？
