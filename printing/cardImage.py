"""
Card image builder for thermal receipt printer.
Generates PIL images with card rank and suit using separate fonts.

Config keys:
    widthImage (int): Image width in pixels.
    heightImage (int): Image height in pixels.
    rankFont (str): Path to .ttf font file for rank.
    suitFont (str): Path to .ttf font file for suit.
    rankFontSize (int): Font size for rank in points.
    suitFontSize (int): Font size for suit in points.
"""
from PIL import Image, ImageDraw, ImageFont

def buildCardImage(rank: str, suit: str, config: dict) -> Image.Image:
    """Builds a thermal printer compatible card image with rank and suit side by side.
    Rank and suit are rendered with separate fonts and centered horizontally."""
    width = config["widthImage"]
    height = config["heightImage"]
    rankFontPath = config["rankFont"]
    suitFontPath = config["suitFont"]
    rankSize = config["rankFontSize"]
    suitSize = config["suitFontSize"]

    img = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(img)
    fontRank = ImageFont.truetype(rankFontPath, rankSize)
    fontSuit = ImageFont.truetype(suitFontPath, suitSize)
    rw = d.textlength(rank, font=fontRank)
    sw = d.textlength(suit, font=fontSuit)
    total_w = rw + 10 + sw
    x = (width - total_w) / 2
    d.text((x, 24), rank, font=fontRank, fill="black")
    d.text((x + rw, 10), suit, font=fontSuit, fill="black")
    return img  








