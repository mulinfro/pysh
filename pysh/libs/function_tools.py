
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
    """
      diff(a:iterable, b: iterable)
          a - b; elements in a but not in b
      
      args:
          a: iterable, b: iterable => eg: [1,2,3], [1]
      return:
          a list of (a - b)        => eg: [2,3]
    """
    ans = []
    sb = set(b)
    for e in a:
        if e not in sb:
            ans.append(e)

    return ans

def comm(a, b):
    """
      comm(a: iterable, b: iterable)
          a ∩ b; elements in a and in b

      args:
          a: iterable, b: iterable => eg: [1,2,3], [1]
      return:
          a list of (a ∩ b)        => eg: [1]
    """
    ans = []
    sb = set(b)
    for e in a:
        if e in sb:
            ans.append(e)
    return ans

def matrix(m,n, init=0):
    """
      matrix(m: int, n: int, init = 0)
          new a matrix with size m * n;

      args:
          m: int, n: int => eg: 3, 3
      kwargs:
          init (default 0): Initial value
      return:
          a list of list => eg: [[0,0,0], [0,0,0], [0,0,0]]
    """
    return [[init for j in range(m)] for i in range(n)]

def tail(lst):
    """
      tail(lst: list)
          1 to len of a list 

      args:
          a list => eg: [1,2,3]
      return:
          a list => [2,3]
    """
    return lst[1:]

def tailN(n, lst):
    """
      tailN(n: int, lst: list)
          last n elements of a list; if n <= 0 or n > len return all elements 

      args:
          n: int; lst: list => eg: 2; [1,2,3,4,5]
      return:
          a list => [4,5]
    """
    if n <= 0 or n>len(lst): n=0
    else: n = -n
    return list(lst)[n:]

def head(lst):
    """
      head(lst: list)
          first element of a list

      args:
          lst: list => eg: [1,2,3,4,5]
      return:
          element   => eg: 1
    """
    return lst[0]

def mean(iterable):
    """
      mean(iter: iterable)
          mean of a list with numbers

      args:
          iterable: list => eg: 0, [1,2,3,4,5]
      return:
          number   => eg: 3
    """
    ss, i = 0, 0
    for e in iterable:
        i += 1
        ss += e
    return ss / i

def fany(func, iterable):
    """
       fany(func: function, iter: iterable)
            return true if any element x make func(x) == True

       args:
            func = x > 0,  iter = [-1,0,1]
       return:
            True
    """
    for x in iterable:
        if func(x): return True
    return False

def fall(func, iterable):
    """
       fall(func: function, iter: iterable)
            return true if all element x make func(x) == True

       args:
            func = x > 0,  iter = [-1,0,1]
       return:
            False
    """
    for x in iterable:
        if not func(x): return False
    return True

def slf(x):
    """
       slf(x)
       slf = lambda x: x
    """
    return x

def count(iterable):
    """
       count(iter: iterable)
       element numbers

       args:
            iter = [0,1,1,2]
       return:
            {0:1, 1:2, 2:1}
    """
    ans = {}
    for x in iterable:
        ans[x] = ans.get(x, 0) + 1
    return ans

def countBy(key, iterable):
    """
       countBy(key: function, iter: iterable)
           count element numbers of transformed by key()

       args:
            key = lambda x: x>0, iter = [0,1,1,2]
       return:
            {False:1, True:3}
            
    """
    ans = {}
    for x in iterable:
        kx = key(x)
        ans[kx] = ans.get(kx, 0) + 1
    return ans

def items(dct):
    """
       items(dct: dict)
           return items of a dict

       args:
            dct = {1:2, "1":"2"}
       return:
            [(1,2), ("1", "2")]
    """
    return list(dct.items())

def swapListEle(list_obj, i=0, j=1):
    """
        swapListEle(lst: list, i=0, j=1)
            swap two elements of lst with i,j position

        args:
            lst = [1,2,3], i=0, j=1
        return:
            [2,1,3]
    """
    list_obj = list(list_obj)
    tmp = list_obj[i]
    list_obj[i] = list_obj[j]
    list_obj[j] = tmp

def sequence(funcs, ele):
    """ 
       sequence(funcs: list[function], ele:any)
            [func(ele) for func in funcs] 
       
       args:
           funcs = [L x: x+1, L x: x+2];  ele = 1
       return:
           [2,3]

    """
    return [ func(ele) for func in funcs ] 

