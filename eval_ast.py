from builtin import operators, op_order, Binary, Unary, op_right
import copy,sys
from env import Env
from syntax_check import Error, syntax_cond_assert

PARTIAL_FLAG = lambda : None
PARTIAL_FLAG_LAMBDA = lambda env: PARTIAL_FLAG

# 使用异常来实现控制流跳转
class Return_exception(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Continue_exception(Exception):
    def __init__(self):
        self.value = "continue"
    def __str__(self):
        return repr(self.value)

class Break_exception(Exception):
    def __init__(self):
        self.value = "break"
    def __str__(self):
        return repr(self.value)


def parse(node):
    if  node["type"] == 'DEF': 
        val = parse_def(node)
    elif node["type"] == 'IMPORT': 
        val = parse_import(node)
    else:
        val = parse_block_expr(node)
    return val

def parse_block_expr(node):
    if node["type"] == 'IF':
        val = parse_if(node)
    elif node["type"] == 'WHILE': 
        val = parse_while(node)
    elif node["type"] == "FOR":
        val = parse_for(node)
    elif node["type"] in ["BREAK", "CONTINUE", "RETURN"]:
        val = parse_flow_goto(node)
    else:
        val = parse_expr(node)
    return val

def parse_expr(node):
    if node["type"] in ("ASSIGN", "GASSIGN"):
        val = parse_assign(node)
    elif node["type"] == "PASSIGN":
        val = parse_pattern_assign(node)
    else:
        val = parse_simple_expr(node)
    return val

def parse_simple_expr(node):
    if node["type"] == "SIMPLEIF":
        val = parse_simpleif_expr(node)
    elif node["type"] == "BIEXPR":
        val = parse_binary_expr(node)
    else:
        val = parse_unary(node)
    return val

def parse_flow_goto(node):
    if node["type"] == "RETURN":
        rval = parse_expr(node["rval"])
        val = Return_exception(rval)
    elif node["type"] == "BREAK":
        val = Break_exception()
    else:
        val = Continue_exception()

    def _raise_error(val):
        raise val
    return lambda env: _raise_error(val)

def parse_import(node):

    import sys, os
    def python_import(_from, _import, _as):
        env = {}
        as_name = [ tkn.val for tkn in _as if tkn.tp!="SEP" ] + [None]*len(_import)
        if _from: 
            fromlist = _from.split(".")
            top_module = __import__(_from, fromlist = fromlist)
        for t,g in zip(_import, as_name):
            if t.tp == "SEP": continue
            nm = g if g else t.val
            if _from: env[nm] = top_module.__getattribute__(t.val)
            else:     env[nm] = __import__(_import[0])
        return env
            
    def user_import_py(path, _as):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(_as, path).load_module()

    def user_import_package(path):
        pass

    def user_import_psh(path):
        pass

    def user_package_import(path, file_suffix):
        if file_suffix == ".py":
            return user_import_py(path + file_suffix, _as)
        elif file_suffix == ".psh":
            return user_import_psh(path)
        else:
            onlyfiles = [ f for f in os.listdir(path) ]
            env[_as] = user_import_package(path)

    _from, _import, _as = node["from"], node["import"], node["as"]
    module = {}
    if _from or _import[0].tp != "PARN":
        module = python_import(_from, _import, _as)
    else:
        path = _import[0].val
        if path.endswith(".py"):
            module_context = user_import_py(path)
        if path.endswith(".psh"):
            module_context = user_import_psh(path)
        syntax_cond_assert(len(_as) <= 1, "can only import one module once")
        if len(_as) == 1:
            module_name = _as[0]
        else:
            module_name = os.path.split(path)[1].split(".")[0]
            module = {module_name: module_context}
            
    def update_env(env):
        env.update(module)

    return update_env

def parse_assign(node):
    val = parse_expr(node["val"])
    var = node["var"]["name"]
    def _assign(env):
        v = val(env)
        if node["type"] == "GASSIGN":
            env = env.globals
        env[var] = v
        return v
    return _assign

def lst_combine(var, v):
    syntax_cond_assert(len(var) <= len(v), "syntax error: to many variables")
    pairs = list(zip(var, v))
    tail = (pairs[-1][0], [pairs[-1][1]] + v[len(var)])
    pairs.pop()
    pairs.append(tail)
    return pairs

def parse_pattern_assign(node):
    val = parse_expr(node["val"])
    var = node["var"]["variables"]
    
    def _update(env):
        env.update(lst_combine(var, val(env)))
    return _update
        
def parse_simpleif_expr(node):
    cond = parse_simple_expr(node["cond"])
    then = parse_simple_expr(node["then"])
    else_t = parse_simple_expr(node["else"])
    return lambda env: then(env) if cond(env) else else_t(env)

def parse_bi_oper(node):
    op_info = {"name": node["val"], 
               "order": op_order[node["val"] ],
               "right": node["val"] in op_right,
               "func" : Binary[node["val"]] }
    return op_info


def parse_binary_expr(node):
    g_vals = list(map(parse_unary, node["val"]))
    g_ops  = list(map(parse_bi_oper, node["op"]))

    partial_idx  = -1
    for i in range(len(g_vals)):
        if g_vals[i] is PARTIAL_FLAG_LAMBDA:
            syntax_cond_assert(partial_idx < 0, "expression partial function can only one argument")
            partial_idx = i
    
    def compute_expr(env, vals, ops):

        def binary_order(left, preorder):
            if len(ops) <= 0: return left
            if preorder >= ops[0]["order"]: return left
            my_op = ops.pop(0)

            # Logic short circuit
            if (my_op["name"] == 'OR' and left ) or (my_op["name"] == 'AND' and (not left)):
                return left

            right = vals.pop(0)(env)
            if len(ops) > 0:
                his_op = ops[0]
                if his_op["order"] > my_op["order"] or \
                    (his_op["order"] == my_op["order"] and his_op["right"]):
                    right = binary_order(right, my_op["order"])

            new_left = my_op["func"](left,right)
            return binary_order(new_left, preorder)

        left = vals.pop(0)(env)
        return binary_order(left, -1)
    
    def ori_warpper(env):
        vals, ops = copy.copy(g_vals), copy.copy(g_ops)
        return compute_expr(env, vals, ops)

    def partial_warpper(env):
        def warpper(v):
            vals, ops = copy.copy(g_vals), copy.copy(g_ops)
            vals[partial_idx] = lambda env: v
            return compute_expr(env, vals, ops)
        return warpper

    return ori_warpper if partial_idx < 0 else partial_warpper

def parse_args(node):
    syntax_cond_assert(node["type"] in ("ARGS", "TUPLE", "PARN", "PARTIAL"), "error type")
    arg_vals = list(map(parse_expr, node["val"]))
    default_vals = []
    if "default_vals" in node:
        default_vals = list(map(parse_expr, node["default_vals"]))

    def _args(env):
        r_default = {}
        if "default_args" in node:
            r_default_vals = [f(env) for f in default_vals]
            r_default = dict(zip(node["default_args"], r_default_vals))
        r_arg_vals = [f(env) for f in arg_vals]
        return (r_arg_vals, r_default)

    return _args


# 返回第一个值
def parse_parn(node):
    syntax_cond_assert(len(node["val"]) == 1 , "error: empty parn")
    parn_node = parse_expr(node["val"][0])
    return lambda env: parn_node(env)
    

def parse_suffix_op(op):
    if op["type"] in ("PARN", "TUPLE", "ARGS"):
        snv = parse_args(op)
        return lambda env: lambda f: Unary["CALL"](f, snv(env))
    elif op["type"] is "PARTIAL":
        return parse_partial(op)
    elif op["type"] is "DOT":
        return lambda env: lambda x: x.__getattribute__(op["attribute"])
    else:
        snv = parse_list(op["val"])
        return lambda env: lambda v: Unary["GET"](v, snv(env))

def parse_partial(node):
    h_args = parse_args(node)
    def _fdo(env, f):
        args, default_args = h_args(env)
        def _do(*p_args):
            total_args, i = [], 0
            for h in args:
                if h is not PARTIAL_FLAG:
                    total_args.append(h)
                else:
                    if i >= len(p_args): Error("too many args")
                    total_args.append(p_args[i])
                    i = i + 1
            if i < len(p_args): Error("too less args")
            return f(*total_args, **default_args)
        return _do
    return lambda env: lambda f: _fdo(env, f)


def parse_unary(node):
    if node["type"] != "UNARY": return parse_val_expr(node)
    prefix_ops = [Unary[v] for v in node["prefix"] ]
    prefix_ops.reverse()
    obj = parse_val_expr(node["obj"])
    suffix_ops = list(map(parse_suffix_op, node["suffix"]))
    
    def _unary(env):
        v = obj(env)
        for sf in suffix_ops: v = sf(env)(v)
        for pf in prefix_ops: v = pf(v)
        return v
    return _unary
        
# function call; var; literal value; unary operator
def parse_val_expr(node):
    t_type = node["type"]
    if t_type is 'VAR':
        atom = parse_var(node)
    elif t_type is 'LIST': 
        atom = parse_list(node["val"])
    elif t_type is 'TUPLE':
        atom = parse_tuple(node)
    elif t_type is 'DICT': 
        atom = parse_dict(node)
    elif t_type in ("BOOL", 'NUM', 'STRING', "NONE"):
        atom = lambda env : node["val"]
    elif t_type is 'SYSCALL':
        atom = parse_syscall(node)
    elif t_type is 'SYSFUNC':
        atom = parse_sysfunc(node)
    elif t_type is 'LAMBDA':
        atom = parse_lambda(node)
    elif t_type is 'PARN':
        atom = parse_parn(node)
    else:
        Error("val_expr: " + t_type)
    return atom

def parse_list_comp(node):
    interval = lambda env: 1
    if 1 != node["interval"]:
        interval = parse_expr(node["interval"])
    beg = parse_expr(node["beg"])
    end = parse_expr(node["end"])

    def _list_range(env):
        beg_v = beg(env)
        end_v = end(env)
        interval_v = interval(env)
        return range(beg_v, end_v, interval_v)

    return  _list_range

def parse_list(node_list):
    res = []
    for ele in node_list:
        if ele["type"] == "LISTCOM":
            res.append(("COMP", parse_list_comp(ele)))
        else:
            res.append(("ELE", parse_expr(ele)))

    def _p_list(env):
        v = []
        for r in res:
            if r[0] == "COMP": v.extend(r[1](env))
            else:  v.append(r[1](env))
        return v

    return _p_list

def parse_tuple(node):
    val = parse_list(node["val"])
    return lambda env: tuple(val(env))

def parse_dict(node):
    keys = parse_list(node["key"])
    vals = parse_list(node["val"])
    res = {}
    def _dict(env):
        res.update(list(zip(keys(env), vals(env))))
        return res
    return _dict
        
def parse_if(node):
    cond = parse_simple_expr(node["cond"])
    then_f = parse_block(node["then"])
    else_f = lambda env: None
    if node["else"]:
        else_f = parse_block(node["else"])
    return lambda env: then_f(env) if cond(env) else else_f(env)

def parse_in(node):
    v = parse_expr(node["val"])
    def _in(env):
        var = node["var"]["name"]
        for ele in v(env):
            yield [(var, ele)]

    def _p_in(env):
        var = node["var"]["variables"]
        for ele in v(env):
            yield lst_combine(var, ele)

    return _p_in if node["var"]["type"] == "PATTERNVAR" else _in

def parse_for(node):
    in_f = parse_in(node["in"])
    body_f = parse_block(node["body"])

    def _for(env):
        iters = in_f(env)
        for g in iters:
            try:
                env.update(g)
                body_f(env)
            except Continue_exception:
                continue
            except Break_exception:
                break
        
    return _for

def parse_while(node):
    cond = parse_simple_expr(node["cond"])
    body_f = parse_block(node["body"])
    
    def _while(env):
        while cond(env):
            try:
                body_f(env)
            except Continue_exception:
                continue
            except Break_exception:
                break

    return _while

def os_call(sh):
    import subprocess
    out_bytes = subprocess.check_output(sh)
    return out_bytes.decode('utf-8')

def parse_syscall(node):
    return lambda env:os_call(node["val"])

def parse_sysfunc(node):
    return lambda env : lambda args: os_call(node["val"]% args)

# Q default args
def parse_lambda(node):
    arg_var_list = [e["name"] for e in node["args"]["val"]]
    def _lambda(env):
        body_f = parse_expr(node["body"])
        def proc(*arg_val_list):
            new_env = Env(outer = env)
            if len(arg_var_list) != len(arg_val_list): Error("not enough arguments")
            new_env.update(zip(arg_var_list,arg_val_list))
            return body_f(new_env)
        return proc

    return _lambda

def parse_var(node):
    var = node["name"]
    def find(env):
        t = env.find(var)
        if t is None: Error(var + " not find")
        return t[var]
    return PARTIAL_FLAG_LAMBDA if var == "_" else find
    
def parse_block(node):
    exprs = list(map(parse, node))
    def squence_do(env):
        for expr in exprs: 
            expr(env)
    return squence_do

def parse_def(node):
    args_node = node["args"]["val"]
    args = []
    for ag in args_node:
        if ag["type"] != "VAR": Error("syntax error in function def arguments")
        args.append(ag["name"])

    default_args, default_vals = [], []
    if "default_args" in args:
        default_vals = parse_expr(args["default_vals"])
        default_args = parse_expr(args["default_args"])

    def _def(env):
        def proc(*args_vals, **kwargs):
            if len(args_vals) < len(args) or len(args_vals) > len(args) + len(default_args):
                Error("%s() unexpected argument number"% node["name"])
            for k,v in kwargs.items():
                if k not in default_args:
                    Error("%s() not defined argument %s"%(node["name"], k))
            new_env = Env(outer = env)
            body_f = parse_block(node["body"])
            # default args, every call re-eval, update them
            r_default_vals = [a(new_env) for a in default_vals]
            new_env.update(list(zip(default_args, r_default_vals)))
            av = list(zip(args + default_args, args_vals))
            new_env.update(av)
            new_env.update(kwargs)

            try:
                body_f(new_env)
            except Return_exception as r:
                return r.value(new_env)

        env[node["funcname"]] = proc
        return "function: " + node["funcname"]
    return _def
