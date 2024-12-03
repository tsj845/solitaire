from tinput import *
from logic import *
from render import render

def resetY(p: PlayArea) -> None:
    if p.cpos[0] != 0:
        p.cpos[1] = len(p.stacks[p.cpos[0]-1].stack)-1
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
    p: PlayArea = None
    # p.deck.cards.clear()
    while True:
        if p:
            render(p)
        i: Input = readInput(not p, not p)
        if i.itype == InputType.Motion:
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
            elif v == "stop":
                p = None
                writi("stopped\n")
            elif v == "select":
                p.select()
            elif v == "start":
                p = PlayArea()
            elif v == "force":
                if not p:
                    writi("must be in game to force move\n")
                elif p.selloc != NOSEL:
                    p.select(True)
            elif v == "flip":
                if not p:
                    writi("must be in game to flip card\n")
                else:
                    c = p.getCard(p.cpos)
                    if c:
                        c.faceup = not c.faceup
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
                    keybinds[b.value] = eval(f"Input(InputType.{parts[0]}, {parts[1]})")
            elif v == "savelist":
                if p:
                    writi("cannot view save list in game\n")
                else:
                    writi("TODO\n")
            elif v == "save":
                if not p:
                    writi("cannot save outside of game\n")
                    continue
                savelogic()
            elif v.startswith("load "):
                p2 = None
                try:
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
