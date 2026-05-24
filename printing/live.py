"""
LivePrinter listens to game events and prints receipts in real time as the game progresses.

Register it with: log.on(LivePrinter(printer).hook)
"""
from core.events import DrinkEvent, GiveEvent, GuessEvent, PhaseEvent, BoardCardEvent, BoardCardDoneEvent, GameEndEvent, TaskDrawEvent, TaskDrinkSummaryEvent, TaskChainStartEvent, RouletteResultEvent, RaceStartEvent, BetsPlacedEvent, RaceRoundEvent, HorseEventFiredEvent, RaceFinishedEvent, TiebreakStartEvent, TiebreakRoundEvent, TiebreakEliminationEvent, TiebreakWinnerEvent, RavitBettorDrinkEvent
from printing.receipts.bujaFormatter import formatTurn, formatHand, formatBoardCard, formatBoardCardReveal, formatBoardCardOutcome, formatTally, formatRouletteResult, configure as _configureBujaFormatter
from printing.receipts.taskGameFormatter import formatTaskDraw, formatDrinkSummary, formatChainDraw, formatTally as formatTaskTally, configure as _configureTaskGameFormatter
from printing.receipts.ravitFormatter import formatHorseList, formatBettingReceipt, formatJockeyList, formatRaceRound, formatHorseEvent, formatRavitFinal, formatTiebreakStart, formatTiebreakRound, formatTiebreakElimination, formatTiebreakWinner, formatBettorDrink, configure as _configureRavitFormatter
from games.diceGame.diceEvents import MexicanChallengeEvent, MexicanAcceptEvent
from printing.receipts.diceFormatter import formatChallenge as _formatMexicoChallenge, formatAccept as _formatMexicoAccept, formatTally as _formatMexicoTally, configure as _configureDiceFormatter


class LivePrinter:
    """Reacts to game events and prints each receipt the moment it's ready."""
    def __init__(self, printer, gameTitle=""):
        self._printer = printer
        self._gameTitle = gameTitle
        printerConfig = getattr(printer, "config", {})
        _configureBujaFormatter(printerConfig)
        _configureTaskGameFormatter(printerConfig)
        _configureRavitFormatter(printerConfig)
        _configureDiceFormatter(printerConfig)
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
            reveal = {"card": event.card, "action": event.action, "drinks": event.drinks, "matched": event.matched}
            self._printer.printWith(lambda p, r=reveal: formatBoardCardReveal(r, p))

        elif isinstance(event, BoardCardDoneEvent):
            data = log.toDict()
            idx = self._boardCardCount - 1
            if idx >= 0 and idx < len(data["board"]):
                card = data["board"][idx]
                if card["outcomes"]:
                    self._printer.printWith(lambda p, c=card: formatBoardCardOutcome(c, p))
                self._printedBoardCards.add(idx)

        elif isinstance(event, TaskDrawEvent):
            self._printer.printWith(lambda p, e=event: formatTaskDraw(e, p))

        elif isinstance(event, TaskChainStartEvent):
            self._printer.printWith(lambda p, e=event: formatChainDraw(e, p))

        elif isinstance(event, TaskDrinkSummaryEvent):
            self._printer.printWith(lambda p, e=event: formatDrinkSummary(e, p))

        elif isinstance(event, RouletteResultEvent):
            self._printer.printWith(lambda p, e=event: formatRouletteResult(e, p))

        elif isinstance(event, RaceStartEvent):
            self._ravitHorses = event.horses
            self._printer.printWith(lambda p, h=event.horses: formatHorseList(h, p))

        elif isinstance(event, BetsPlacedEvent):
            self._ravitBets = event.bets
            if event.jockeys:
                self._printer.printWith(lambda p, j=event.jockeys: formatJockeyList(j, p))
            self._printer.printWith(lambda p, h=event.horses, b=event.bets: formatBettingReceipt(h, b, p))

        elif isinstance(event, RaceRoundEvent):
            self._printer.printWith(lambda p, e=event: formatRaceRound(e, p))

        elif isinstance(event, HorseEventFiredEvent):
            if event.eventType in ("death", "backwards", "lightning", "lightningDeath", "fightDeath"):
                self._printer.printWith(lambda p, e=event: formatHorseEvent(e, p))

        elif isinstance(event, RavitBettorDrinkEvent):
            self._printer.printWith(lambda p, e=event: formatBettorDrink(e, p))

        elif isinstance(event, RaceFinishedEvent):
            self._ravitFinalPositions = event.finalPositions

        elif isinstance(event, TiebreakStartEvent):
            self._printer.printWith(lambda p, e=event: formatTiebreakStart(e, p))

        elif isinstance(event, TiebreakRoundEvent):
            self._printer.printWith(lambda p, e=event: formatTiebreakRound(e, p))

        elif isinstance(event, TiebreakEliminationEvent):
            if len(event.combatants) > 2:
                self._printer.printWith(lambda p, e=event: formatTiebreakElimination(e, p))

        elif isinstance(event, TiebreakWinnerEvent):
            self._printer.printWith(lambda p, e=event: formatTiebreakWinner(e, p))

        elif isinstance(event, MexicanAcceptEvent):
            self._printer.printWith(lambda p, e=event: _formatMexicoAccept(e, p))

        elif isinstance(event, MexicanChallengeEvent):
            self._printer.printWith(lambda p, e=event: _formatMexicoChallenge(e, p))

        elif isinstance(event, GameEndEvent):
            data = log.toDict()
            if self._gameTitle == "Mexico":
                self._printer.printWith(lambda p, s=data["scores"]: _formatMexicoTally(s, p))
            elif self._gameTitle == "TaskGame":
                self._printer.printWith(lambda p, s=data["scores"]: formatTaskTally(s, p))
            elif self._gameTitle == "Buja":
                self._printer.printWith(lambda p, s=data["scores"]: formatTally(s, p))
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
