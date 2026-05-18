from PIL import Image, ImageDraw, ImageFont
from escpos.printer import Dummy

PAPER_W   = 576
PADDING   = 20
CONTENT_W = PAPER_W - PADDING * 2
INK       = "#000000"
PAPER     = "#ffffff"


def render_preview(p: Dummy) -> Image.Image:
    data = bytes(p.output)

    segments = []
    state = {"bold": False, "dw": False, "dh": False, "invert": False, "align": "left"}
    buf = ""

    def flush():
        nonlocal buf
        if buf:
            segments.append((buf, dict(state)))
            buf = ""

    i = 0
    while i < len(data):
        b = data[i]
        if b == 0x1b and i+2 < len(data) and data[i+1] == 0x21:
            flush()
            n = data[i+2]
            state["bold"] = bool(n & 0x08)
            state["dw"]   = bool(n & 0x20)
            state["dh"]   = bool(n & 0x10)
            i += 3
        elif b == 0x1b and i+2 < len(data) and data[i+1] == 0x45:
            flush(); state["bold"] = bool(data[i+2]); i += 3
        elif b == 0x1b and i+2 < len(data) and data[i+1] == 0x61:
            flush(); state["align"] = ["left","center","right"][min(data[i+2], 2)]; i += 3
        elif b == 0x1d and i+2 < len(data) and data[i+1] == 0x42:
            flush(); state["invert"] = bool(data[i+2]); i += 3
        elif b == 0x1b and i+2 < len(data) and data[i+1] == 0x74:
            i += 3
        elif 0x20 <= b <= 0x7e or b == 0x0a:
            buf += chr(b); i += 1
        else:
            i += 1
    flush()

    def line_h(dh): return (32 if dh else 20) + 6

    total_h = PADDING
    for text, st in segments:
        for line in text.split("\n"):
            total_h += line_h(st["dh"]) if line else line_h(st["dh"]) // 2
    total_h += PADDING

    img = Image.new("RGB", (PAPER_W, max(total_h, 100)), PAPER)
    d   = ImageDraw.Draw(img)
    y   = PADDING

    for text, st in segments:
        base = 32 if st["dh"] else 20
        fnt  = ImageFont.load_default(size=base)
        lh   = base + 6

        for line in text.split("\n"):
            if not line:
                y += lh // 2
                continue

            tw = d.textlength(line, font=fnt) * (2 if st["dw"] else 1)
            if st["align"] == "center":  x = PADDING + (CONTENT_W - tw) / 2
            elif st["align"] == "right": x = PAPER_W - PADDING - tw
            else:                        x = float(PADDING)

            if st["invert"]:
                d.rectangle([x - 4, y - 2, x + tw + 4, y + lh], fill=INK)
                fg = PAPER
            else:
                fg = INK

            if st["dw"]:
                cx = x
                for ch in line:
                    cw = d.textlength(ch, font=fnt)
                    d.text((cx, y), ch, font=fnt, fill=fg)
                    d.text((cx + 1, y), ch, font=fnt, fill=fg)
                    cx += cw * 2
            else:
                d.text((x, y), line, font=fnt, fill=fg)

            y += lh

    return img


def save_preview(p: Dummy, path: str = "receipt_preview.png") -> None:
    render_preview(p).save(path)


if __name__ == "__main__":
    from escpos.printer import Dummy
    from receipt import card_receipt

    card = {"suit": "H", "value_name": "Q", "suit_name": "Hertta", "color": "Punainen"}

    p = Dummy()
    card_receipt(p, card, "Mikko", "1/4 - Musta vai punainen?", "Punainen")
    save_preview(p)
    print("Tallennettu: receipt_preview.png")