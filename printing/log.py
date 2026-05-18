from core.events import (
    GameStartEvent, PhaseEvent, GuessEvent,
    DrinkEvent, GiveEvent, ShareEvent,
    BoardCardEvent, GameEndEvent,
)

class GameLog:
    def __init__(self):
        self.events = []
        self._callbacks = []

    def on(self, callback) -> None:
        self._callbacks.append(callback)

    def add(self, event) -> None:
        self.events.append(event)
        for cb in self._callbacks:
            cb(event, self)

    def clear(self) -> None:
        self.events = []

    def toDict(self) -> dict:
        result = {
            "players": [],
            "timestamp": "",
            "phases": [],
            "board": [],
            "scores": [],
        }

        current_phase_name = None
        current_turn = None
        in_board = False
        player_hands = {}

        for event in self.events:
            if isinstance(event, GameStartEvent):
                result["players"] = event.players
                result["timestamp"] = event.timestamp.strftime("%Y-%m-%d %H:%M")
                player_hands = {name: [] for name in event.players}

            elif isinstance(event, PhaseEvent):
                if event.player == "":
                    in_board = True
                    current_turn = None
                else:
                    in_board = False
                    if event.phase != current_phase_name:
                        current_phase_name = event.phase
                        result["phases"].append({"name": event.phase, "turns": []})

                    current_turn = {
                        "player": event.player,
                        "guess": None,
                        "card": None,
                        "correct": None,
                        "gave_to": None,
                        "drinks": 0,
                        "note": None,
                        "hand_before": list(player_hands.get(event.player, [])),
                    }
                    result["phases"][-1]["turns"].append(current_turn)

            elif isinstance(event, GuessEvent):
                if current_turn is not None:
                    current_turn["guess"] = event.guess
                    current_turn["card"] = event.card
                    current_turn["correct"] = event.correct
                    if event.card is not None and event.player in player_hands:
                        player_hands[event.player].append(event.card)

            elif isinstance(event, DrinkEvent):
                if in_board and result["board"]:
                    result["board"][-1]["outcomes"].append({
                        "player": event.player,
                        "type": "drink",
                        "drinks": event.amount,
                    })
                elif current_turn is not None:
                    current_turn["drinks"] = event.amount
                    if event.reason != "wrong guess":
                        current_turn["note"] = event.reason

            elif isinstance(event, GiveEvent):
                if in_board and result["board"]:
                    result["board"][-1]["outcomes"].append({
                        "giver": event.giver,
                        "receiver": event.receiver,
                        "type": "give",
                        "drinks": event.amount,
                    })
                elif current_turn is not None:
                    current_turn["gave_to"] = event.receiver
                    current_turn["drinks"] = event.amount

            elif isinstance(event, ShareEvent):
                if in_board and result["board"]:
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

        result["hands"] = player_hands

        return result
