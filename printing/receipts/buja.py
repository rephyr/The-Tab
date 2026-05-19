def formatReceipt(data: dict, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("BUJA")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    p.textln(data["timestamp"])
    p.textln(", ".join(data["players"]))
    p.textln("=" * 24)

    if data["board"]:
        p.set(align="center", bold=True)
        p.textln("LAUTA")
        p.set(align="left", bold=False)
        p.textln("-" * 24)

        for card in data["board"]:
            p.set(align="center", bold=True, double_width=True, double_height=True, invert=bool(card["matched"]))
            p.textln(card["card"])
            p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
            p.textln(f"{card['action'].upper()} {card['drinks']}")

            if not card["matched"]:
                p.textln("Ei osumia")
            else:
                for outcome in card["outcomes"]:
                    if outcome["type"] == "drink":
                        p.textln(f"{outcome['player']} juo {outcome['drinks']}")
                    elif outcome["type"] == "give":
                        p.textln(f"{outcome['giver']} -> {outcome['receiver']} juo {outcome['drinks']}")
                    elif outcome["type"] == "share":
                        p.textln(f"{outcome['player1']} & {outcome['player2']} kippistää {outcome['drinks']}")
            p.textln("-" * 24)

    p.set(align="center", bold=True)
    p.textln("LOPPUSALDO")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for score in data["scores"]:
        p.textln(f"{score['name']}: joi {score['drank']} | antoi {score['gave']}")
    p.textln("=" * 24)
