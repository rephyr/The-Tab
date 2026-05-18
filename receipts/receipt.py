"""
base receipt
"""
from dataclasses import dataclass
from escpos.escpos import Escpos
from core.player import Player
from core.cards import Cards

COLS    = 32
IS_RED  = {"Hearts", "Diamonds"}


@dataclass
class Receipt:
    title: str
    player: Player

    def print(self, p: Escpos) -> None:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln(self.title)
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("=" * COLS)
        p.textln(f"Pelaaja : {self.player.getName()}")
        p.ln(3)
        p.cut()


@dataclass
class CardReceipt(Receipt):
    card: Cards
    phase: str
    guess: str

    def print(self, p: Escpos) -> None:
        p.set(align="center", bold=True, double_width=True, double_height=True)
        p.textln(self.title)
        p.set(align="left", bold=False, double_width=False, double_height=False)
        p.textln("=" * COLS)
        p.textln(f"Pelaaja : {self.player.getName()}")
        p.textln(f"Vaihe   : {self.phase}")
        p.textln(f"Arvaus  : {self.guess}")
        p.textln("-" * COLS)

        red = self.card.suit in IS_RED
        p.set(align="center", bold=True, double_width=True, double_height=True, invert=red)
        p.textln(str(self.card))
        p.set(align="center", bold=False, double_width=False, double_height=False, invert=False)

        p.textln("-" * COLS)
        p.textln(f"{self.card.suit}")
        p.ln(3)
        p.cut()