def seqDo(funcs, ele):
    """ 
       seqDo(funcs: list[function], ele:any)
            for func in funcs:
                ele = func(ele)
       
       args:
           funcs = [L x: x+1, L x: x+2];  ele = 1
       return:
           ((1 + 1) + 2) = > 4
    """

    ele = None
    for func in funcs:
        ele = func(ele)
    return ele

def foreach(func, iterable):
    """
       foreach(func: function, iter:iterable)
            foreach x in iterable apply func(x)
            return None

       args:
           func = L x: print(x);  ele = [0,1,2]
       return:
           None
            
    """
    for x in iterable:
        func(x)

def _while(cond, func):
    """
        _while(cond: function, func: function)

        implement:
            while cond:
                func()

    """
    while cond:
        func()

def pbar(n=5000, callback=None):
    """
        pbar(n=5000, callback=None)
            each N step: display progress in pipe and call callback func
            
        example:
            [1:100] | pbar(30, L :print("SS")) | list

        console output:
            Done: 30 items
            SS
            Done: 60 items
            SS
            Done: 90 items
            SS
            Done All: 99 items
            SS
    """
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
    """
        _if(cond, true_v, false_v)
            return true_v if cond else false_v
    """
    if cond:
        return true_v
    else:
        return false_v

def splitList(cond, lst):
    """
        splitList(cond: function, iter: iterable)
            split list with pred function

        args:
             cond = L x: x%3=0;  iter = [1,2,3,4,5,6,7]

        return: Lazyed!! value type is generator
            [1,2]..[4,5], [7]

    """
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
    """
        repeat(func: function, n:int)
            repeat apply no-parameters func n times
            return each step result

        args:
            func = L:"REP", n = 3 
        return: Lazyed!! value type is generator
            REP.. REP.. REP
    """
    i = 0
    while n < 0 or i < n:
        yield func()
        i += 1

def wrapList(item):
    """
        wrapList(item: any)

        implement:
            if type(item) != list:
                return [item]
            return item
    """
    if type(item) != list:
        return [item]
    return item

def chunks(n, iterable):
    """
       chunks(n:int, iter:iterable)
           yield every successive n-sized chunks from l.

       args:
           n = 3, iter = [1,2,3,4,5,6,7]
       return: Lazyed!! return type is generator
           [1,2,3].. [4,5,6] .. [7]
    """
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
    """
        zip4(l1: iterable, l2: iterable)
           zip 2 iterable objs

        args:
            l1 = [1,2], l2 = [2,3]
        return: Lazyed!! return type is generator
            (1,2).. (2,3)

    """
    for x in zip(l1, l2):
        yield x

def zip3(l1, l2, l3):
    """
        zip3(l1: iterable, l2: iterable, l3: iterable)
           zip 3 iterable objs

        args:
            [1,2], [2,3], [3,4,5]
        return: Lazyed!! return type is generator
            (1,2,3).. (2,3,4)

    """
    for x in zip(l1, l2, l3):
        yield x

def zipWithIndex(iterable, start=0):
    """ 
        zipWithIndex(iter:iterable, start=0)
            zip iterable with indexes
       
        args:
            iter = "abc"
        return: Lazyed!! return type is generator
            [(0, "a"), (1, "b"), (2, "c")]
    """
    i = start
    for x in iterable:
        yield (x, i)
        i = i + 1

def sliding(sz, iterable):
    """
        sliding(n: int, iter: iterable)
        yield every successive n-sized chunks from l.

        args:
           n = 3, iter = [1,2,3,4,5,6,7]
        return: Lazyed!! return type is generator
           [1,2,3].. [4,5,6] .. [7]
    """
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
    """
        unzip(iter: iterable)

        example:
            unzip([ [1,2], ["a","b"]])
        return:
            [(1, 'a'), (2, 'b')]
    """
    return list(zip(*iterable))

def groupBy(key, iterable):
    """
        groupBy(key: function, iter: iterable)
            iterable elements grouped by key function

        args:
            key = L x: x%2,   iter = [1,2,3]
        return:
            {0:[2], 1:[1,3]}
    """
    res = {}
    for x in iterable:
        k = key(x)
        if k not in res: res[k] = []
        res[k].append(x)
    return res

def groupMap(key_func, value_func, iterable):
    """
        groupMap(key_func: function, value_func: function, iter: iterable)
            group elements with key_func, transform values with value_func

        args:
            key_func = L x: x%2,  value_func = L x: -x,  iter = [1,2,3]
        return:
            {0:[-2], 1:[-1,-3]}
    """
    res = {}
    for x in iterable:
        k = key_func(x)
        if k not in res: res[k] = []
        res[k].append(value_func(x))
    return res

