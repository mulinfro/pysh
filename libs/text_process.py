import re, random
from types import GeneratorType
from libs.os_cmd import isDir, replace_if_star_dir
from collections.abc import Iterable
import json, collections

_pipe_func = ['grep', 'egrep', 'colSel', 'colRm', 'listFormat', 'format', 
            'extract', 'replace', 'tojson', 'dumps', 'strip', 
            'split', 'rSel', "uniqBy","uniqKvBy", "toUtf8", "jStr" ]
_other_func = ['sample', 'shuf', 'gen', 'wc', 'cat', 'more', 'readPair', 'readStringPair',
            'findall', 'search', 'uniq', 'ksort', 'sort', 'json_equal', 'replaceWithList']

__all__ = _pipe_func + _other_func

def jStr(m):
    return json.dumps(m, ensure_ascii =False, indent=2)

def json_equal(ja, jb):
    return json.dumps(ja, sort_keys=True) == json.dumps(jb, sort_keys=True)

def replaceWithList(pats, iterable, cnt=-1):
    ans = [ pats.get(i, i) for i in iterable ]
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
    """Lazyed: sample(sample_rate, iterable)"""
    for x in iterable:
        if random.uniform(0,1) < sample_rate:
            yield x

def shuf(iterable):
    """shuf(iterable)\ninplace shuf, return self """
    random.shuffle(iterable)
    return iterable


def grep(pat, line):
    """_grep(pat, line)\npat in line?  """
    if pat in line:
        return line

def toUtf8(s, encoding="gbk"):
    """_toUtf8(s, encoding="gbk"): s to utf8"""
    return s.decode(encoding).encode("utf-8")

def egrep(pat, line, p="i"):
    """_egrep(pat, line, p="i")"""
    if "i" in p: pattern = re.compile(pat, re.I)
    else:        pattern = re.compile(pat)
    match = pattern.search(line)
    if match:
        return line

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
    """ for e in iterable: yield e """
    for e in iterable:
        yield e

def colSel(idxes, iterable):
    """_colSel(idxes, iterable)"""
    if type(idxes) not in (list, tuple):
        return iterable[idxes]
    return [iterable[idx] for idx in idxes]

def colRm(idxes, iterable):
    if type(idxes) not in (list, tuple):
        idxes = [idxes]
    return [ iterable[i] for i in range(len(iterable)) if i not in idxes]

def listFormat(iterable, pat="{0}", sep="\t"):
    """_listFormat(iterable, pat, sep=" ")"""
    return sep.join( [pat.format(ele) for ele in iterable] )

"""
if isinstance(x, Iterable):
    return pat.format(*x)
else:
    return pat.format(x)
"""

def format(pat, x):
    """_format(pat, x): 
   Iterable: pat.format(*x) else pat.format(x)
    """
    return pat.format(x)

def wc(iterable):
    """ wc(iterable)\niterable count """
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

def cat(iterable, p="utf-8"):
    """ shell: cat
        input: a single path or a list of pathes
    """
    if type(iterable) == str: iterable = [iterable]
    for path in iterable:
        pathes = replace_if_star_dir(path)
        for file_name in pathes:
            if isDir(file_name): continue
            f = open(file_name, "r", encoding=p)
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
    """_strip(string, p=" \t\n\r")"""
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
    """ksort(k, lst, key, p="")
    key(ele[k]): kth element as key
    p="r" -> reversed
    """
    rev_flag = True if "r" in p else False
    lst.sort(key=lambda x:key(x[k]), reverse = rev_flag)
    return lst

def sort(lst, key=lambda x:x, p=""):
    """sort(lst, key, p="")
    key(ele): element as key
    p="r" -> reversed
    """
    rev_flag = True if "r" in p else False
    lst.sort(key=key, reverse = rev_flag)
    return lst

def uniq(iterable):
    """uniq(iterable) = list(set(iterable))"""
    return list(set(iterable))

def uniqBy(iterable, key=lambda x:x):
    """uniqBy(iterable, key=func)"""
    dic = collections.OrderedDict()
    for x in iterable:
        key_v = key(x)
        if key_v not in ans:
            dic[key_v] = x
    return dic.values()

def uniqKvBy(iterable, key=lambda x:x):
    return list(uniqBy(iterable, key))
