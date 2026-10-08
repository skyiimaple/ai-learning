# 第 1 周考试 · 参考答案

考生交卷前不要看本文件。

## 第 1 题

B. `None`，以及 `True` / `False`。

## 第 2 题

C. `0`。键不存在时 `dict.get` 返回给定的默认值，不抛 KeyError。

## 第 3 题

B. `[0, 2, 4]`。`range(5)` 是 0 到 4。

## 第 4 题

B. 和 `stats.py` 放在同一目录的 `data.json`。`__file__` 是脚本自己的路径，不看你从哪个目录启动。

## 第 5 题

C. `args.pass_line`。命令行上的连字符会变成属性名里的下划线。

## 第 6 题

A、B、C。

D 错：`summarize` 在列表为空时只返回 `{"count": 0}`，没有 `avg` 和 `by_class`。

## 第 7 题

- 路径不存在：`InputNotFoundError`
- 扩展名或内容格式不对：`FileFormatError`
- 分数转不成整数：`ScoreParseError`
- 三者都继承 `AppError`，`except AppError` 能一起接住并打印「业务错误」
- 不写 `except Exception`，是为了让除零、名字写错这类意外继续抛出，不被当成业务失败吞掉

## 第 8 题

- `*args` 是 tuple，对应 JS 的 rest
- `**kwargs` 是 dict，对应把剩余具名参数收成一个对象
- `bucket=[]` 只在定义时创建一次，之后不传参的调用会共享并改到同一个列表
- 写成 `None`，在函数体内再判断并新建列表，每次调用才有自己的列表

## 第 9 题

`all` 是内置函数，不是字符串 `"all"`。写入 CSV 时会变成函数的字符串表示，scope 列不再是「总体」标记。应改成 `"scope": "all"`。

## 第 10 题

- `raise SystemExit(main())` 会把 `return 1` 当成进程失败，即使统计已经打印出来。成功应 `return 0`
- 合并分支的 print 在循环外，`file` 停在最后一个文件上：标签是最后那个文件名，人数却是全部文件之和
- 合并结果要用固定标签（例如「合并」），不要用循环变量 `file.name`
