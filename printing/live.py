"""
LivePrinter listens to game events and prints receipts in real time as the game progresses,
rather than printing everything at the end.

Register it with: log.on(LivePrinter(printer).hook)
"""
from core.events import DrinkEvent, GiveEvent, PhaseEvent, BoardCardEvent, BoardCardDoneEvent, GameEndEvent, TaskDrawEvent, RouletteResultEvent
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
            self._boardCardCount += 1

        elif isinstance(event, BoardCardDoneEvent):
            data = log.toDict()
            idx = self._boardCardCount - 1
            if idx >= 0 and idx < len(data["board"]):
                card = data["board"][idx]
                self._printer.printWith(lambda p, c=card: formatBoardCard(c, p))
                self._printedBoardCards.add(idx)

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