def take(n, iterable):
    """
        take(n:int, iter: iterable)
            take first n elements of iterable obj

        args:
            n = 5; iter = [1,2,3,4,5,6]
        return: Lazyed!! return type is generator
            1.. 2.. 3.. 4.. 5
    """
    i = 0
    for x in iterable:
        if i >= n: break
        i+=1
        yield x

def takeWhile(key, iterable):
    """
        takeWhile(key: function, iter: iterable)
            Lazyed: iterable take while condition is statisfied 

        args:
            key = L x: x<0, iter = [-2, -1, 0, -1, -2]
        return: Lazyed!! return type is generator
            -2.. -1
    """
    for x in iterable:
        if not key(x): break
        yield x

def drop(n, iterable):
    """
        drop(n:int, iter: iterable)
            drop first n elements of iterable obj

        args:
            n = 3; iter = [1,2,3,4,5,6]
        return: Lazyed!! return type is generator
            4.. 5.. 6
    """
    i = 0
    for x in iterable:
        if i >= n: yield x
        i+=1

def dropWhile(key, iterable):
    """
        dropWhile(key: function, iter: iterable)
            Lazyed: drop while condition is statisfied 

        args:
            key = L x: x<0, iter = [-2, -1, 0, -1, -2]
        return: Lazyed!! return type is generator
            0.. -2.. -1
    """

    need_drop = True
    for x in iterable:
        if need_drop and key(x): continue
        else: need_drop = False
        yield x

def map(func, iterable):
    """
        map(func: function, iter: iterable)
            foreach element of iterable apply func

        args:
            func = L x: x+1;  iter = [1,2,3]
        return: Lazyed!!
            2.. 3.. 4
    """
    for ele in iterable:
        yield func(ele)

def mmap(func, iterable):
    """
        mmap(func: function, iterable: iterable of iterable)

        args:
            func = L x: x+1;  iter = [[1,2], [2,3]]
        return:Lazyed!! return type is generator
            [2,3].. [3,4]
    """
    for ele in iterable:
        yield [func(e) for e in ele]

def dmap(func1, func2, iterable):
    """
        dmap(func1: function, func2: function, iter:iterable)
            apply two map functions in iterable

        args:
            func1 = L x: x+1; func2 = L x: -x; iter = [[1,2], [2,3]]
        return:Lazyed!! return type is generator
            [(2, -1), (3, -2)].. [(3, -2), (4, -3)]
    """
    for ele in iterable:
        yield (func1(ele), func2(ele))

def colMap(k, func, iterable):
    """
        colMap(cols: int of list[int], func: function, iter:iterable)
           apply map function in iterable with selected cols

        args:
            k = 1, func = L x: x*2; iter = [[1,2], [2,3]]
        return:Lazyed!! return type is generator
            [(1,4)].. [(2, 6)]

        args:
            k = [1,2], func = L x: x*2; iter = [[1,2,1], [2,3,2]]
        return:Lazyed!! return type is generator
            [(1, 4, 2)].. [(2, 6, 4)]

    """
    for ele in iterable:
        ele = list(ele)
        if type(k) in [list, tuple]:
            for ki in k: ele[ki] = func(ele[ki])
        else:
            ele[k] = func(ele[k])
        yield ele

def filter(func, iterable):
    """
        filter(func: function, iter:iterable)
            filter "iter" with predicate function "func"

        args:
            func = L x: x>0; iter = [1,-1,0,2,-2]
        return:Lazyed!! return type is generator
            1.. 2
    """
    for ele in iterable:
        if func(ele):
            yield ele

def filterNot(func, iterable):
    """
        filterNot(func: function, iter:iterable)
            filter "iter" with inverted predicate function "func"

        args:
            func = L x: x>0; iter = [1,-1,0,2,-2]
        return:Lazyed!! return type is generator
            -1.. 0.. -2
    """
    for ele in iterable:
        if not func(ele):
            yield ele


def foldl(func, iterable, init=None):
    """
        foldl(func: function, iter: iterable, init=None)
        fold left with init, same with python reduce
    """
    if init is None:
        return reduce(func, iterable)
    else:
        return reduce(func, iterable, init)

