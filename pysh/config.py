import sys
__all__ = [ "history", "HIS_LENGTH", "IN", "repl_init_str", "PSH_DIR", "ARGV" ]

# repl command history
history = []
# record repl commands length
HIS_LENGTH = 200
IN = "$> "


repl_init_str = """  PYSH: shell & python & functional programming
  repl commands: [history -> cmd list; exit -> exit;  clear -> clear environment]
"""

PSH_DIR = sys.path[0]
ARGV = sys.argv[1:]
