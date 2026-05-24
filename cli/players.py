from core.player import Player
from core.playerStore import PlayerStore
from cli.utils import _clearScreen


def deduplicateName(name: str, existingNames: set[str]) -> str:
    if name not in existingNames:
        return name
    counter = 2
    while f"{name} ({counter})" in existingNames:
        counter += 1
    return f"{name} ({counter})"


def selectPlayers(store: PlayerStore) -> list[Player]:
    savedNames = store.getAllPlayerNames()
    players: list[Player] = []
    existingNames: set[str] = set()

    _clearScreen()
    print("\nSyötä pelaajat:")
    if savedNames:
        print()
        for i, name in enumerate(savedNames, 1):
            print(f"  {i}. {name}")
    print()

    playerId = 1
    while True:
        raw = input(f"Pelaaja {playerId} (numero tai nimi, Enter lopettaa): ").strip()
        if raw == "":
            break
        if raw.isdigit() and 1 <= int(raw) <= len(savedNames):
            name = savedNames[int(raw) - 1]
        else:
            name = raw.title()
        uniqueName = deduplicateName(name, existingNames)
        if uniqueName != name:
            print(f"  Nimi on jo käytössä, käytetään '{uniqueName}'")
        existingNames.add(uniqueName)
        players.append(Player(playerId, uniqueName))
        playerId += 1

    return players
