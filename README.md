
# pysh

pysh可以看作是兼具`shell`和`python`特点的解释器。主要目的是为了在交互模式下, 能同时使用到shell的方便和python的强大表达能力。
在其中，我又加入了一些函数式编程的特性，使得pysh表达能力更强，能写出比python简短多的代码。 
依本人的实践经验，10到20行的python文本处理脚本，pysh常常只需要几行pipeline就能解决

 **如果你在开发过程中有大量的文本处理需求，花半小时了解下，你会发现pysh是一把利器！**


## 主要特性

#### 调用shell命令
"$"后面直接接bash命令; `sh`关键字调用命令
```
$ cd ~ | grep py
$ vim "test.psh"
cmd = " rm %s"
files = ls(".", 'rf') | grep @ ".tmp"
# sh 关键字
for( f in files)
    sh cmd % f   # 删除目录,子目录下所有tmp文件
end
# cd 关键字
cd "/home/user/" + "docs"
cdh   # 全局变量，记录最近访问的目录列表
cd 1  # cd 1 == cd cdh[1]
``` 

#### shell命令python函数化
为了简化原始shell命令的参数记忆，重写的命令只实现了原shell命令的主要功能，再搭配上少量的常用可选参数; 尽量将用法简单化
```python
grep("world", "hello world" )
cat("/home/user/doc/*")  # lazy values 
ls("/home/user/", "f")   # "f" is flag, will return only files
```

#### 惰性求值
惰性求值主要是性能上的考虑，利用的是python的generator机制, 基本上文本处理相关的shell命令，如`cat, grep, replace, extract, more`等，都应用了惰性求值的特性，这样在处理大文件时，pipeline操作不容易遇到瓶颈；


有两个辅助函数：
- `gen` 输入一个可迭代对象返回一个生成器
- `repeat` 输入一个函数，返回一个执行N次的生成器，N==-1则为无限次

> 需要注意的是这些函数返回值必须先取出来才能使用, 比如`"  abc " | strip | next`


#### FP
匿名函数，偏函数, 函数组合, 高阶函数的使用，能写出高效简洁的代码, 常用高阶函数如 `map, mmap, filter, flat, flatMap, fold` 等 
```python
a = L(x, y): x + y  # 匿名函数 L == lambda
_ > 2 ** 3  # L(x):x>2**3
len(_) > 2  # L(x):len(x) > 2
foo(x,_)    # L(y): foo(x, y)
b = a@1     # 函数组合, L(1, y): 1 + y;  b(2) == 3
map@ len # 给定list求每个元素的长度
cat("nnn.txt") | map( _.split(), _) | flatMap( _.strip(',.!"'), _)  | uniq  # list of string 的词汇表
```

#### Pipe & IO
- IO重定向到文件：`&>, &>>`
- 对数据的格式化输入输出，常用函数：`format, list_format, tojson, dumps`等
- 通过管道把不同函数组合起来
```python
 # 从每行都是一个json字符串的文件中解析出json data，并选择["color","size"]两个字段，重新写入新的文件
cat("josn.log") | tojson |  colSel(["color","size"], _) | dumps &> "new_json.log"
 # 统计目录下所有py源文件中的函数定义的数量
cat("source/*") | egrep("^def\s", _) | wc 
 # 输出目录下所有py源文件中的函数名称
cat("source/*") | egrep("^def\s", _) | extract( "def\((\w+)\)", _) | format("{0}", _ ) | list
 
 
 # NLP中的一个常见任务，把分词文件映射成one-hot形式
 # 输入文件格式，空格分开的句子 "knowledge is power"  =>  输出是"100 2 3"这种格式
 # 并且要统计词频，只取top 10000的高频词，不在高频词中的当作UNK，映射到2
 word_count = cat("input.txt") | split@" " | flatMap @ slf | mapValues@ len | list 
 sorted(word_count, key=L(x):x[1], reverse = True)
 word_count | colSel@0 | zipWithIndex(_, 10) | format@ "{0}\t{1}" &> "words"      # word: index file;  maping start from 10
 word_idx_dict = cat("words") | take@10000 | split@"\t" | dict      # 只使用top10000高频词
 cat("input.txt") | split@" " | mmap@int | mmap@ word_idx_dict.get(_, 2)  | list_format@"{0}"  &>  "output.txt"    #  不在10000个词中的词用2代替，
 
```

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
3.  关键词列表：def, is, in, if, else, elif, for, while, break, continue, return, lambda, L, True, False, None, _ , assert, del, sh
4.  操作符列表：and, or, not, +, -, *, **, /, //, %, =, :=, $, |, . , &>, &>>, >, >=, <, <=, !=, ==, @

#### 除了python的关键词与操作符外， 额外增加了一些操作符

- `$`: 代表执行原生的shell命令；比如 `$ls; $cat file | grep xxx`  注意**$** 会fork一个新的子进程运行命令; 所以像$cd这样的命令在当前进程不会生效
- `sh` 关键字实际效果跟`$`一样， 区别是`sh`后面是表达式（返回结果是string即可）， `$`后面直到行尾的都是shell命令的一部分，类似于宏
- `:=`: 代表赋值给全局变量; 功能上替换了python的global关键字
- `&`, `&>>`:  IO重定向，功能上与shell的 ">, >>" 一样， 方便快速输出到文件
- `|`: pipe功能,前面的值当作后面函数的输入， `a | b | c | d = d(c(b(a)))`
- `L`: 等价于lambda关键字，主要为了少打点字， 注： 与python不同的是lambda后面的参数必须用小括号包起来
- `_`: 参数占位符，方便定义偏函数， 这个特性结合PIPE非常方便, 
- `@`: 吸收一个参数返回函数，`f@m == f(m)(..)`



