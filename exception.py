
# 使用异常来实现控制流跳转
class Return_exception(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return "return"

class Assert_exception(Exception):
    def __init__(self, value, msg):
        self.value = value
        self.msg = msg
    def __str__(self):
        return "assert"

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

class Trace_exception(Exception):
    def __init__(self, errortype, trace):
        self.errortype = errortype
        self.traces = [trace]
    def __str__(self):
        return repr(self.errortype) + "\n" + "\n".join(self.traces)
    def add_trace(self, trace):
        self.traces.append(trace)

def exception_warp(func, msg):
    def _run_with_catch_exception(*args, **kargs):
        try:
            return func(*args, **kargs)
        except Trace_exception as r:
            r.add_trace("-> " + msg)
            raise r
        except Exception as r:
            raise Trace_exception(repr(r), "-> " + msg)
            
    return _run_with_catch_exception
