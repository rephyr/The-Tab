"""
base game class
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List
from .player import Player

@dataclass
class Game(ABC):
    name: str
    players: List[Player] = field(default_factory=list)
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
        raise NotImplementedError