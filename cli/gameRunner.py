from core.player import Player
from core.playerStore import PlayerStore
from printing.log import GameLog
from printing.printer import ReceiptPrinter, NullPrinter
from printing.live import LivePrinter
from cli.utils import _clearScreen


def showSessionResult(scores: list[dict], title: str) -> None:
    if not scores:
        return
    _clearScreen()
    print(f"\n--- {title} — tulos ---\n")
    print(f"{'Nimi':<20} {'Joi':>6} {'Antoi':>6}")
    print("-" * 34)
    for s in sorted(scores, key=lambda x: x["drank"], reverse=True):
        print(f"{s['name']:<20} {s['drank']:>6} {s['gave']:>6}")
    print()
    input("Paina Enter jatkaaksesi...")


def configureGame(gameTitle: str, configData: dict) -> dict:
    defaults = configData.get(gameTitle.lower(), {})

    if not defaults:
        import json
        from pathlib import Path
        examplePath = Path("config.example.json")
        if examplePath.exists():
            with open(examplePath, "r", encoding="utf-8") as f:
                defaults = json.load(f).get(gameTitle.lower(), {})
    if not defaults:
        return {}

    keys = list(defaults.keys())
    overrides = dict(defaults)

    while True:
        _clearScreen()
        print(f"\nPeliasetukset ({gameTitle}):\n")
        for i, key in enumerate(keys, 1):
            print(f"  {i}. {key} = {overrides[key]}")

        raw = input("\nMuuta asetus? (numero tai Enter ohittaaksesi): ").strip()
        if not raw:
            break
        if not raw.isdigit() or not (1 <= int(raw) <= len(keys)):
            print("Virheellinen valinta.")
            continue
        key = keys[int(raw) - 1]
        newVal = input(f"  {key} = ").strip()
        try:
            overrides[key] = type(defaults[key])(newVal)
        except (ValueError, TypeError):
            print("Virheellinen arvo, pidetään alkuperäinen.")

    return overrides


def _checkDeckCount(gameClass: type, players: list[Player], gameConfig: dict) -> dict:
    if not hasattr(gameClass, "cardsNeeded"):
        return gameConfig

    boardLength = gameConfig.get("boardLength", 3)
    needed = gameClass.cardsNeeded(len(players), boardLength)
    while True:
        deckCount = gameConfig.get("deckCount", 1)
        available = 52 * deckCount
        if needed <= available:
            print(
                f"\nPakkakiintiö: tarvitaan {needed} korttia, "
                f"saatavilla {available} ({deckCount} pakka(a)). OK."
            )
            break
        recommended = -(-needed // 52)
        print(
            f"\nPakkakiintiö: tarvitaan {needed} korttia {len(players)} pelaajalle, "
            f"saatavilla vain {available} ({deckCount} pakka(a))."
        )
        print(f"Suositellaan: {recommended} pakka(a).")
        choice = input("Aseta pakkojen määrä tai paina Enter jatkaaksesi: ").strip()
        if not choice:
            break
        if choice.isdigit() and int(choice) > 0:
            gameConfig["deckCount"] = int(choice)
        else:
            print("Virheellinen numero.")

    return gameConfig


def runGame(
    gameClass: type,
    players: list[Player],
    gameConfig: dict,
    store: PlayerStore,
    receiptMode: bool,
    debug: bool,
    saveData: bool,
    printerConfig: dict,
) -> dict:
    gameConfig = _checkDeckCount(gameClass, players, gameConfig)
    gameConfig.setdefault("separatorWidth", int(printerConfig.get("receiptWidth", 32)))

    printer = ReceiptPrinter(printerConfig, debug=debug) if receiptMode else NullPrinter()
    log = GameLog()
    store.gameTitle = gameClass.gameTitle
    log.on(LivePrinter(printer, gameTitle=gameClass.gameTitle).hook)
    if not debug and saveData:
        log.on(store.hook)

    game = gameClass(players=players, log=log, config=gameConfig)
    print(f"\nAloitetaan {game.gameTitle}...\n")
    game.playRound()

    return log.toDict()
