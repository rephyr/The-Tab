"""
LivePrinter listens to game events and prints receipts in real time as the game progresses,
rather than printing everything at the end.

Register it with: log.on(LivePrinter(printer).hook)
"""
from core.events import DrinkEvent, GiveEvent, PhaseEvent, BoardCardEvent, GameEndEvent, TaskDrawEvent, RouletteResultEvent
from printing.formatter import formatTurn, formatHand, formatBoardCard, formatTally, formatTaskDraw, formatRouletteResult


class LivePrinter:
    """Reacts to game events and prints each receipt the moment it's ready."""
    def __init__(self, printer):
        self._printer = printer
        self._inBoard = False
        self._boardCardCount = 0

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
            if self._boardCardCount > 0:
                prev = data["board"][self._boardCardCount - 1]
                self._printer.printWith(lambda p, c=prev: formatBoardCard(c, p))
            self._boardCardCount += 1

        elif isinstance(event, TaskDrawEvent):
            self._printer.printWith(lambda p, e=event: formatTaskDraw(e, p))

        elif isinstance(event, RouletteResultEvent):
            self._printer.printWith(lambda p, e=event: formatRouletteResult(e, p))

        elif isinstance(event, GameEndEvent):
            data = log.toDict()
            if data["board"]:
                last = data["board"][-1]
                self._printer.printWith(lambda p, c=last: formatBoardCard(c, p))
            self._printer.printWith(lambda p, s=data["scores"]: formatTally(s, p))
            self._printer.close()
