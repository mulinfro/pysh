
__all__ = [ "history" ]

# repl command history
history = []
# record repl commands length
HISLENGTH = 200
IN = "$> "


repl_init_str = """  PYSH: shell & python & functional programming
  repl commands: [history -> cmd list; exit -> exit;  clear -> clear environment]
"""
