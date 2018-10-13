# pysh：融合python和shell的脚本语言

pysh的目的是希望能够像python那样写shell命令, 简洁富有表达力
项目背景源于本人在学习使用shell的时候感到的一些麻烦：
- shell命令参数众多，难以记忆
- shell命令的语法不是太严格，不同命令之间的用法会有差异, 还有挺多恼人的特殊情形
- shell没有数据结构，管道连接的是文本， 这使得shell很难处理复杂一点的任务

在日常处理数据中，常常需要写一些简单的python脚本，虽然不复杂，但python终究没有shell命令来的灵活和直接；
由此我尝试把这两种语言的特点结合起来，在实现这个想法的过程中，我又加入了函数式编程中的特性，使得pysh表达能力更强。 
本人的实践体验：10到20行的python脚本，pysh常常只需要一行pipeline就能解决

> 如果你在开发过程中有大量的文本处理需求，花半小时了解下，你会发现pysh是一把利器！


## 数据结构：

#### 与python基本一致

**String**： 
```python
"hello world!" 
'joes\'s apple' 
""" multiline "line" ... line """
```
**Tuple**:   
```python
(1,2,3) 
(1+2, len("scala"))
```
**List**:    
```python
[1, lambda(x): x+1, [2,3,4]] 
[0, 2:100:2, 100] == [0] + list(range(0, 100, 2)) + [100] 
```
**Dict**:
```python
{1:'a', 'c':3}
```
**Expression**:
```python
fl = L(x,y,z): x+y    # L == lambda
fl2 = lambda (x,y): x * y  # 匿名函数
add_one = fl(_, 1)  # 偏函数
2/2 + 2/3.0 -(5.2 + 2 * add_one(2) + fl2(2, -+-3))  # -15.5333333
```

#### 不同之处：

- tuple语法上不支持 `(1,)` 这种长度为1的tuple，想用可以用`tuple([1])`替代
- list支持 start:stop:[, step] => range(start, stop, step)
- 支持多选， 比如：
```python
lst = [0:100]          # [1,2,3,..,99]
lst[1,3,5] == [1,3,5]  #True
dict([(1,'a'),(3,'c')]) [1,3] == ['a', 'c']   # True
```


## 关键词和内置函数：

1.  支持python的所有内置函数
2.  关键词列表：def, is, in, if, else, elif, for, while, break, continue, return, lambda, L, True, False, None, _
3.  操作符列表：and, or, not, +, -, *, **, /, //, %, =, :=, $, |, . , &>, &>>, >, >=, <, <=, !=, ==

#### 除了python的关键词与操作符外， 额外增加了一些操作符

- `$`: 代表执行原生的shell命令；比如 `$ls; $cat file | grep xxx`  注意**$** 会fork一个新的子进程运行命令; 所以像$cd这样的命令在当前进程不会生效
- `:`: 代表赋值给全局变量; 功能上替换了python的global关键字
- `&`, `&>>`:  IO重定向，功能上与shell的 ">, >>" 一样， 方便快速输出到文件
- `|`: pipe功能,前面的值当作后面函数的输入， `a | b | c | d = d(c(b(a)))`
- `L`: 等价于lambda关键字，主要为了少打点字， 注： 与python不同的是lambda后面的参数必须用小括号包起来
- `_`: 参数占位符，方便定义偏函数， 这个特性结合PIPE非常方便, 

```python
_ > 2 ** 3  # L(x):x>2**3
len(_) > 2  # L(x):len(x) > 2
_.strip()   # L(x):x.strip()
foo(x,_)    # L(y): foo(x, y)
```

#### 没有支持的python关键词

- try, except, raise, finally, assert, with, pass, yield, class
- exec用 **$** 代替; global赋值用 **:=** 代替, 还是避免全局变量与本地变量名称一致


## shell & FP：

#### 新增函数主要来自于：1.shell命令的python函数形式；2. Functional Programe的一些函数

- shell命令列表： ls, pwd, rm, cp, mv, mkdir, rm find, grep, egrep, wc, cat, more, uniq, head, xsort
- FP函数列表： map, filter, take, takeWhile, flat, flatMap, drop, groupBy, join, mapValues, xzip, zipWithIndex, chunks
- 其他一些有用函数：, format, extract, replace, split, tojson, dumps, gen

#### Examples：  

```python
py_files = ls(".", p='rf') | gen | egrep(_, ".py$") | map(_, cat) 
```

## 一些与python不一样的地方：

#### 取消了python的缩进，这样在命令行模式下更加灵活

- 不需要缩进
- 每个block用end结束
- lambda, L 的参数必须用小括号包起来
- if, for, while, def后面的冒号去掉;  eg. if(a > b) pass end;  经常忘打冒号，干脆去掉 

## import机制：

1.  支持python的package管理机制，用法跟python的import用法一样；
2.  python源文件，必须是.py格式
3.  pysh源文件， 必须是.psh格式

```python
import sys, math
from os import path
import("/home/user/ll/emath.py" )   # 用法emath.log  
import("/home/user/ll/cmds.psh" )   # 用法cmds.log  
import("/home/user/ll/emath.py" ) as mh   # 用法mh.log  
```

## Examples

```python
    lst = [1,2,8,1:5, 10:1:-2]
    def qsort(lst)
         if (len(lst) <= 1)
             return lst
         end

         leftpart = filter(lst, _ < lst[0]) | list
         rightpart = filter(lst, _ > lst[0]) | list
         eqpart = filter(lst, L(x): x == lst[0]) | list
         return  qsort(leftpart) + eqpart + qsort(rightpart)
    end
```

## TODO
