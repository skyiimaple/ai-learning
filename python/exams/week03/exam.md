# 第 3 周考试 · FastAPI + SQL 够用版

- 时长：40 分钟
- 总分：100
- 范围：day05, day06, day07, day08
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

GET /students?min_score=60 里的 min_score 是什么？

- A. 路径参数
- B. 查询参数，默认 0，并且限制在 0 到 100
- C. 请求体里的 JSON 字段
- D. 请求头

## 第 2 题（单选 · 8 分）

列出学生时，班级名是怎么来的？

- A. students 表里本来就有 class_name 这一列
- B. students 用 class_id JOIN classes，选出 c.name
- C. GROUP BY 会自动生成班级名
- D. 前端拿到 id 后再猜一个名字

## 第 3 题（单选 · 8 分）

/stats/by-class 在算什么？

- A. 每个学生单独一行，不做聚合
- B. 按班级 COUNT 人数、AVG 分数，JOIN classes 后 GROUP BY c.id
- C. 只按分数 WHERE，没有聚合
- D. 把所有班级合成一个平均数

## 第 4 题（单选 · 8 分）

POST /students 创建成功时，状态码是？

- A. 200
- B. 201
- C. 204
- D. 404

## 第 5 题（单选 · 8 分）

PUT /students/{id} 时这个 id 在库里不存在，应该？

- A. 返回 201
- B. 返回 400，因为 JSON 不合法
- C. 返回 404，detail 为学生不存在
- D. 返回 200 且 body 为 null

## 第 6 题（多选 · 10 分）

哪些说法和这一周的接口一致？

- A. response_model 用来约束响应的字段形状
- B. Depends 可以把「查库得到的行」注进路由函数
- C. 删除成功用 204，响应没有正文
- D. 不 JOIN 也能从 students 表读出班级名字段

## 第 7 题（简答 · 14 分）

学生表为什么存 class_id，而不是把班级名写在每一行？查询和按班级统计时，JOIN 各自解决什么？

## 第 8 题（简答 · 12 分）

「分数不是整数」和「这个学生 id 不存在」应该分成哪两种 HTTP 结果？这和前端表单校验失败、打开一个不存在的详情页有什么对应？

## 第 9 题（改错 · 12 分）

有人写成 SELECT class_name, COUNT(*) FROM students GROUP BY class_id。这个语句为什么拿不到班级名？写成和 day07 一样要补哪一段。

## 第 10 题（改错 · 12 分）

get_one_student 查完没有判断，直接 return student。id 不存在时客户端会看到什么状态码？应该改成哪一行？
