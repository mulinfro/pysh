
from functools import reduce
from types import GeneratorType
from collections import Iterable

_pipe_func = ["wrapList", 'take', 'takeWhile', 'drop', 'dropWhile', 
            'map', 'filter', 'filterNot', 'flat', 'flatMap', 'flatOnlyList', 'chunks', 
            'zip2','zip3', 'zipWithIndex', 'FM', 'MF', 'mmap', 'dmap', 'colMap', 'splitList']

__all__ = [ 'pbar', 'groupBy', 'mapValues', 'groupMap', 'unzip', 'sliding', 'foreach', 'items', 'mean', 'tail', 'tailN', 'head',
            '_while', 'join', 'joinMap', 'joinDict', 'join3Map', 'count', 'countBy', 'foldl', 'repeat', 'matrix',
            'slf', '_if', "seqDo","sequence", "swapListEle", "fany", "fall", "diff", "comm"] + _pipe_func

def diff(a, b):
    ans = []
    sb = set(b)
    for e in a:
        if e not in sb:
            ans.append(e)

    return ans

def comm(a, b):
    ans = []
    sb = set(b)
    for e in a:
        if e in sb:
            ans.append(e)
    return ans

def matrix(m,n, init=0):
    return [[init for j in range(m)] for i in range(n)]

def tail(lst):
    return lst[1:]

def tailN(n, lst):
    if n <= 0 or n>len(lst): n=0
    else: n = -n
    return list(lst)[n:]

def head(lst):
    return lst[0]

def mean(iterable):
    ss, i = 0, 0
    for e in iterable:
        i += 1
        ss += e
    return ss / i

def fany(func, iterable):
    """fany(func, iterable)"""
    for x in iterable:
        if func(x): return True
    return False

def fall(func, iterable):
    """fall(func, iterable)"""
    for x in iterable:
        if not func(x): return False
    return True

def slf(x):
    """ slf: return self"""
    return x

def count(iterable):
    """count(iterable)"""
    ans = {}
    for x in iterable:
        ans[x] = ans.get(x, 0) + 1
    return ans

def countBy(key, iterable):
    """countBy(key, iterable)"""
    ans = {}
    for x in iterable:
        kx = key(x)
        ans[kx] = ans.get(kx, 0) + 1
    return ans

def items(dct):
    """ return items list of a dict """
    return list(dct.items())

def swapListEle(list_obj, i=0, j=1):
    """ swapListEle(list_obj, i=0, j=1) """
    list_obj = list(list_obj)
    tmp = list_obj[i]
    list_obj[i] = list_obj[j]
    list_obj[j] = tmp

def sequence(funcs, ele):
    """ sequence(funcs, ele)"""
    return [ func(ele) for func in funcs ] 

def seqDo(funcs, ele):
    """ seqDo(funcs, ele)"""
    ele = None
    for func in funcs:
        ele = func(ele)
    return ele

def foreach(func, iterable):
    """foreach(func, iterable)"""
    for x in iterable:
        func(x)

def _while(cond, func):
    """_while(cond, func)"""
    while cond:
        func()

def pbar(n=5000, callback=None):
    """ each N step: display progress in pipe and call callback func """
    def _pbar(iterable):
        i = 0
        for x in iterable:
            i = i + 1
            if i % n == 0:
                print("Done: %d items"%i)
                if callback: callback()
            yield x
        print("Done All: %d items"%i)
        if callback: callback()
    return _pbar
   
def _if(cond, true_v, false_v):
    """_if(cond, true_v, false_v)"""
    if cond:
        return true_v
    else:
        return false_v

def splitList(cond, lst):
    """splitList(cond, lst)"""
    ans = []
    for x in lst:
        if cond(x):
            yield ans
            ans = []
        else:
            ans.append(x)
    if ans:
        yield ans

def repeat(func, n):
    i = 0
    while n < 0 or i < n:
        yield func()
        i += 1

def wrapList(item):
    if type(item) != list:
        return [item]
    return item

def chunks(n, iterable):
    """Lazyed: chunks(n, iterable)
    Yield successive n-sized chunks from l."""
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


def zip2(l1, l2):
    """ Lazyed: zip two iterables, python zip return zip object, while zip2 return a generator """
    for x in zip(l1, l2):
        yield x

def zip3(l1, l2, l3):
    """zip3(l1, l2, l3)\nLazyed: zip three iterables, python zip return zip object, while zip3 return a generator """
    for x in zip(l1, l2, l3):
        yield x

def zipWithIndex(iterable, start=0):
    """ zipWithIndex(iterable, start=0)
    Lazyed: zip iterable with indexes: "abc" => [(0, "a"), (1, "b"), (2, "c")] """
    i = start
    for x in iterable:
        yield (x, i)
        i = i + 1


def sliding(sz, iterable):
    """sliding iterable to list of fixed size tuple """
    if sz <= 0: sz = 1
    ans = []
    i = 0
    for ele in iterable:
        ans.append(ele)
        i = i + 1
        if i % sz == 0:
            yield ans
            ans = []

    if len(ans):
        yield ans


def unzip(iterable):
    """unzip(iterable) """
    return list(zip(*iterable))

def groupBy(key, iterable):
    """ iterable groupBy key function
        key: a function; for each element generate group identity
    """
    res = {}
    for x in iterable:
        k = key(x)
        if k not in res: res[k] = []
        res[k].append(x)
    return res

