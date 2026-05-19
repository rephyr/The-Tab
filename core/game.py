"""
Base class for all games. Handles players, event emitting, and defines the playRound interface.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from .player import Player

@dataclass
class Game(ABC):
    """Abstract base for a game. Subclasses must implement playRound()."""
    name: str = ""
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

    def reset(self) -> None:
        for player in self.players:
            player.setDrinksTaken(0)

    def getPlayerNames(self) -> List[str]:
        return [player.name for player in self.players]

    @abstractmethod
    def playRound(self) -> None:
        pass