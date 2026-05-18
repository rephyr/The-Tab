def formatReceipt(data: dict, p) -> None:
    for phase in data["phases"]:
        for turn in phase["turns"]:
            p.textln("=" * 24)
            p.set(align="center", bold=True)
            p.textln(phase["name"].upper())
            p.set(align="left", bold=False)
            p.textln("-" * 24)
            p.textln(f"Pelaaja : {turn['player']}")
            if phase["name"] == "Inside or Outside" and turn.get("hand_before"):
                hand = turn["hand_before"]
                p.textln(f"Kädessä : {' | '.join(hand)}")
            if turn["guess"]:
                p.textln(f"Arvaus  : {turn['guess']}")
            if turn["card"]:
                if phase["name"] == "Higher or Lower" and turn.get("hand_before"):
                    display = f"{turn['hand_before'][-1]}  {turn['card']}"
                else:
                    display = turn["card"]
                p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
                p.textln(display)
                p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
            if turn["gave_to"]:
                p.textln(f"Oikein! {turn['gave_to']} juo {turn['drinks']}.")
            elif turn["drinks"] > 0:
                note = f" ({turn['note']})" if turn["note"] else ""
                p.textln(f"Väärin! Juo {turn['drinks']}{note}.")
            p.textln("-" * 24)
            p.cut()

    for player, cards in data["hands"].items():
        p.set(align="center", bold=True)
        p.textln(player.upper())
        p.set(align="left", bold=False)
        p.textln("=" * 24)
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("  ".join(cards))
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("=" * 24)
        p.cut()

    for card in data["board"]:
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=bool(card["matched"]))
        p.textln(card["card"])
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.textln(f"{card['action'].upper()} - {card['drinks']} drinks")
        if not card["matched"]:
            p.textln("No match")
        else:
            for outcome in card["outcomes"]:
                if outcome["type"] == "drink":
                    p.textln(f"{outcome['player']} drinks {outcome['drinks']}")
                elif outcome["type"] == "give":
                    p.textln(f"{outcome['giver']} -> {outcome['receiver']} drinks {outcome['drinks']}")
                elif outcome["type"] == "share":
                    p.textln(f"{outcome['player1']} & {outcome['player2']} share {outcome['drinks']}")
        p.cut()

    p.set(align="center", bold=True)
    p.textln("FINAL TALLY")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for score in data["scores"]:
        p.textln(f"{score['name']}: drank {score['drank']} | gave {score['gave']}")
    p.textln("=" * 24)
