# 第 6 周考试 · 结构化输出与安全

- 时长：40 分钟
- 总分：100
- 范围：day11
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

ScoreReport 上的 model_validator(mode="after") 用来检查什么？

- A. 单个 score 是否在 0 到 100
- B. 对象组装完成后，pass_count 是否等于分数不低于 60 的人数
- C. HTTP 状态码
- D. 文件是否存在

## 第 2 题（单选 · 8 分）

StudentScore.score 的 Field(ge=0, le=100) 挡住的是？

- A. 跨字段不一致
- B. 单个分数越界
- C. 网络超时
- D. JSON 外面的说明文字

## 第 3 题（单选 · 8 分）

模型把 JSON 包在 ```json 围栏里时，下一步应该？

- A. 对整段原文直接 json.loads，一定能过
- B. 先剥掉围栏，再 json.loads
- C. 重新训练模型
- D. 把围栏当成合法 JSON

## 第 4 题（单选 · 8 分）

这一周要求校验失败时怎么处理？

- A. 无限重试直到成功
- B. 把错误信息反馈给模型，再试一次
- C. 忽略错误，把原始字符串返回给前端
- D. 改去查 SQLite

## 第 5 题（单选 · 8 分）

POST /extract 的请求体是什么？

- A. 已经校验过的 ScoreReport
- B. 原始成绩描述 text，由服务端抽 JSON 再校验
- C. 一条 SQL
- D. CSV 文件路径

## 第 6 题（多选 · 10 分）

哪些说法正确？

- A. 先从模型文本里抽出 JSON，再 model_validate
- B. pass_count 必须等于 students 里 score 不低于 60 的人数
- C. 字段范围和跨字段一致性是两层校验
- D. 校验失败时可以把未校验的 dict 当成功响应

## 第 7 题（简答 · 14 分）

JSON 已经能 json.loads，为什么 Pydantic 仍可能拒绝？重试时要把哪句错误喂回模型？

## 第 8 题（简答 · 12 分）

这和前端用 schema 解析接口响应有什么相同点？

## 第 9 题（改错 · 12 分）

校验写成 if self.pass_count != len(self.students)。及格线是 60 分。错在哪里？应怎么数？

## 第 10 题（改错 · 12 分）

现在的 extract.py 在校验失败时直接 raise RuntimeError，没有第二次请求。要补上「重试一次」，messages 里应再加什么？
