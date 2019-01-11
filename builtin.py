"""
    builtin operators
"""
import operator
import json
from collections import Iterable

operators = {
    '+': 'ADD',
    '*': 'MUL',
    '**': 'POWER',
    '/': 'DIV',
    '//': 'ZDIV',
    '-': 'MINUS',
    '%': 'MOD',
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
    "or":"OR",
    "and":"AND",
    "not":"NOT",
}

special_op = {
    '::': 'PASSIGN',
    '=': 'ASSIGN',
    ':=': 'GASSIGN',
    "=>": "INFER",
    "<<": "INFER_ASSIGN",
}

pipe_op = {
    "|": 'PIPE',
    "$": 'LEFT_PIPE',
    "->": 'PIPE_ASSIGN',
    '&>': 'WRITE',
    '$>': 'BIN_WRITE',
    '&>>': 'APPEND',
    "@" :"COMB",
}

operator_val_dict = dict( [ (y,x) for x, y in operators.items() ] +
                        [ (y,x) for x, y in special_op.items() ] +
                        [ (y,x) for x, y in pipe_op.items() ])

op_order = {
    'WRITE':1, 'APPEND':1,'BIN_WRITE':1,
    "PIPE": 2, 'PIPE_ASSIGN': 2,
    "LEFT_PIPE": 3,
    'COMB':5,
    "OR": 6,
    "AND": 7,
    "IS": 8, "IN": 8, "NOT_IS":8, "NOT_IN":8,
    "LT": 9, "GT": 9, "LE": 9, "GE": 9, "EQUAL": 9, "NEQ": 9,
    "ADD": 10, "MINUS": 10,
    "MOD": 15,
    "MUL": 20, "DIV": 20, "ZDIV": 20,
    "POWER": 21,
}

# 结合性; 右结合
op_right = {
    "EQUAL": 2,
    "LEFT_PIPE":3,
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
_left_pipe = lambda f,x: f(x)
_in  = lambda x,y: x in y
_not_in  = lambda x,y: x not in y
_is  = lambda x,y: x is y
_not_is  = lambda x,y: x is not y
_power = lambda x,y: x**y
_zdiv = lambda x, y: x//y

def _pipe_assign(env):
    def _pipe_assign_env(val, var_name):
        if isinstance(val, Iterable):
            for e in val:
                env[var_name] = e
                yield e
        else:
            env[var_name] = val
            yield val
    return _pipe_assign_env

def var2str(var):
    if type(var) != str:
        return json.dumps(var, ensure_ascii=False)
    return var

def _write_helper(var, filename, mode):
    with open(filename, mode) as f:
        #if isinstance(var, types.GeneratorType):
        if isinstance(var, Iterable) and type(var) != str:
            for e in var: f.write(var2str(e) + "\n")
        else:
            f.write(var2str(var))
        
def _bin_write(var, filename):
    with open(filename, "wb") as f:
        f.write(bytearray(var))
        
def _write(var, filename):
    _write_helper(var, filename, 'w')

def _append(var, filename):
    _write_helper(var, filename, 'a')

def _call(f, arg):
    return f(*arg[0], **arg[1])

def _get(v, k):
    if v is None: return None
    if type(v) is dict: 
        r = [v.get(ki, None) for ki in k]
    else: 
        r = [v[ki] for ki in k]
        if type(v) == str:
            return "".join(r)
    if len(r) == 1: 
        return r[0]
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
    'LEFT_PIPE': _left_pipe,
    'PIPE_ASSIGN': _pipe_assign,
    'WRITE':  _write,
    'BIN_WRITE': _bin_write,
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
    'ADD': lambda x:x,
    'MINUS': lambda x:-x,
    'NOT': _not,
    "CALL": _call,
    "GET" : _get,
    "RETURN": _return,
}
