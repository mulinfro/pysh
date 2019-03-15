
__all__ = []


def _listFormat(iterable, pat="{0}", sep="\t"):
    """_listFormat(iterable, pat, sep=" ")"""
    return sep.join( [pat.format(ele) for ele in iterable] )

listFormat = pipe_itertool(_listFormat, 0)

"""
if isinstance(x, Iterable):
    return pat.format(*x)
else:
    return pat.format(x)
"""

def _format(pat, x):
    """_format(pat, x): 
 Iterable: pat.format(*x) else pat.format(x)
    """
    return pat.format(x)

format = pipe_itertool(_format, 1)

""".2f """

def _kvFormat(item, sep="\t", vpat="{0}", p=""):
    """ k,v tuple items """
    k_str = pat.format(item[0])
    if "l" in p:
    [vpat.format(ele) for ele in item[1]]
    v_str = 
    return 

def confuseMat():
    pass
