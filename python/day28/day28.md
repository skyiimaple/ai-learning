# Day 28 · 毕业项目 Day1：选题 + 骨架 · 未学习

- **日期**：按实际学习日
- **时段**：2 小时
- **课程根**：`~/code/ai-learning/python`
- **阶段**：A 路线 · 第 4 个月 · 毕业项目 MVP①
- **今日主题**：二选一锁定方向；搭好目录、API、空 UI；主路径伪代码/空实现跑通
- **原则**：今天不追求业务完美，只求骨架可启动
- **状态**：未学习
- **大纲**：`learning-outline.md` Day28

## 方向（锁定其一，写入 `CHOICE.md`）

| 代号 | 方向 | 主路径 |
|------|------|--------|
| A | PR Review Agent | GitHub token → 拉 PR diff → LLM 审 → 结构化评论 JSON |
| B | CSV 数据分析 Agent | 上传 CSV → NL 问题 → 受限 Python/统计 → 结论（+可选图） |

**推荐**：无 GitHub token / 想少依赖外网 → **B**；想贴「工程协作」叙事 → **A**。

## 今日目标

1. `CHOICE.md` 写明方向与成功标准（3 分钟 Demo 脚本草稿）
2. FastAPI 骨架：`/health` + 主业务空路由
3. `static/index.html` 空壳可打开
4. `pipeline.py`（或 `review.py` / `analyze.py`）主路径函数签名 + mock 返回

## 今日不学

同时开两个方向、Webhook 生产部署、复杂鉴权

---

## 时间表

| 时间 | 内容 | 产出 |
|------|------|------|
| 0:00–0:20 | 选题 + CHOICE | 锁定 |
| 0:20–1:00 | 目录 + API + 空 UI | 可 uvicorn |
| 1:00–1:05 | 休息 | — |
| 1:05–1:45 | 主路径 mock | 端到端假数据 |
| 1:45–2:00 | Demo 脚本草稿 | 明日清单 |

---

## 开工

```bash
cd ~/code/ai-learning/python && source .venv/bin/activate && mkdir -p day28/static day28/sample
cd day28
```

---

## 详细安排

### 0:00–0:20｜选题（20 分）

**`CHOICE.md`：**

```markdown
# 毕业项目选择

- 方向：A / B（删掉另一个）
- 用户是谁：
- 3 分钟 Demo 步骤：
  1.
  2.
  3.
- 非目标（不做）：
- 复用已有能力：Tool Calling / RAG / FastAPI / …
```

---

### 0:20–1:00｜骨架（40 分）

**方向 B 示例 `main.py`：**

```python
from pathlib import Path

from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from analyze import analyze_csv

app = FastAPI(title="capstone-csv-agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

UPLOAD = Path(__file__).with_name("uploads")
UPLOAD.mkdir(exist_ok=True)


@app.get("/health")
def health():
    return {"ok": True}


class AskIn(BaseModel):
    file_id: str
    question: str


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    dest = UPLOAD / file.filename
    dest.write_bytes(await file.read())
    return {"file_id": file.filename, "path": str(dest)}


@app.post("/analyze")
def analyze(body: AskIn):
    path = UPLOAD / body.file_id
    return analyze_csv(path, body.question)


app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

**方向 A 示例路由：** `POST /review {owner,repo,pull_number}` → `review_pr(...)`。

**`static/index.html`：** 标题 + 输入框 + 结果 `<pre>`，先打 `/health`。

```bash
uvicorn main:app --host 127.0.0.1 --port 8028
```

---

### 1:05–1:45｜主路径 mock（40 分）

**方向 B `analyze.py`：**

```python
from pathlib import Path


def analyze_csv(path: Path, question: str) -> dict:
    # Day28：先 mock；Day29 再接 pandas + LLM
    if not path.exists():
        return {"error": "file missing", "path": str(path)}
    return {
        "question": question,
        "summary": f"（mock）已收到 {path.name}，明日将用受限工具回答。",
        "columns": [],
        "chart": None,
    }
```

**方向 A `review.py`：** mock 返回 `{"findings":[{"level":"warn","msg":"..."}]}`。

放一份 `sample/demo.csv` 或记下要用的公开 PR。

**验收：** curl/浏览器走通 upload→analyze 或 review，返回 mock JSON。

---

### 1:45–2:00｜明日清单

写下 Day29 必须真接的 3 个点（例如：读 CSV 头、tool: describe、最终回答）。

---

## 验收清单

- [ ] CHOICE 已锁定唯一方向
- [ ] uvicorn 可起，/health 200
- [ ] 主路径 mock 端到端通

## 明日预告

Day29：happy path 真接通 + Chat/结果 UI 可演示。
