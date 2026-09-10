# 默认参数
def greet(name,message = "Hellow"):
    print(f"{message}, {name}!")

greet("Alice")
greet("Bob", "Good morning")
greet("Charlie", message="Good afternoon")


# 默认参数不要用可变对象 []/{}：会有问题。
# 可变默认参数只创建一次，之后每次调用共用同一个列表。
#
# 若写成 def add_item(item, buck=[])，三次调用会变成：
#   print(add_item("apple"))   # ['apple']
#   print(add_item("banana"))  # ['apple', 'banana']   ← 不是只有 banana
#   print(add_item("cherry"))  # ['apple', 'banana', 'cherry']
# 期望每次新列表，实际却在往同一个 buck 里追加。
#
# 原因：buck = [] 在函数定义时就建好了，不是每次调用新建。
# 正确写法用 None（如下）；同样不要用 {}、自定义可变对象当默认值。
# 不可变的（None、0、""、()）没这个问题。
def add_item(item, buck=None):
    if buck is None:
        buck = []
    buck.append(item)
    return buck

print(add_item("apple"))
print(add_item("banana"))
print(add_item("cherry"))


def total(_args,*nums):
    return sum(nums)
print(total(1, 2, 3, 4))

def create_user(name,age,**kwargs):
    return {
        name:name,
        age:age,
        **kwargs
    }
print(create_user("Alice", 20, city="Beijing", email="alice@example.com"))
print(create_user("Bob", 21, **{"city":"Shanghai", "email":"bob@example.com"}))


def create_user2(name, age, *args):
    print("args", args)
    # 方式1：整包返回（args 是 tuple）
    # return {"name": name, "age": age, "args": args}

    # 方式2：合并 args 里的 dict —— 几种写法等价（后面的键覆盖前面的）
    # for + update（好读）
    # result = {"name": name, "age": age}
    # for a in args:
    #     result.update(a)
    # return result

    # 推导式一次展开（更紧凑）
    # return {"name": name, "age": age, **{k: v for d in args for k, v in d.items()}}

    # 3.9+ 用 | / |= 合并字典（语法糖）：
    #   a | b   → 返回新字典，a、b 本身不变；等价于 {**a, **b}
    #   a |= b  → 就地更新 a；等价于 a.update(b)
    # 键冲突时右边覆盖左边。Python < 3.9 没有 |，会 TypeError。
    # 例：{"name": "Bob"} | {"city": "Shanghai"}
    #   → {'name': 'Bob', 'city': 'Shanghai'}
    # result = {"name": name, "age": age}
    # for a in args:
    #     result |= a   # 循环里不断 update
    # return result

    return {"name": name, "age": age, **{k: v for d in args for k, v in d.items()}}
# print(create_user2("Alice2", 20, city="Beijing", email="alice@example.com"))  # 关键字参数要用 **kwargs
print(create_user2("Bob2", 21, {"city": "Shanghai", "email": "bob@example.com"}))



# 3) lambda ≈ 箭头函数当回调
students = [
    {"name": "Bob", "score": 95},
    {"name": "Amy", "score": 80},
]
data = sorted(students,key = lambda s : s['score'],reverse=True)
for x in data:
    print(x['name'], x['score'])
# print([x['name'] for x in data])

def summarize_scores(*scores, pass_line=60):
    """返回 dict: count / avg / passed_count"""
    count = len(scores)
    avg = sum(scores) / count
    passed_count = len([s for s in scores if s >= pass_line])
    return {
        'count': count,
        'avg': avg,
        'passed_count': passed_count
    }

print(summarize_scores(80, 55, 70, 60, 100))
print(summarize_scores(80, 95, 70, 60, 100, pass_line=95))










