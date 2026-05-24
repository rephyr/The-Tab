from core.playerStore import PlayerStore
from cli.utils import _clearScreen
from cli.sessions import showSession, _printSessionList


def manageData(store: PlayerStore) -> None:
    try:
        while True:
            _clearScreen()
            print("\nHallitse dataa:")
            print("1. Katso sessiot")
            print("2. Poista pelaaja")
            print("3. Poista sessio")
            print("4. Takaisin")

            choice = input("\nValinta: ").strip()

            if choice == "1":
                showSession(store)

            elif choice == "2":
                names = store.getRegisteredPlayerNames()
                if not names:
                    print("Pelaajia ei löydy.")
                    continue
                print()
                for name in names:
                    print(f"  {name}")
                print()
                name = input("Poistettavan pelaajan nimi: ").strip()
                if not name:
                    continue
                confirm = input(f"Poista '{name}' ja kaikki tilastot? (k/e): ").strip().lower()
                if confirm != "k":
                    print("Peruutettu.")
                    continue
                if store.deletePlayer(name):
                    print(f"Pelaaja '{name}' poistettu.")
                else:
                    print(f"Pelaaja '{name}' löytyy vain sessiohistoriassa eikä sitä voi poistaa.")

            elif choice == "3":
                sessions = store.getSessions()
                if not sessions:
                    print("Ei sessioita poistettavaksi.")
                    continue

                print()
                _printSessionList(sessions)

                raw = input("\nPoistettavan session numero (tai Enter peruuttaaksesi): ").strip()
                if not raw:
                    continue
                if not raw.isdigit() or not (1 <= int(raw) <= len(sessions)):
                    print("Virheellinen numero.")
                    continue
                index = int(raw) - 1
                s = sessions[index]
                players = ", ".join(sc["name"] for sc in s["scores"])
                confirm = input(
                    f"Poista sessio [{s['timestamp']}] {s['game']} — {players}? (k/e): "
                ).strip().lower()
                if confirm != "k":
                    print("Peruutettu.")
                    continue
                if store.deleteSession(index):
                    print("Sessio poistettu.")
                else:
                    print("Virheellinen numero.")

            elif choice == "4":
                break
    except KeyboardInterrupt:
        print()
