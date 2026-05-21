"""
Receipt formatters for the Ravit horse-race game.

Receipts are printed in this order during a game:

formatHorseList        — before betting; lists horses and odds
formatBettingReceipt   — after all bets are placed
formatRaceRound        — every round (roundNumber 0 = starting line)
formatHorseEvent       — per horse when a notable event fires
formatTiebreakStart    — when tied horses enter sudden-death combat
formatTiebreakRound    — each combat round
formatTiebreakElimination — when a combatant is eliminated (3+ fighters only)
formatTiebreakWinner   — when one combatant remains
formatRavitFinal       — end of game; standings and drink scores

Printer API used in this module:

p.set(align, bold, double_width, double_height, invert)
p.textln(text) — prints one line
"""

_W = 32


def configure(config: dict) -> None:
    """Read receiptWidth from printer config. Call once before printing."""
    global _W
    _W = int(config.get("receiptWidth", 32))


from printing.receipts.textWrapper import wrapText as _wrapText


def formatHorseList(horses: list, p) -> None:
    """Print the horse roster with ids and odds."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("RAVIT")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    p.set(bold=True)
    p.textln("HEVOSET")
    p.set(bold=False)
    p.textln("-" * _W)
    for h in horses:
        p.textln(f"#{h['id']} {h['name']:<12}kerroin: x{h['odds']}")
    p.textln("=" * _W)


def formatBettingReceipt(horses: list, bets: list, p) -> None:
    """Print each player's bet — horse id, name, and amount."""
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("VEDONLYÖNTI")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    for bet in bets:
        horseName = next((h["name"] for h in horses if h["id"] == bet["horseId"]), "?")
        p.textln(f"{bet['player']}: #{bet['horseId']} {horseName} x{bet['amount']}")
    p.textln("=" * _W)


def formatRaceRound(event, p) -> None:
    """Print the track state for one round. roundNumber 0 prints as the starting line."""
    p.set(align="center", bold=True)
    p.textln("LÄHTOVIIVA" if event.roundNumber == 0 else f"KIERROS {event.roundNumber}")
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    for pos in event.positions:
        if pos["status"] == "racing":
            barLen = int(pos["position"] / event.trackLength * 15)
            bar = "-" * barLen + "@" + "-" * (15 - barLen)
            p.textln(f"{pos['name']:<12}[{bar}]")
        else:
            label = "KUOLI" if pos["status"] == "dead" else "DNF"
            p.textln(f"{pos['name']:<12}[{label:^16}]")
    if event.raceEvents:
        p.textln("=" * _W)
        for ev in event.raceEvents:
            for line in _wrapText(ev["detail"], _W):
                p.textln(line)
            p.textln("-" * _W)
    p.textln("=" * _W)


def formatHorseEvent(event, p) -> None:
    """Print a mid-race horse event card.

    lightning or fightDeath — inverted R.I.P. header
    death (DNF)             — normal DNF header
    other events            — normal horse name header
    """
    if event.eventType in ("lightning", "fightDeath"):
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln(f"R.I.P {event.horseName.upper()}")
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.textln("=" * _W)
        for line in _wrapText(event.detail, _W):
            p.textln(line)
        p.textln("=" * _W)
    elif event.eventType == "death":
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln(f"DNF {event.horseName.upper()}")
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("=" * _W)
        for line in _wrapText(event.detail, _W):
            p.textln(line)
        p.textln("=" * _W)
    else:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln(event.horseName.upper())
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("=" * _W)
        for line in _wrapText(event.detail, _W):
            p.textln(line)
        p.textln("=" * _W)


def _hpBar(health, maxHealth, width=6) -> str:
    filled = int(health / maxHealth * width) if maxHealth > 0 else 0
    filled = max(0, min(width, filled))
    return "=" * filled + "-" * (width - filled)


