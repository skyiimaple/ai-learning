# 第 3 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

B. 查询参数，默认 0，并且限制在 0 到 100

## 第 2 题

B. students 用 class_id JOIN classes，选出 c.name

## 第 3 题

B. 按班级 COUNT 人数、AVG 分数，JOIN classes 后 GROUP BY c.id

## 第 4 题

B. 201

## 第 5 题

C. 返回 404，detail 为学生不存在

## 第 6 题

A、B、C
- A. response_model 用来约束响应的字段形状
- B. Depends 可以把「查库得到的行」注进路由函数
- C. 删除成功用 204，响应没有正文

## 第 7 题

班级改名只改 classes 一处，避免每一行学生都抄一份名字。查询时 JOIN 把 class_id 换成班级名。按班级统计时同样 JOIN 后再 GROUP BY 班级，COUNT 和 AVG 才对得上名字。

## 第 8 题

字段不合法是校验错误（FastAPI 对 Pydantic 默认 422，创建接口里主动抛的 ValueError 用了 400）。资源不存在是 404。表单红字对应校验失败，详情页找不到对应 404。

## 第 9 题

students 表没有 class_name。要 JOIN classes AS c ON s.class_id = c.id，选出 c.name AS class_name，再 GROUP BY c.id。

## 第 10 题

查不到时返回的是空值，状态码仍是 200。应在返回前 if not student: raise HTTPException(404)。
