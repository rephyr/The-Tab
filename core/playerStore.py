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
        """Read the store file, or return an empty structure if it does not exist or is invalid."""
        if not self.path.exists():
            return {"players": {}, "sessions": []}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return {"players": {}, "sessions": []}

    def _resolvePlayerKey(self, name: str) -> str:
        """Return the existing key that matches name case-insensitively, or title-cased name."""
        lower = name.strip().lower()
        for key in self.data["players"]:
            if key.lower() == lower:
                return key
        return name.strip().title()

    def _save(self):
        """Write current data back to the store file."""
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

    def hook(self, event, log):
        """GameLog callback updates player totals and appends a session on GameEndEvent."""
        if not isinstance(event, GameEndEvent):
            return

        for score in event.scores:
            name = self._resolvePlayerKey(score["name"])
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
                    "name": self._resolvePlayerKey(s["name"]),
                    "drinksTaken": s["drinksTaken"],
                    "drinksGiven": s["drinksToGive"],
                }
                for s in event.scores
            ],
        })

        self._save()

    def getLeaderboard(self):
        """Return all players sorted by total drinks taken, descending.

        Players with a stored entry use their accumulated stats. Players who
        appear only in session history have their stats calculated from sessions.
        """
        result = {name: dict(stats) for name, stats in self.data["players"].items()}

        for session in self.data.get("sessions", []):
            for score in session["scores"]:
                name = score["name"]
                if name not in result:
                    result[name] = {"gamesPlayed": 0, "totalDrinksTaken": 0, "totalDrinksGiven": 0}
                    for s in self.data["sessions"]:
                        for sc in s["scores"]:
                            if sc["name"] == name:
                                result[name]["gamesPlayed"] += 1
                                result[name]["totalDrinksTaken"] += sc["drinksTaken"]
                                result[name]["totalDrinksGiven"] += sc.get("drinksGiven", 0)

        return sorted(
            [{"name": name, **stats} for name, stats in result.items()],
            key=lambda p: p["totalDrinksTaken"],
            reverse=True,
        )

    def getSessions(self):
        """Return the full list of stored game sessions."""
        return self.data.get("sessions", [])

    def deletePlayer(self, name):
        """Remove a player entry by name. Returns True if found and deleted, False otherwise."""
        if name not in self.data["players"]:
            return False
        del self.data["players"][name]
        self._save()
        return True

    def getRegisteredPlayerNames(self):
        """Return names of players with a stats entry (excludes session-only players)."""
        return sorted(self.data["players"].keys())

    def getAllPlayerNames(self):
        """Return all unique player names from both the players dict and session history."""
        names = set(self.data["players"].keys())
        for session in self.data.get("sessions", []):
            for score in session["scores"]:
                names.add(score["name"])
        return sorted(names)

    def deleteSession(self, index):
        """Remove a session by its list index. Returns True if valid, False otherwise."""
        sessions = self.data.get("sessions", [])
        if 0 <= index < len(sessions):
            sessions.pop(index)
            self._save()
            return True
        return False
