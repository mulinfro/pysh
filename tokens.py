from builtin import operators, special_op, pipe_op, elevator_op

keywords = {
    'and': ("OP", 'AND'),
    'or' : ("OP", 'OR'),
    'not': ("OP", 'NOT'),
    'def': 'DEF',
    'lambda': 'LAMBDA',
    'L': 'LAMBDA',
    'if': 'IF',
    'else': 'ELSE',
    'elif': 'ELIF',
    'True': ("BOOL",True),
    'False': ("BOOL",False),
    'end': 'END',
    'is' : ("OP", 'IS'),
    'in' : ("OP", 'IN'),
    'while': "WHILE",
    'for'  : "FOR",
    "None" : ("NONE",None),
    "Nil"  : "NIL",
    "return": "RETURN",
    "break": "BREAK",
    "continue" : "CONTINUE",
    "import":  "IMPORT",
    "from" :  "FROM",
    "as" :  "AS",
    "module":  "MODULE",
    "assert" :  "ASSERT",
    "del" :  "DEL",
    "sh" :  "SH",
    "help": "HELP",
    "cd" :  "CD",
    "catch": "CATCH",
    "catched": "CATCHED",
    "raise": "RAISE",
    "case" : "CASE",
    "match" : "MATCH",
    "do": "DO",
    "when": "WHEN",
    "CL" : "CASE_LAMBDA",
    "caselambda" : "CASE_LAMBDA",
    "otherwise" : "OTHERWISE",
}

# 字符转义表， 字符串解析中使用
escape_table = {
    'n' : '\n',
    'r' : '\r',
    't' : '\t',
    '\\' : '\\',
    'a' : '\a',
    '"' : '"',
    'v' : '\v',
    'f' : '\f',
    'b' : '\b',
    '\n': '',
}

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

""" 
脚本文件先解析成token的列表;
一个token包含: 类型(tp), 值, 位于文件行数及列数 
"""
class token():
    def __init__(self, tkn_type, tkn_val, line=0, col=0):
        self.tp   = tkn_type
        self.val  = tkn_val
        self.line = line
        self.col  = col

    def __repr__(self):
        return ("type:%s; val %s; line %d col %d") %(self.tp, self.val, self.line, self.col)

