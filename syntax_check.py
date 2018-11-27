# syntax check help functions

class Eval_exception(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

'''
def Error(msg, tkn=None):
    import sys
    if tkn:
        print(tkn)
        print("Syntax Error: In line %d Col %d %s" % (tkn.line,tkn.col, msg), file=sys.stderr)
    raise Exception(msg)
'''

def Error(msg, line=None, col=None):
    prefix = "" 
    if line and col: prefix = "In line %d col %d"%(line, col)
    raise Eval_exception(prefix + ": " + msg)
    
def syntax_check(tkn, need_tkn, not_ = False):
    if type(need_tkn) is tuple: flag = (tkn.tp, tkn.val) == need_tkn 
    else:      flag = tkn.tp == need_tkn 
    return not flag if not_ else flag

def syntax_assert(tkn, need_tkn,  errstr = "", not_ = False):
    if not syntax_check(tkn, need_tkn, not_):
        Error(tkn.val + ": " + errstr, tkn.line, tkn.col)
    return True

def syntax_cond_assert(cond,  errstr = "", not_ = False):
    if not cond: Error(errstr)
    return True
