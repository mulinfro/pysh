import re
from types import GeneratorType
from itertools import chain
from functools import reduce
from sh.os_cmd import is_dir, replace_if_star_dir
from collections.abc import Iterable

__all__ = [ 'grep', 'gen', 'colSel', 'format', 'pbar',
            'wc', 'egrep', 'extract', 'replace', 'cat', 'tojson', 'dumps', 'more', 
            'groupBy', 'take', 'takeWhile', 'drop', 'xreduce', 'head', 'join', 
            'map', 'filter', 'mapValues', 'flat', 'flatMap', 'awk', 'sed', 'split', 
            'findall', 'search', 'xsort', 'uniq', 'chunks', 'zip2','zip3', 'zipWithIndex', 
            'sample', 'shuf', 'FM', 'MF', 'foldl']


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


def pbar(n=5000):
    """ each N step: display progress in pipe """
    def _pbar(iterable):
        i = 0
        for x in iterable:
            i = i + 1
            if i % n == 0:
                print("Done: %d items"%i)
            yield x
        print("Done All: %d items"%i)
    return _pbar
    

def chunks(iterable, n=2):
    """Yield successive n-sized chunks from l."""
    if not isinstance(iterable, GeneratorType):
        for i in range(0, len(iterable), n):
            yield iterable[i:i + n]
    else:
        i = 0
        ans = list()
        for x in iterable:
            ans.append(x)
            i = i + 1
            if i%n == 0:
                yield ans
                ans = list()
        if len(ans) > 0: yield ans

def sample(iterable, sample_rate):
    import random
    for x in iterable:
        if random.uniform(0,1) < sample_rate:
            yield x

def shuf(iterable):
    import random
    random.shuffle(iterable)
    return iterable

def zip2(l1, l2):
    """ zip two iterables, python zip return zip object, while zip2 return a generator """
    for x in zip(l1, l2):
        yield x

def zip3(l1, l2, l3):
    """ zip three iterables, python zip return zip object, while zip3 return a generator """
    for x in zip(l1, l2, l3):
        yield x

def zipWithIndex(iterable, start=0):
    """ zip iterable with indexes: "abc" => [(0, "a"), (1, "b"), (2, "c")] """
    i = start
    for x in iterable:
        yield (x, i)
        i = i + 1

@pipe_text_itertool
def grep(line, pat, p=""):
    if pat in line: 
        return line

@pipe_text_itertool
def egrep(line, pat, p="i"):
    if "i" in p: pattern = re.compile(pat, re.I)
    else:        pattern = re.compile(pat)
    match = pattern.search(line)
    if match:
        return line

def gen(iterable):
    for e in iterable:
        yield e

@pipe_gen_itertool
def colSel(iterable, idxes):
    if type(idxes) not in (list, tuple):
        return iterable[idxes]
    return [iterable[idx] for idx in idxes]

@pipe_gen_itertool
def list_format(x, pat, sep=" "):
    return sep.join( [pat.format(ele) for ele in x] )

@pipe_gen_itertool
def format(x, pat):
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
def extract(line, pat):
    match = re.search(pat, line)
    if match:
        return match.groups()

@pipe_text_itertool
def replace(line, pat, repl, cnt=-1, p=""):
    """string replace
       parms: line, pattern, replace_str, cnt=inf
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
    import json
    return json.loads(line.strip())

@pipe_gen_itertool
def dumps(var):
    """python json dumps"""
    import json
    return json.dumps(var)

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

def groupBy(iterable, key = lambda x:x[0]):
    """ iterable groupBy key function
        key: a function; for each element generate group identity
        default key = lambda x:x[0]
    """
    res = {}
    for x in iterable:
        k = key(x)
        if k not in res: res[k] = []
        res[k].append(x)
    return res

def take(iterable, n):
    """ iterable take first n elements """
    i = 0
    for x in iterable:
        if i >= n: break
        i+=1
        yield x

def takeWhile(iterable, key):
    """ iterable take while condition is statisfied """
    for x in iterable:
        if not key(x): break
        yield x

def drop(iterable, n):
    """ iterable drop first n elements """
    i = 0
    for x in iterable:
        if i >= n: yield x
        i+=1
            
def head(iterable, n=10):
    """ shell: head """
    i = 0
    for line in iterable:
        i += 1
        if i > n: break
        yield line

def join():
    pass

def map(iterable, func):
    for ele in iterable:
        yield func(ele)

def filter(iterable, func):
    for ele in iterable:
        if func(ele):
            yield ele

def foldl(iterable, func, init=None):
    if init is None:
        return reduce(func, iterable)
    else:
        return reduce(func, iterable, init)

def MF(iterable, mfunc, ffunc):
    for ele in iterable:
        v = mfunc(ele)
        if ffunc(v):
            yield v

def FM(iterable, mfunc, ffunc):
    for ele in iterable:
        if ffunc(ele):
            yield mfunc(ele)

def mapValues(dict_obj, key):
    res = {}
    for k,v in dict_obj.items():
        res[k] = key(v)
    return res

def flat(listOfLists):
    return chain.from_iterable(listOfLists)

def flatMap(f, items):
    return chain.from_iterable(map(items, f))

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

