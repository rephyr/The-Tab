def formatReceipt(data: dict, p) -> None:
    p.set(align="center", bold=True, double_width=True, double_height=True)
    p.textln("TASKGAME")
    p.set(align="left", bold=False, double_width=False, double_height=False)
    p.textln("=" * 24)
    p.textln(data["timestamp"])
    p.textln(", ".join(data["players"]))
    p.textln("=" * 24)

    p.set(align="center", bold=True)
    p.textln("FINAL TALLY")
    p.set(align="left", bold=False)
    p.textln("=" * 24)
    for score in data["scores"]:
        p.textln(f"{score['name']}: drank {score['drank']} | gave {score['gave']}")
    p.textln("=" * 24)
    p.set(align="center")