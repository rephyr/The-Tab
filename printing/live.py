"""
LivePrinter listens to game events and prints receipts in real time as the game progresses,
rather than printing everything at the end.

Register it with: log.on(LivePrinter(printer).hook)
"""
from core.events import DrinkEvent, GiveEvent, PhaseEvent, BoardCardEvent, GameEndEvent, TaskDrawEvent, RouletteResultEvent
from printing.formatter import formatTurn, formatHand, formatBoardCard, formatTally, formatTaskDraw, formatRouletteResult
from printing.receipts.taskGame import formatReceipt as formatTaskGameReceipt
from printing.receipts.buja import formatReceipt as formatBujaReceipt


class LivePrinter:
    """Reacts to game events and prints each receipt the moment it's ready."""
    def __init__(self, printer, gameTitle=""):
        self._printer = printer
        self._gameTitle = gameTitle
        self._inBoard = False
        self._boardCardCount = 0
        self._printedBoardCards = set()

    def hook(self, event, log):
        """Called by GameLog after every event. Decides what to print based on event type."""
        if isinstance(event, PhaseEvent) and event.player == "":
            self._inBoard = True
            data = log.toDict()
            for player, cards in data["hands"].items():
                self._printer.printWith(lambda p, pl=player, c=cards: formatHand(pl, c, p))

        elif isinstance(event, (DrinkEvent, GiveEvent)) and not self._inBoard:
            data = log.toDict()
            lastPhase = data["phases"][-1]
            lastTurn = lastPhase["turns"][-1]
            self._printer.printWith(
                lambda p, ph=lastPhase["name"], t=lastTurn: formatTurn(ph, t, p)
            )

        elif isinstance(event, BoardCardEvent) and self._inBoard:
            data = log.toDict()
            currentIdx = self._boardCardCount
            if currentIdx > 0 and (currentIdx - 1) not in self._printedBoardCards:
                prev = data["board"][currentIdx - 1]
                self._printer.printWith(lambda p, c=prev: formatBoardCard(c, p))
                self._printedBoardCards.add(currentIdx - 1)
            current = data["board"][currentIdx]
            if not current["matched"]:
                self._printer.printWith(lambda p, c=current: formatBoardCard(c, p))
                self._printedBoardCards.add(currentIdx)
            self._boardCardCount += 1

        elif isinstance(event, TaskDrawEvent):
            self._printer.printWith(lambda p, e=event: formatTaskDraw(e, p))

        elif isinstance(event, RouletteResultEvent):
            self._printer.printWith(lambda p, e=event: formatRouletteResult(e, p))

        elif isinstance(event, GameEndEvent):
            data = log.toDict()
            if self._gameTitle == "TaskGame":
                self._printer.printWith(lambda p, d=data: formatTaskGameReceipt(d, p))
            elif self._gameTitle == "Buja":
                self._printer.printWith(lambda p, d=data: formatBujaReceipt(d, p))
            else:
                if data["board"]:
                    lastIdx = len(data["board"]) - 1
                    if lastIdx not in self._printedBoardCards:
                        last = data["board"][lastIdx]
                        self._printer.printWith(lambda p, c=last: formatBoardCard(c, p))
                self._printer.printWith(lambda p, s=data["scores"]: formatTally(s, p))
            self._printer.close()