def MF(mfunc, ffunc, iterable):
    """
        MF(mfunc: function, ffunc: function, iter: iterable)
            MF = map | filter
            first apply map, then apply filter

        args:
            mfunc = L x: x + 2; ffunc = L x: x >= 2;  iter = [-1, 0, 1]
        return:Lazyed!! return type is generator
            2.. 3
    """
    for ele in iterable:
        v = mfunc(ele)
        if ffunc(v):
            yield v


def FM(mfunc, ffunc, iterable):
    """
        FM(mfunc: function, ffunc: function, iter: iterable)
            MF = filter | map
            first apply filter, then apply map

        args:
            mfunc = L x: x + 2; ffunc = L x: x >= 2;  iter = [-1, 0, 1]
        return:Lazyed!! return type is generator
            empty
    """
    for ele in iterable:
        if ffunc(ele):
            yield mfunc(ele)


def mapValues(key, dict_obj):
    """
        mapValues(func: function, obj: dict)
            transformed dict values with "func"

        args:
            func = L x: -x; obj = {"a":0, "b":1}
        retun:
            transformed dict
            {"a": 0, "b": -1}
    """
    for k,v in dict_obj.items():
        dict_obj[k] = key(v)
    return dict_obj


def flatOnlyList(listOfLists):
    """
        flatOnlyList(lst)
            only flatten the List type element of iterable

        args:
            lst = [[1,2], 0, [2,3], "abc", (1, 2)]
        return:Lazyed!! return type is generator
            1.. 2.. 0.. 2.. 3.. "abc", (1, 2)
    """
    for lst in listOfLists:
        if isinstance(lst, list):
            for x in lst:
                yield x
        else:
            yield lst

def flat(listOfLists):
    """
        flat(iterOfiter: iterable of iterable)
            flatten a iterable of iterable to iterable

        args:
            iterOfiter = [[1,2], [2,3]]
        return:Lazyed!! return type is generator
            1.. 2.. 2.. 3
    """
    for lst in listOfLists:
        if isinstance(lst,Iterable):
            for x in lst:
                yield x
        else:
            yield lst

def flatMap(func, listOfLists):
    """
        flatMap(func: function,  iterOfiter: iterable of iterable)
            flatten a iterable of iterable to iterable then apply "func"

        args:
            func = L x: x + 1;  iterOfiter = [[1,2], [2,3]]
        return:Lazyed!! return type is generator
            2.. 3.. 3.. 4
    """
    for lst in listOfLists:
        for x in lst:
            yield func(x)

def join(key_func, lst1, lst2):
    """
      join(key_func: function, iter1: iterable, iter2: iterable)
          jion two iterable, return a dict

      args:
          key_func = L x: -x;  iter1 = [1,2,3];  iter2 = [2,3,4]
      return a dict with {key_func(ele): (ele, ele)}
          不存在的用None代替
          {-1: (1, None), -2: (2, 2), -3: (3, 3), -4: (None, 4)}
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
    """
      joinDict(dict1: dict, dict2: dict)
          jion two dict, return a new dict

      args:
          dict1 = {1:1, 2:2};  dict2 = {2:2, 3:3}
      return a dict 不存在的用None代替
          {1: (1, None), 2: (2, 2), 3: (None, 3)}
    """
    ans = {}
    for k,v in dict1.items():
        ans[k] = (v, None)
    for k,v in dict2.items():
        l1v = ans[k][0] if k in ans else None
        ans[k] = (l1v, v)
    return ans

def joinMap(key_func, value_func, lst1, lst2):
    """
      joinMap(key_func: function, value_func: function, iter1: iterable, iter2: iterable)
          return a dict with {key_func(ele): (value_func(ele), value_func(ele))}
                  None if one key is not in a lst

      args:
          joinMap(L x: -x, L x: x*2, [1,2,3], [2,3,4])
      returns:
          {-1: (2, None), -2: (4, 4), -3: (6, 6), -4: (None, 8)}
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
    """
      join3Map(key_func: function, value_func: function, iter1: iterable, iter2: iterable, iter3: iterable)
          return a dict with {key_func(ele): (value_func(ele), value_func(ele), value_func(ele))}
                  None if one key is not in a lst

      args:
          join3Map(L x: -x, L x: x*2, [1,2,3], [2,3,4], [3,4,5])
      returns:
          {-1: (2, None, None), -2: (4, 4, None), -3: (6, 6, 6), -4: (None, 8, 8), -5: (None, None, 10)}
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
