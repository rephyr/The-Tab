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

    def _interactiveAssignDrinks(self, budget: int = None) -> bool:
        """Numbered player list for assigning drinks. Returns True if quit was requested.

        budget: total drinks available to assign; None means unlimited.
        Shows remaining budget at top, errors if an assignment would exceed it.
        """
        players = list(self.players)
        remaining = budget

        while True:
            print()
            if remaining is not None:
                print(f"  Jaettavana: {remaining} juomaa")
            for i, p in enumerate(players, 1):
                print(f"  {i}. {p.getName()}")
            print("  (Enter lopettaaksesi)")
            raw = input("  Kenelle? ").strip()
            if not raw:
                return False
            if raw.lower() == "quit":
                return True

            target = self._findTargetByNameOrNumber(raw, players)
            if not target:
                print("  Tuntematon pelaaja, yritä uudelleen.")
                continue

            amountRaw = input(f"  Montako {target.getName()}lle? ").strip()
            try:
                amount = int(amountRaw)
                if amount <= 0:
                    raise ValueError
            except ValueError:
                print("  Virheellinen määrä.")
                continue
            if remaining is not None and amount > remaining:
                print(f"  Liikaa! Voit antaa enintään {remaining} juomaa.")
                continue

            print(f"  {target.getName()} juo {amount}")
            self._assignDrinks(target, amount)
            if remaining is not None:
                remaining -= amount
                if remaining <= 0:
                    break

        return False

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