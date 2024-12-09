from typing import Any
from util import *
from logic import *

SPACING: str = " "
# POSCOL: str = "\x1b[48;5;244m"
POSCOL: str = "\x1b[48;5;8m"
# POSCOL: str = "\x1b[48;2;100;100;100m"
SHOWPOS: bool = False

def toggleShowpos() -> None:
    global SHOWPOS
    SHOWPOS = not SHOWPOS

# def primRend(area: PlayArea) -> None:
def render(area: PlayArea) -> None:
    write(f"moves: {area.moves}\n")
    for i in range(4):
        if tuple(area.cpos) == (-(i+1),0):
            write(POSCOL)
        write(f"{'[]\x1b[0m' if len(area.aces[i].stack) == 0 else str(area.aces[i].stack[-1])}{SPACING}")
    write('\n')
    if tuple(area.cpos) == (0,0):
        write(POSCOL)
    write(f"{'@@' if len(area.deck.cards) > 0 else '[]'}\x1b[0m{SPACING}")
    for i in range(max(area.lengths)):
        if i == 1:
            if tuple(area.cpos) == (0,1):
                write(POSCOL)
            write(f"\x1b[G{'  \x1b[0m' if len(area.pile) == 0 else str(area.pile[-1].as_faceup())}{SPACING}")
        for (j,s) in enumerate(area.stacks):
            if len(s.stack) > i:
                if (j+1,i) == tuple(area.cpos):
                    write(POSCOL)
                write(f"{s.stack[i]}")
            elif i == 0 and area.cpos[0] == j+1:
                write(f"{POSCOL}  \x1b[0m")
            else:
                write("  ")
            write(f"{SPACING}")
        write(f"\n  {SPACING}")
    write('\n')
    if SHOWPOS:
        write(f":{area.cpos}: {POSCOL}{'' if tuple(area.selloc) == (-1,-1) else area.selloc}\x1b[0m\n")
    flush()
# def render(area: PlayArea) -> None:
#     cl = area.deltas.changes()
#     area.deltas.commit()
