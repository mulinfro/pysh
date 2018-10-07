
import re, types
from itertools import chain
from sh.os_cmd import is_dir, replace_if_star_dir
from collections.abc import Iterable


__all__ = []

def pipe_itertool(func):
    def wrapper(*args, **kw):
        assert(len(args) > 0)
        if not isinstance(ans, types.GeneratorType):
            return func(*args, **kw)
        for line in args[0]:
            new_args = (line,) + args[1:]
            ans = func(*new_args, **kw)
            if ans is not None: yield ans
    return wrapper
    
@pipe_itertool
def grep(line, pat, p=""):
    if pat in line: return line

def gen(iterable):
    for e in iterable:
        yield e

@pipe_itertool
def format(pat):
    for x in iterable:
        if isinstance(x, Iterable):
            yield pat.format(*x)
        else:
            yield pat.format(x)

def wc(iterable, p="l"):
    i = 0
    for x in iterable:
        i += 1
    return i

@pipe_itertool
def egrep(line, pat, p="i"):
    if "i" in p: pattern = re.compile(pat, re.I)
    else:        pattern = re.compile(pat)
    match = pattern.search(line)
    if match:
        return line

@pipe_itertool
def replace(line, pat, repl, p="", cnt=0):
    if "v" not in p:
        return line.replace(pat, repl)
    else:
        return re.replace(pat, repl, line, cnt)


def cat(iterable):
    if type(iterable) == str: iterable = [iterable]
    for path in iterable:
        pathes = replace_if_star_dir(path)
        for file_name in pathes:
            if is_dir(file_name): continue
            f = open(file_name, "r")
            for line in f:
                yield line.rstrip("\n")
            f.close()

@pipe_itertool
def tojson(line):
    import json
    return json.loads(line.strip())

@pipe_itertool
def dumps(var):
    import json
    return json.dump(var, f)

def more(file_name):
    f = open(file_name, "r")
    i = 0
    for line in f:
        yield line
        i += 1
        if i % 10 ==0:
            is_continue = input("more? ")
            if is_continue not in ["", "y", "Y"]: break
    f.close()

def groupby():
    pass

def xreduce(iterable):
    pass

def head(iterable, n=10):
    i = 0
    for line in iterable:
        i += 1
        if i > n: break
        yield line

def awk():
    pass


def join():
    pass

def map(iterable, func):
    for ele in iterable:
        yield func(ele)

def filter(iterable, func):
    for ele in iterable:
        if func(ele):
            yield ele

def mapValues():
    pass

def flat(listOfLists):
    return chain.from_iterable(listOfLists)

def flatMap(f, items):
    return chain.from_iterable(map(items, f))

def sed():
    pass

@pipe_itertool
def split(string, sep="", cnt=0, p=""):
    if "v" in p:
        return re.split(sep, string, cnt)
    else:
        return string.split(sep, cnt)

def findall():
    pass

def search():
    pass

def xsort(lines, n=-1, f="", p=""):
    pass

def uniq(iterable):
    pass
