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
_CARD_PADDING = 20
_CARD_GAP = 8

_SUIT_MAP = {"❤︎⁠": "Hearts", "♥": "Hearts", "♦": "Diamonds", "♣": "Clubs", "♠": "Spades"}
_VALID_RANKS = {"2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"}
_INVERTED_SUITS = {"❤︎⁠", "♥", "♦"}
# Normalize suit symbols to font-renderable equivalents for image building
_SUIT_FONT_SYMBOL = {"❤︎⁠": "♥"}

def _loadFont(path, size=_FONT_SIZE):
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _wrap(text, font, draw, maxWidth):
    """Split text into lines that fit within maxWidth, breaking at word boundaries."""
    if draw.textlength(text, font=font) <= maxWidth:
        return [text]
    words = text.split(" ")
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if draw.textlength(candidate, font=font) <= maxWidth:
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
        suit_sym = next((s for s in sorted(_SUIT_MAP, key=len, reverse=True) if token.startswith(s)), None)
        if suit_sym is None:
            return None
        rank = token[len(suit_sym):]
        if rank not in _VALID_RANKS:
            return None
        result.append((rank, suit_sym))
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


def _buildCardRowImage(cards, config):
    """Build a stitched PIL image of a card row from [(rank, suit), ...].
    Returns None if fonts are unavailable."""
    from printing.cardImage import buildCardImage
    cfg = dict(config)
    cfg["rankFontSize"] = int(cfg.get("rankFontSize", 80))
    cfg["suitFontSize"] = int(cfg.get("suitFontSize", 90))
    try:
        cardImgs = []
        for rank, suit in cards:
            ci = _cropCard(buildCardImage(rank, _SUIT_FONT_SYMBOL.get(suit, suit), cfg))
            if suit in _INVERTED_SUITS:
                ci = ImageOps.invert(ci)
            cardImgs.append(ci)
    except Exception:
        return None
    totalW = sum(ci.width for ci in cardImgs) + _CARD_GAP * (len(cardImgs) - 1)
    maxH = max(ci.height for ci in cardImgs)
    row = Image.new("RGB", (totalW, maxH), "white")
    x = 0
    for ci in cardImgs:
        row.paste(ci, (x, 0))
        x += ci.width + _CARD_GAP
    return row


