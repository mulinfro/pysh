
__all__ = []


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

""".2f """

def kvFormat(item, sep="\t", vpat="{0}", p=""):
    """ k,v tuple items """
    k_str = pat.format(item[0])
    if "l" in p:
    [vpat.format(ele) for ele in item[1]]
    v_str = 
    return 

def confuseMat():
    pass
