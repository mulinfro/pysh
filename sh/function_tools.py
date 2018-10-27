
from itertools import chain
from functools import reduce
from types import GeneratorType
__all__ = [ 'pbar', 'groupBy', 'take', 'takeWhile', 'drop', 'dropWhile', 'map', 'filter',
            'mapValues', 'flat', 'flatMap', 'chunks', 'zip2','zip3', 'zipWithIndex', 
            'FM', 'MF', 'mmap', 'dmap', 'kmap', 'foldl', 'repeat', 'M', 'slf', '_if']

def slf(x):
    """ slf: return self"""
    return x

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
   
def _if(cond, true_v, false_v):
    if cond:
        return true_v
    else:
        return false_v

def M(func, iterable):
    return [ func(x) for x in iterable ]

def repeat(func, n):
    i = 0
    while n < 0 or i < n:
        yield func()
        i += 1

def chunks(n, iterable):
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

def groupBy(key, iterable):
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

def take(n, iterable):
    """ iterable take first n elements """
    i = 0
    for x in iterable:
        if i >= n: break
        i+=1
        yield x

def takeWhile(key, iterable):
    """ iterable take while condition is statisfied """
    for x in iterable:
        if not key(x): break
        yield x

def drop(n, iterable):
    """ iterable drop first n elements """
    i = 0
    for x in iterable:
        if i >= n: yield x
        i+=1

def dropWhile(key, iterable):
    need_drop = True
    for x in iterable:
        if need_drop and key(x): continue
        else: need_drop = False
        yield x
            
def map(func, iterable):
    for ele in iterable:
        yield func(ele)

def mmap(func, iterable):
    for ele in iterable:
        yield [func(e) for e in ele]

def dmap(func1, func2, iterable):
    for ele in iterable:
        yield (func1(ele), func2(ele))

def kmap(k, func, iterable):
    for ele in iterable:
        ele = list(ele)
        ele[k] = func(ele[k])
        yield ele

def filter(func, iterable):
    for ele in iterable:
        if func(ele):
            yield ele

def foldl(func, iterable, init=None):
    """ fold left: python reduce """
    if init is None:
        return reduce(func, iterable)
    else:
        return reduce(func, iterable, init)

def MF(mfunc, ffunc, iterable):
    """  MF = map | filter
         paras: 1.iterable,  2. map_key_func,  3.filter_key_func
    """
    for ele in iterable:
        v = mfunc(ele)
        if ffunc(v):
            yield v

def FM(mfunc, ffunc, iterable):
    """  FM = filter | map
         paras: 1.iterable,  2. map_key_func,  3.filter_key_func
    """
    for ele in iterable:
        if ffunc(ele):
            yield mfunc(ele)

def mapValues(key, dict_obj):
    for k,v in dict_obj.items():
        dict_obj[k] = key(v)
    return dict_obj

def flat(listOfLists):
    return chain.from_iterable(listOfLists)

def flatMap(f, items):
    return chain.from_iterable(map(items, f))


if __name__ == "__main__":
    pass
