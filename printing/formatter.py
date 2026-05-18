"""
Receipt formatter functions. Each one writes to a printer object p using
p.set(), p.textln(), and p.text(). formatReceipt() runs the full game through all of them.
"""


def formatTurn(phase_name: str, turn: dict, p) -> None:
    """Print one player's turn receipt for a phase."""
    p.textln("=" * 24)
    p.set(align="center", bold=True)
    p.textln(phase_name.upper())
    p.set(align="left", bold=False)
    p.textln("-" * 24)
    p.textln(f"Pelaaja : {turn['player']}")
    if phase_name == "Inside or Outside" and turn.get("hand_before"):
        hand = turn["hand_before"]
        p.textln(f"Kädessä : {' | '.join(hand)}")
    if turn["guess"]:
        p.textln(f"Arvaus  : {turn['guess']}")
    if turn["card"]:
        if phase_name == "Higher or Lower" and turn.get("hand_before"):
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


def formatHand(player: str, cards: list, p) -> None:
    """Print a player's full hand as a single receipt."""
    p.set(align="center", bold=True)
    p.textln(player.upper())
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("  ".join(cards))
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)


def formatBoardCard(card: dict, p) -> None:
    """Print a board card receipt with its action and outcomes."""
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


def formatTally(scores: list, p) -> None:
    """Print the final drink tally for all players."""
    p.set(align="center", bold=True)
    p.textln("FINAL TALLY")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for score in scores:
        p.textln(f"{score['name']}: drank {score['drank']} | gave {score['gave']}")
    p.textln("=" * 24)


def formatReceipt(data: dict, p) -> None:
    """Print the full game receipt: all turns, hands, board cards, and tally."""
    for phase in data["phases"]:
        for turn in phase["turns"]:
            formatTurn(phase["name"], turn, p)
            p.cut()
    for player, cards in data["hands"].items():
        formatHand(player, cards, p)
        p.cut()
    for card in data["board"]:
        formatBoardCard(card, p)
        p.cut()
    formatTally(data["scores"], p)
