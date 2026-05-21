"""
Receipt formatter functions. Each one writes to a printer object p using
p.set(), p.textln(), and p.text(). formatReceipt() runs the full game through all of them.
"""

_W = 24


def _wrapText(text: str, width: int = _W) -> list:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [""]


def formatTurn(phaseName: str, turn: dict, p) -> None:
    """Print one player's turn receipt for a phase."""
    p.textln("=" * 24)
    p.set(align="center", bold=True)
    p.textln(phaseName.upper())
    p.set(align="left", bold=False)
    p.textln("-" * 24)
    p.textln(f"Pelaaja : {turn['player']}")
    if phaseName == "Välistä vai ulkoa?" and turn.get("handBefore"):
        hand = turn["handBefore"]
        p.textln(f"Kädessä : {' | '.join(hand)}")
    if turn["guess"]:
        p.textln(f"Arvaus  : {turn['guess']}")
    if turn["card"]:
        if phaseName == "Isompi vai pienempi?" and turn.get("handBefore"):
            display = f"{turn['handBefore'][-1]}  {turn['card']}"
        else:
            display = turn["card"]
        p.textln("")
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln(display)
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.textln("")
    if turn["gaveTo"]:
        p.textln(f"Oikein! {turn['gaveTo']} juo {turn['drinks']}.")
    elif turn.get("correct") is True:
        p.textln("Oikein!")
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
    p.set(align="center", bold=True)
    p.textln("=" * 24)
    p.set(align="center", bold=True, double_width=True, double_height=True, invert=bool(card["matched"]))
    p.textln(card["card"])
    p.set(align="left", bold=False, invert=False)
    p.textln("-" * 24)  
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
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.set(align="center", bold=True)
    p.textln("=" * 24)


def formatTally(scores: list, p) -> None:
    """Print the final drink tally for all players."""
    p.set(align="center", bold=True)
    p.textln("LOPPUSALDO")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for score in scores:
        p.textln(f"{score['name']}: joi {score['drank']} | antoi {score['gave']}")
    p.textln("=" * 24)


def formatRouletteResult(event, p) -> None:
    """Print a single player's roulette pull result."""
    p.set(align="center", bold=True)
    p.textln("VENÄLÄINEN RULETTI")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(event.player.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    if event.hit:
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln("OSUMA!")
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.textln(f"Juo {event.drinks}!")
    else:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln("OHI!")
        p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)


def formatTaskDraw(event, p) -> None:
    """Print a single TaskGame task receipt."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(event.title.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    for line in _wrapText("Pelaajat: " + ", ".join(event.targets)):
        p.textln(line)
    for line in _wrapText(event.description):
        p.textln(line)
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
