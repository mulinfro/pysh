pysh：融合python和shell的脚本语言
=======

pysh使用python实现，语法大部分继承自python，在此基础增加了一些shell的语法特性。


pysh的特点
-------

1.  支持python的所有内置函数
2.  支持python的package管理机制，用法跟python的import用法一样；python文件及pysh文件都支持
3.  数据结构跟python一样，List， Dict， Tuple，True|False， String
4.  关键词列表: def, is, in, if, else, for, while, break, continue, return, lambda 
5.  操作符列表：and, or, not, +, -, *, /, %, =, :=, $, |, . , &>, &>>, >, >=, <, <=, !=, ==


与python不一样的地方
----------------

1. 不需要缩进，用end来表示一个block的结束
2. lambda后面的参数跟函数定义一样需要括号
3. for, if ,while, def这些定义需要括号，最后面不需要冒号，eg. if(a > b) pass end


新增的特性
----------------
1. 管道PIPE, eg: ls() | cat(p="r") | wc (统计当前目录下的所有文件的行数; "r"参数表示包含所有子目录中文件)
2. IO重定向到文件的操作符 &>  &>>  用于快速输出文件
3. 调用shell原生命令的操作符； 如果需要调用原始的shell命令，用这个语法
4. 偏函数定义; 用"_"表示占位符，f(_, y)(x) == f(x,y); 这个特性结合PIPE很方便
5. list切片，dict取list里所有对象
6. 部分shell命令的pythonic实现

examples
-------
		[1,2,8,1:5, 10:1:-2]
		def qsort(lst)
            if (len(lst) <= 1)
                return lst
            end

            leftpart = filter(lst, _ < lst[0]) | list
            rightpart = filter(lst, _ > lst[0]) | list
            eqpart = filter(lst, L(x): x == lst[0]) | list
            return  qsort(leftpart) + eqpart + qsort(rightpart)
		end
		
重写的shell命令介绍
--------------------

sh目录中把一些常见的shell命令都用python重新实现了下，输入输出参数会与原始的shell命令有差异
grep
egrep
cat
ls



TODO
--------------------
