from core.playerStore import PlayerStore
from cli.utils import _clearScreen


def _printSessionList(sessions: list[dict]) -> None:
    for i, s in enumerate(sessions):
        players = ", ".join(sc["name"] for sc in s["scores"])
        print(f"{i + 1}. [{s['timestamp']}] {s['game']} — {players}")


def showLeaderboard(store: PlayerStore) -> None:
    board = store.getLeaderboard()
    _clearScreen()
    if not board:
        print("\nEi dataa vielä.\n")
        input("Paina Enter jatkaaksesi...")
        return

    print("\n--- Tulostaulukko ---\n")
    print(f"{'#':<4} {'Nimi':<20} {'Joi':>6} {'Antoi':>6} {'Pelit':>6}")
    print("-" * 46)
    for i, p in enumerate(board):
        print(f"{i + 1:<4} {p['name']:<20} {p['totalDrinksTaken']:>6} {p['totalDrinksGiven']:>6} {p['gamesPlayed']:>6}")

    print()
    input("Paina Enter jatkaaksesi...")


def showDailyLeaderboard(store: PlayerStore) -> None:
    sessions = store.getSessions()
    dates = sorted({s["timestamp"][:10] for s in sessions}, reverse=True)
    _clearScreen()
    if not dates:
        print("\nEi sessioita tallennettu.\n")
        input("Paina Enter jatkaaksesi...")
        return

    print("\n--- Päivän tulostaulukko ---\n")
    for i, d in enumerate(dates, 1):
        print(f"  {i}. {d}")

    raw = input("\nValitse päivä (numero tai Enter peruuttaaksesi): ").strip()
    if not raw:
        return
    if not raw.isdigit() or not (1 <= int(raw) <= len(dates)):
        print("Virheellinen numero.")
        return

    date = dates[int(raw) - 1]
    board = store.getDailyLeaderboard(date)
    _clearScreen()
    print(f"\n--- {date} ---\n")
    print(f"{'#':<4} {'Nimi':<20} {'Joi':>6} {'Antoi':>6} {'Pelit':>6}")
    print("-" * 46)
    for i, p in enumerate(board):
        print(f"{i + 1:<4} {p['name']:<20} {p['totalDrinksTaken']:>6} {p['totalDrinksGiven']:>6} {p['gamesPlayed']:>6}")

    print()
    input("Paina Enter jatkaaksesi...")


def showSession(store: PlayerStore) -> None:
    sessions = store.getSessions()
    _clearScreen()
    if not sessions:
        print("\nEi sessioita tallennettu.")
        input("Paina Enter jatkaaksesi...")
        return

    print("\n--- Sessiot ---\n")
    _printSessionList(sessions)

    raw = input("\nKatsottavan session numero (tai Enter peruuttaaksesi): ").strip()
    if not raw:
        return
    if not raw.isdigit() or not (1 <= int(raw) <= len(sessions)):
        print("Virheellinen numero.")
        return

    s = sessions[int(raw) - 1]
    _clearScreen()
    print(f"\n[{s['timestamp']}] {s['game']}\n")
    print(f"{'Nimi':<20} {'Joi':>6} {'Antoi':>6}")
    print("-" * 35)
    for sc in s["scores"]:
        print(f"{sc['name']:<20} {sc['drinksTaken']:>6} {sc['drinksGiven']:>6}")
    print()
    input("Paina Enter jatkaaksesi...")
