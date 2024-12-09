from enum import Enum
from typing import Self, Any
from random import shuffle
from util import default

STACK_COUNT: int = 7

class Difficulty(Enum):
    Easy = 1
    Hard = 3

DiffSetting = Difficulty.Easy

class Suit(Enum):
    Inv = 0
    Hea = 1
    Dia = 2
    Clu = 3
    Spa = 4

SuitKinds: list[bool] = [None, True, True, False, False]
CardColors: list[str] = ["\x1b[0m","\x1b[38;5;196m","\x1b[38;5;202m","\x1b[38;5;27m","\x1b[38;5;21m"]
SuitSymbols: str = "@hdcs"
CardSymbols: str = "@@23456789TJQKA"
SelectedColor: str = "\x1b[38;2;244m"

class Card:
    def __init__(self, suit: Suit, value: int, faceup: bool = False) -> None:
        self.suit = suit
        self.value = value
        self.faceup = faceup
        self.selected = False
    def to_bytes(self) -> bytes:
        return bytes([self.suit.value, self.value, int(self.faceup)])
    def from_bytes(data: bytes) -> Self:
        return Card(Suit._value2member_map_[data[0]], data[1], bool(data[2]))
    def from_name(name: str) -> Self:
        sval = "-hdcs".index(name[1].lower())
        if sval < 1:
            return None
        vval = CardSymbols.index(name[0].upper())
        if vval < 2:
            return None
        return Card(Suit._value2member_map_[sval], vval)
    @property
    def kind(self) -> bool:
        return SuitKinds[self.suit.value]
    def as_faceup(self) -> Self:
        c = Card(self.suit, self.value, True)
        c.selected = self.selected
        return c
    def __eq__(self, other: Self) -> bool:
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.value == other.value
    def __str__(self) -> str:
        if not self.faceup:
            return f"{SelectedColor if self.selected else ''}@@{CardColors[Suit.Inv.value]}"
        return f"{SelectedColor if self.selected else CardColors[self.suit.value]}{CardSymbols[self.value]}{SuitSymbols[self.suit.value]}{CardColors[Suit.Inv.value]}"
    def __repr__(self) -> str:
        return str(self)


type StackData = tuple[Card]
type MoveData = int
type PosData = tuple[int, int]
type Delta[T] = tuple[T, T]

class Deltas:
    def __init__(self, t: dict[str, Delta] | None) -> None:
        self.tracks: dict[str, Delta] = t or {}
    def track(self, trackname: str, initval: Any) -> None:
        self.tracks[trackname] = (initval, initval)
    def recDelta(self, trackname: str, newval: Any) -> None:
        self.tracks[trackname] = (self.tracks[trackname][0], newval)
    def changes(self) -> list[tuple[str, Delta]]:
        """returns a list of all entries that were changed"""
        return [tuple(item) for item in self.tracks.items() if item[1][1] != item[1][0]]
    def commit(self) -> None:
        for k in self.tracks.keys():
            self.tracks[k] = (self.tracks[k][1], None)
    def __getitem__(self, name: str) -> Delta:
        return self.tracks[name]
    def __setitem__(self, name: str, val: Any) -> None:
        self.recDelta(name, val)

class CardStack:
    def __init__(self) -> None:
        self.stack: list[Card] = []
    def addCard(self, card: Card) -> None:
        self.stack.append(card)

class Deck:
    def __init__(self, multiple: int = None) -> None:
        """creates a new deck with random card order

        multiple is used to define how many cards get pulled at a time, defaults to the difficulties specification"""
        self.cards = [Card(s, v) for v in range(2,15) for s in (Suit.Hea,Suit.Dia,Suit.Clu,Suit.Spa)]
        shuffle(self.cards)
        self.multiple = multiple if multiple is not None else DiffSetting.value
    def deal(self) -> Card:
        """returns one card"""
        return self.cards.pop()
    def draw(self) -> list[Card]:
        """returns cards equal to the multiple, in display order"""
        return [self.cards.pop() for _ in range(min(len(self.cards), self.multiple))]

