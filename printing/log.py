"""
GameLog collects events emitted during a game and converts them to a
structured dict that the formatter can use to print receipts.
"""
from core.events import (
    GameStartEvent, PhaseEvent, GuessEvent,
    DrinkEvent, GiveEvent, ShareEvent,
    BoardCardEvent, GameEndEvent,
)

class GameLog:
    """Collects game events and can convert them to a dict for printing."""
    def __init__(self):
        self.events = []
        self._callbacks = []

    def on(self, callback) -> None:
        """Register a callback(event, log) called after every event is added."""
        self._callbacks.append(callback)

    def add(self, event) -> None:
        self.events.append(event)
        for cb in self._callbacks:
            cb(event, self)

    def clear(self) -> None:
        self.events = []

    def toDict(self) -> dict:
        """
        Convert the event log to a dict with keys:
        players, timestamp, phases, board, hands, scores.
        """
        result = {
            "players": [],
            "timestamp": "",
            "phases": [],
            "board": [],
            "scores": [],
        }

        currentPhaseName = None
        currentTurn = None
        inBoard = False
        playerHands = {}

        for event in self.events:
            if isinstance(event, GameStartEvent):
                result["players"] = event.players
                result["timestamp"] = event.timestamp.strftime("%Y-%m-%d %H:%M")
                playerHands = {name: [] for name in event.players}

            elif isinstance(event, PhaseEvent):
                if event.player == "":
                    inBoard = True
                    currentTurn = None
                else:
                    inBoard = False
                    if event.phase != currentPhaseName:
                        currentPhaseName = event.phase
                        result["phases"].append({"name": event.phase, "turns": []})

                    currentTurn = {
                        "player": event.player,
                        "guess": None,
                        "card": None,
                        "correct": None,
                        "gaveTo": None,
                        "drinks": 0,
                        "note": None,
                        "handBefore": list(playerHands.get(event.player, [])),
                    }
                    result["phases"][-1]["turns"].append(currentTurn)

            elif isinstance(event, GuessEvent):
                if currentTurn is not None:
                    currentTurn["guess"] = event.guess
                    currentTurn["card"] = event.card
                    currentTurn["correct"] = event.correct
                    if event.card is not None and event.player in playerHands:
                        playerHands[event.player].append(event.card)

            elif isinstance(event, DrinkEvent):
                if inBoard and result["board"]:
                    result["board"][-1]["outcomes"].append({
                        "player": event.player,
                        "type": "drink",
                        "drinks": event.amount,
                    })
                elif currentTurn is not None:
                    currentTurn["drinks"] = event.amount
                    if event.reason != "wrong guess":
                        currentTurn["note"] = event.reason

            elif isinstance(event, GiveEvent):
                if inBoard and result["board"]:
                    result["board"][-1]["outcomes"].append({
                        "giver": event.giver,
                        "receiver": event.receiver,
                        "type": "give",
                        "drinks": event.amount,
                    })
                elif currentTurn is not None:
                    currentTurn["gaveTo"] = event.receiver
                    currentTurn["drinks"] = event.amount

            elif isinstance(event, ShareEvent):
                if inBoard and result["board"]:
                    result["board"][-1]["outcomes"].append({
                        "player1": event.player1,
                        "player2": event.player2,
                        "type": "share",
                        "drinks": event.amount,
                    })

            elif isinstance(event, BoardCardEvent):
                result["board"].append({
                    "card": event.card,
                    "action": event.action,
                    "drinks": event.drinks,
                    "matched": event.matched,
                    "outcomes": [],
                })

            elif isinstance(event, GameEndEvent):
                result["scores"] = [
                    {
                        "name": s["name"],
                        "drank": s["drinksTaken"],
                        "gave": s["drinksToGive"],
                    }
                    for s in event.scores
                ]

        result["hands"] = playerHands

        return result
