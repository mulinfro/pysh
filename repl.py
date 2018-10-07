from stream import stream
from char_stream import char_stream
from eval_ast import parse, Env
from ast_dict import AST
from tokens import token_list
from env import get_builtin_env
import types, re

import readline
readline.parse_and_bind('tab: complete')
readline.parse_and_bind('set editing-mode vi')

builtins = locals()["__builtins__"]

def load_history_cmds():
    return []

def REPL():
    history_cmds = load_history_cmds()
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
        cmd = cmd + input(IN).strip()
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

def parse_and_eval_with_env(script, env):
    tokens = token_list(script).tokens
    #print("tokens", tokens)
    ast_tree = AST(stream(tokens))
    for node in ast_tree.ast:
        ans = parse(node)(env)
        if ans is None or node["type"] == "ASSIGN": continue
        if isinstance(ans, types.GeneratorType):
            for e in ans: print(":> ", e)
        else:
            print(":> ", ans)
    

def pysh(psh_file):
    with open(psh_file) as f:
        script = char_stream(f.read())
    env = get_builtin_env(builtins)
    parse_and_eval_with_env(script, env)
    #print(node)
    #print(parse(node)(env))

    if "main" in env:
        import sys
        main(*sys.argv[1:])
        
if __name__ == "__main__":
    path = "D:\\github\\pysh\\"
    pysh(path + "test1.psh")
    REPL()