#### 没有支持的python关键词

- try, except, raise, finally, with, pass, yield, class
- exec用 **$** 代替; global赋值用 **:=** 代替, 还是避免全局变量与本地变量名称一致


## Shell & FP

新增函数主要来自于：
- 1.shell命令的python函数形式；
- 2.Functional Programing的一些函数
- 3.其他一些实用函数

具体列表可以看下面 **函数介绍** 的章节

想了解每个函数的用法，可以使用doc函数，比如: `doc(ls)`, 会给出每个函数的定义


## 与python不一样的地方

#### 取消了python的缩进，这样在命令行模式下更加灵活

- 不需要缩进, 每个block用end结束
- lambda, L 的参数必须用小括号包起来
- if, for, while, def后面的冒号去掉;  eg. if(a > b) pass end;  经常忘打冒号，干脆去掉 
- 支持`for( x,y in [(1,2),(3,4),(5,6)])`; 但不支持 `x,y = 1,2`
- 不支持lst[0:]; 可以用lst[0:len(lst)] 替代;  

> 后面两个python语法不支持，主要是实现上相对麻烦

## import机制

1.  支持python的package管理机制，用法跟python的import用法一样
2.  python源文件，必须是.py格式
3.  pysh源文件， 必须是.psh格式

```python
import sys, math
from os import path
import "/home/user/ll/emath.py"     # 用法emath.xxx 
import "/home/user/ll/cmds.psh"     # 用法cmds.xxx  
import "/home/user/ll/emath.py" as mh   # 用法mh.xxx  
```

## Examples

```python
    lst = [1,2,8,1:5, 10:1:-2]
    def qsort(lst)
         if (len(lst) <= 1)
             return lst
         end

         leftpart = (filter@ ( _ < lst[0])) (lst) | list
         rightpart = filter(_ > lst[0], lst) | list
         eqpart = filter(L(x): x == lst[0], lst) | list
         return  qsort(leftpart) + eqpart + qsort(rightpart)
    end
    file = "test.txt"
	# 把test文件去除空行，然后每50行保存到不同的文件下
    line_chunks = cat(file) | filter(L(x): len(x.strip()) >0, _ ) | chunks(50, _)
    for(ck in zipWithIndex(line_chunks))
        ck[0] &> "%d.txt"%ck[1]
    end
```

## Requirements
- python 3
- readline[optional]

## Usage

```sh
python3 repl.py      # open a interactive console
python3 repl.py test.psh params  # run a psh file, main function is entry point
```
命令行模式下支持Vi mode

支持简单的Tab补全

## 函数介绍

|id| functions | describe |
|---| :------------: |:---------------:|
|1| take, takeWhile, drop, dropWhile |  describe |
|2| map,_map, filter, FM, MF, mmap, dmap, kmap | _map:非lazed, FM = filter&map, MF与FM相反, mmap = map&map, dmap = (map1, map2) , kmap= map kth element  | 
|3| groupBy, groupMap, mapValues, flat, flatMap, foldl  |  foldl=reduce, flat= [[..],[..]..] -> [...]; flatMap=flat&map, mapValues对dict value的map，会修改原dict |
|4| zip2, zip3, zipWithIndex, unzip, chunks | zip functions |
|5| gen, slf, repeat, _if , _rSel, _colSel | slf返回自身, _colSel = L(x)：x[...]  |
|6 | pbar, sample, shuf , doc, wrapList   | pbar每N个对象display下,用于监控处理进度, doc可以查看每个函数的定义 |

|id| functions | describe |
|---| :------------: |:---------------:|
|1 | _format, _list_format, _tojson, _dumps |  字符串格式化; 建议直接将python对象dump成可解析的json格式  |
|2 | _grep, _egrep , _extract, _replace, _strip, _split |  文本处理函数，p参数中带"v"则使用正则匹配 |
|3 | wc, cat, more, head, uniq, ksort  |  功能和对应的shell命令相似|
|4 | pwd, is_file, is_dir, ls, mkdir, rm, cp, mv, find | 功能和对应的shell命令相似, 参数p="r"代表递归子目录；建议可以使用$或sh直接调用shell命令 |

"_"开头的函数(除了`_if`, `_map`与map不是对应)都有一个对应的不带下划线的函数，方便批量处理，
func会遍历一个可迭代对象，并调用_func, `func = map@ _func(...)`; 
`grep, egrep, colSel, list_format, format, extract, replace, tojson, dumps, strip, split, rSel`


` wrapList, take, takeWhile, drop, dropWhile, map, filter, filter_not, flat, flatMap, chunks, zip2,zip3, zipWithIndex, FM, MF, mmap, dmap, kmap`
这些函数是惰性求值的(lazyed)， 返回结果是一个生成器对象，有的时候希望立刻得到所有值，有两种方式，一种是 `map(..) | list`, 另一种方式是用带前缀下划线”_“的版本,如 `_map(..)`;  

`_wrapList, _take, _takeWhile, _drop, _dropWhile, _map, _filter, filter_not, _flat, _flatMap, _chunks, _zip2, _zip3, _zipWithIndex, _FM, _MF, _mmap, _dmap, _kmap`
            
值得注意， 上面和下面的带下划线的函数与其对应不带下划线的函数间的关系是有差异的
			
## TODO
1. 补充文档注释
2. import机制的完成测试
