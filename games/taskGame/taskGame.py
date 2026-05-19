"""
TaskGame: a turn-based drinking game where each turn a random task is drawn.
Tasks can target a single player, multiple random players, or everyone.
"""
from core.game import Game
from core.events import GameStartEvent, GameEndEvent
from dataclasses import dataclass, field
from games.taskGame.tasks import TASKS
import random

# Each task has:
#   title       -- short name printed in large text on the receipt
#   description -- the rule or challenge text
#   players     -- how many players are picked: 1, 2, N, or "all"
#                  1 targets the drawing player themselves

@dataclass
class TaskGame(Game):
    """
    Task-based drinking game. Players take turns drawing a random task.
    The task defines how many players are involved.
    """
    gameTitle: str = "TaskGame"

    config: dict = field(default_factory=dict)

    def playRound(self) -> None:
        """Run a full game: players take turns drawing tasks until someone quits."""
        self.emit(GameStartEvent([p.getName() for p in self.players]))

        taskPool = list(TASKS)

        if not taskPool:
            print("No tasks defined.")
            return

        running = True
        while running:
            for player in self.players:
                input(f"\n{player.getName()}'s turn -- press Enter to draw a task")

                if not taskPool:
                    taskPool = list(TASKS)

                task = random.choice(taskPool)

                targets = self._resolveTargets(task["players"], player)
                targetNames = ", ".join(p.getName() for p in targets)

                print(f"\n>>> {task['title']}")
                print(f"Players: {targetNames}")
                print(task["description"])

                quit = input("\nContinue? (Enter = yes, q = quit): ").strip().lower()
                if quit == "q":
                    running = False
                    break

        self.emit(GameEndEvent([
            {"name": p.getName(), "drinksTaken": p.getDrinksTaken(), "drinksToGive": p.drinksToGive}
            for p in self.players
        ]))

    def _resolveTargets(self, playerCount, drawer):
        """Return the list of players targeted by a task."""
        if playerCount == "all":
            return list(self.players)
        if playerCount == 1:
            return [drawer]
        return self._pickRandom(playerCount, exclude=drawer)

    def _pickRandom(self, count: int, exclude=None):
        """Return `count` randomly chosen players, excluding the given player if provided."""
        pool = [p for p in self.players if p != exclude]
        return random.sample(pool, min(count, len(pool)))