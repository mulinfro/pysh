import re
from types import GeneratorType
from sh.os_cmd import is_dir, replace_if_star_dir
from collections.abc import Iterable
import json

__all__ = ['sample', 'shuf', 'grep', 'egrep', 'gen', 'colSel', 'list_format', 'format', 
            'wc', 'extract', 'replace', 'cat', 'tojson', 'dumps', 'more', 'strip', 'head',
            'join', 'split', 'findall', 'search', 'uniq', ]


def pipe_gen_itertool(func):
    def wrapper(*args, **kw):
        assert(len(args) > 0)
        if not isinstance(args[0], GeneratorType):
            ans = func(*args, **kw)
            if ans is not None: yield ans
        else:
            for line in args[0]:
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
    import random
    for x in iterable:
        if random.uniform(0,1) < sample_rate:
            yield x

def shuf(iterable):
    import random
    random.shuffle(iterable)
    return iterable


@pipe_text_itertool
def grep(pat, line, p=""):
    if pat in line: 
        return line

@pipe_text_itertool
def egrep(pat, line, p="i"):
    if "i" in p: pattern = re.compile(pat, re.I)
    else:        pattern = re.compile(pat)
    match = pattern.search(line)
    if match:
        return line

def gen(iterable):
    for e in iterable:
        yield e

@pipe_gen_itertool
def colSel(idxes, iterable):
    if type(idxes) not in (list, tuple):
        return iterable[idxes]
    return [iterable[idx] for idx in idxes]

@pipe_gen_itertool
def list_format(pat, iterable, sep=" "):
    return sep.join( [pat.format(ele) for ele in iterable] )

@pipe_gen_itertool
def format(pat, x):
    if isinstance(x, Iterable):
        return pat.format(*x)
    else:
        return pat.format(x)

def wc(iterable, p="l"):
    i = 0
    for x in iterable:
        i += 1
    return i


@pipe_text_itertool
def extract(pat, line):
    match = re.search(pat, line)
    if match:
        return match.groups()

@pipe_text_itertool
def replace(pat, repl, line, cnt=-1, p=""):
    """string replace
       parms: pattern, replace_str, line, cnt=inf
       p = [v] v: using python module re.sub
    """
    if "v" not in p:
        return line.replace(pat, repl, cnt)
    else:
        if cnt < 0: cnt = 0
        return re.sub(pat, repl, line, cnt)


def cat(iterable):
    """ shell: cat
        input: a single path or a list of pathes
    """
    if type(iterable) == str: iterable = [iterable]
    for path in iterable:
        pathes = replace_if_star_dir(path)
        for file_name in pathes:
            if is_dir(file_name): continue
            f = open(file_name, "r", encoding="utf-8")
            for line in f:
                yield line.rstrip("\n")
            f.close()

@pipe_gen_itertool
def tojson(line):
    """python json loads"""
    return json.loads(line.strip())

@pipe_gen_itertool
def dumps(var):
    """python json dumps"""
    return json.dumps(var, ensure_ascii=False)

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
                break


@pipe_text_itertool
def strip(string, p=" \t\n\r"):
    return string.strip(p)


def head(iterable, n=10):
    """ shell: head """
    i = 0
    for line in iterable:
        i += 1
        if i > n: break
        yield line


def join():
    pass

def awk():
    pass

def sed():
    pass

@pipe_text_itertool
def split(string, sep=None, cnt=-1, p=""):
    if "v" in p:
        if cnt < 0: cnt = 0
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
    ans = set()
    for x in iterable:
        if x not in ans:
            ans.add(x)
    return list(ans)

