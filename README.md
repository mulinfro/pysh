
# pysh

`pysh`是融合了`shell`, `python`和`函数式编程`特点的脚本语言。
- `shell`是一种命令语言，可以方便地与操作系统交互；但语言本身比较"弱", 且语法比较"另类"， 难处理复杂需求
- `python`有灵活的数据结构，有丰富的第三方库，是使用最多的脚本语言之一;  但在命令行模式下不太方便
- `函数式编程的特性`，能够更加高效的组织代码， 写出简短的表达能力更强的代码

`pysh`融合了其各自的优点， 是一种在命令行模式下可以便捷地处理数据， 操作文件等。
依本人的实践经验，10到20行的python文本处理脚本，pysh常常只需要几行pipeline就能解决。
如果你对shell命令及参数不熟悉， 或在开发过程中有大量的数据处理需求，花半小时了解下， 可能会对你有用。


## 主要特性

1. 可以和shell一样，在控制台交互式运行
2. 在脚本中可以直接调用shell命令
3. pysh语法和数据结构整体继承自python， 大家熟悉
4. 引入函数式编程的特性， 提高代码灵活性
6. 管道和IO重定向
7. 有大量实用的内置函数，交互更简单 

## Usage
```sh
python3 repl.py                  # open a interactive console
python3 repl.py test.psh params  # run a psh file, main function is entry point

可以配置alias别名, 使用起来跟python一样
alias pysh = 'python3 ${path}/repl.py'
pysh                             # open a interactive console
pysh test.psh params             # run a psh file
```

## Requirements

- python 3.5+
- readline[optional]

> 命令行模式下， readline模块可以支持Vi编辑命令, 支持Tab自动补全等功能

## 数据结构和语法

- pysh是一个解释器，会把新的语言脚本转换成python代码执行，所以数据结构与python基本一致
- 语法上整体差别比较大，表达式层面与python语法差不多，但额外增加函数式语言和管道的特性， 取消了缩进等； 具体见`SYNTAX.md`文件

## 内置函数
想了解内置函数的用法，可以使用doc函数，比如: `doc(ls)`, 会给出对应函数的定义和用法

## Examples

##### 例子1: 执行shell命令
```python
    # 两种方式: 1. "$"后面直接接bash命令 
    # 打开vim, 编辑文件
    $ vim test.py
    # 2.`sh`关键字调用命令
    # 运行test.psh文件
    cmd = "python3 test.py"
    sh cmd

    # 递归地将所有文件名中的大写字母改为小写字母
    base_dir = "/home/user/mulinfor"
    cd base_dir + "/docs"
    # ls命令， r是递归， f表示只选取文件，不输出目录
    files = ls(".", "rf")
    # 导入python的库
    import os.path as path
    cmd = "mv %s %s"
    for f in files
        dname = path.dirname(f)
        fname = path.basename(f).lower()
        sh cmd % (f, path.join(dname + fname))
    end
```

##### 例子2: 函数式语言特性
```python
    def qsort(lst)
        if len(lst) <= 1
            return lst
        end

        # @ 可以构造偏函数， func2 = func@a = func(a, ..)
        # _ 表示匿名函数中参数, _ < 1 等价于 lambda x: x < 1
        left  = lst | filter@ _ < lst[0] | list
        right = lst | filter@ _ > lst[0] | list
        eqs   = filter(_ == lst[0], lst) | list
        return  qsort(left) + eqs + qsort(right)
    end


    # 1:5 == range(1, 5)
    lst = [1,2,8, 1:5, 10:1:-2]
    qsort(lst) 
    输出： [1, 1, 2, 2, 2, 3, 4, 4, 6, 8, 8, 10]
```

##### 例子3: 管道, IO重定向和内置函数
```python
    # word count
    file = "test.txt"
    # 最后返回 the:111,  good:10, ...； 需要注意有些函数如filter是惰性的， 通过list强制完成所有计算
    # ~ 符号会提升一个函数， ~func 效果等价于 map@func
    #  逐行读入文件| 按tab分割   | flatten | 转成小写字母| 计数 |过滤空字符串 
    words = cat(file) | ~split@"\t" | flat | map@_.lower() | count | items | filter@L x: len(x.strip()) >0 | list
    # 按照数量逆序排序, L是lambda的简写
    words_sorted = words | sort(_, key=L x: -x[1])
    # 按照 word \t cnt的格式， 输出到out.txt 文件
    words_sorted | listFormat &> "out.txt"

	# 把test文件去除空行，然后每50行保存到不同的文件下
    line_chunks = cat(file) | filter@L x: len(x.strip()) >0 | chunks@50
    for ck in zipWithIndex(line_chunks)
        ck[0] &> "%d.txt"%ck[1]
    end
```