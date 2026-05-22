import json
from pathlib import Path

class Config:
    def __init__(self, path="config.json"):
        self.path = path
        self.data = self.load()

    def load(self):
        path = Path(self.path)
        if not path.exists():
            fallback = Path("config.example.json")
            if fallback.exists():
                with open(fallback, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def save(self):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def getGameConfig(self, gameName: str):
        return self.data.get(gameName, {})