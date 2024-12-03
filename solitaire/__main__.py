import sys
import tty
import termios

from glue import run

_default_attr = tty.setraw(sys.stdin)
try:
    run()
finally:
    termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, _default_attr)
