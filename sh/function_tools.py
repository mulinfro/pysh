
from functools import reduce
from types import GeneratorType
from sh.utils import pipe_itertool, unlazyed

_pipe_func = ["wrapList", 'take', 'takeWhile', 'drop', 'dropWhile', 
            'map', 'filter', 'filter_not', 'flat', 'flatMap', 'chunks', 
            'zip2','zip3', 'zipWithIndex', 'FM', 'MF', 'mmap', 'dmap', 'colMap', 'splitList']

_pipe_func_ori = list(map(lambda x: "_" + x, _pipe_func))

__all__ = [ 'pbar', 'groupBy', 'mapValues', 'groupMap', 'unzip', 'foreach',
            '_while', 'join', 'joinMap', 'count', 'countBy', 'foldl', 'repeat',
            'slf', '_if', "sequence", "swapListEle"] + _pipe_func + _pipe_func_ori

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

def swapListEle(list_obj, i=0, j=1):
    """ swapListEle(list_obj, i=0, j=1) """
    list_obj = list(list_obj)
    tmp = list_obj[i]
    list_obj[i] = list_obj[j]
    list_obj[j] = tmp


def sequence(funcs, ele):
    """ sequence(funcs, ele)"""
    return [ func(ele) for func in funcs ] 

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
    ans = []
    for x in lst:
        if cond(x):
            yield ans
            ans = []
        else:
            ans.append(x)
    if ans:
        yield ans

_splitList = unlazyed(splitList)

def _map(func, iterable):
    """ Not lazyed: map"""
    return [ func(x) for x in iterable ]

def repeat(func, n):
    i = 0
    while n < 0 or i < n:
        yield func()
        i += 1

def _wrapList(item):
    if type(item) != list:
        return [item]
    return item

wrapList = pipe_itertool(_wrapList, 0)

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

_chunks = unlazyed(chunks)


def zip2(l1, l2):
    """ Lazyed: zip two iterables, python zip return zip object, while zip2 return a generator """
    for x in zip(l1, l2):
        yield x
_zip2 = unlazyed(zip2)

def zip3(l1, l2, l3):
    """zip3(l1, l2, l3)\nLazyed: zip three iterables, python zip return zip object, while zip3 return a generator """
    for x in zip(l1, l2, l3):
        yield x
_zip3 = unlazyed(zip3)

def zipWithIndex(iterable, start=0):
    """ zipWithIndex(iterable, start=0)
    Lazyed: zip iterable with indexes: "abc" => [(0, "a"), (1, "b"), (2, "c")] """
    i = start
    for x in iterable:
        yield (x, i)
        i = i + 1

_zipWithIndex = unlazyed(zipWithIndex)

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

_take = unlazyed(take)

def takeWhile(key, iterable):
    """takeWhile(key, iterable)
       Lazyed: iterable take while condition is statisfied """
    for x in iterable:
        if not key(x): break
        yield x

_takeWhile = unlazyed(takeWhile)

def drop(n, iterable):
    """drop(n, iterable)
    iterable drop first n elements """
    i = 0
    for x in iterable:
        if i >= n: yield x
        i+=1

_drop = unlazyed(drop)

def dropWhile(key, iterable):
    """dropWhile(key, iterable)"""
    need_drop = True
    for x in iterable:
        if need_drop and key(x): continue
        else: need_drop = False
        yield x

_dropWhile = unlazyed(dropWhile)
            
def map(func, iterable):
    """Lazyed: map"""
    for ele in iterable:
        yield func(ele)

def mmap(func, iterable):
    """Lazyed: map with map"""
    for ele in iterable:
        yield [func(e) for e in ele]
_mmap = unlazyed(mmap)

def dmap(func1, func2, iterable):
    """dmap(func1, func2, iterable)
    Lazyed: """
    for ele in iterable:
        yield (func1(ele), func2(ele))
_dmap = unlazyed(dmap)

def colMap(k, func, iterable):
    """Lazyed: colMap(cols, func, iterable)"""
    for ele in iterable:
        ele = list(ele)
        if type(k) in [list, tuple]:
            for ki in k: ele[ki] = func(ele[ki])
        else:
            ele[k] = func(ele[k])
        yield ele
_colMap = unlazyed(colMap)

def filter(func, iterable):
    """filter(func, iterable)"""
    for ele in iterable:
        if func(ele):
            yield ele
_filter = unlazyed(filter)

def filter_not(func, iterable):
    """filter(func, iterable)"""
    for ele in iterable:
        if not func(ele):
            yield ele

_filter_not = unlazyed(filter_not)

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

_MF = unlazyed(MF)

def FM(mfunc, ffunc, iterable):
    """FM(mfunc, ffunc, iterable)
    FM = filter | map
     paras: 1.iterable,  2. map_key_func,  3.filter_key_func
    """
    for ele in iterable:
        if ffunc(ele):
            yield mfunc(ele)

_FM = unlazyed(FM)

def mapValues(key, dict_obj):
    """mapValues(key, dict_obj)"""
    for k,v in dict_obj.items():
        dict_obj[k] = key(v)
    return dict_obj

def flat(listOfLists):
    """flat(listOfLists)"""
    for lst in listOfLists:
        for x in lst:
            yield x

_flat = unlazyed(flat)

def flatMap(func, listOfLists):
    """ flatMap(func, listOfLists)"""
    for lst in listOfLists:
        for x in lst:
            yield func(x)

_flatMap = unlazyed(flatMap)


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

def joinMap(key_func, value_func, lst1, lst2):
    """join(key_func, value_func, iter1, iter2)
      return a dict with {key_func(ele): (value_func(ele1), value_func(ele2))}
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
            ans[key] = (l1key, value_func(ele))
        else:
            ans[key] = (None, value_func(ele))

    return ans
