"""Receipt formatters for the Ravit horse-race game."""


def formatHorseList(horses: list, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("RAVIT")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    p.set(bold=True)
    p.textln("HEVOSET")
    p.set(bold=False)
    p.textln("-" * 24)
    for h in horses:
        p.textln(f"#{h['id']} {h['name']}\tkerroin: x{h['odds']}")
    p.textln("=" * 24)


def formatBettingReceipt(horses: list, bets: list, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("VEDONLYÖNTI")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    for bet in bets:
        horseName = next((h["name"] for h in horses if h["id"] == bet["horseId"]), "?")
        p.textln(f"{bet['player']}: #{bet['horseId']} {horseName} x{bet['amount']}")
    p.textln("=" * 24)


def formatRaceRound(event, p) -> None:
    p.set(align="center", bold=True)
    p.textln("LÄHTOVIIVA" if event.roundNumber == 0 else f"KIERROS {event.roundNumber}")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for pos in event.positions:
        if pos["status"] == "racing":
            barLen = int(pos["position"] / event.trackLength * 15)
            bar = "-" * barLen + "@" + "-" * (15 - barLen)
            p.textln(f"{pos['name']}\t[{bar}]")
        else:
            label = "[KUOLI]" if pos["status"] == "dead" else "[DNF]"
            p.textln(f"{pos['name']}\t{label}")
    if event.raceEvents:
        p.textln("=" * 24)
        for ev in event.raceEvents:
            p.textln(ev["detail"])
            p.textln("-" * 24)
    p.textln("=" * 24)


def formatHorseEvent(event, p) -> None:
    if event.eventType in ("lightning", "fightDeath"):
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
        p.textln(f"R.I.P {event.horseName.upper()}")
        p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
        p.textln("=" * 24)
        p.textln(event.detail)
        p.textln("=" * 24)
    elif event.eventType == "death":
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln(f"DNF {event.horseName.upper()}")
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("=" * 24)
        p.textln(event.detail)
        p.textln("=" * 24)
    else:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln(event.horseName.upper())
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("=" * 24)
        p.textln(event.detail)
        p.textln("=" * 24)


def _hpBar(health, maxHealth, width=14) -> str:
    filled = int(health / maxHealth * width) if maxHealth > 0 else 0
    filled = max(0, min(width, filled))
    return "=" * filled + "-" * (width - filled)


def formatTiebreakStart(event, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
    p.textln("TASAPELI!")
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.textln("=" * 24)
    p.set(align="center", bold=True)
    p.textln("LOPPUKAMPPAILU")
    p.set(align="left", bold=False)
    p.textln("-" * 24)
    for c in event.combatants:
        bar = _hpBar(c["health"], c["maxHealth"])
        p.textln(f"{c['name']:<10}\t[{bar}] {c['health']}/{c['maxHealth']} v:{c['strength']}")
    p.textln("=" * 24)


def _formatCombatantBars(combatants, p) -> None:
    for c in combatants:
        bar = _hpBar(c["health"], c["maxHealth"])
        if c["health"] <= 0:
            p.set(invert=True)
            p.textln(f"{c['name']:<10}\t[{bar}] [KUOLI]")
            p.set(invert=False)
        else:
            p.textln(f"{c['name']:<10}\t[{bar}] {c['health']}/{c['maxHealth']} v:{c['strength']}")


def formatTiebreakRound(event, p) -> None:
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
    p.textln("=" * 24)
    _formatCombatantBars(event.combatants, p)
    p.textln("=" * 24)


def formatTiebreakElimination(event, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
    p.textln(f"R.I.P {event.loserName.upper()}")
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.textln("=" * 24)
    _formatCombatantBars(event.combatants, p)
    p.textln("=" * 24)


def formatTiebreakWinner(event, p) -> None:
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(f"{event.winnerName.upper()} VOITTAA")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)


def formatRavitFinal(data: dict, p) -> None:
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
    p.textln("=" * 24)
    p.textln(data.get("timestamp", ""))
    p.textln("=" * 24)
    oddsMap = {h["name"]: h["odds"] for h in data.get("horses", [])}
    p.set(bold=True)
    p.textln("SIJOITUKSET")
    p.set(bold=False)
    p.textln("-" * 24)
    _STATUS_ORDER = {"racing": 0, "dnf": 1, "dead": 2}
    for fp in sorted(data.get("finalPositions", []), key=lambda x: (_STATUS_ORDER.get(x["status"], 99), x["place"])):
        name = fp["horseName"]
        odds = oddsMap.get(name, "?")
        if fp["status"] == "dead":
            p.set(invert=True)
            p.textln(f"KUOLLUT {name}\tkerroin: x{odds}")
            p.set(invert=False)
        elif fp["status"] == "dnf":
            p.textln(f"DNF {name}\tkerroin: x{odds}")
        else:
            p.textln(f"{fp['place']}. {name}\tkerroin: x{odds}")
    p.textln("=" * 24)
    p.set(bold=True)
    p.textln("JUOMAT")
    p.set(bold=False)
    p.textln("-" * 24)
    for s in data.get("scores", []):
        p.textln(f"{s['name']}: joi {s['drank']} | antoi {s['gave']}")
    p.textln("=" * 24)
