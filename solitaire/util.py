from typing import Iterable
from sys import stdout
def write(s: str | Iterable[str], flush: bool = False) -> None:
    if type(s) == str:
        stdout.write(s.replace("\n", "\r\n"))
    else:
        write(''.join(s))
    if flush:
        stdout.flush()
def writi(s: str | Iterable[str]) -> None:
    write(s, True)
def flush() -> None:
    stdout.flush()
def hide() -> None:
    write('\x1b[?25l')
    flush()
def show() -> None:
    write('\x1b[?25h')
    flush()

def default(value):
    def deco(f):
        def wf(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except:
                return value
        return wf
    return deco

def hide_after(f):
    def wf(*args, **kwargs):
        r = f(*args, **kwargs)
        hide()
        return r
    return wf
