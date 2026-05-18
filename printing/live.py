from core.events import DrinkEvent, GiveEvent, PhaseEvent, BoardCardEvent, GameEndEvent
from printing.formatter import formatTurn, formatHand, formatBoardCard, formatTally


class LivePrinter:
    def __init__(self, printer):
        self._printer = printer
        self._in_board = False
        self._board_card_count = 0

    def hook(self, event, log):
        if isinstance(event, PhaseEvent) and event.player == "":
            self._in_board = True
            data = log.toDict()
            for player, cards in data["hands"].items():
                self._printer.printWith(lambda p, pl=player, c=cards: formatHand(pl, c, p))

        elif isinstance(event, (DrinkEvent, GiveEvent)) and not self._in_board:
            data = log.toDict()
            last_phase = data["phases"][-1]
            last_turn = last_phase["turns"][-1]
            self._printer.printWith(
                lambda p, ph=last_phase["name"], t=last_turn: formatTurn(ph, t, p)
            )

        elif isinstance(event, BoardCardEvent) and self._in_board:
            data = log.toDict()
            if self._board_card_count > 0:
                prev = data["board"][self._board_card_count - 1]
                self._printer.printWith(lambda p, c=prev: formatBoardCard(c, p))
            self._board_card_count += 1

        elif isinstance(event, GameEndEvent):
            data = log.toDict()
            if data["board"]:
                last = data["board"][-1]
                self._printer.printWith(lambda p, c=last: formatBoardCard(c, p))
            self._printer.printWith(lambda p, s=data["scores"]: formatTally(s, p))
            self._printer.close()
