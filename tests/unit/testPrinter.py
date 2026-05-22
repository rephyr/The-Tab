import unittest
from unittest.mock import MagicMock, patch
from printing.printer import ReceiptPrinter, CardAwareWrapper, FontWrapper


def _usbConfig(useCardImages=True, escposFont="a"):
    return {
        "connection": "usb",
        "vendorId": "0x4b43",
        "productId": "0x3830",
        "inEp": "0x81",
        "outEp": "0x03",
        "escposFont": escposFont,
        "useCardImages": useCardImages,
    }


@patch("printing.printer.ESCPOS_AVAILABLE", True)
@patch("printing.printer.Usb")
class TestUsbCardImages(unittest.TestCase):

    def test_card_images_applies_wrapper(self, MockUsb):
        MockUsb.return_value = MagicMock()
        printer = ReceiptPrinter(_usbConfig(useCardImages=True))
        printer._connect()
        self.assertIsInstance(printer._p, CardAwareWrapper)

    def test_no_card_images_skips_wrapper(self, MockUsb):
        MockUsb.return_value = MagicMock()
        printer = ReceiptPrinter(_usbConfig(useCardImages=False))
        printer._connect()
        self.assertNotIsInstance(printer._p, CardAwareWrapper)

    def test_font_wrapper_inside_card_wrapper(self, MockUsb):
        MockUsb.return_value = MagicMock()
        printer = ReceiptPrinter(_usbConfig(useCardImages=True, escposFont="b"))
        printer._connect()
        self.assertIsInstance(printer._p, CardAwareWrapper)
        self.assertIsInstance(printer._p._p, FontWrapper)

    def test_font_wrapper_without_card_images(self, MockUsb):
        MockUsb.return_value = MagicMock()
        printer = ReceiptPrinter(_usbConfig(useCardImages=False, escposFont="b"))
        printer._connect()
        self.assertIsInstance(printer._p, FontWrapper)
        self.assertNotIsInstance(printer._p, CardAwareWrapper)
