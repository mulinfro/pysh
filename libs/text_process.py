import re, random
from types import GeneratorType
from libs.os_cmd import isDir, replace_if_star_dir
from collections.abc import Iterable
import json, collections

_pipe_func = ['grep', 'egrep', 'colSel', 'colRm', 'listFormat', 'format', 
            'extract', 'replace', 'tojson', 'dumps', 'strip', 
            'split', 'rSel', "uniqBy","uniqKvBy", "toUtf8", "jStr" ]
_other_func = ['sample', 'shuf', 'gen', 'wc', 'cat', 'more', 'readPair', 'readStringPair',
            'findall', 'search', 'uniq', 'ksort', 'sort', 'jsonEqual', 'replaceWithList']

__all__ = _pipe_func + _other_func

def jStr(m):
    """
        jStr(json_obj: object)
            dumps a object to string
        
        args:
            json_obj = "{1:2}"
        return json string:
    """
    return json.dumps(m, ensure_ascii =False, indent=2)

def jsonEqual(ja, jb):
    """
       jsonEqual(obj1, obj2) -> Boolean
            determine two object(can be dumped by json) whether is equal

       args:
           obj1 = {1:1, {2:2, "a":"a"}};  obj2 = {1:1, {2:2, "a":"a"}}
       return: Boolean
           True
    """
    return json.dumps(ja, sort_keys=True) == json.dumps(jb, sort_keys=True)

def replaceWithList(pats, iterable, cnt=-1):
    ans = [pats.get(i, i) for i in iterable]
    return "".join(ans)

def pipe_gen_itertool(func, N=0):
    def wrapper(*args, **kw):
        assert(len(args) > 0)
        if not isinstance(args[0], GeneratorType):
            ans = func(*args, **kw)
            if ans is not None: yield ans
        else:
            for line in args[N]:
                new_args = (line,) + args[1:]
                ans = func(*new_args, **kw)
                if ans is not None: yield ans
    return wrapper

def pipe_text_itertool(func):
    def wrapper(*args, **kw):
        assert(len(args) > 0)
        if type(args[0]) == str:
            ans = func(*args, **kw)
            if ans is not None: yield ans
        else:
            for line in args[0]:
                new_args = (line,) + args[1:]
                ans = func(*new_args, **kw)
                if ans is not None: yield ans
    return wrapper

def sample(sample_rate, iterable):
    """
        sample(sample_rate, iterable)
            get samples from iterable with "sample_rate" percent 

        args:
            sample_rate = 0.1; iterable = [1,2,3,4,5,6,7,8,9,0]
        return: Lazyed!! return type is generator
            samples
    """
    for x in iterable:
        if random.uniform(0,1) < sample_rate:
            yield x

def shuf(iterable):
    """
        shuf(iter: List)
            shuf List, return self

        args:
           iter = [1,2,3]
        return: 
           may be: [2,3,1]
    """
    random.shuffle(iterable)
    return iterable

def grep(pat, lines):
    """
        grep(pat: string, lines: iterable[string])
            determine if pat in each line

        args:
            pat = "hello";  lines = ["hello world", "haha", "QQ hello"]
        return: Lazyed!! return type is generator
            "hello world"..  "QQ hello"

    """
    for line in lines:
        if pat in line:
            yield line

def toUtf8(s, encoding="gbk"):
    """
        toUtf8(s: string, encoding="gbk")
            s to utf8 encoding
    """
    return s.decode(encoding).encode("utf-8")

def egrep(pat, lines, p="i"):
    """
        egrep(pat: string, lines: iterable[string], p="i")
            determine if regular patttern match each line

            pat is python regular expression
            p = "i" ignore case

        args:
            pat = "^hello";  lines = ["hello world", "haha", "QQ hello"]
        return: Lazyed!! return type is generator
            "hello world"
    """
    for line in lines:
        if "i" in p: pattern = re.compile(pat, re.I)
        else:        pattern = re.compile(pat)
        match = pattern.search(line)
        if match:
            yield line

def readPair(iterable, beg_tkn, end_tkn):
    t_iter = iter(iterable)
    for ele in t_iter:
        if ele != beg_tkn:
            yield (ele, "SINGLE")
        else:
            ans, tp = [], "HALF_CLOSE" 
            for ele in t_iter:
                if ele == end_tkn:
                    tp = "CLOSE"
                    break
                else:
                    ans.append(ele)
            yield (ans, tp)


def readStringPair(str_input, beg_tkn, end_tkn):
    ans, i = [], 0
    while i < len(str_input):
        if not str_input.startswith(beg_tkn, i):
            ans.append(str_input[i])
            i = i + 1
        else:
            k = i
            i = i + len(beg_tkn)
            tp = "HALF_CLOSE" 
            while i < len(str_input):
                if str_input.startswith(end_tkn, i):
                    tp = "CLOSE"
                    break
                else:
                    i = i + 1
            if tp == "HALF_CLOSE":
                ans.extend(list(str_input[k: i]))
            else:
                ans.append(str_input[k+len(beg_tkn): i])
                i = i + len(end_tkn)

    return ans

def gen(iterable):
    """ 
        gen(iter: iterable)
        accept a iterable object; return a generator

        implement:
            for e in iterable: yield e
    """
    for e in iterable:
        yield e

def colSel(idxes, iterable):
    """
        colSel(idxes, iter: iterable)

        example: 
            idxes = 1;     iter = [1,2,3] => 2
            idxes = [1,2]; iter = [1,2,3] => [2, 3]
            idxes = ("b", "a"); iter = {"a":"a", "b":"b"} => ["b", "a"]
    """
    if type(idxes) not in (list, tuple):
        return iterable[idxes]
    return [iterable[idx] for idx in idxes]