type Location = tuple[int, int]
NOSEL: Location = [-1, -1]

class TrackedLoc:
    def __init__(self, tracker: Deltas, trackname: str, val: Location = None) -> None:
        self.intern = val if val else [0,0]
        self.tracker = tracker
        self.trackname = trackname
        self.tracker.track(trackname, tuple(val))
    def __getitem__(self, i: int) -> int:
        return self.intern[i]
    def __setitem__(self, i: int, v: int) -> None:
        self.intern[i] = v
        self.tracker.recDelta(self.trackname, tuple(self.intern))
    def __iter__(self):
        return iter(self.intern)
    def __eq__(self, other):
        return self.intern == other
    def copy(self):
        return self.intern.copy()
    def setTo(self, val):
        self.intern = val
        self.tracker.recDelta(self.trackname, tuple(val))

class PlayArea:
    def __init__(self) -> None:
        # self.deltas = Deltas(dict([("moves",0),("deckempty",False),("pileitem",None)]+[(f"stack{i}",()) for i in range(STACK_COUNT)]))
        # self._selloc = TrackedLoc(self.deltas, "selloc", NOSEL)
        # self._cpos = TrackedLoc(self.deltas, "cpos", [1,0])
        # self._moves = 0
        self.selloc: Location = NOSEL
        self.cpos: Location = [1,0]
        self.moves = 0
        self.deck = Deck()
        self.pile: list[Card] = []
        self.aces = [CardStack() for _ in range(4)]
        self.stacks = [CardStack() for _ in range(STACK_COUNT)]
        for i in range(STACK_COUNT):
            for _ in range(i+1):
                self.stacks[i].addCard(self.deck.deal())
            self.stacks[i].stack[-1].faceup = True
    # @property
    # def moves(self) -> int:
    #     return self._moves
    # @moves.setter
    # def moves(self, val: int) -> None:
    #     self._moves = val
    #     self.deltas.recDelta("moves", val)
    # @property
    # def selloc(self) -> Location:
    #     return self._selloc
    # @selloc.setter
    # def selloc(self, val: Location) -> None:
    #     self._selloc.setTo(val)
    # @property
    # def cpos(self) -> Location:
    #     return self._cpos
    # @cpos.setter
    # def cpos(self, val: Location) -> None:
    #     self._cpos.setTo(val)
    @property
    def lengths(self) -> list[int]:
        return [len(s.stack) for s in self.stacks]+[int(len(self.pile)>0)]
    @default(None)
    def getCard(self, l: Location) -> Card:
        if l[0] < 0:
            return self.aces[-(l[0]+1)].stack[-1]
        if l[0] == 0:
            return self.pile[-1]
        return self.stacks[l[0]-1].stack[l[1]]
    def checkMove(self, s: Location, d: Location) -> bool:
        cs = self.getCard(s)
        cd = self.getCard(d)
        if d[0] < 0:
            if cs.suit.value != -d[0]:
                return False
            if cd == None:
                return cs.value == 14
            if cd.value == 14 and cs.value == 2:
                return True
            if cs.value != cd.value + 1:
                return False
            return True
        if d[0] == 0:
            return False
        if d[1] < max(0, len(self.stacks[d[0]-1].stack)-1):
            return False
        if cd == None:
            return cs.value == 13
        if cs.kind == cd.kind:
            return False
        if cs.value == 14:
            return cd.value == 2
        if cs.value != (cd.value-1):
            return False
        return True
    def select(self, force: bool = False) -> None:
        if self.cpos[0] == 0:
            if self.cpos[1] != 0:
                if self.selloc == NOSEL:
                    self.selloc = self.cpos.copy()
                else:
                    self.selloc = NOSEL
            else:
                if len(self.deck.cards) == 0:
                    self.deck.cards = self.pile
                    self.deck.cards.reverse()
                    self.pile = []
                else:
                    self.pile.extend(self.deck.draw())
                    self.moves += 1
            return
        if self.selloc != NOSEL:
            if self.cpos == self.selloc:
                self.selloc = NOSEL
            elif self.cpos[1] == max(0, len(self.stacks[self.cpos[0]-1].stack)-1) or self.cpos[0] < 0:
                if force or self.checkMove(self.selloc, self.cpos):
                    self.moves += 1
                    if self.cpos[0] < 0:
                        st = self.aces[-(self.cpos[0]+1)]
                        if self.selloc[0] == 0:
                            st.stack.append(self.pile.pop().as_faceup())
                        else:
                            st.stack.append(self.stacks[self.selloc[0]-1].stack.pop())
                            if len(self.stacks[self.selloc[0]-1].stack):
                                self.stacks[self.selloc[0]-1].stack[-1].faceup = True
                    else:
                        if self.selloc[0] == 0:
                            self.stacks[self.cpos[0]-1].stack.append(self.pile.pop().as_faceup())
                        else:
                            self.stacks[self.cpos[0]-1].stack.extend(self.stacks[self.selloc[0]-1].stack[self.selloc[1]:])
                            self.stacks[self.selloc[0]-1].stack = self.stacks[self.selloc[0]-1].stack[:self.selloc[1]]
                            if len(self.stacks[self.selloc[0]-1].stack):
                                self.stacks[self.selloc[0]-1].stack[-1].faceup = True
                    self.selloc = NOSEL
        else:
            if self.getCard(self.cpos) == None:
                return
            self.selloc = self.cpos.copy()
    def locate(self, card: Card) -> Location:
        for i in range(len(self.aces)):
            s = self.aces[i]
            if len(s.stack):
                if s.stack[-1] == card:
                    return [-(i+1), 0]
        if len(self.pile):
            if self.pile[-1] == card:
                return [0, 1]
        for i in range(len(self.stacks)):
            s = self.stacks[i]
            for j in range(len(s.stack)):
                if s.stack[j].faceup and s.stack[j] == card:
                    return [i+1, j]
        return NOSEL
    def flip(self) -> None:
        c = self.getCard(self.cpos)
        if c:
            c.faceup = not c.faceup
    def flipall(self, onlyup: bool) -> None:
        def flip(c: Card):
            c.faceup = onlyup or not c.faceup
        for s in self.stacks:
            for c in s.stack:
                flip(c)
    def save(self) -> bytes:
        b: list[int] = []
        b.extend(self.moves.to_bytes(2))
        b.extend(self.deck.multiple.to_bytes(1))
        b.extend(len(self.pile).to_bytes(1))
        for i in range(len(self.pile)):
            b.extend(self.pile[i].to_bytes())
        b.extend(len(self.deck.cards).to_bytes(1))
        for i in range(len(self.deck.cards)):
            b.extend(self.deck.cards[i].to_bytes())
        b.extend(len(self.stacks).to_bytes(1))
        for s in self.stacks:
            b.extend(len(s.stack).to_bytes(1))
            for i in range(len(s.stack)):
                b.extend(s.stack[i].to_bytes())
        for s in self.aces:
            b.extend(len(s.stack).to_bytes(1))
            for i in range(len(s.stack)):
                b.extend(s.stack[i].to_bytes())
        return bytes(b)
    def load(data: bytes) -> Self:
        a = PlayArea()
        a.moves = int.from_bytes(data[:2])
        a.deck.multiple = data[2]
        dp: int = 4
        for _ in range(data[3]):
            a.pile.append(Card.from_bytes(data[dp:dp+3]))
            dp += 3
        a.deck.cards.clear()
        dp += 1
        for _ in range(data[dp-1]):
            a.deck.cards.append(Card.from_bytes(data[dp:dp+3]))
            dp += 3
        dp += 1
        a.stacks = [CardStack() for _ in range(data[dp-1])]
        for i in range(data[dp-1]):
            dp += 1
            for _ in range(data[dp-1]):
                a.stacks[i].addCard(Card.from_bytes(data[dp:dp+3]))
                dp += 3
        for s in a.aces:
            l = data[dp]
            dp += 1
            for _ in range(l):
                s.addCard(Card.from_bytes(data[dp:dp+3]))
                dp += 3
        return a
