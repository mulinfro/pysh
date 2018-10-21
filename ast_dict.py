"""
     将tokens转化成ast; 加上一定的语法检查
     一个ast节点用字典表示，字典中包含了解析此node的必要信息
"""
from stream import stream
from syntax_check import *
from builtin import Binary, Unary

Tautology = lambda x: True

# 分隔符语法检查
def syntax_assert_helper(stm, flag):
    md = { "EXPR_END": "SEP",
           "NEWLINE": ("SEP", "NEWLINE"),
           "COMMA"  : ("SEP", "COMMA")
        }
    if not stm.eof():
        tkn = stm.next()
        error_msg = "syntax error: expected %s, accully token %s with val %s" % (flag, tkn.tp, tkn.val)
        syntax_assert(tkn, md[flag], error_msg)

def check_expr_end(stm):
    syntax_assert_helper(stm, "EXPR_END")

def check_newline(stm):
    syntax_assert_helper(stm, "NEWLINE")

def check_comma(stm):
    syntax_assert_helper(stm, "COMMA")

def check_eof(stm):
    syntax_cond_assert(stm.eof(), "syntax error")

def line_eof(stm):
    return stm.eof() or syntax_check(stm.peek(),  ("SEP", "NEWLINE"))

class AST():
    
    def __init__(self, tokens):
        self.tokens = tokens
        self.ast = []
        self.build_ast()

    def build_ast(self):
        while True:
            self.newlines(self.tokens)
            if self.tokens.eof(): break
            tkn = self.tokens.peek()
            if tkn.tp == 'DEF':
                val = self.ast_def(self.tokens)
            elif tkn.tp in ["FROM", 'IMPORT']:
                val = self.ast_import(self.tokens)
            elif tkn.tp in ['IF', 'FOR', 'WHILE']:
                val = self.ast_control(self.tokens)
            else:
                val = self.ast_assign_or_command(self.tokens)

            self.ast.append(val)

    # 赋值；可连续赋值 x=y=z=1+1
    def ast_try_assign(self, stm):
        left = self.ast_expr(stm)
        if not stm.eof() and stm.peek().tp in ("ASSIGN", "GASSIGN"):
            tkn = stm.next()
            right = self.ast_try_assign(stm)
            return {"type":tkn.tp, "var":left, "val":right}
        else:
            check_expr_end(stm)
            return left
        
    def ast_var_list(self, stm):
        var_list = []
        while not line_eof(stm) and stm.peek().tp == "VAR" :
            var_list.append(stm.next().val)
            if line_eof(stm) or stm.peek().tp != "SEP": break
            stm.next()

        if len(var_list) == 1:
            return {"type":"VAR", "name":var_list[0]}
        return {"type":"VAR_LIST", "names":var_list}

    # python的import语法; 
    # pysh的import:  import(file_path) as name
    def ast_import(self, stm):
        _from, _import, _as = [], [], []
        if stm.peek().tp == "FROM":
            stm.next()
            while not line_eof(stm) and stm.peek().tp != "IMPORT":
                _from.append(stm.next().val)
            syntax_cond_assert(len(_from) >0, "Empty from")
        syntax_assert(stm.next(), "IMPORT", "expect import") 
        while not line_eof(stm) and stm.peek().tp != "AS":
            _import.append(stm.next())
        
        syntax_cond_assert(len(_import) >0, "Empty import")
        if not line_eof(stm):
            syntax_assert(stm.next(), "AS", "expect as") 
            var_list = self.ast_var_list(stm)
            if var_list["type"] == "VAR_LIST":
                _as = var_list["names"]
            else:
                _as =  [ var_list["name"] ]
            syntax_cond_assert(len(_as) >0, "Empty as")
        if not line_eof(stm): Error("Syntax error: unexpected words %s in import"%stm.peek().val)
        return {"type":"IMPORT", "from":"".join(_from), "import":_import, "as":_as}

    def ast_same_type_seq(self, stm, is_valid):
        tps = []
        while not stm.eof() and is_valid(stm.peek()):
            tps.append(stm.next().val)
        return tps

    def newlines(self, stm):
        is_valid = lambda tkn: syntax_check(tkn, ("SEP","NEWLINE"))
        vals = self.ast_same_type_seq(stm, is_valid)
        return len(vals) > 0

    def ast_block_expr(self, stm):
        if stm.peek().tp in ['IF', 'FOR', 'WHILE']:
            return self.ast_control(stm)
        elif stm.peek().tp in ["BREAK", "CONTINUE"]:
            return self.ast_bc(stm)
        elif stm.peek().tp == "RETURN":
            return self.ast_return_assert(stm, stm.peek().tp)
        else:
            return self.ast_assign_or_command(stm)

    def ast_bc(self, stm):
        tp = stm.next().tp
        check_newline(stm)
        return {"type": tp}

    def ast_return_assert(self, stm, tp):
        stm.next()
        expr = self.ast_expr(stm)
        msg = None
        if not stm.eof() and syntax_check(stm.peek(), ("SEP", "COMMA")):
            stm.next()
            msg = self.ast_expr(stm)
        check_newline(stm)
        syntax_cond_assert(tp == "ASSERT" or msg==None, "syntax error: return")
        return {"type": tp, "rval": expr, "msg":msg}

    def ast_del(self, stm):
        stm.next()
        syntax_assert(stm.peek(), "VAR", "Usage: del var")
        var = self.ast_a_var(stm)
        check_newline(stm)
        return {"type": "DEL", "var": var["name"] }

    def ast_control(self, stm):
        tkn = stm.peek()
        if   tkn.tp == 'IF':
            return self.ast_if(stm)
        elif tkn.tp == 'FOR':
            return self.ast_for(stm)
        elif tkn.tp == 'WHILE':
            return self.ast_while(stm)

    def ast_simple_args(self, stm):
        _vars = []
        while not stm.eof():
            syntax_cond_assert(stm.peek().tp == "VAR", "syntax error: need a var")
            _vars.append(stm.next().val)
            check_comma(stm)
        return _vars

            
    def ast_parn(self, stm):
        eles = self.ast_parn_eles(stm)
        vals, default_args, default_vals = [], [], []
        is_assign, is_partial = False, False
        eles_iter = iter(eles)
        for e in eles_iter:
            if e["type"] == "ASSIGN": is_assign = True
            if is_assign:
                syntax_cond_assert(e["type"] == "ASSIGN", "error undefault args follow default args")
                syntax_cond_assert(e["val"]["type"] != "ASSIGN", "unexpected continue assign")
                syntax_cond_assert(e["var"]["type"] == "VAR", "unexpected expression")
                default_args.append(e["var"]["name"])
                default_vals.append(e["val"])
            else:
                vals.append(e)
                if e["type"] == "VAR" and e["name"] == "_": is_partial = True
        
        if is_partial or len(default_args) > 0:
            tp = "ARGS" if not is_partial else "PARTIAL"
            return {"type":tp, "val":vals, 
                 "default_args": default_args, "default_vals":default_vals}
        elif len(vals) != 1:
            return {"type":"TUPLE", "val":vals}
        else:
            return {"type":"PARN",  "val":vals}
                

    def ast_parn_eles(self, stm):
        eles = []
        while not stm.eof():
            t = self.ast_try_assign(stm)
            eles.append(t)
        return eles

    def ast_assign_or_command(self, stm):
        if stm.peek().tp == "ASSERT":
            return self.ast_return_assert(stm, "ASSERT")
        elif stm.peek().tp == "DEL":
            return self.ast_del(stm)
        else:
            return self.ast_try_assign(stm)

    def ast_expr(self, stm):
        true_part = self.ast_binary_expr(stm)
        if not stm.eof() and stm.peek().tp == "IF":
            stm.next()
            cond = self.ast_binary_expr(stm)
            syntax_assert(stm.next(), "ELSE", "need else branch")
            else_part = self.ast_binary_expr(stm)
            return {"type":"SIMPLEIF", "then":true_part,
                    "cond":cond, "else":else_part}
        return true_part
                
    def ast_def(self, stm):
        stm.next()
        funcname = self.ast_a_var(stm, "need funcname")
        args = self.ast_args(stm)
        body = self.ast_body(stm, self.ast_func_body)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":'DEF', "funcname":funcname["name"], 
                "args":args, "body":body}
        
    def ast_args(self, stm):
        syntax_assert(stm.peek(), "PARN", "need parenthese")
        t = self.ast_parn(stream(stm.next().val))
        t["type"] = "ARGS"
        return t

    def ast_body(self, stm, parse_func):
        body = []
        while True:
            self.newlines(stm)
            if stm.peek().tp in ("ELSE", "END", "ELIF"): return body
            body.append(parse_func(stm))
    
    def ast_func_body(self, stm):
        tkn = stm.peek()
        if tkn.tp == 'DEF':
            return self.ast_def(stm)
        else:
            return self.ast_block_expr(stm)
        
    def ast_a_var(self, stm, error_msg = "expect a variable"):
        tkn = stm.next()
        syntax_assert(tkn, "VAR", error_msg)
        return {"type":"VAR", "name":tkn.val}

    def ast_if(self, stm):
        condlist, do_list = [], []
        while stm.peek().tp in ["ELIF", "IF"]:
            stm.next(); tkn = stm.next()
            syntax_assert(tkn, "PARN", "need parn")
            cond_stream = stream(tkn.val)
            cond = self.ast_expr(cond_stream)
            check_eof(cond_stream)
            true_part = self.ast_body(stm, self.ast_block_expr)
            condlist.append(cond)
            do_list.append(true_part)

        tkn, else_part = stm.peek(), None
        if tkn.tp == "ELSE":
            stm.next()
            else_part = self.ast_body(stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "'%s' missing END"%tkn.val)
        return {"type":'IF', "cond":condlist, "then":do_list, "else":else_part}
        
    def ast_for(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn, "PARN",  "missing (")
        _in = self.ast_in(stream(tkn.val))
        body = self.ast_body(stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":"FOR", "in":_in, "body":body}

    def ast_while(self, stm):
        stm.next(); tkn = stm.next()
        syntax_assert(tkn, "PARN",  "missing (")
        cond_stream = stream(tkn.val)
        cond = self.ast_expr(cond_stream)
        check_eof(cond_stream)
        body = self.ast_body(stm, self.ast_block_expr)
        syntax_assert(stm.next(), "END", "missing END")
        return {"type":"WHILE", "cond":cond, "body":body}

    def ast_in(self, stm):
        var = self.ast_var_list(stm)
        syntax_assert(stm.next(), ("OP", "IN"), "syntax error in for setence")
        val = self.ast_expr(stm)
        check_eof(stm)
        return {"type":"IN", "var":var, "val":val }

    def ast_unary(self, stm):
        prefix = self.ast_prefix_op(stm)
        obj_val = self.ast_val(stm)
        suffix = self.ast_suffix_op(stm)
        if len(prefix["val"]) + len(suffix["val"]) == 0: return obj_val
        return {"type":"UNARY", "prefix":prefix["val"],
                "obj":obj_val, "suffix":suffix["val"]}

    def ast_prefix_op(self, stm):
        is_valid = lambda tkn: tkn.tp == "OP" and tkn.val in Unary
        tps = self.ast_same_type_seq(stm, is_valid)
        return {"type":"PREFIXOP", "val":tps}

    def ast_suffix_op(self, stm):
        tps = []
        while not stm.eof():
            tp = stm.peek().tp 
            if tp in ("LIST", "PARN", "TUPLE" ):
                tps.append(self.ast_val(stm))
            elif tp == "DOT":
                tps.append(self.ast_dot(stm))
            else:
                break
        return {"type":"SUFFIXOP", "val":tps}

    def ast_dot(self, stm):
        stm.next()
        var = self.ast_a_var(stm)
        return {"type":"DOT", "attribute": var["name"]}

    def ast_binary_expr(self, stm):
        vals , ops = [], []
        vals.append(self.ast_unary(stm))
        while not stm.eof():
            op = self.ast_try_op(stm)
            if op is None: break
            ops.append(op)
            vals.append(self.ast_unary(stm))
        if len(ops) == 0: return vals[0]
        else: return {"type":"BIEXPR", "val":vals, "op":ops}

    def ast_try_op(self, stm):
        tkn = stm.peek()
        if tkn.tp == "OP" and tkn.val in Binary:
            return {"type":tkn.tp, "val":stm.next().val}
        return None

    def ast_val(self, stm):
        tkn = stm.next()
        if tkn.tp == "LAMBDA":
            val = self.ast_lambda(stm)
        elif tkn.tp == "LIST":
            val = self.ast_list(stream(tkn.val))
        elif tkn.tp == "PARN":
            val = self.ast_parn(stream(tkn.val))
        elif tkn.tp == "DICT":
            val = self.ast_dict(stream(tkn.val))
        elif tkn.tp == "VAR":
            val = {"type":"VAR", "name":tkn.val}
        elif tkn.tp in ('NUM', 'STRING', 'BOOL', "SYSCALL" ,"SYSFUNC", "NONE"):
            val = {"type":tkn.tp, "val":tkn.val}
        else:
            Error("Parse Error:%s,%s"%(tkn.tp, str(tkn.val)), tkn.line, tkn.col)

        return val
            
    def ast_lambda(self, stm):
        args = self.ast_args(stm)
        syntax_assert(stm.next(), ("OP", "COLON"), "lambda missing :")
        body = self.ast_expr(stm)
        return {"type":"LAMBDA", "args":args, "body":body}

    def ast_list_comp(self, stm):
        beg = self.ast_expr(stm)
        end, interval  = None, 1
        if not stm.eof() and syntax_check(stm.peek(), ("OP", "COLON") ):
            stm.next(); end = self.ast_expr(stm)
            if not stm.eof() and syntax_check(stm.peek(), ("OP", "COLON")):
                stm.next(); interval = self.ast_expr(stm)
        check_comma(stm)
        if end is None: return beg
        return {"type":"LISTCOM", "beg":beg, "end":end, "interval":interval}
        
    def ast_list(self, stm):
        vals = []
        while not stm.eof():
            vals.append(self.ast_list_comp(stm))
        return {"type":"LIST", "val": vals}

    def ast_dict(self, stm):
        key,val = [],[]
        while not stm.eof():
            key.append(self.ast_expr(stm))
            syntax_assert(stm.next(), ("OP","COLON"),  "missing colon :")
            val.append(self.ast_expr(stm))
            check_comma(stm)
        return {"type":"DICT", "key":key, "val":val}
