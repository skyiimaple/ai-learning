# 第 1 周考试 · Python 语法速通①

- 时长：40 分钟
- 总分：100
- 范围：Day01–04（语法对照、JSON/CSV、argparse、pathlib、自定义异常）
- 说明：先自己做，做完再看 answers.md 或让 Cursor 批改

## 第 1 题（单选 · 8 分）

对照 JavaScript：Python 里「没有值」和布尔字面量怎么写？

- A. null，以及 true / false
- B. None，以及 True / False
- C. undefined，以及 True / False
- D. None，以及 true / false

## 第 2 题（单选 · 8 分）

`user = {"name": "a"}`。`user.get("age", 0)` 的结果是？

- A. 抛出 KeyError
- B. None
- C. 0
- D. undefined

## 第 3 题（单选 · 8 分）

`[x for x in range(5) if x % 2 == 0]` 得到什么？

- A. [1, 3]
- B. [0, 2, 4]
- C. [2, 4]
- D. [0, 2, 4, 6]

## 第 4 题（单选 · 8 分）

`stats.py` 里用 `Path(__file__).with_name("data.json")` 打开成绩文件。这个路径指的是？

- A. 运行命令时的当前工作目录下的 data.json
- B. 和 stats.py 放在同一目录的 data.json
- C. 用户主目录下的 data.json
- D. 只在名为 day01 的字符串里查找

## 第 5 题（单选 · 8 分）

argparse 写了 `add_argument("--pass-line", type=int, default=60)`。解析之后，及格线在代码里用哪个属性？

- A. args["--pass-line"]
- B. args.pass-line
- C. args.pass_line
- D. args.passLine

## 第 6 题（多选 · 10 分）

关于这一周的读写和异常，哪些说法正确？

- A. csv.DictReader 读出的每一行是 dict，键来自表头
- B. Path.glob("*.csv") 只看这一层；rglob 会进入子目录
- C. FileFormatError 和 ScoreParseError 都继承 AppError，except AppError 能接住它们
- D. summarize 在学生列表为空时，仍会返回 avg 和 by_class

## 第 7 题（简答 · 14 分）

前端会把「用户能看懂的失败」和「没想到的系统错误」分开。对照 day04 的异常：InputNotFoundError、FileFormatError、ScoreParseError 各在什么情况下抛出？batch_stats.py 为什么只捕获 AppError，而不是裸写 except Exception？

## 第 8 题（简答 · 12 分）

函数参数：*args 和 **kwargs 分别是什么类型？这和 JS 的 rest、对象展开各对应什么？为什么默认参数要写成 bucket=None，而不是 bucket=[]？

## 第 9 题（改错 · 12 分）

day03/cli.py 写汇总时有一行：`"scope": all`。这里的 all 没有加引号。写出这一格实际会变成什么，以及应该怎么改。

## 第 10 题（改错 · 12 分）

day04/batch_stats.py 的 main：统计成功时，函数末尾仍是 `return 1`。合并模式下打印用的是循环结束后的 `file.name`，但人数却是所有文件加在一起的。指出这两处分别会让调用者看到什么，并写出应有的返回码和打印对象。