def formatTiebreakStart(event, p) -> None:
    """Print the tiebreak announcement with all combatants' starting HP and strength."""

    p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
    p.textln("TASAPELI!")
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True)
    p.textln("LOPPUKAMPPAILU")
    p.set(align="left", bold=False)
    p.textln("-" * _W)
    for c in event.combatants:
        bar = _hpBar(c["health"], c["maxHealth"])
        p.textln(f"{c['name']:<12}[{bar}] {c['health']}/{c['maxHealth']} v:{c['strength']}")
    p.textln("=" * _W)


def _formatCombatantBars(combatants, p) -> None:
    for c in combatants:
        bar = _hpBar(c["health"], c["maxHealth"])
        if c["health"] <= 0:
            p.set(invert=True)
            p.textln(f"{c['name']:<12}[{bar}] [KUOLI]")
            p.set(invert=False)
        else:
            p.textln(f"{c['name']:<12}[{bar}] {c['health']}/{c['maxHealth']} v:{c['strength']}")


def formatTiebreakRound(event, p) -> None:
    """Print one tiebreak combat round. In a 2-fighter duel the final round becomes an R.I.P. card."""

    dead = [c for c in event.combatants if c["health"] <= 0]
    isDuel = len(event.combatants) == 2
    if dead and isDuel:
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln(f"R.I.P {dead[0]['name'].upper()}")
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    else:
        p.set(align="center", bold=True)
        p.textln(f"TAISTELUKIERROS {event.roundNumber}")
        p.set(align="left", bold=False)
    p.textln("=" * _W)
    _formatCombatantBars(event.combatants, p)
    p.textln("=" * _W)


def formatTiebreakElimination(event, p) -> None:
    """Print an R.I.P. card when a combatant is eliminated in a 3+ fighter tiebreak."""

    p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
    p.textln(f"R.I.P {event.loserName.upper()}")
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.textln("=" * _W)
    _formatCombatantBars(event.combatants, p)
    p.textln("=" * _W)


def formatTiebreakWinner(event, p) -> None:
    """Print the tiebreak winner announcement."""
    p.set(align="left", bold=False)
    p.textln("=" * _W)
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(f"{event.winnerName.upper()} VOITTAA")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)


def formatRavitFinal(data: dict, p) -> None:
    """Print the end-of-game summary: timestamp, final standings, and drink scores.

    data keys: players, timestamp, horses, bets, finalPositions, scores
    finalPositions — {horseId, horseName, position, place, status}; status racing/dnf/dead
    scores         — {name, drank, gave}
    """
    trackLength = len(data.get("finalPositions", [])) and max(
        (fp["position"] for fp in data.get("finalPositions", []) if fp["status"] == "racing"),
        default=20
    )
    # Use horses snapshot to recover trackLength if possible
    trackLength = 20  # default; horses data doesn't carry trackLength
    if data.get("horses"):
        # Not stored, so keep 20 as the display value
        pass

    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("RAVIT")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * _W)
    p.textln(data.get("timestamp", ""))
    p.textln("=" * _W)
    oddsMap = {h["name"]: h["odds"] for h in data.get("horses", [])}
    p.set(bold=True)
    p.textln("SIJOITUKSET")
    p.set(bold=False)
    p.textln("-" * _W)
    _STATUS_ORDER = {"racing": 0, "dnf": 1, "dead": 2}
    for fp in sorted(data.get("finalPositions", []), key=lambda x: (_STATUS_ORDER.get(x["status"], 99), x["place"])):
        name = fp["horseName"]
        odds = oddsMap.get(name, "?")
        if fp["status"] == "dead":
            p.set(invert=True)
            p.textln(f"RIP {name:<14}x{odds}")
            p.set(invert=False)
        elif fp["status"] == "dnf":
            p.set(invert=True)
            p.textln(f"DNF {name:<14}x{odds}")
            p.set(invert=False)
        else:
            p.textln(f"{fp['place']}.  {name:<14}x{odds}")
    p.textln("=" * _W)
    p.set(bold=True)
    p.textln("JUOMAT")
    p.set(bold=False)
    p.textln("-" * _W)
    for s in data.get("scores", []):
        p.textln(f"{s['name']}: joi {s['drank']} | antoi {s['gave']}")
    p.textln("=" * _W)
