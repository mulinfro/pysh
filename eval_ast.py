from builtin import operators, op_order, Binary, Unary, op_right, os_call, cd
import copy
from types import GeneratorType
from env import Env
from syntax_check import Error, syntax_cond_assert
from exception import Return_exception, Assert_exception, Continue_exception, Break_exception, exception_warp, Pipe_generator
PARTIAL_FLAG = lambda f: f  
PARTIAL_FLAG_LAMBDA = lambda env: PARTIAL_FLAG



def parse(node):
    if  node["type"] == 'DEF': 
        val = parse_def(node)
    elif node["type"] == 'IMPORT': 
        val = parse_import(node)
    else:
        val = parse_block_expr(node)
    return val

def parse_del(node):
    name = node["var"]
    def _del(env):
        t = env.find(name)
        if t is None: Error("undefind variable %s"%name)
        del t[name]
    return exception_warp(_del, node["msg"])

def parse_sh(node):
    cmd = parse_pipe_or_expr(node["cmd"])
    def _sh(env):
        cmd_val = cmd(env)
        syntax_cond_assert(type(cmd_val) == str, "Value Error: sh handles a string")
        return os_call(cmd_val)
    return exception_warp(_sh, node["msg"])

def parse_cd(node):
    cmd = parse_pipe_or_expr(node["cmd"])
    def _cd(env):
        cmd_val = cmd(env)
        syntax_cond_assert(type(cmd_val) in [str, int], "Value Error: cd accept a string or int")
        return cd(cmd_val)
    return exception_warp(_cd, node["msg"])


def parse_catched(node):
    expr = parse_block_expr(node["expr"])
    if type(node["handle"]) == list:
        handle = parse_block(node["handle"])
    else:
        handle = parse_pipe_or_expr(node["handle"])

    def _catched(env):
        try:
            val = expr(env)
            return Pipe_generator(val, handle, env)
        except Exception as e:
            print("type error: " + str(e))
            handled_value = handle(env)
            if node["expr"]["type"] == "PIPE" and "__pipe_continue_point" in env:
                return expr(env, env["__pipe_continue_point"])
            return handled_value

    return _catched

def parse_rasie(node):
    if node["expr"]:
        expr = parse_pipe_or_expr(node["rval"])
    else:
        expr = lambda env: None

    def _raise(env):
        val = expr(env)
        raise Exception(val)

    return _raise

def parse_block_expr(node):
    if node["type"] == 'IF':
        val = parse_if(node)
    elif node["type"] == 'WHILE': 
        val = parse_while(node)
    elif node["type"] == "FOR":
        val = parse_for(node)
    elif node["type"] in ["BREAK", "CONTINUE", "RETURN"]:
        val = parse_flow_goto(node)
    elif node["type"] == "PIPE":
        val = parse_pipe(node)
    else:
        val = parse_expr_or_command(node)
    return val

def parse_expr_or_command(node):
    if node["type"] == "ASSERT":
        val = parse_assert(node)
    elif node["type"] == "DEL":
        val = parse_del(node)
    elif node["type"] == "SH":
        val = parse_sh(node)
    elif node["type"] == "CD":
        val = parse_cd(node)
    elif node["type"] == "RAISE":
        val = parse_rasie(node)
    else:
        val = parse_pipe_or_expr(node)
    return val

def parse_pipe_or_expr(node):
    if node["type"] == "PIPE":
        return parse_pipe(node)
    elif node["type"] == "CATCHED":
        return parse_catched(node)
    else:
        return parse_expr(node)

def parse_pipe(node):
    tmp = list(map(parse_expr, node["exprs"]))
    left, g_exprs = tmp[0], tmp[1:]
    g_ops  = list(map(parse_bi_oper, node["pipes"]))

    def _eval_pipe(env, continue_point = None):
        if continue_point is None:
            left_val = left(env)
            if isinstance(left_val, GeneratorType):
                env["__pipe_continue_point"] = left_val
        else:
            left_val = continue_point
        exprs, ops = copy.copy(g_exprs), copy.copy(g_ops)
        ans_val =  compute_expr(env, exprs, ops, left_val)
        if "__pipe_continue_point" in env:  del env["__pipe_continue_point"]
        return ans_val

    return exception_warp(_eval_pipe, node["msg"])

def parse_expr(node):
    if node["type"] in ("ASSIGN", "GASSIGN"):
        val = parse_assign(node)
    elif node["type"] == "MULTI_ASSIGN":
        val = parse_multi_assign(node)
    else:
        val = parse_simple_expr(node)
    return val

