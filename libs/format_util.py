
__all__ = []

def confuseMat():
    pass

def kvFormat():
    """ k,v tuple items"""

def _listFormat(iterable, pat="{0}", sep=" "):
    """_listFormat(iterable, pat, sep=" ")"""
    return sep.join( [pat.format(ele) for ele in iterable] )

listFormat = pipe_itertool(_listFormat, 0)

def _format(pat, x):
    """_format(pat, x): 
 Iterable: pat.format(*x) else pat.format(x)
    """
    if isinstance(x, Iterable):
        return pat.format(*x)
    else:
        return pat.format(x)

format = pipe_itertool(_format, 1)

""".2f """
