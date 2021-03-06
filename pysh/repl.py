from env import get_builtin_env
from eval_ast import parse_and_eval_with_env
from config import *
import os

def repl_readline_helper(env):
    try:
        import readline, atexit, rlcompleter
    except ImportError:
        print("readline module is not installed! use raw input")
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode vi')
    readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'",<>?')
    completer = rlcompleter.Completer(env, readline)
    readline.set_completer(completer.complete)
    #readline.set_completer(completer.pathCompleter)
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
    for kw in ["def", "for", "while"]:
        if helper(cmd, kw): 
            return True
    # very trick and  have some bugs
    if helper(cmd, "if") and ":" not in cmd: 
        return True
    return False

def REPL():
    cmd_history = []
    print(repl_init_str)
    env = get_builtin_env(builtins)
    repl_readline_helper(env)
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
            if len(cmd_history) > HIS_LENGTH: cmd_history.pop(0)
        if is_block(cmd): block_num = block_num + 1
        if cmd.endswith("end"): 
            if block_num > 0 and (len(cmd) == 3 or cmd[-4] in [" ", "\t"]):
                block_num = block_num - 1
        cmd = ""
            
        if block_num == 0:
            raw_script = "\n".join(cmdlines) +"\n"
            cmdlines.clear()
            #parse_and_eval_with_env(raw_script, env)
            try:
                parse_and_eval_with_env(raw_script, env)
            except Exception as e:
                print(repr(e))
            except KeyboardInterrupt:
                print("KeyboardInterrupt")


def pysh(psh_file, run=True, not_print=True):
    with open(psh_file, encoding="utf-8") as f:
        raw_script = f.read()
    env = get_builtin_env(builtins)
    #parse_and_eval_with_env(raw_script, env)
    try:
        parse_and_eval_with_env(raw_script, env, not_print=not_print)
    except Exception as e:
        print(repr(e))
        return None

    if run and "main" in env:
        return env["main"](ARGV[1:])

    return env

def test_psh_file():
    pysh(os.path.join(PSH_DIR,"test/test.psh"),  run=True, not_print=False)
    pysh(os.path.join(PSH_DIR,"test/test2.psh"), run=True, not_print=False)
        
if __name__ == "__main__":
    if len(ARGV) == 0:
        REPL()
    elif ARGV[0] == "-test":
        test_psh_file()
    else:
        pysh(ARGV[0])
