from ast_dict import AST
from tokens import token_list
from env import get_builtin_env, Env, obj
from types import GeneratorType
from parse_ast import parse
from stream import stream, char_stream
from exception import Generator_with_catch

def parse_and_eval_with_env(raw_script, env, not_print=False):
    script = char_stream(raw_script)
    tokens = token_list(script).tokens
    #print("tokens", tokens)
    ast_tree = AST(stream(tokens))
    #print("AST_TREE", ast_tree.ast)
    for node in ast_tree.ast:
        ans = parse(node)(env)
        if not_print or ans is None or node["type"] == "ASSIGN": continue
        if isinstance(ans, GeneratorType) or isinstance(ans, Generator_with_catch):
            for e in ans: 
                print(":> ", e)
        else:
            print(":> ", ans)
    
def load_psh_file(psh_file, env):
    with open(psh_file, encoding="utf-8") as f:
        script = char_stream(f.read())
    tokens = token_list(script).tokens
    ast_tree = AST(stream(tokens))
    for node in ast_tree.ast:
        parse(node)(env)
    return obj(env)

