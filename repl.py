from stream import stream
from char_stream import char_stream
from eval_ast import parse
from ast_dict import AST
from tokens import token_list
from env import get_builtin_env, Env
from config import IN, HISLENGTH, repl_init_str
import os, types, sys, glob
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

def is_block(cmd):
    def helper(line, keyword):
        return line.startswith(keyword) and len(line) > len(keyword) and line[len(keyword)] in " \t("
    for kw in ["def", "if", "for", "while"]:
        if helper(cmd, kw): 
            return True
    return False

def REPL():
    cmd_history = []
    try:
        repl_readline_helper()
    except ImportError:
        print("readline module is not installed! use raw input")
    print(repl_init_str)
    env = get_builtin_env(builtins)
    env["history"] = cmd_history

    cmdlines, block_num, cmd = [], 0, ""

    while True:
        try:
            new_cmd = input(IN).strip()
        except KeyboardInterrupt:
            print(" CTRL-C")
            cmdlines.clear()
            block_num, cmd = 0, ""
            continue
        except EOFError:
            break
        cmd += new_cmd
        if cmd in ['quit', 'exit']: break
        if cmd == 'clear':
            del env
            env = get_builtin_env(builtins)
            block_num, cmd, env["history"] = 0, "", cmd_history
            cmdlines.clear()
            continue
        # in repl every multiline expr need \ 
        if cmd.endswith("\\"):
            cmd = cmd[0:-1]
            continue

        cmdlines.append(cmd)
        if cmd not in ["end", "", "exit", "history","clear"] and cmd not in cmd_history:
            cmd_history.append(cmd)
            if len(cmd_history) > HISLENGTH: cmd_history.pop(0)
        if is_block(cmd): block_num = block_num + 1
        if cmd.endswith("end"): 
            if len(cmd) == 3 or cmd[-4] in [" ", "\t"]:
                block_num = block_num - 1
        cmd = ""
            
        if block_num == 0:
            script = char_stream("\n".join(cmdlines) +"\n")
            cmdlines.clear()
            parse_and_eval_with_env(script, env)
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
        #print(node)
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
    #parse_and_eval_with_env(script, env)
    try:
        parse_and_eval_with_env(script, env)
    except Exception as e:
        print(repr(e))
        return None

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