def groupMap(key_func, value_func, iterable):
    """groupMap(key_func, value_func, iterable):
    iterable groupBy key function
    key_func: a function; for each element generate group identity
    """
    res = {}
    for x in iterable:
        k = key_func(x)
        if k not in res: res[k] = []
        res[k].append(value_func(x))
    return res

def take(n, iterable):
    """take(n, iterable)
    lazyed: iterable take first n elements """
    i = 0
    for x in iterable:
        if i >= n: break
        i+=1
        yield x

def takeWhile(key, iterable):
    """takeWhile(key, iterable)
       Lazyed: iterable take while condition is statisfied """
    for x in iterable:
        if not key(x): break
        yield x

def drop(n, iterable):
    """drop(n, iterable)
    iterable drop first n elements """
    i = 0
    for x in iterable:
        if i >= n: yield x
        i+=1

def dropWhile(key, iterable):
    """dropWhile(key, iterable)"""
    need_drop = True
    for x in iterable:
        if need_drop and key(x): continue
        else: need_drop = False
        yield x

def map(func, iterable):
    """Lazyed: map"""
    for ele in iterable:
        yield func(ele)

def mmap(func, iterable):
    """Lazyed: map with map"""
    for ele in iterable:
        yield [func(e) for e in ele]

def dmap(func1, func2, iterable):
    """dmap(func1, func2, iterable)
    Lazyed: """
    for ele in iterable:
        yield (func1(ele), func2(ele))

def colMap(k, func, iterable):
    """Lazyed: colMap(cols, func, iterable)"""
    for ele in iterable:
        ele = list(ele)
        if type(k) in [list, tuple]:
            for ki in k: ele[ki] = func(ele[ki])
        else:
            ele[k] = func(ele[k])
        yield ele

def filter(func, iterable):
    """filter(func, iterable)"""
    for ele in iterable:
        if func(ele):
            yield ele

def filterNot(func, iterable):
    """filter(func, iterable)"""
    for ele in iterable:
        if not func(ele):
            yield ele


def foldl(func, iterable, init=None):
    """ foldl(func, iterable, init=None)
    fold left: python reduce """
    if init is None:
        return reduce(func, iterable)
    else:
        return reduce(func, iterable, init)

def MF(mfunc, ffunc, iterable):
    """MF(mfunc, ffunc, iterable)
    MF = map | filter
         paras: 1.iterable,  2. map_key_func,  3.filter_key_func
    """
    for ele in iterable:
        v = mfunc(ele)
        if ffunc(v):
            yield v


def FM(mfunc, ffunc, iterable):
    """FM(mfunc, ffunc, iterable)
    FM = filter | map
     paras: 1.iterable,  2. map_key_func,  3.filter_key_func
    """
    for ele in iterable:
        if ffunc(ele):
            yield mfunc(ele)


def mapValues(key, dict_obj):
    """mapValues(key, dict_obj)"""
    for k,v in dict_obj.items():
        dict_obj[k] = key(v)
    return dict_obj


def flatOnlyList(listOfLists):
    """flatOnlyList(listOfLists)"""
    for lst in listOfLists:
        if isinstance(lst, list):
            for x in lst:
                yield x
        else:
            yield lst

def flat(listOfLists):
    """flat(iterableOfiterable)"""
    for lst in listOfLists:
        if isinstance(lst,Iterable):
            for x in lst:
                yield x
        else:
            yield lst


def flatMap(func, listOfLists):
    """ flatMap(func, listOfLists)"""
    for lst in listOfLists:
        for x in lst:
            yield func(x)

def join(key_func, lst1, lst2):
    """join(key_func, iter1, iter2)
      return a dict with {key_func(ele): (ele1, ele2)}
      None if one key is not in a lst
       """
    ans = {}
    for ele in lst1:
        key = key_func(ele)
        ans[key] = (ele, None)
    for ele in lst2:
        key = key_func(ele)
        if key in ans:
            l1key = ans[key][0]
            ans[key] = (l1key, ele)
        else:
            ans[key] = (None, ele)

    return ans


def joinDict(dict1, dict2):
    ans = {}
    for k,v in dict1.items():
        ans[k] = (v, None)
    for k,v in dict2.items():
        l1v = ans[key][0] if key in ans else None
        ans[k] = (l1v, v)
    return ans

def joinMap(key_func, value_func, lst1, lst2):
    """join(key_func, value_func, iter1, iter2)
      return a dict with {key_func(ele): (value_func(ele1), value_func(ele2))}
      None if one key is not in a lst
       """
    ans = {}
    for ele in lst1:
        key = key_func(ele)
        ans[key] = (value_func(ele), None)
    for ele in lst2:
        key = key_func(ele)
        l1key = ans[key][0] if key in ans else None
        ans[key] = (l1key, value_func(ele))

    return ans

def join3Map(key_func, value_func, lst1, lst2, lst3):
    """join(key_func, value_func, iter1, iter2)
      return a dict with {key_func(ele): (value_func(ele1), value_func(ele2))}
      None if one key is not in a lst
       """
    ans = {}
    for ele in lst1:
        key = key_func(ele)
        ans[key] = (value_func(ele), None, None)
    for ele in lst2:
        key = key_func(ele)
        l1key = ans[key][0] if key in ans else None
        ans[key] = (l1key, value_func(ele), None)
    for ele in lst3:
        key = key_func(ele)
        l1key = ans[key] if key in ans else (None, None)
        ans[key] = (l1key[0], l1key[1], value_func(ele))

    return ans