def parse_simple_expr(node):
    if node["type"] == "SIMPLEIF":
        val = parse_simpleif_expr(node)
    elif node["type"] == "BIEXPR":
        val = parse_binary_expr(node)
    else:
        val = parse_unary(node)[1]
    return val


def parse_assert(node):
    rval = parse_pipe_or_expr(node["rval"])
    msg = parse_pipe_or_expr(node["info"]) if node["info"] else None

    def _assert_condition(env):
        cond = rval(env)
        if not cond:
            raise Assert_exception(cond, msg(env))

    return _assert_condition

def parse_flow_goto(node):
    def _raise_error(val):
        raise val

    if node["type"] == "RETURN":
        rval = parse_pipe_or_expr(node["rval"])
        return lambda env: _raise_error(Return_exception(rval))
    elif node["type"] == "BREAK":
        val = Break_exception()
    else:
        val = Continue_exception()

    if node["cond"]:
        cond = parse_pipe_or_expr(node["cond"])
    else:
        cond = lambda env: True

    return lambda env: _raise_error(val) if cond(env) else None

def parse_import(node):

    import sys, os
    def python_import(_from, _import, _as):
        if _from: 
            fromlist = _from.split(".")
            top_module = __import__(_from, fromlist = fromlist)
        _import_str, _import_val = "", [] 
        for tkn in _import:
            if tkn.tp == "SEP":
                if _import_str:
                    _import_val.append(_import_str)
                    _import_str = ""
            else:
                _import_str += tkn.val

        if _import_str: _import_val.append(_import_str)

        env = {}
        as_name = _as + [None]*len(_import_val)
        for t,g in zip(_import_val, as_name):
            nm = g if g else t.split(".")[0]
            if _from: env[nm] = top_module.__getattribute__(t)
            else:     env[nm] = __import__(t)
        return env
            
    def user_import_py(path, _as):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader(_as, path).load_module()

    def user_import_psh(path):
        syntax_cond_assert(os.path.is_file(path),  "Error: path %s is not a file"%path)
        import repl
        return repl.pysh(path, run=False)

    """  not neccssily
    def user_import_package(path, file_suffix):
        if file_suffix == ".py":
            return user_import_py(path + file_suffix, _as)
        elif file_suffix == ".psh":
            return user_import_psh(path)
        else:
            onlyfiles = [ f for f in os.listdir(path) ]
            env[_as] = user_import_package(path)
    """

    _from, _import, _as = node["from"], node["import"], node["as"]
    module = {}
    if _from or _import[0].tp != "STRING":
        module = python_import(_from, _import, _as)
    else:
        path = _import[0].val.strip()
        if path.endswith(".py"):
            module_context = user_import_py(path)
        if path.endswith(".psh"):
            module_context = user_import_psh(path)
        syntax_cond_assert(len(_as) <= 1, "User Import Error: too many names after AS")
        if len(_as) == 1:
            module_name = _as[0]
        else:
            module_name = os.path.split(path)[1].split(".")[0]

        module = {module_name: module_context}
            
    def update_env(env):
        env.update(module)

    return update_env

def parse_assign(node):
    val = parse_pipe_or_expr(node["val"])
    var_idx_val = None
    def _assign_var(env):
        v = val(env)
        if node["type"] == "GASSIGN":
            env = env.globals
        env[var] = v
        return v
    
    def _assign_expr_val(env):
        right_val = val(env)
        left_val = var_val(env)
        left_idx =  var_idx_val(env)
        left_val[left_idx] = right_val
        return right_val

    if node["var"]["type"] == "VAR":
        var = node["var"]["name"] 
        return _assign_var
    else:
        var = node["var"]
        syntax_cond_assert(var["type"] == "UNARY" and len(var["suffix"]) > 0, "assign: left value is invalid")
        var_idx = var["suffix"][-1]
        var["suffix"] = var["suffix"][0:-1]
        syntax_cond_assert(var_idx["type"] == "LIST", "assign: left value is invalid")
        syntax_cond_assert(len(var_idx["val"]) == 1,  "assign: left value is invalid")
        var_idx_val = parse_pipe_or_expr(var_idx["val"][0])
        var_val = parse_pipe_or_expr(var)
        return _assign_expr_val

def lst_combine(var, v):
    syntax_cond_assert(len(var) == len(v), "Value error: unpack %d values with %d variables"%(len(var), len(v)) )
    return list(zip(var, v))

def parse_multi_assign(node):
    val = parse_pipe_or_expr(node["val"])
    var = node["var"]["names"]
    
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


def compute_expr(env, vals, ops, left):
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

    val = binary_order(left, -1)
    del vals, ops
    return val


