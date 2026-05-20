"""
ImagePrinter renders receipts as JPG images for visual formatting preview.
Each cut() call saves a numbered receipt image to the output directory.

Config keys used (shared with cardImage):
    widthImage      (int): Receipt width in pixels.
    heightImage     (int): Card image height in pixels.
    rankFont        (str): Path to rank .ttf font.
    suitFont        (str): Path to suit .ttf font.
    rankFontSize    (int): Rank font size in points.
    suitFontSize    (int): Suit font size in points.
    receiptFont     (str): Path to receipt text .ttf font.
    receiptFontBold (str): Path to bold receipt text .ttf font.
    outputDir       (str): Folder to save images (default: "output").
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

_FONT_SIZE = 18
_MARGIN = 6
_CARD_GAP = 8

_SUIT_MAP = {"♥": "Hearts", "♦": "Diamonds", "♣": "Clubs", "♠": "Spades"}
_VALID_RANKS = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"}


def _loadFont(path, size=_FONT_SIZE):
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _wrap(text, font, draw, max_width):
    """Split text into lines that fit within max_width, breaking at word boundaries."""
    if draw.textlength(text, font=font) <= max_width:
        return [text]
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def _parseCards(text):
    """Parse '♥Q  ♣5  ♠A' into [('Q','♥'), ('5','♣'), ('A','♠')].
    Returns None if the text is not a valid card string."""
    tokens = [t for t in text.split() if t]
    if not tokens:
        return None
    result = []
    for token in tokens:
        if token[0] not in _SUIT_MAP:
            return None
        rank = token[1:]
        if rank not in _VALID_RANKS:
            return None
        result.append((rank, token[0]))
    return result


def _cropCard(img):
    """Crop a card image to its content bounding box with a small padding."""
    from PIL import ImageChops
    bg = Image.new("RGB", img.size, "white")
    diff = ImageChops.difference(img, bg)
    bbox = diff.getbbox()
    if bbox is None:
        return img
    pad = 6
    bbox = (
        max(0, bbox[0] - pad),
        max(0, bbox[1] - pad),
        min(img.width, bbox[2] + pad),
        min(img.height, bbox[3] + pad),
    )
    return img.crop(bbox)


def _buildCardRowImage(cards, config, invert=False):
    """Build a stitched PIL image of a card row from [(rank, suit), ...].
    Returns None if fonts are unavailable."""
    from printing.cardImage import buildCardImage
    cfg = dict(config)
    cfg["rankFontSize"] = int(cfg.get("rankFontSize", 80))
    cfg["suitFontSize"] = int(cfg.get("suitFontSize", 90))
    try:
        card_imgs = [_cropCard(buildCardImage(rank, suit, cfg)) for rank, suit in cards]
    except Exception:
        return None
    if invert:
        card_imgs = [ImageOps.invert(ci) for ci in card_imgs]
    total_w = sum(ci.width for ci in card_imgs) + _CARD_GAP * (len(card_imgs) - 1)
    max_h = max(ci.height for ci in card_imgs)
    row = Image.new("RGB", (total_w, max_h), "white")
    x = 0
    for ci in card_imgs:
        row.paste(ci, (x, 0))
        x += ci.width + _CARD_GAP
    return row


class ImagePrinter:
    """Renders receipt content to numbered JPG images for layout preview."""

    def __init__(self, config: dict, output_dir: str = "output"):
        self.width = int(config.get("widthImage", 576))
        self._config = config
        self.output_dir = output_dir
        fp = config.get("receiptFont", "")
        fb = config.get("receiptFontBold", "") or fp
        self._font = _loadFont(fp)
        self._font_bold = _loadFont(fb)
        self._font_2x = _loadFont(fp, size=_FONT_SIZE * 2)
        self._font_2x_bold = _loadFont(fb, size=_FONT_SIZE * 2)
        self._receipt_num = 0
        self._lines = []
        self._pending = ""
        self._style = self._default_style()

    def _default_style(self):
        return {
            "align": "left",
            "bold": False,
            "double_width": False,
            "double_height": False,
            "invert": False,
        }

    def set(self, **kwargs):
        self._style.update(kwargs)

    def textln(self, text=""):
        full = self._pending + str(text)
        self._pending = ""
        self._lines.append((full, dict(self._style)))

    def text(self, text=""):
        self._pending += str(text)

    def cut(self):
        if self._pending:
            self.textln()
        if not self._lines:
            return
        self._receipt_num += 1
        self._render()
        self._lines = []
        self._style = self._default_style()

    def close(self):
        pass

    def _pick_font(self, style):
        bold = style.get("bold", False)
        big = style.get("double_width") or style.get("double_height")
        if big:
            return self._font_2x_bold if bold else self._font_2x
        return self._font_bold if bold else self._font

    def _expand(self, draw):
        """Return render-ready items: ('text', text, style) or ('cards', [(rank,suit),...], style)."""
        items = []
        max_w = self.width - _MARGIN * 2
        for text, style in self._lines:
            is_double = style.get("double_width") or style.get("double_height")
            if is_double:
                cards = _parseCards(text)
                if cards is not None:
                    items.append(("cards", cards, style))
                    continue
            f = self._pick_font(style)
            for line in _wrap(text, f, draw, max_w):
                items.append(("text", line, style))
        return items

    def _text_line_height(self, style):
        base = _FONT_SIZE + 6
        return base * 2 if style.get("double_height") else base

    def _card_row_height(self):
        return int(self._config.get("heightImage", 120)) + _MARGIN * 2

    def _render(self):
        dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        items = self._expand(dummy_draw)

        total_h = _MARGIN
        for kind, _, style in items:
            total_h += self._card_row_height() if kind == "cards" else self._text_line_height(style)
        total_h += _MARGIN

        img = Image.new("RGB", (self.width, total_h), "white")
        d = ImageDraw.Draw(img)

        y = _MARGIN
        for kind, content, style in items:
            if kind == "cards":
                y = self._drawCardRow(img, y, content, style)
            else:
                y = self._drawTextLine(d, y, content, style)

        os.makedirs(self.output_dir, exist_ok=True)
        path = os.path.join(self.output_dir, f"receipt_{self._receipt_num:03d}.jpg")
        img.save(path, "JPEG")
        print(f"[Tallennettu: {path}]")

    def _drawTextLine(self, d, y, text, style):
        f = self._pick_font(style)
        lh = self._text_line_height(style)
        align = style.get("align", "left")
        invert = style.get("invert", False)

        tw = d.textlength(str(text), font=f)
        if align == "center":
            x = max(_MARGIN, (self.width - tw) / 2)
        elif align == "right":
            x = max(_MARGIN, self.width - tw - _MARGIN)
        else:
            x = _MARGIN

        if invert:
            d.rectangle([0, y, self.width, y + lh], fill="black")
            d.text((x, y + 2), str(text), font=f, fill="white")
        else:
            d.text((x, y + 2), str(text), font=f, fill="black")

        return y + lh

    def _drawCardRow(self, img, y, cards, style):
        invert = style.get("invert", False)
        row_h = self._card_row_height()

        row_img = _buildCardRowImage(cards, self._config, invert)
        if row_img is None:
            d = ImageDraw.Draw(img)
            text = "  ".join(f"{s}{r}" for r, s in cards)
            return self._drawTextLine(d, y, text, style)

        max_w = self.width - _MARGIN * 2
        if row_img.width > max_w:
            scale = max_w / row_img.width
            row_img = row_img.resize(
                (int(row_img.width * scale), int(row_img.height * scale)),
                Image.LANCZOS,
            )

        x = (self.width - row_img.width) // 2
        card_y = y + max(0, (row_h - row_img.height) // 2)
        img.paste(row_img, (x, card_y))
        return y + row_h
