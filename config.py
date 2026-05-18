import json
from pathlib import Path

class Config:
    def __init__(self, path="config.json"):
        self.path = path
        self.data = self.load()

    def load(self):
        with open(self.path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_game_config(self, game_name: str):
        return self.data.get(game_name, {})