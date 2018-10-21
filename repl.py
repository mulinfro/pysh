from stream import stream
from char_stream import char_stream
from eval_ast import parse, Env
from ast_dict import AST
from tokens import token_list
from env import get_builtin_env
import os, types, re, sys, glob
PSH_DIR = sys.path[0]

def pathCompleter(self,text,state):
        """ 
        This is the tab completer for systems paths.
        Only tested on *nix systems
        """
        line   = readline.get_line_buffer().split()
        return [x for x in glob.glob(text+'*')][state]

def repl_readline_helper():
    import readline, atexit #,rlcompleter
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')
    #readline.set_completer(pathCompleter)
    histfile = os.path.join(PSH_DIR, ".pyhist")
    try:
        readline.read_history_file(histfile)
        # default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(1000)
    except IOError:
        pass
    atexit.register(readline.write_history_file, histfile)

builtins = locals()["__builtins__"]

def REPL():
    try:
        repl_readline_helper()
    except ImportError:
        print("readline module is not installed! use raw input")
    IN = "$> "
    env = get_builtin_env(builtins)
    def is_block(cmd):
        def helper(line, n):
            return len(line) > n and line[n] in " \t("
        if cmd.startswith("def") or cmd.startswith("for"):
            return helper(cmd, 3)
        elif cmd.startswith("if"):
            return helper(cmd, 2)
        elif cmd.startswith("while"):
            return helper(cmd, 5)
        else:
            return False

    cmdlines, block_num, = [], 0
    cmd = ""
    while True:
        try:
            cmd = cmd + input(IN).strip()
        except KeyboardInterrupt:
            print(" CTRL-C")
        if cmd in ['quit', 'exit']: break
        # in repl every multiline expr need \ 
        if cmd.endswith("\\"):
            cmd = cmd[0:-1]
            continue

        cmdlines.append(cmd)
        if is_block(cmd): block_num = block_num + 1
        if cmd.endswith("end"): 
            if len(cmd) == 3 or cmd[-4] in [" ", "\t"]:
                block_num = block_num - 1
        cmd = ""
            
        if block_num == 0:
            script = char_stream("\n".join(cmdlines) +"\n")
            cmdlines = []
            try:
                parse_and_eval_with_env(script, env)
            except Exception as e:
                print(repr(e))
            except KeyboardInterrupt:
                print("KeyboardInterrupt")

def parse_and_eval_with_env(script, env):
    tokens = token_list(script).tokens
    #print("tokens", tokens)
    ast_tree = AST(stream(tokens))
    for node in ast_tree.ast:
        ans = parse(node)(env)
        if ans is None or node["type"] == "ASSIGN": continue
        if isinstance(ans, types.GeneratorType):
            for e in ans: 
                print(":> ", e)
        else:
            print(":> ", ans)
    
def pysh(psh_file, run=True):
    with open(psh_file, encoding="utf-8") as f:
        script = char_stream(f.read())
    env = get_builtin_env(builtins)
    parse_and_eval_with_env(script, env)

    if run and "main" in env:
        return env["main"](*sys.argv[2:])

    return env


def test_psh_file():
    pysh(os.path.join(PSH_DIR,"test.psh"))
        
if __name__ == "__main__":
    #test_psh_file()
    if len(sys.argv) > 1:
        pysh(sys.argv[1])
    else:
        REPL()
