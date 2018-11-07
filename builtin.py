"""
    builtin operators
"""
import operator, os, config
import types, json

operators = {
    '+': 'ADD',
    '*': 'MUL',
    '**': 'POWER',
    '/': 'DIV',
    '//': 'ZDIV',
    '-': 'MINUS',
    '%': 'MOD',
    '$': 'OSCALL',
    '=': 'ASSIGN',
    ':': 'COLON',
    "<": "LT",
    ">": "GT",
    "<=": "LE",
    ">=": "GE",
    '==':'EQUAL',
    "!=": "NEQ",
    ".": "DOT",
    "is":"IS",
    "in":"IN",
}

operator_val_dict = dict( [ (y,x) for x, y in operators.items() ])

special_op = {
    '::': 'PASSIGN',
    '=': 'ASSIGN',
    ':=': 'GASSIGN',
}

pipe_op = {
    "|": 'PIPE',
    '&>': 'WRITE',
    '&>>': 'APPEND',
    "@" :"COMB",
}

op_order = {
    'WRITE':1,
    'APPEND':1,
    "PIPE": 2,
    'COMB':3,
    "OR": 4,
    "AND": 5,
    "IS": 6, "IN": 6, "NOT_IS":6, "NOT_IN":6,
    "LT": 7, "GT": 7, "LE": 7, "GE": 7, "EQUAL": 7, "NEQ": 7,
    "ADD": 10, "MINUS": 10,
    "MOD": 15,
    "MUL": 20, "DIV": 20, "ZDIV": 20,
    "POWER": 21,
}

# 结合性; 右结合
op_right = {
    "EQUAL": 2,
}

_add = lambda x,y: x + y
_minus = lambda x,y: x - y    
_mul = lambda x,y: x * y    
_div = lambda x,y: x / y    
_mod = lambda x,y: x % y    
_equal = lambda x,y: x == y
_and = lambda x,y: x and y
_or = lambda x,y: x or y 
_not = lambda x: not x
_pipe = lambda x,f: f(x)
_in  = lambda x,y: x in y
_not_in  = lambda x,y: x not in y
_is  = lambda x,y: x is y
_not_is  = lambda x,y: x is not y
_power = lambda x,y: x**y
_zdiv = lambda x, y: x//y


def os_call(sh):
    import subprocess
    out_bytes = subprocess.run(sh, shell=True, stderr=subprocess.STDOUT)
    return out_bytes.stdout

HOME_DIR = os.path.expanduser("~")
CDHIST = [("~", os.getcwd() )]

def cd(path = ".."):
    """cd: int -> hitory cd path in cdh; string -> cd to this path""" 

    def _cd_helper():
        config.cdh.clear()
        config.cdh.extend([  (x[0], i) for i, x in enumerate(CDHIST) ])
        os.chdir(CDHIST[0][1])

    if type(path) == int:
        cd_path = CDHIST.pop(path)
        CDHIST.insert(0, cd_path)
        _cd_helper()
        return

    path = path.strip()
    if path.startswith("~"):
        path = HOME_DIR + path[1:]
    if not os.path.isdir(path):
        print("Error Not_a_dir: %s" % path )
    abspath = os.path.abspath(path)
    CDHIST.insert(0, (path, abspath))
    # LRU
    for i in range(1, len(CDHIST)):
        if CDHIST[i][0] == CDHIST[0][0]:
            CDHIST.pop(i)
            break
    if len(CDHIST) > 20: CDHIST.pop(-1)
    _cd_helper()

def var2str(var):
    if type(var) != str:
        return json.dumps(var, ensure_ascii=False)
    return var

def _write_helper(var, filename, mode):
    with open(filename, mode) as f:
        if isinstance(var, types.GeneratorType):
            for e in var: f.write(var2str(e) + "\n")
        else:
            f.write(var2str(var))
        
def _write(var, filename):
    _write_helper(var, filename, 'w')

def _append(var, filename):
    _write_helper(var, filename, 'a')

def _call(f, arg):
    return f(*arg[0], **arg[1])

def _get_dict(v, k):
    r = [v[ki] if ki in v else None for ki in k]
    if len(r) == 1: return r[0]
    return r

def _get(v, k):
    if type(v) is dict: return _get_dict(v,k)
    if len(k) == 1: 
        return v[k[0]]
    else: 
        r = [v[ki] for ki in k]
        if type(v) == str:
            return "".join(r)
        return r


def _assign(var, val, env):
    env[var] = val
    return val

def _return(v):
    raise v

def _comb(f, comb_arg):
    def _comb_warper(*args, **keyargs):
        new_arg = (comb_arg,) + args
        return f( *new_arg, **keyargs )
    return _comb_warper

Binary = {
    'PIPE':   _pipe,
    'WRITE':  _write,
    'APPEND': _append,
    'ADD':    _add,
    'MUL':    _mul,
    'POWER':  _power,
    'DIV':    _div,
    'ZDIV':   _zdiv,
    'MINUS':  _minus,
    'MOD':    _mod,
    'EQUAL':  _equal,
    'ASSIGN': _assign,
    'AND':    _and,
    'OR':     _or,
    "IS":     _is,
    "NOT_IS": _not_is,
    "IN":     _in,
    "NOT_IN": _not_in,
    "GT":     operator.gt,
    "GE":     operator.ge,
    "LT":     operator.lt,
    "LE":     operator.le,
    "NEQ":    operator.ne,
    "EQUAL":  operator.eq,
    "COMB" :  _comb,
}


Unary = {
    'OSCALL': None,
    'ADD': lambda x:x,
    'MINUS': lambda x:-x,
    'NOT': _not,
    "CALL": _call,
    "GET" : _get,
    "RETURN": _return,
}
