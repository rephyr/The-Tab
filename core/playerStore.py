"""
PlayerStore persists all-time player stats and session history to a JSON file.

Register its hook with GameLog to automatically save after each game:
    store = PlayerStore(gameTitle="Buja")
    log.on(store.hook)
"""
import json
from pathlib import Path
from datetime import datetime
from core.events import GameEndEvent


class PlayerStore:
    """Loads and saves player stats and session history from a JSON file."""

    def __init__(self, path="players.json", gameTitle="Unknown"):
        self.path = Path(path)
        self.gameTitle = gameTitle
        self.data = self._load()

    def _load(self):
        """Read the store file, or return an empty structure if it does not exist."""
        if not self.path.exists():
            return {"players": {}, "sessions": []}
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save(self):
        """Write current data back to the store file."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def hook(self, event, log):
        """GameLog callback updates player totals and appends a session on GameEndEvent."""
        if not isinstance(event, GameEndEvent):
            return

        for score in event.scores:
            name = score["name"]
            if name not in self.data["players"]:
                self.data["players"][name] = {
                    "gamesPlayed": 0,
                    "totalDrinksTaken": 0,
                    "totalDrinksGiven": 0,
                }
            p = self.data["players"][name]
            p["gamesPlayed"] += 1
            p["totalDrinksTaken"] += score["drinksTaken"]
            p["totalDrinksGiven"] += score["drinksToGive"]

        self.data["sessions"].append({
            "id": datetime.now().isoformat(timespec="seconds"),
            "game": self.gameTitle,
            "timestamp": event.timestamp.strftime("%Y-%m-%d %H:%M"),
            "scores": [
                {
                    "name": s["name"],
                    "drinksTaken": s["drinksTaken"],
                    "drinksGiven": s["drinksToGive"],
                }
                for s in event.scores
            ],
        })

        self._save()

    def getLeaderboard(self):
        """Return all players sorted by total drinks taken, descending."""
        return sorted(
            [{"name": name, **stats} for name, stats in self.data["players"].items()],
            key=lambda p: p["totalDrinksTaken"],
            reverse=True,
        )

    def getSessions(self):
        """Return the full list of stored game sessions."""
        return self.data.get("sessions", [])

    def deletePlayer(self, name):
        """Remove a player by name. Returns True if found and deleted, False otherwise."""
        if name in self.data["players"]:
            del self.data["players"][name]
            self._save()
            return True
        return False

    def deleteSession(self, index):
        """Remove a session by its list index. Returns True if valid, False otherwise."""
        sessions = self.data.get("sessions", [])
        if 0 <= index < len(sessions):
            sessions.pop(index)
            self._save()
            return True
        return False