"""
token解析类: 每次调用read_a_token返回一个token; 文件末尾时候返回None
token主要类型为几类: STRING, NUM, LIST, DICT, PARN, SYS_CALL, SEP, OP(操作符), VAR, KEYWORDS
"""
class token_list():
    
    def __init__(self, chars):
        self.chars = chars
        self.pre_token = token("SEP", "NEWLINE")
        self.tokens = self.read_tokens()

    def read_tokens(self):
        tokens = []
        while True:
            self.pre_token = tkn = self.read_a_token()
            if tkn is None:
                return tokens
            tokens.append(tkn)
        
    def read_a_token(self):
        self.read_white_space(" \t")
        if self.chars.eof(): return None
        ch = self.chars.peek()
        if ch in ('"', "'"): tkn = self.read_string()
        elif ch == '#': tkn = self.read_note()
        elif ch == '[': tkn = self.read_list()
        elif ch == '{': tkn = self.read_hashmap()
        elif ch == '(': tkn = self.read_parn()
        elif ch == '.': tkn = self.read_dot()
        elif ch == '$': tkn = self.read_dollar()
        elif str.isdigit(ch): tkn = self.read_num()
        elif str.isalpha(ch) or ch == '_': tkn = self.read_var()
        elif ch in ',\n':     tkn = self.read_sep()
        elif ch == '\\':      tkn = self.link()
        else: tkn = self.read_op()   # throw exception
        return tkn

    def read_dollar(self):
        if self.pre_token.tp == "SEP" and self.pre_token.val == "NEWLINE":
            return self.read_sys_call()
        else:
            return self.read_op()
           
   # 注释
    def read_note(self):
        while not self.chars.eof() and self.chars.peek() != "\n":
            self.chars.next()
        return self.read_a_token()

   # 拼接两行为一行命令; 跟python中一样
    def link(self):
        self.chars.next()
        if self.chars.next() != '\n':
            self.chars.crack("unexpected char after line continuation")
        return self.read_a_token()

    # 系统调用；$开头的单行命令
    def read_sys_call(self):
        line, col = self.chars.line, self.chars.col
        self.chars.next()
        self.read_white_space()
        command = ""
        while not self.chars.eof() and self.chars.peek() != '\n':
            command += self.chars.next()
        return token("SYSCALL", command, line, col)

    def read_sep(self):
        line, col = self.chars.line, self.chars.col
        ch = self.chars.next()
        if ch == ',':
            self.read_white_space(" \t\n")
            return token('SEP', 'COMMA', line, col)
        else: 
            return token('SEP', 'NEWLINE', line, col)
        
    # 跳过空格
    def read_white_space(self, ss = " \t"):
        while not self.chars.eof() and self.chars.peek() in ss:
            self.chars.next()
            
    # 变量；区分出关键字
    def read_var(self):
        line, col = self.chars.line, self.chars.col
        var = ""
        is_valid = lambda x: str.isalnum(x) or x == '_'
        while not self.chars.eof() and is_valid(self.chars.peek()):
            var += self.chars.next()
        if var in keywords: 
            kw = keywords[var]
            if var in ("None", "True", "False", "is", "in", "and", "or", "not"): 
                return token(kw[0], kw[1], line, col)
            else: 
                return token(kw, var, line, col)
        return token("VAR", var, line, col)
        
    def read_op(self):
        line, col = self.chars.line, self.chars.col
        op = ""
        if self.chars.peek() in '+-':
            op += self.chars.next()
            if self.chars.peek() in [">"]:
                op += self.chars.next()
        else:
            while self.chars.peek() in '!=<>|&@%*/.:~$':
                op += self.chars.next()

        if op in special_op:
            return token(special_op[op], op, line, col)
        elif op in elevator_op:
            return token("ELEVATOR", elevator_op[op], line, col)
        elif op in pipe_op: 
            return token("PIPE", pipe_op[op], line, col)
        elif op in operators: 
            return token("OP", operators[op], line, col)
        else:
            self.chars.crack('Undefined operator '+ op)

   # 读一个() [] or {}
    def read_pair(self, tp, end_ch):
        line, col = self.chars.line, self.chars.col
        val = []
        self.chars.next()
        while not self.chars.eof():
            self.read_white_space(" \t\n")
            ch = self.chars.peek()
            if ch == end_ch:
                self.chars.next()
                return token(tp, val, line, col)
            else:
                val.append(self.read_a_token())

        self.chars.crack('missing ' + end_ch)

    def read_list(self):
        return self.read_pair("LIST", ']')

    def read_hashmap(self):
        return self.read_pair("DICT", '}')

    def read_parn(self):
        return self.read_pair("PARN",')')

    def read_num(self):
        line, col = self.chars.line, self.chars.col
        ns = ""
        has_e = False
        while not self.chars.eof():
            ch = self.chars.peek()
            if str.isdigit(ch) or ch in '.Ee':
                ns += ch
                if ch in "Ee": has_e = True
            elif has_e and (ch == '+' or ch == '-'):
                ns += ch     # 科学记数法
            else:
                break

            self.chars.next()
            if ch not in "Ee": has_e = False
        return token("NUM", num(ns), line, col)

   # dot开头的可能是num，也可能是点操作符
    def read_dot(self):
        line, col = self.chars.line, self.chars.col
        self.chars.next()
        if str.isdigit(self.chars.peek()): 
            self.chars.back()
            return self.read_num()
        else: 
            return token('DOT', '.', line, col)

    def check_multi_string(self, tc):
        if tc != self.chars.peek():  return False
        if self.chars.eof() or tc != self.chars.looknext(): return False
        self.chars.next(), self.chars.next()
        return True

    # String语法与python中一样,可能是 "  ' , 多行string用""" , ''''
    def read_string(self):
        line, col = self.chars.line, self.chars.col
        val = ""
        isEscape = False
        terminal_char = self.chars.next()
        is_multi = self.check_multi_string(terminal_char)
        while not self.chars.eof():
            ch = self.chars.next()
            if isEscape:
                isEscape = False
                if ch in escape_table: val += escape_table[ch]
                else: val += "\\" + ch
            elif ch == '\n' and not is_multi:
                self.chars.crack('missing terminal %s'%terminal_char)
            elif ch == '\\':
                isEscape = True
            elif (ch == terminal_char) and (not is_multi \
                     or self.check_multi_string(ch)) :
                return token('STRING', val, line, col)
            else:
                val += ch

        self.chars.crack('missing terminal %s'%terminal_char)
