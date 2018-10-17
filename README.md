# pysh

pysh可以看作是兼具`shell`和`python`特点的解释器。主要目的是为了在交互模式下, 能同时使用到shell的方便和python的强大表达能力。
在其中，我又加入了一些函数式编程的特性，使得pysh表达能力更强，能写出比python简短多的代码。 
依本人的实践经验，10到20行的python文本处理脚本，pysh常常只需要一行pipeline就能解决

 **如果你在开发过程中有大量的文本处理需求，花半小时了解下，你会发现pysh是一把利器！**


## 数据结构

#### 与python基本一致

```python
"String" 
"hello world!" 
'joes\'s apple' 
""" multiline "line" ... line """

"Tuple"   
(1,2,3) 
(1+2, len("scala"))

"List"    
[1, lambda(x): x+1, [2,3,4]] 
[0, 2:100:2, 100] == [0] + list(range(0, 100, 2)) + [100] 

"Dict"
{1:'a', 'c':3}

"Expression"
fl = L(x,y,z): x+y    # L == lambda
fl2 = lambda (x,y): x * y  # 匿名函数
add_one = fl(_, 1)  # 偏函数
2/2 + 2/3.0 -(5.2 + 2 * add_one(2) + fl2(2, -+-3))  # -15.5333333
```

#### 不同之处

- tuple语法上不支持 `(1,)` 这种长度为1的tuple，想用可以用`tuple([1])`替代
- list支持 start:stop:[, step] => range(start, stop, step)
- 支持一次取多值， 比如：
```python
lst = [0:100]          # [1,2,3,..,99]
lst[1,3,5] == [1,3,5]  #True
dict([(1,'a'),(3,'c')]) [1,3] == ['a', 'c']   # True
```


## 关键词和内置函数

1.  `#`:表示缩进
2.  支持python的所有内置函数
3.  关键词列表：def, is, in, if, else, elif, for, while, break, continue, return, lambda, L, True, False, None, _
4.  操作符列表：and, or, not, +, -, *, **, /, //, %, =, :=, $, |, . , &>, &>>, >, >=, <, <=, !=, ==  

#### 除了python的关键词与操作符外， 额外增加了一些操作符

- `$`: 代表执行原生的shell命令；比如 `$ls; $cat file | grep xxx`  注意**$** 会fork一个新的子进程运行命令; 所以像$cd这样的命令在当前进程不会生效
- `:=`: 代表赋值给全局变量; 功能上替换了python的global关键字
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


## Shell & FP

新增函数主要来自于：1.shell命令的python函数形式；2. Functional Program的一些函数

- shell命令列表： ls, pwd, rm, cp, mv, mkdir, rm, find, grep, egrep, wc, cat, more, uniq, head, xsort
- FP函数列表： map, filter, take, takeWhile, flat, flatMap, drop, groupBy, join, mapValues, zip2, zipWithIndex, chunks
- 其他一些有用函数：format, extract, replace, split, tojson, dumps, gen, help
想了解每个函数的用法，可以使用help函数，比如: `help(ls)`

#### Examples

```python
 # 从每行都是一个json字符串的文件中解析出json data，并选择["color","size"]两个字段，重新写入新的文件
cat("josn.log") | tojson |  colSel(_, ["color","size"]) | dumps &> "new_json.log"
 # 统计目录下所有py源文件中的函数定义的数量
cat("source/*") | egrep(_, "^def\s") | wc 
 # 输出目录下所有py源文件中的函数名称
cat("source/*") | egrep(_, "^def\s") | extract(_, "def\((\w+)\)") | list
 # 
py_files = ls(".", p='rf') | gen | egrep(_, ".py$") | map(_, cat) 
```

## 与python不一样的地方

#### 取消了python的缩进，这样在命令行模式下更加灵活

- 不需要缩进
- 每个block用end结束
- lambda, L 的参数必须用小括号包起来
- if, for, while, def后面的冒号去掉;  eg. if(a > b) pass end;  经常忘打冒号，干脆去掉 

## import机制

1.  支持python的package管理机制，用法跟python的import用法一样
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
    file = "test.txt"
	# 把test文件去除空行，然后每50行保存到不同的文件下
    line_chunks = cat(file) | filter(_, L(x): len(x.strip()) >0 ) | chunks(_, 50)
    for(ck in zipWithIndex(line_chunks))
        ck[0] &> "%d.txt"%ck[1]
    end
```

## requirements:
- python 3
- readline[optional]

## Usage

```sh
python3 repl.py      # open a interactive console
python3 repl.py test.psh params  # run a psh file, main function is entry point
```


## TODO
1. 补充文档注释
2. import机制的完成测试

