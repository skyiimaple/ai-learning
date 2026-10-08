# 第 12 周考试 · 评测与观测

- 时长：40 分钟
- 总分：100
- 范围：day25
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

Day25 问答页优先用哪套检索？

- A. 只读 vectors.npy
- B. Day24 的 pipeline，导入失败再退回 Chroma
- C. 不检索
- D. 只做关键词全等

## 第 2 题（单选 · 8 分）

一条 rag_ask trace 至少要能看到？

- A. 回答的文采分数
- B. 问题、模型、耗时和来源
- C. 用户的 API key
- D. 全部文档向量

## 第 3 题（单选 · 8 分）

已安装的 Langfuse 4 里，记录一次观察要用？

- A. client.trace()
- B. start_as_current_observation
- C. print
- D. 写进 gold.json

## 第 4 题（单选 · 8 分）

没有配置 Langfuse 钥匙时，trace.py 可以？

- A. 必须抛异常退出
- B. 把同一份记录追加到本地 traces.jsonl
- C. 自动开始训练
- D. 关掉检索

## 第 5 题（单选 · 8 分）

LANGFUSE_HOST 怎么填？

- A. 永远写 cloud.langfuse.com，和项目区域无关
- B. 必须和项目所在区域一致；美国区是 us.cloud.langfuse.com
- C. 用云服务时写成 localhost
- D. 留空

## 第 6 题（多选 · 10 分）

哪些说法正确？

- A. 页面上的回答要带着引用
- B. flush 之后，云端 Traces 里才能看到刚发送的记录
- C. uvicorn 没有 --reload 时，改完代码要重启进程
- D. 有了 trace 就不需要黄金集命中率

## 第 7 题（简答 · 14 分）

命中率和一条 trace 各回答什么问题？为什么简历里要有一次真实提问的 trace，而不是只写「接了 Langfuse」？

## 第 8 题（简答 · 12 分）

Langfuse 的 secret key 为什么不能写进静态页面？

## 第 9 题（改错 · 12 分）

代码仍调用 lf.trace(...)。在 langfuse 4.17 上会报什么？应改成哪两层观察？

## 第 10 题（改错 · 12 分）

main.py 把异常收成 HTTP 500 的 detail，终端只打印 500 Internal Server Error。排错时还要看哪里？
