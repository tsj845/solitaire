from tinput import *
from logic import *
# from render import render, primRend, toggleShowpos
from render import render, toggleShowpos

def resetY(p: PlayArea) -> None:
    if p.cpos[0] != 0:
        p.cpos[1] = max(len(p.stacks[p.cpos[0]-1].stack)-1, 0)
    if p.cpos[0] == 0:
        p.cpos[1] = 0
def checkY(p: PlayArea, y: int) -> bool:
    if p.cpos[0] == 0:
        if y == 0:
            return True
        if len(p.pile) and y == 1:
            return True
        return False
    return y >= 0 and y < len(p.stacks[p.cpos[0]-1].stack)

def _setclean(f):
    def wf():
        setup()
        try:
            f()
        finally:
            cleanup()
    return wf

@_setclean
def run() -> None:
    def savelogic() -> None:
        while True:
            fn = readInput(True)
            if fn.itype == InputType.Name:
                try:
                    if ".." in fn.value or "." in fn.value:
                        raise ValueError()
                    with open("solitaire/saves/"+str(fn.value)+".sol", "wb") as f:
                        f.truncate(0)
                        f.write(p.save())
                    break
                except:
                    pass
    # d = Deck()
    # for i in range(len(d.cards)):
    #     if i % 4 == 0:
    #         print('\r')
    #     print(d.cards[i], end=' ')
    # print('\r')
    # p = PlayArea()
    writi("welcome to TUI solitaire, enter 'help' to get started\n")
    p: PlayArea = None
    # p.deck.cards.clear()
    anystep = False
    while True:
        if p:
            render(p)
            # primRend(p)
        i: Input = readInput(not p, not p)
        if i.itype == InputType.Name:
            if i.value == "help":
                writi("not a valid name, did you mean the command ',help'?\n")
            elif i.value == "ace":
                osel = p.selloc.copy()
                if p.selloc == NOSEL:
                    p.selloc = p.cpos.copy()
                x = p.cpos.copy()
                c = p.getCard(p.selloc)
                if c:
                    p.cpos = [-c.suit.value, 0]
                    p.select()
                    p.cpos = x
                    resetY(p)
                else:
                    p.cpos = x
                p.selloc = osel
            elif i.value == "any":
                oc = p.getCard(p.cpos)
                if oc != None and (oc.faceup if p.cpos[0] > 0 else True):
                    osel = p.selloc.copy()
                    p.selloc = p.cpos.copy()
                    if osel == p.selloc:
                        osel = NOSEL
                    x = p.cpos.copy()
                    p.cpos = NOSEL
                    if anystep:
                        write(f"OS{osel}:CS{p.selloc}:OP{x}:CP{p.cpos}")
                        getConfirm()
                    if oc.value == 13:
                        for i in range(len(p.stacks)):
                            if len(p.stacks[i].stack) == 0:
                                p.cpos = [i+1, 0]
                                if anystep:
                                    write(f"DP{p.cpos}")
                                    getConfirm()
                                break
                    else:
                        tar1 = Card(Suit.Clu if oc.kind else Suit.Hea, 2 if oc.value == 14 else oc.value + 1)
                        tar2 = Card(Suit.Spa if oc.kind else Suit.Dia, 2 if oc.value == 14 else oc.value + 1)
                        if anystep:
                            write(f"TRYLOC:{tar1.suit.name}{tar1.value}")
                            getConfirm()
                        p.cpos = p.locate(tar1)
                        if tuple(p.cpos) == (-1,-1) or not p.checkMove(p.selloc, p.cpos):
                            if anystep:
                                write(f"FAIL {'v' if not p.checkMove(p.selloc, p.cpos) else 'f'},TRYLOC:{tar2.suit.name}{tar2.value}")
                                getConfirm()
                            p.cpos = p.locate(tar2)
                    if tuple(p.cpos) != (-1,-1):
                        p.select()
                    elif anystep:
                        write("FAIL")
                        getConfirm()
                    p.cpos = x
                    resetY(p)
                    p.selloc = osel
            else:
                c = Card.from_name(i.value)
                if c:
                    l = p.locate(c)
                    if l != NOSEL:
                        p.cpos = l
        elif i.itype == InputType.Motion:
            if not p:
                continue
            if i.value == Motion.Up:
                if tuple(p.cpos) == (0,0):
                    p.cpos[0] -= 1
                elif checkY(p, p.cpos[1]-1):
                    p.cpos[1] -= 1
                else:
                    p.cpos = [-1, 0]
            elif i.value == Motion.Down:
                if p.cpos[0] < 0:
                    p.cpos = [0,0]
                elif checkY(p, p.cpos[1]+1):
                    p.cpos[1] += 1
                else:
                    p.cpos[1] = 0
            elif i.value == Motion.Right:
                if p.cpos[0] < 0:
                    if p.cpos[0] > -4:
                        p.cpos[0] -= 1
                elif p.cpos[0] < STACK_COUNT:
                    p.cpos[0] += 1
                    resetY(p)
            elif i.value == Motion.Left:
                if p.cpos[0] < 0:
                    if p.cpos[0] < -1:
                        p.cpos[0] += 1
                elif p.cpos[0] > 0:
                    p.cpos[0] -= 1
                    resetY(p)
        elif i.itype == InputType.Cmd:
            v: str = i.value
            if v == "quit":
                return
            elif v == "help":
                if not p:
                    writi('\n'.join([
                        "commands are started by typing ',', 'i', or 'return' + ','",
                        "Commands:",
                        "  quit",
                        "  start -- starts a new game",
                        "  stop -- stops the game",
                        "  save -- saves the game to the next entered name, names cannot include dots or slashes",
                        "  load [name]",
                        "  flip -- flips the card at the current position",
                        "  flipall -- flips all cards to faceup, if anything else is added to the command, flips all cards",
                        "  force -- forces the currently selected card (and any below it) to be put at the selected location",
                        "Controls:",
                        "  use arrow keys or WASD to move, F also acts as an 'up' input",
                        "  press 'e' to put the card at the current location onto an ace stack, if possible",
                        "  press 'c' to move the card at the current location to a valid place on the playing area, if available",
                        "  press 'm', 'h', or 'return' to open the name dialog",
                        "Name Dialog:",
                        "  by entering the display names of cards as seen in the terminal (case insensitive) into the name dialog, the cursor will be put at that position\n"
                        ]))
                else:
                    writi("cannot display help text while game is running, enter ',stop' to stop the game")
                    getConfirm()
            elif v == "stop":
                p = None
                writi("stopped\n")
            elif v == "select":
                p.select()
            elif v == "start":
                p = PlayArea()
                # primRend(p)
            elif v == "force":
                if not p:
                    writi("must be in game to force move\n")
                elif p.selloc != NOSEL:
                    p.select(True)
            elif v == "flip":
                if not p:
                    writi("must be in game to flip card\n")
                else:
                    p.flip()
            elif v.startswith("flipall"):
                if v == "flipall":
                    p.flipall(True)
                else:
                    p.flipall(False)
            elif v == "bind":
                writi("binding")
                b = readInput(single=True)
                writi("\x1b[Gtarget\x1b[K\n")
                parts = readInput(name=True).value.split(" ", 1)
                if len(parts) == 1:
                    keybinds[b.value] = keybinds[parts[0]]
                else:
                    checks = [("(","=")[k] in parts[j] for j in range(2) for k in range(2)]
                    # print(checks, end="\r\n", flush=True)
                    if not any(checks):
                        keybinds[b.value] = eval(f"Input(InputType.{parts[0]}, {parts[1]})")
                    else:
                        writi("bad value\n")
            elif v == "pos":
                toggleShowpos()
            elif v == "astep":
                anystep = not anystep
            elif v == "delts":
                writi(f"{p.deltas.changes()}\n")
                getConfirm()
            elif v == "savelist":
                if p:
                    writi("cannot view save list in game\n")
                else:
                    writi("TODO\n")
            elif v == "escape":
                if p:
                    p.selloc = NOSEL
            elif v == "save":
                if not p:
                    writi("cannot save outside of game\n")
                    continue
                savelogic()
            elif v.startswith("load "):
                p2 = None
                try:
                    if ".." in v or "." in v:
                        raise ValueError()
                    with open("solitaire/saves/"+v.split(' ', 1)[1]+".sol", "rb") as f:
                        p2 = PlayArea.load(f.read())
                except:
                    writi("could not load\n")
                if p2:
                    if p:
                        write("save current game? ")
                        if getConfirm():
                            savelogic()
                    p = p2
                    # primRend(p)
