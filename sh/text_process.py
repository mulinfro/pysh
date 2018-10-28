import re, random
from types import GeneratorType
from sh.os_cmd import is_dir, replace_if_star_dir
from collections.abc import Iterable
import json


_pipe_func = ['grep', 'egrep', 'colSel', 'list_format', 'format', 
            'extract', 'replace', 'tojson', 'dumps', 'strip', 
            'split', 'rSel' ]
_other_func = ['sample', 'shuf', 'gen', 'wc', 'cat', 'more', 'head',
            'join', 'findall', 'search', 'uniq', 'ksort']

__all__ = _pipe_func + _other_func + list(map(lambda x: "_"+x, _pipe_func))

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


def pipe_itertool(func, n):
    def wrapper(*args, **kw):
        for line in args[n]:
            new_args = args[0:n] + (line, ) + args[n+1:]
            ans = func(*new_args, **kw)
            if ans is not None: yield ans
    return wrapper


def sample(sample_rate, iterable):
    """Lazyed: sample(sample_rate, iterable)"""
    for x in iterable:
        if random.uniform(0,1) < sample_rate:
            yield x

def shuf(iterable):
    """shuf(iterable)\ninplace shuf, return self """
    random.shuffle(iterable)
    return iterable


def _grep(pat, line):
    """_grep(pat, line)\npat in line?  """
    if pat in line:
        return line

grep = pipe_itertool(_grep, 1)

def _egrep(pat, line, p="i"):
    """_egrep(pat, line, p="i")"""
    if "i" in p: pattern = re.compile(pat, re.I)
    else:        pattern = re.compile(pat)
    match = pattern.search(line)
    if match:
        return line

egrep = pipe_itertool(_egrep, 1)

def gen(iterable):
    """ for e in iterable: yield e """
    for e in iterable:
        yield e

def _colSel(idxes, iterable):
    """_colSel(idxes, iterable)"""
    if type(idxes) not in (list, tuple):
        return iterable[idxes]
    return [iterable[idx] for idx in idxes]
colSel = pipe_itertool(_colSel, 1)

def _list_format(pat, iterable, sep=" "):
    """_list_format(pat, iterable, sep=" ")"""
    return sep.join( [pat.format(ele) for ele in iterable] )

list_format = pipe_itertool(_list_format, 1)

def _format(pat, x):
    """_format(pat, x): 
 Iterable: pat.format(*x) else pat.format(x)
    """
    if isinstance(x, Iterable):
        return pat.format(*x)
    else:
        return pat.format(x)

format = pipe_itertool(_format, 1)

def wc(iterable):
    """ wc(iterable)\niterable count """
    i = 0
    for x in iterable:
        i += 1
    return i


def _extract(pat, line):
    """ _extract(pat, line)
        re.search(pat, line).groups()
    """
    match = re.search(pat, line)
    if match:
        return match.groups()

extract = pipe_itertool(_extract, 1)

def _rSel(iterable):
    """ _rSel(iterable)\nrandom select a element"""
    if type(iterable) == dict:
        return random.choice(list(iterable.items()))
    else:
        idx = random.randint(0, len(iterable) - 1)
        return iterable[idx]

rSel = pipe_itertool(_rSel, 0)

def _replace(pat, repl, line, cnt=-1, p=""):
    """string replace
       parms: pattern, replace_str, line, cnt=inf
       p = [v] v: using python module re.sub
    """
    if "v" not in p:
        return line.replace(pat, repl, cnt)
    else:
        if cnt < 0: cnt = 0
        return re.sub(pat, repl, line, cnt)

replace = pipe_itertool(_replace, 2)

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

def _tojson(line):
    """python json loads"""
    return json.loads(line.strip())

tojson = pipe_itertool(_tojson, 0)

def _dumps(var, indent=None):
    """python json dumps"""
    return json.dumps(var, indent=indent, ensure_ascii=False)

dumps = pipe_itertool(_dumps, 0)

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


def _strip(string, p=" \t\n\r"):
    """_strip(string, p=" \t\n\r")"""
    return string.strip(p)

strip = pipe_itertool(_strip, 0)


def head(iterable, n=10):
    """ shell: head """
    i = 0
    for line in iterable:
        i += 1
        if i > n: break
        yield line


def _split(sep, string, cnt=-1, p=""):
    """_split(sep, string, cnt=-1, p="")
    p="v": use re.split
    """
    if "v" in p:
        if cnt < 0: cnt = 0
        return re.split(sep, string, cnt)
    else:
        return string.split(sep, cnt)

split = pipe_itertool(_split, 1)

def ksort(k, lines, p=""):
    """ksort(k, lines, p="")
    k: kth element as key
    p="r" -> reversed
    """
    rev_flag = True if "r" in p else False
    return sorted(lines, key=lambda x:x[k], reverse = rev_flag)

def uniq(iterable):
    """uniq(iterable)"""
    ans = set()
    for x in iterable:
        if x not in ans:
            ans.add(x)
    return list(ans)