def colRm(idxes, iterable):
    if type(idxes) not in (list, tuple):
        idxes = [idxes]
    return [ iterable[i] for i in range(len(iterable)) if i not in idxes]

def listFormat(iterable, pat="{0}", sep="\t"):
    """
        listFormat(iter: iterable, pat="{0}", sep="\t")
            format a list to string
            pat format each list element
            sep join the elements

        args:
            iter = [[1,2], [2,3], [3,4]], pat="{0[1]}"; sep = ";"
        return:
            "2;3;4"
    """
    return sep.join( [pat.format(ele) for ele in iterable] )

def format(pat, x):
    """
        format(pat, x)
           pat.format(x)
    """
    return pat.format(x)

def wc(iterable):
    """
        wc(iter: iterable)
            return size of "iter"

        args:
            iter = [[1,2], [2,3], [3,4]]   iter = {}
        return:
            3                              0

    """
    i = 0
    for x in iterable:
        i += 1
    return i


def extract(pat, line):
    """ extract(pat, line)
        re.search(pat, line).groups()
    """
    match = re.search(pat, line)
    if match:
        return match.groups()

def rSel(iterable):
    """ rSel(iterable)\nrandom select a element"""
    if type(iterable) == dict:
        return random.choice(list(iterable.items()))
    else:
        idx = random.randint(0, len(iterable) - 1)
        return iterable[idx]

def replace(pat, repl, line, cnt=-1, p=""):
    """string replace
       parms: pattern, replace_str, line, cnt=inf
       p = [v] v: using python module re.sub
    """
    if "v" not in p:
        if type(pat) == str:
            return line.replace(pat, repl, cnt)
        else:
            for pp in pat:
                line = line.replace(pp, repl, cnt)
            return line
    else:
        if cnt < 0: cnt = 0
        return re.sub(pat, repl, line, cnt)

def cat(iterable, p="utf-8", errors='ignore'):
    """ 
       cat(iter: string | List[string], p="utf-8", errors='ignore')
       input: a single path or a list of pathes

       return: Lazyed!! lines
       example:
           cat("file1.txt")
           cat(["file1.txt", "file2.txt", "file3.txt"], "gbk")

    """
    if type(iterable) == str: iterable = [iterable]
    for path in iterable:
        pathes = replace_if_star_dir(path)
        for file_name in pathes:
            if isDir(file_name): continue
            f = open(file_name, "r", encoding=p, errors=errors)
            for line in f:
                yield line.rstrip("\n\r")
            f.close()

def tojson(line):
    """python json loads"""
    return json.loads(line.strip())

def dumps(var, indent=None):
    """python json dumps"""
    return json.dumps(var, indent=indent, ensure_ascii=False)

def more(file_name):
    """shell: more
       y, Y, Enter: continue 
       others: break 
    """
    i = 0
    if type(file_name) == str:
        iterable = cat(file_name)
    else:
        iterable = file_name
    for line in iterable:
        yield line
        i += 1
        if i % 10 ==0:
            try:
                if input("more? ").strip() not in ["", "y", "Y"]: break
            except KeyboardInterrupt:
                print("\n")
                break


def strip(string, p=" \t\n\r"):
    """
        strip(string, p=" \t\n\r")
    """
    return string.strip(p)

def split(sep, string, cnt=-1, p=""):
    """_split(sep, string, cnt=-1, p="")
    p="v": use re.split
    """
    if "v" in p:
        if cnt < 0: cnt = 0
        return re.split(sep, string, cnt)
    else:
        return string.split(sep, cnt)

def ksort(k, lst, key=lambda x:x, p=""):
    """
        ksort(k, lst, key, p="")
        key(ele[k]): kth element as key
        p="r" -> reversed
    """
    rev_flag = True if "r" in p else False
    lst.sort(key=lambda x:key(x[k]), reverse = rev_flag)
    return lst

def sort(lst, key=lambda x:x, p=""):
    """
        sort(lst, key, p="")
        key(ele): key function
        p="r" -> reversed
    """
    rev_flag = True if "r" in p else False
    lst.sort(key=key, reverse = rev_flag)
    return lst

def uniq(iterable):
    """
        uniq(iter: iterable)
            return list of all elements with no duplication
            list(set(iter))

        args:
            iter = "abbcdd"
        return:
            ["a", "c", "b", "d"]
    """
    return list(set(iterable))

def uniqBy(iterable, key=lambda x:x):
    """
        uniqBy(iter: iterable, key=func)
            inplaced; won't change relative position
            key function to identity 
            
        args:
            iter = "abbcdd"; key = L x: {{"b":"c"}.get(x, x)}
        return: 
            ['a', 'b', 'd']
    """
    dic = collections.OrderedDict()
    for x in iterable:
        key_v = key(x)
        if key_v not in dic:
            dic[key_v] = x
    return list(dic.values())

def uniqKvBy(iterable, key=lambda x:x):
    """
        uniqKvBy(iter: iterable, key=func)
            inplaced; won't change relative position
            key function to identity 
            return [ (key(ele), ele )]
            
        args:
            iter = "abbcdd"; key = L x: {{"b":"c"}.get(x, x)}
        return: 
            [('a', 'a'), ('c', 'b'), ('d', 'd')]
    """
    dic = collections.OrderedDict()
    for x in iterable:
        key_v = key(x)
        if key_v not in dic:
            dic[key_v] = x
    return list(dic.items())
    
