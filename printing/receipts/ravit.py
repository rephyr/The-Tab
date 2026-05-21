def formatBettingSlip(horses: list, bets: list, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("RAVIT")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    p.set(bold=True)
    p.textln("HEVOSET")
    p.set(bold=False)
    p.textln("-" * 24)
    for h in horses:
        p.textln(f"#{h['id']} {h['name']:<12} x{h['odds']}")
    p.textln("=" * 24)
    p.set(bold=True)
    p.textln("VEDONLYÖNTI")
    p.set(bold=False)
    p.textln("-" * 24)
    for bet in bets:
        horseName = next((h["name"] for h in horses if h["id"] == bet["horseId"]), "?")
        p.textln(f"{bet['player']}: #{bet['horseId']} {horseName} x{bet['amount']}")
    p.textln("=" * 24)


def formatRaceRound(event, p) -> None:
    p.set(align="center", bold=True)
    p.textln(f"KIERROS {event.roundNumber}")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for pos in event.positions:
        if pos["alive"]:
            barLen = int(pos["position"] / event.trackLength * 15)
            bar = "-" * barLen + "@" + "-" * (15 - barLen)
            p.textln(f"{pos['name']}\t[{bar}]")
        else:
            p.textln(f"{pos['name']}\t[KUOLLUT]")
    if event.raceEvents:
        p.textln("-" * 24)
        for ev in event.raceEvents:
            p.textln(ev["detail"])
    p.textln("=" * 24)


def formatHorseEvent(event, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True,
          invert=(event.eventType == "death"))
    p.textln(event.horseName.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
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


def formatTiebreakElimination(event, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True, invert=True)
    p.textln(event.loserName.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False, invert=False)
    p.textln("=" * 24)
    p.textln("kaatuu loppukamppailussa!")
    p.textln("-" * 24)
    for c in event.combatants:
        bar = _hpBar(c["health"], c["maxHealth"])
        marker = " [KAATUI]" if c["health"] <= 0 else f" v:{c['strength']}"
        p.textln(f"{c['name']:<10}\t[{bar}] {c['health']}/{c['maxHealth']}{marker}")
    p.textln("=" * 24)


def formatTiebreakWinner(event, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln(event.winnerName.upper())
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    p.set(align="center", bold=True)
    p.textln("VOITTAA LOPPUKAMPPAILUN!")
    p.set(align="left", bold=False)
    bar = _hpBar(event.health, event.maxHealth)
    p.textln(f"{event.winnerName:<10}\t[{bar}] {event.health}/{event.maxHealth} v:{event.strength}")
    p.textln("=" * 24)


def formatRavitFinal(data: dict, p) -> None:
    trackLength = len(data.get("finalPositions", [])) and max(
        (fp["position"] for fp in data.get("finalPositions", []) if fp["alive"]),
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
    p.set(bold=True)
    p.textln("SIJOITUKSET")
    p.set(bold=False)
    p.textln("-" * 24)
    for fp in sorted(data.get("finalPositions", []), key=lambda x: x["place"]):
        if fp["alive"]:
            p.textln(f"{fp['place']}. {fp['horseName']:<12} {fp['position']} ruutua")
        else:
            p.textln(f"[KUOLLUT] {fp['horseName']}")
    p.textln("=" * 24)
    p.set(bold=True)
    p.textln("JUOMAT")
    p.set(bold=False)
    p.textln("-" * 24)
    for s in data.get("scores", []):
        p.textln(f"{s['name']}: joi {s['drank']} | antoi {s['gave']}")
    p.textln("=" * 24)
