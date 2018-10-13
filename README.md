# pysh：融合python和shell的脚本语言

pysh使用python实现，语法大部分继承自python，在此基础增加了一些shell和FP的特点。


## 数据结构：

### 与python基本一致

**String**： 
```python
"hello world!" 
'joes\' apple' 
""" multiline "line" ... line """
```
**Tuple**:   
```python
(1,2,3) 
(1+2, len("sacla"))
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
### 不同之处：

- tuple语法上不支持(1,) 这种长度为1的tuple，可以用tuple([1])替代
- list支持 start:stop:[, step] = range(start, stop, step)
- 支持多选， 比如：
```python
lst = [0:100]          # [1,2,3,..,99]
lst[1,3,5] == [1,3,5]  #True
dict([(1,'a'),(3,'c')]) [1,3] == ['a', 'c']   # True
```


## 关键词和内置函数：

1.  支持python的所有内置函数
2.  关键词列表：def, is, in, if, else, elif，for, while, break, continue, return, lambda，L, True， False， None, _
3.  操作符列表：and, or, not, +, -, *, /, %, =, :=, $, |, . , &>, &>>, >, >=, <, <=, !=, ==

### 关键词与操作符含义与python基本一致，但也有一些不同的地方

- "$": 代表执行原生的shell命令；比如 $ls; $cat file | grep xxx; 注意$会fork一个新的子进程运行命令; 所以像$cd这样的命令在当前进程不会生效
- ":=": 代表赋值给全局变量; 功能上替换了python的global关键字
- "&>", "&>>" 功能上与shell的 ">, >>" 一样， IO重定向，方便快速输出到文件
- "|": pipe功能,前面的值当作后面函数的输入， a | b | c | d = d(c(b(a)))； 这个特性结合PIPE非常方便
- "L": 等价于lambda关键字，主要是能少打点字， 注： 与python不同的是lambda后面的参数必须用小括号包起来
- "_" : 参数占位符，方便定义偏函数， 比如 _ > 2 => L(x):x>2;  len(_) > 2;  _.strip() => L(x):x.strip();  foo(x,_) => L(y): foo(x, y)


## shell & FP：

### 新增函数主要来自于：1.shell命令的python函数形式；2. Functional Programe的一些函数

- shell命令列表： ld, pwd, rm, cp, mv, mkdir, rm find, grep, egrep, wc, cat, more, uniq, head, xsort
- FP函数列表： map, filter, take, takeWhile, flat, flatMap, drop, groupBy, join, mapValues, xzip, zipWithIndex, chunks
- 其他一些有用函数：, format, extract, replace, split, tojson, dumps, gen

### Examples：  

```python
py_files = ls(".", p='rf') | gen | egrep(_, ".py$") | map(_, cat) 
```

## 缩进：

### 取消了python的缩进，这样在命令行模式下更加灵活

1. 不需要缩进
2. 每个block用end结束

## import机制：

1.  支持python的package管理机制，用法跟python的import用法一样；python文件及pysh文件都支持
2. lambda后面的参数跟函数定义一样需要括号
3. for, if ,while, def这些定义需要括号，最后面不需要冒号，eg. if(a > b) pass end

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

重写的shell命令介绍
sh目录中把一些常见的shell命令都用python重新实现了下，输入输出参数会与原始的shell命令有差异