class ImagePrinter:
    """Renders receipt content to numbered JPG images for layout preview."""

    def __init__(self, config: dict, outputDir: str = "output"):
        self.width = int(config.get("widthImage", 576))
        self._config = config
        self.outputDir = outputDir
        fp = config.get("receiptFont", "")
        fb = config.get("receiptFontBold", "") or fp
        self._font = _loadFont(fp)
        self._fontBold = _loadFont(fb)
        self._font2x = _loadFont(fp, size=_FONT_SIZE * 2)
        self._font2xBold = _loadFont(fb, size=_FONT_SIZE * 2)
        self._receiptNum = 0
        self._lines = []
        self._pending = ""
        self._style = self._defaultStyle()
        self._tabStop = 0

    def _defaultStyle(self):
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
        self._receiptNum += 1
        self._render()
        self._lines = []
        self._style = self._defaultStyle()

    def close(self):
        pass

    def _pickFont(self, style):
        bold = style.get("bold", False)
        big = style.get("double_width") or style.get("double_height")
        if big:
            return self._font2xBold if bold else self._font2x
        return self._fontBold if bold else self._font

    def _expand(self, draw):
        """Return render-ready items: ('text', text, style) or ('cards', pil_image, style)."""
        items = []
        maxW = self.width - _MARGIN * 2
        for text, style in self._lines:
            isDouble = style.get("double_width") or style.get("double_height")
            if isDouble:
                cards = _parseCards(text)
                if cards is not None:
                    rowImg = _buildCardRowImage(cards, self._config)
                    if rowImg is not None:
                        scale = float(self._config.get("imageCardScale", 1.0))
                        if scale != 1.0:
                            rowImg = rowImg.resize(
                                (int(rowImg.width * scale), int(rowImg.height * scale)),
                                Image.LANCZOS,
                            )
                        items.append(("cards", rowImg, style))
                        continue
                    text = "  ".join(f"{s}{r}" for r, s in cards)
            f = self._pickFont(style)
            for line in _wrap(text, f, draw, maxW):
                items.append(("text", line, style))
        return items

    def _textLineHeight(self, style):
        base = _FONT_SIZE + 6
        return base * 2 if style.get("double_height") else base

    def _render(self):
        dummyDraw = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        self._tabStop = 0
        for text, style in self._lines:
            if "\t" in text:
                left = text.split("\t", 1)[0]
                f = self._pickFont(style)
                w = int(dummyDraw.textlength(left, font=f))
                if w + _MARGIN * 3 > self._tabStop:
                    self._tabStop = w + _MARGIN * 3
        items = self._expand(dummyDraw)

        totalH = _MARGIN
        for kind, content, style in items:
            if kind == "cards":
                totalH += content.height + _CARD_PADDING * 2
            else:
                totalH += self._textLineHeight(style)
        totalH += _MARGIN

        img = Image.new("RGB", (self.width, totalH), "white")
        d = ImageDraw.Draw(img)

        y = _MARGIN
        for kind, content, style in items:
            if kind == "cards":
                y = self._drawCardRow(img, y, content)
            else:
                y = self._drawTextLine(d, y, content, style)

        os.makedirs(self.outputDir, exist_ok=True)
        path = os.path.join(self.outputDir, f"receipt_{self._receiptNum:03d}.jpg")
        img.save(path, "JPEG")
        print(f"[Tallennettu: {path}]")

    def _drawTextLine(self, d, y, text, style):
        f = self._pickFont(style)
        lh = self._textLineHeight(style)
        align = style.get("align", "left")
        invert = style.get("invert", False)
        fill = "white" if invert else "black"

        text = str(text)

        if "\t" in text:
            left, _, right = text.partition("\t")
            if right.startswith("[") and "]" in right:
                close = right.index("]")
                bar_chars = right[1:close]
                after = right[close + 1:].lstrip()
                if bar_chars and all(c in "=-" for c in bar_chars):
                    return self._drawHpBarLine(d, y, left, bar_chars.count("="), len(bar_chars), after, style)
            if invert:
                d.rectangle([0, y, self.width, y + lh], fill="black")
            d.text((_MARGIN, y + 2), left, font=f, fill=fill)
            d.text((_MARGIN + self._tabStop, y + 2), right, font=f, fill=fill)
            return y + lh

        if text and len(set(text)) == 1:
            charW = d.textlength(text[0], font=f)
            if charW > 0:
                count = int((self.width - _MARGIN * 2) / charW)
                text = text[0] * count

        tw = d.textlength(text, font=f)
        if align == "center":
            x = max(_MARGIN, (self.width - tw) / 2)
        elif align == "right":
            x = max(_MARGIN, self.width - tw - _MARGIN)
        else:
            x = _MARGIN

        if invert:
            d.rectangle([0, y, self.width, y + lh], fill="black")
        d.text((x, y + 2), text, font=f, fill=fill)

        return y + lh

    def _drawHpBarLine(self, d, y, left, filled, total, after, style):
        f = self._pickFont(style)
        lh = self._textLineHeight(style)
        invert = style.get("invert", False)
        fill = "white" if invert else "black"
        bg = "black" if invert else "white"

        if invert:
            d.rectangle([0, y, self.width, y + lh], fill="black")

        d.text((_MARGIN, y + 2), left, font=f, fill=fill)

        bar_x = _MARGIN + self._tabStop
        bar_w = self.width // 4
        bar_pad = 3
        bar_y0 = y + bar_pad
        bar_y1 = y + lh - bar_pad

        d.rectangle([bar_x, bar_y0, bar_x + bar_w, bar_y1], outline=fill, fill=bg)
        if total > 0 and filled > 0:
            filled_w = int(filled / total * bar_w)
            d.rectangle([bar_x, bar_y0, bar_x + filled_w, bar_y1], fill=fill)

        after_x = bar_x + bar_w + _MARGIN
        d.text((after_x, y + 2), after, font=f, fill=fill)
        return y + lh

    def _drawCardRow(self, img, y, rowImg):
        maxW = self.width - _MARGIN * 2
        if rowImg.width > maxW:
            scale = maxW / rowImg.width
            rowImg = rowImg.resize(
                (int(rowImg.width * scale), int(rowImg.height * scale)),
                Image.LANCZOS,
            )
        x = (self.width - rowImg.width) // 2
        img.paste(rowImg, (x, y + _CARD_PADDING))
        return y + rowImg.height + _CARD_PADDING * 2
