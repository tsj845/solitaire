from typing import Callable
from enum import Enum
from sys import stdin
from util import *
import os

def poll() -> str | None:
    os.set_blocking(stdin.fileno(), False)
    r = stdin.read(1)
    os.set_blocking(stdin.fileno(), True)
    return r
def readfull() -> str:
    a = stdin.read(1)
    if a == '\x1b':
        t = poll()
        if t:
            a += t
            while not t.isalpha():
                t = stdin.read(1)
                a += t
    return a

class InputType(Enum):
    Motion = 0
    Name = 1
    Cmd = 2
class Motion(Enum):
    Up = 0
    Down = 1
    Left = 2
    Right = 3

class Input:
    def __init__(self, itype: InputType, value: str | int | Motion) -> None:
        self.itype = itype
        self.value = value

_is_setup = False
def setup() -> None:
    global _is_setup
    if _is_setup:
        return
    _is_setup = True
    hide()
def cleanup() -> None:
    show()

keybinds: dict[str, Input] = {
    "a":Input(InputType.Motion, Motion.Left),
    "d":Input(InputType.Motion, Motion.Right),
    "w":Input(InputType.Motion, Motion.Up),
    "f":Input(InputType.Motion, Motion.Up),
    "s":Input(InputType.Motion, Motion.Down),
    "i":Input(InputType.Cmd, "\0cmdstart"),
    "o":Input(InputType.Cmd, "select"),
    "m":Input(InputType.Name, None),
    "h":Input(InputType.Name, None),
    "e":Input(InputType.Name, "ace"),
    "c":Input(InputType.Name, "any")
}

@hide_after
def readInput(name: bool = False, cmd: bool = False, single: bool = False) -> Input:
    global keybinds
    def readRaw(a: bool = False) -> Input:
        global keybinds
        while True:
            c = stdin.read(1)
            if c == '\x03':
                raise KeyboardInterrupt()
            if c == '\x1b':
                t = poll()
                if t != None and len(t):
                    if t != "[":
                        raise ValueError("unexpected control code")
                    n = stdin.read(1)
                    if n == 'A':
                        return Input(InputType.Motion, Motion.Up)
                    elif n == 'B':
                        return Input(InputType.Motion, Motion.Down)
                    elif n == 'C':
                        return Input(InputType.Motion, Motion.Right)
                    elif n == 'D':
                        return Input(InputType.Motion, Motion.Left)
                else:
                    return Input(InputType.Cmd, "escape")
            elif c == '\x0a' or c == '\x0d':
                if a:
                    return Input(InputType.Cmd, "select")
                return Input(InputType.Name, None)
            elif a:
                if c == '\x08' or c == '\x7f':
                    return Input(InputType.Cmd, "bs")
                return Input(InputType.Name, c)
            elif c == ' ':
                # return Input(InputType.Name, None)
                return Input(InputType.Cmd, "select")
            elif c == ',':
                return Input(InputType.Cmd, "\0cmdstart")
            elif c in keybinds.keys():
                return keybinds[c]
    if single:
        return readRaw(True)
    if not name:
        r = readRaw()
        if r.itype != InputType.Name:
            if r.itype == InputType.Cmd and r.value == "\0cmdstart":
                cmd = True
            else:
                return r
        elif r.value != None:
            return r
    show()
    buf = []
    bpos = 0
    if cmd:
        buf.append(',')
        bpos = 1
        write(',')
        flush()
    while True:
        inp = readRaw(True)
        if inp.itype == InputType.Cmd and inp.value == "escape":
            return Input(InputType.Cmd, "")
        if inp.itype == InputType.Name:
            buf.insert(bpos, inp.value)
            write(buf[bpos:])
            bpos += 1
            write(f"\x1b[{bpos+1}G")
            # write(inp.value)
            flush()
        elif inp.itype == InputType.Cmd:
            if inp.value == "bs":
                if bpos > 0:
                    bpos -= 1
                    buf.pop(bpos)
                    write('\x1b[D\x1b[0K')
                    write(buf[bpos:])
                    write(f"\x1b[{bpos+1}G")
                    flush()
            elif inp.value == "select":
                write('\x1b[2K\x1b[1G')
                if len(buf):
                    if buf[0] == ',':
                        return Input(InputType.Cmd, ''.join(buf[1:]))
                return Input(InputType.Name, ''.join(buf))
        elif inp.itype == InputType.Motion:
            match inp.value:
                case Motion.Up:
                    bpos = 0
                    write('\x1b[G')
                    flush()
                case Motion.Down:
                    bpos = len(buf)
                    write(f"\x1b[{bpos+1}G")
                    flush()
                case Motion.Left:
                    if bpos > 0:
                        bpos -= 1
                        write('\x1b[D')
                        flush()
                case Motion.Right:
                    if bpos < len(buf):
                        bpos += 1
                        write('\x1b[C')
                        flush()
@hide_after
def getConfirm(default: bool = False) -> bool:
    show()
    write("(y/N)" if not default else "(Y/n)")
    flush()
    if readfull().lower() != 'y':
        write('\x1b[2K\x1b[G')
        flush()
        return default
