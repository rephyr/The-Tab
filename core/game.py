from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from .player import Player

@dataclass
class Game(ABC):
    name: str = ""
    gameTitle: str = ""
    players: List[Player] = field(default_factory=list)
    log: Optional[object] = field(default=None)

    def emit(self, event) -> None:
        if self.log is not None:
            self.log.add(event)

    def addPlayer(self, player: Player) -> None:
        self.players.append(player)

    def removePlayer(self, player_id: int) -> None:
        self.players = [p for p in self.players if p.id != player_id]

    def reset(self) -> None:
        for player in self.players:
            player.setDrinksTaken(0)

    def getPlayerNames(self) -> List[str]:
        return [player.name for player in self.players]

    @abstractmethod
    def playRound(self) -> None:
        pass