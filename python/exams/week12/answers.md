# 第 12 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

B. Day24 的 pipeline，导入失败再退回 Chroma

## 第 2 题

B. 问题、模型、耗时和来源

## 第 3 题

B. start_as_current_observation

## 第 4 题

B. 把同一份记录追加到本地 traces.jsonl

## 第 5 题

B. 必须和项目所在区域一致；美国区是 us.cloud.langfuse.com

## 第 6 题

A、B、C
- A. 页面上的回答要带着引用
- B. flush 之后，云端 Traces 里才能看到刚发送的记录
- C. uvicorn 没有 --reload 时，改完代码要重启进程

## 第 7 题

命中率回答期望文件有没有进 Top-K。trace 回答这一次用了哪个模型、花了多久、带来源是什么。截图证明这条链路真的跑过。

## 第 8 题

静态页会被浏览器下载。secret 应只留在服务端环境变量里，由 Python 上报。

## 第 9 题

报没有 trace 这个属性。改成名为 rag_ask 的 span，里面再记一条名为 answer 的 generation，然后 flush。

## 第 10 题

看浏览器或响应体里的 detail。原始异常文字在那里，不在访问日志的那一行。