def parse_binary_expr(node):
    g_flag_vals = list(map(parse_unary, node["val"]))
    g_ops  = list(map(parse_bi_oper, node["op"]))
    g_vals = []

    partial_idx  = -1
    for i in range(len(g_flag_vals)):
        g_vals.append(g_flag_vals[i][1])
        if g_flag_vals[i][0] == "PARTIAL":
            syntax_cond_assert(partial_idx < 0, "partial binary expression can only have one unknown arg")
            partial_idx = i
    
    def ori_warpper(env):
        vals, ops = copy.copy(g_vals[1:]), copy.copy(g_ops)
        return compute_expr(env, vals, ops, vals[0](env))

    def partial_warpper(env):
        def warpper(v):
            vals, ops = copy.copy(g_vals), copy.copy(g_ops)
            vals[partial_idx] = lambda env: g_vals[partial_idx](env)(v)
            return compute_expr(env, vals[1:], ops, vals[0](env))
        return warpper

    func = ori_warpper if partial_idx < 0 else partial_warpper
    return exception_warp(func, node["msg"])

def parse_args(node):
    syntax_cond_assert(node["type"] in ("ARGS", "TUPLE", "PARN", "PARTIAL"), "error type")
    arg_vals = list(map(parse_pipe_or_expr, node["val"]))
    default_vals = []
    if "default_vals" in node:
        default_vals = list(map(parse_pipe_or_expr, node["default_vals"]))

    partial_idx = []
    for i,t in enumerate(arg_vals):
        if t is PARTIAL_FLAG_LAMBDA:
            partial_idx.append(i)

    def _args(env):
        r_default = {}
        if "default_args" in node:
            r_default_vals = [f(env) for f in default_vals]
            r_default = dict(zip(node["default_args"], r_default_vals))
        r_arg_vals = [f(env) for f in arg_vals]
        return (r_arg_vals, r_default)

    return _args, tuple(partial_idx)


# 返回第一个值
def parse_parn(node):
    syntax_cond_assert(len(node["val"]) == 1 , "error: empty parn")
    parn_node = parse_pipe_or_expr(node["val"][0])
    return lambda env: parn_node(env)
    
def parse_suffix_op(op):
    if op["type"] in ("PARN", "TUPLE", "ARGS"):
        snv, _ = parse_args(op)
        return lambda env: lambda f: Unary["CALL"](f, snv(env))
    elif op["type"] == "PARTIAL":
        return parse_partial(op)
    elif op["type"] == "DOT":
        return lambda env: lambda x: x.__getattribute__(op["attribute"])
    else:
        snv = parse_list(op["val"])
        return lambda env: lambda v: Unary["GET"](v, snv(env))

def parse_partial(node):
    h_args, p_args_idx = parse_args(node)
    p_args_num = len(p_args_idx)
    def _fdo(env, f):
        args, default_args = h_args(env)
        def _do(*p_args, **key_args):
            if p_args_num != len(p_args): Error("Expect %d args given %d"%(p_args_num, len(p_args)))
            default_args.update(key_args)
            for i, k in enumerate(p_args_idx):
                args[k] = p_args[i]
            return f(*args, **default_args)
        return _do
    return lambda env: lambda f: _fdo(env, f)


def parse_unary(node):
    if node["type"] != "UNARY": return parse_val_expr(node)
    prefix_ops = [Unary[v] for v in node["prefix"] ]
    prefix_ops.reverse()
    p_flag, obj = parse_val_expr(node["obj"])
    suffix_ops = list(map(parse_suffix_op, node["suffix"]))
    
    def _unary_helper(env, v):
        for sf in suffix_ops: v = sf(env)(v)
        for pf in prefix_ops: v = pf(v)
        return v

    def _unary(env):
        v = obj(env)
        return _unary_helper(env, v)

    def _unary_partial(env):
        def warpper(v):
            return _unary_helper(env, v)
        return warpper    

    if p_flag == "PARTIAL":
        return ("PARTIAL", exception_warp(_unary_partial, node["msg"]) )

    for op in node["suffix"]:
        if op["type"] == "PARTIAL":
            return ("PARTIAL", exception_warp(_unary, node["msg"]))

    return ("UNARY", exception_warp(_unary, node["msg"]))
        
# function call; var; literal value; unary operator
def parse_val_expr(node):
    t_type = node["type"]
    if t_type == 'VAR':
        return parse_var(node)
    elif t_type == 'LIST': 
        atom = parse_list(node["val"])
    elif t_type == 'TUPLE':
        atom = parse_tuple(node)
    elif t_type == 'DICT': 
        atom = parse_dict(node)
    elif t_type in ("BOOL", 'NUM', 'STRING', "NONE"):
        atom = lambda env : node["val"]
    elif t_type == 'SYSCALL':
        atom = parse_syscall(node)
    elif t_type == 'SYSFUNC':
        atom = parse_sysfunc(node)
    elif t_type == 'LAMBDA':
        atom = parse_lambda(node)
    elif t_type == 'PARN':
        atom = parse_parn(node)
    else:
        Error("val_expr: " + t_type)
    return ("VAL", exception_warp(atom, node["msg"]))

