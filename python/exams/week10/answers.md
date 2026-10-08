# 第 10 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

B. collection.query

## 第 2 题

B. 重新运行 build_chroma.py

## 第 3 题

B. Top-K 结果里有没有期望的 source

## 第 4 题

B. Day21 落盘的 docs.json 和 vectors.npy

## 第 5 题

A. 问题和期望命中的来源文件

## 第 6 题

A、B、C
- A. PersistentClient 把向量库放在本地目录
- B. metadata 里要有 source，命中率才能对文件名
- C. 库里只有三篇笔记时，Top-K 很容易把文件都盖住，命中率会偏高

## 第 7 题

检索若没把对的笔记带进来，后面的回答没有正确材料。先确认期望 source 进了 Top-K，再谈句子。

## 第 8 题

source 是哪篇笔记，score 是有多接近，text 是被用到的原文片段。

## 第 9 题

两边的向量不在同一空间，近邻没有意义。建库和查询必须用同一个 embedding 函数。

## 第 10 题

期望来源出现在结果里即可，看交集是否非空，不要求两个集合完全一样。
