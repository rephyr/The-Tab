"""
LivePrinter listens to game events and prints receipts in real time as the game progresses,
rather than printing everything at the end.

Register it with: log.on(LivePrinter(printer).hook)
"""
from core.events import DrinkEvent, GiveEvent, GuessEvent, PhaseEvent, BoardCardEvent, BoardCardDoneEvent, GameEndEvent, TaskDrawEvent, RouletteResultEvent, RaceStartEvent, RaceRoundEvent, HorseEventFiredEvent, RaceFinishedEvent, TiebreakStartEvent, TiebreakEliminationEvent, TiebreakWinnerEvent
from printing.formatter import formatTurn, formatHand, formatBoardCard, formatTally, formatTaskDraw, formatRouletteResult
from printing.receipts.taskGame import formatReceipt as formatTaskGameReceipt
from printing.receipts.buja import formatReceipt as formatBujaReceipt
from printing.receipts.ravit import formatBettingSlip, formatRaceRound, formatHorseEvent, formatRavitFinal, formatTiebreakStart, formatTiebreakElimination, formatTiebreakWinner


class LivePrinter:
    """Reacts to game events and prints each receipt the moment it's ready."""
    def __init__(self, printer, gameTitle=""):
        self._printer = printer
        self._gameTitle = gameTitle
        self._inBoard = False
        self._boardCardCount = 0
        self._printedBoardCards = set()
        self._turnPrinted = False
        self._ravitHorses = []
        self._ravitBets = []
        self._ravitFinalPositions = []

    def hook(self, event, log):
        """Called by GameLog after every event. Decides what to print based on event type."""
        if isinstance(event, PhaseEvent) and event.player == "":
            self._inBoard = True
            data = log.toDict()
            for player, cards in data["hands"].items():
                self._printer.printWith(lambda p, pl=player, c=cards: formatHand(pl, c, p))

        elif isinstance(event, PhaseEvent) and not self._inBoard:
            self._turnPrinted = False

        elif isinstance(event, GuessEvent) and not self._inBoard and event.correct is True:
            data = log.toDict()
            lastPhase = data["phases"][-1]
            lastTurn = lastPhase["turns"][-1]
            self._printer.printWith(
                lambda p, ph=lastPhase["name"], t=lastTurn: formatTurn(ph, t, p)
            )
            self._turnPrinted = True

        elif isinstance(event, (DrinkEvent, GiveEvent)) and not self._inBoard and not self._turnPrinted:
            data = log.toDict()
            if not data["phases"]:
                return
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

        elif isinstance(event, RaceStartEvent):
            self._ravitHorses = event.horses
            self._ravitBets = event.bets
            self._printer.printWith(
                lambda p, h=event.horses, b=event.bets: formatBettingSlip(h, b, p)
            )

        elif isinstance(event, RaceRoundEvent):
            self._printer.printWith(lambda p, e=event: formatRaceRound(e, p))

        elif isinstance(event, HorseEventFiredEvent):
            if event.eventType in ("death", "backwards"):
                self._printer.printWith(lambda p, e=event: formatHorseEvent(e, p))

        elif isinstance(event, RaceFinishedEvent):
            self._ravitFinalPositions = event.finalPositions

        elif isinstance(event, TiebreakStartEvent):
            self._printer.printWith(lambda p, e=event: formatTiebreakStart(e, p))

        elif isinstance(event, TiebreakEliminationEvent):
            self._printer.printWith(lambda p, e=event: formatTiebreakElimination(e, p))

        elif isinstance(event, TiebreakWinnerEvent):
            self._printer.printWith(lambda p, e=event: formatTiebreakWinner(e, p))

        elif isinstance(event, GameEndEvent):
            data = log.toDict()
            if self._gameTitle == "TaskGame":
                self._printer.printWith(lambda p, d=data: formatTaskGameReceipt(d, p))
            elif self._gameTitle == "Buja":
                self._printer.printWith(lambda p, d=data: formatBujaReceipt(d, p))
            elif self._gameTitle == "Ravit":
                ravitData = {
                    "players": data["players"],
                    "timestamp": data["timestamp"],
                    "horses": self._ravitHorses,
                    "bets": self._ravitBets,
                    "finalPositions": self._ravitFinalPositions,
                    "scores": data["scores"],
                }
                self._printer.printWith(lambda p, d=ravitData: formatRavitFinal(d, p))
            else:
                if data["board"]:
                    lastIdx = len(data["board"]) - 1
                    if lastIdx not in self._printedBoardCards:
                        last = data["board"][lastIdx]
                        self._printer.printWith(lambda p, c=last: formatBoardCard(c, p))
                self._printer.printWith(lambda p, s=data["scores"]: formatTally(s, p))
            self._printer.close()
