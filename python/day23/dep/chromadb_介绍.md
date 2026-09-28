# ChromaDB 介绍

ChromaDB（导入名 `chromadb`）是一个嵌入式向量数据库。它把文本块和对应的向量存在本地目录里，并按语义相似度找出最接近的几条。

Day21 的做法是自己把向量存成 `vectors.npy`，查询时在 Python 里算余弦相似度。Chroma 把「存向量」和「找近邻」接过去：你给文档和 id，它负责写入、持久化和 `query`。检索的心智不变，变的是存储。

## 今天为什么用它

- 索引重启后还在，不用每次从 npy 重新加载再手写检索
- `collection.query` 直接返回 Top-K，不用自己维护相似度循环
- 数据落在 `day23/chroma_db/`，单机目录即可，不另起数据库服务

## 今天会碰到的 API

| API | 作用 |
|-----|------|
| `chromadb.PersistentClient(path=...)` | 打开或创建本地库目录 |
| `get_or_create_collection(...)` | 取一个集合；集合大致相当于「这一批 chunk 的表」 |
| `collection.upsert(ids, documents, metadatas)` | 按 id 写入或覆盖文本块 |
| `collection.query(query_texts, n_results)` | 用问题文本找最相近的若干块 |
| `collection.count()` | 看库里有多少条 |

向量从哪来由 Embedding Function 决定。今天用智谱 `embedding-3`，包在自己的 `GlmEmbeddingFunction` 里传给 collection，而不是让 Chroma 用它自带的默认模型。

## 它不负责什么

- 不负责切块：块仍然来自 Day20 的文档
- 不负责生成回答：检索之后仍是把命中块交给 LLM
- 不负责评测：命中率由黄金集脚本自己算
- 不是 LangChain，也不是要单独部署的服务