def parse_list_comp(node):
    interval = lambda env: 1
    if 1 != node["interval"]:
        interval = parse_pipe_or_expr(node["interval"])
    beg = parse_pipe_or_expr(node["beg"])
    end = parse_pipe_or_expr(node["end"])

    def _list_range(env):
        beg_v = beg(env)
        end_v = end(env)
        interval_v = interval(env)
        return range(beg_v, end_v, interval_v)

    return  exception_warp(_list_range, node["msg"])

def parse_list(node_list):
    res = []
    for ele in node_list:
        if ele["type"] == "LISTCOM":
            res.append(("COMP", parse_list_comp(ele)))
        else:
            res.append(("ELE", parse_pipe_or_expr(ele)))

    def _p_list(env):
        v = []
        for r in res:
            if r[0] == "COMP": v.extend(r[1](env))
            else:  v.append(r[1](env))
        return v

    return _p_list

def parse_tuple(node):
    val = parse_list(node["val"])
    return exception_warp(lambda env: tuple(val(env)), node["msg"])

def parse_dict(node):
    keys = parse_list(node["key"])
    vals = parse_list(node["val"])
    def _dict(env):
        return dict(zip(keys(env), vals(env)))
    return exception_warp(_dict, node["msg"])
        
def parse_if(node):
    else_f = parse_block(node["else"]) if node["else"] else lambda env: None 
    cond_f = [parse_simple_expr(cond) for cond in node["cond"]] + [lambda env: True]
    then_f = [parse_block(then) for then in node["then"]]       + [else_f]
    cond_then_pair = list(zip(cond_f, then_f))
    def do_switch(env):
        for cond,then in cond_then_pair:
            if cond(env):
                then(env)
                break
    return do_switch

def parse_in(node):
    v = parse_pipe_or_expr(node["val"])
    def _in(env):
        var = node["var"]["name"]
        for ele in v(env):
            yield [(var, ele)]

    def _p_in(env):
        var = node["var"]["names"]
        for ele in v(env):
            yield lst_combine(var, ele)

    func =  _p_in if node["var"]["type"] == "VAR_LIST" else _in
    return exception_warp(func, node["msg"])

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
            syntax_cond_assert(len(arg_var_list) == len(arg_val_list), "not enough arguments")
            new_env = Env(arg_var_list, arg_val_list, outer = env)
            val = body_f(new_env)
            del new_env
            return val
        return proc

    return exception_warp(_lambda, node["msg"])

def parse_var(node):
    var = node["name"]
    def find(env):
        t = env.find(var)
        if t is None: Error(var + " not find")
        return t[var]
    return ("PARTIAL", PARTIAL_FLAG_LAMBDA) if var == "_" else ("VAL", find)
    
def parse_block(node):
    exprs = list(map(parse, node))
    def squence_do(env):
        for expr in exprs: 
            val = expr(env)
        return val    # last expr as val; same with scala
    return squence_do

def parse_def(node):
    args_node = node["args"]
    args = []
    for ag in args_node["val"]:
        if ag["type"] != "VAR": Error("syntax error in function def arguments")
        args.append(ag["name"])

    default_args, default_vals = [], []
    if "default_args" in args_node:
        default_vals = [parse_pipe_or_expr(v) for v in args_node["default_vals"]]
        default_args = args_node["default_args"]
    body_f = parse_block(node["body"])

    def _def(env):
        r_default_vals = [a(env) for a in default_vals]
        def proc(*args_vals, **kwargs):
            new_env = Env(outer = env)
            if len(args_vals) < len(args) or len(args_vals) > len(args) + len(default_args):
                Error("%s() unexpected argument number"% node["name"])
            for k,v in kwargs.items():
                if k not in default_args:
                    Error("%s() not defined argument %s"%(node["name"], k))
            # default args
            new_env.update(zip(default_args, r_default_vals))
            new_env.update(zip(args + default_args, args_vals))
            new_env.update(kwargs)

            try:
                body_f(new_env)
            except Return_exception as r:
                return r.value(new_env)
            except Assert_exception as r:
                assert r.value, r.msg + "error on here"
            del new_env

        env[node["funcname"]] = proc
        #return "function: " + node["funcname"]
    return _def
