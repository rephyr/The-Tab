"""
Base class for all games. Handles players, event emitting, and defines the playRound interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from .player import Player
from core.events import GiveEvent

@dataclass
class Game(ABC):
    """Abstract base for a game. Subclasses must implement playRound()."""
    gameTitle: str = ""
    players: List[Player] = field(default_factory=list)
    log: Optional[object] = field(default=None)

    def emit(self, event) -> None:
        """Send an event to the log. Does nothing if no log is attached."""
        if self.log is not None:
            self.log.add(event)

    def addPlayer(self, player: Player) -> None:
        self.players.append(player)

    def removePlayer(self, playerId: int) -> None:
        self.players = [p for p in self.players if p.id != playerId]

    def getPlayerNames(self) -> List[str]:
        return [player.name for player in self.players]

    def _interactiveGivePhase(self) -> None:
        """Let each player with pending gives choose a target from the numbered player list."""
        pending = [p for p in self.players if p.pendingGive > 0]
        if not pending:
            return
        print("\n=== JAKO ===\n")
        for player in pending:
            amount = player.pendingGive
            others = [p for p in self.players if p != player]
            if not others:
                continue
            print(f"{player.getName()} antaa {amount} juomaa:")
            for i, p in enumerate(others, 1):
                print(f"  {i}. {p.getName()}")
            while True:
                raw = input("  Kenelle? (numero tai nimi): ").strip()
                target = self._findTargetByNameOrNumber(raw, others)
                if target:
                    target.addDrinks(amount)
                    player.addDrinksToGive(amount)
                    player.pendingGive = 0
                    self.emit(GiveEvent(player.getName(), target.getName(), amount))
                    break
                print("  Tuntematon pelaaja, yritä uudelleen.")

    def _findTargetByNameOrNumber(self, raw: str, players: list):
        """Return a player matching a 1-based number or name (case-insensitive)."""
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(players):
                return players[idx]
        return next((p for p in players if p.getName().lower() == raw.lower()), None)

    @abstractmethod
    def playRound(self) -> None:
        pass