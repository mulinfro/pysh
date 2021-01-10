
class Env(dict):
    "An environment: a dict of {'var':val} pairs, with an outer Env."
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
        self.globals = outer.globals if outer else self
    def find(self, var):
        "Find the innermost Env where var appears."
        if (var in self): return self
        elif self.outer is None: return None
        else: return self.outer.find(var)

#builtins = locals()["__builtins__"]
def get_builtin_env(builtins):
    paras = dir(builtins)
    args  = [builtins.__dict__.get(a) for a in paras]
    all_lib_funcs = []
    from libs import os_cmd, text_process, function_tools, csv
    import config
    register(os_cmd, paras, args, all_lib_funcs)
    register(text_process, paras, args, all_lib_funcs)
    register(function_tools, paras, args, all_lib_funcs)
    register(config, paras, args, all_lib_funcs)
    register(csv, paras, args, all_lib_funcs)
    paras.append("__all_lib_func_names__")
    args.append(all_lib_funcs)
    return Env(parms = paras, args = args)

def register(module, paras, args, all_lib_funcs):
    for p in module.__all__:
        paras.append(p)
        args.append(module.__dict__.get(p))
        all_lib_funcs.append(p)

class obj(object):
    def __init__(self, d):
        for a, b in d.items():
            setattr(self, a, b)
